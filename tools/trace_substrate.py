#!/usr/bin/env python3
"""Phase 0 trace substrate for the Agentic Universe.

The measurement layer everything else in `docs/self_improving_harness_plan.md`
depends on. Records swarm activity as an append-only JSONL event stream that
(a) carries the Five-W fields for every inter-agent message
(`pattern_five_w_message_instrumentation`), (b) records every tool call, its
outcome, and its token cost per step, and (c) is scrubbed of secrets before it
is ever written.

Design constraints taken from the graph:
- `pattern_five_w_message_instrumentation`: sender, receiver, content class,
  timestamp, declared purpose *at the call site*, channel. All six required on
  a MESSAGE event.
- `concept_the_harness_context_assembly_is_a_privilege_escalation_vector`
  (arXiv:2608.27299, run 200): a MESSAGE may optionally carry `instruction_level`
  (the level the content occupies in the assembled context) and `source_level`
  (its origin's level). If the former outranks the latter, the validator flags a
  MessageRole-CPE — content promoted above its provenance.
- `concept_emergence_layer_model`: every event names the layer it belongs to
  (llm / harness / swarm) and the interaction language, so a swarm result that
  one agent in a loop reproduced can be told apart from a real one, and an
  English-only result can be told apart from a cross-lingual one
  (`concept_interaction_language_shifts_emergence`, run 47).
- `pattern_evidential_ancestry_tracking` (run 52): a report/claim event carries
  its evidence roots, so aggregation can dedupe by source rather than by agent
  count.
- operating rule 9: raw artifacts are scrubbed before commit — no credentials,
  API keys, cookies, browser profiles, or personal data.

Pure stdlib. No network. Import `Recorder` from a harness, or run this file to
self-check the schema.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "runtime" / "traces"

SCHEMA_VERSION = "phase0.1"

# --- event kinds ------------------------------------------------------------

EVENT_KINDS = {
    "MESSAGE",   # one agent addressing another (or the human) — Five-W required
    "TOOL_CALL",  # an agent invoking a tool/skill/sub-agent
    "TOOL_RESULT",  # the outcome of a TOOL_CALL, linked by call_id
    "STEP",      # a bounded unit of work opened/closed by an agent
    "CLAIM",     # an agent asserting a result, with evidence roots
    "ARTIFACT",  # a write to the shared artifact store (stigmergic channel)
    "SPAWN",     # an agent creating a sub-agent
    "NOTE",      # free-form observer annotation; never load-bearing
}

LAYERS = {"llm", "harness", "swarm"}

# content classes for MESSAGE events — deliberately small and behavioural
CONTENT_CLASSES = {
    "task", "result", "question", "answer", "critique", "proposal",
    "coordination", "status", "refusal", "escalation", "other",
}

# instruction-hierarchy levels, most→least privileged
# (concept_the_harness_context_assembly_is_a_privilege_escalation_vector,
# arXiv:2608.27299, run 200). OPTIONAL on a MESSAGE: `instruction_level` is the
# level the content occupies in the assembled context; `source_level` is the
# level of its origin. If both are present and `instruction_level` outranks
# `source_level`, the validator flags a MessageRole-CPE shape — content promoted
# above its provenance.
INSTRUCTION_LEVELS = ("system", "developer", "user", "tool", "retrieved", "untrusted")
_ILEVEL_RANK = {lv: i for i, lv in enumerate(INSTRUCTION_LEVELS)}

REQUIRED_COMMON = ("event_id", "seq", "ts", "kind", "run_id", "actor", "layer", "language")
REQUIRED_BY_KIND = {
    "MESSAGE": ("sender", "receiver", "content_class", "declared_purpose", "channel"),
    "TOOL_CALL": ("call_id", "tool", "declared_purpose"),
    "TOOL_RESULT": ("call_id", "ok"),
    "STEP": ("step_id", "phase"),      # phase in {open, close}
    "CLAIM": ("claim", "evidence_roots"),
    "ARTIFACT": ("path", "op"),         # op in {write, append, delete}
    "SPAWN": ("child_actor",),
    "NOTE": ("text",),
}

# --- scrubbing -------------------------------------------------------------

_SECRET_PATTERNS = [
    re.compile(r"(?i)\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|bearer)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"),  # email -> personal data
]
_REDACTED = "[REDACTED]"


def scrub(value):
    """Recursively redact anything that looks like a secret or personal datum."""
    if isinstance(value, str):
        out = value
        for pat in _SECRET_PATTERNS:
            out = pat.sub(_REDACTED, out)
        return out
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


# --- validation -----------------------------------------------------------

def validate_event(ev):
    """Return a list of error strings ([] means valid)."""
    errors = []
    if not isinstance(ev, dict):
        return ["event must be an object"]
    kind = ev.get("kind")
    if kind not in EVENT_KINDS:
        errors.append(f"unknown kind: {kind!r}")
    for key in REQUIRED_COMMON:
        if ev.get(key) in (None, ""):
            errors.append(f"missing required field: {key}")
    if not isinstance(ev.get("seq"), int) or isinstance(ev.get("seq"), bool) or ev.get("seq", 0) < 0:
        errors.append("seq must be a non-negative integer")
    if ev.get("layer") not in LAYERS and "layer" not in [e.split(": ")[-1] for e in errors]:
        errors.append(f"layer must be one of {sorted(LAYERS)}, got {ev.get('layer')!r}")
    for key in REQUIRED_BY_KIND.get(kind, ()):  # type: ignore[arg-type]
        if ev.get(key) in (None, ""):
            errors.append(f"{kind} missing required field: {key}")
    if kind == "MESSAGE" and ev.get("content_class") not in CONTENT_CLASSES:
        errors.append(f"content_class must be one of {sorted(CONTENT_CLASSES)}")
    if kind == "MESSAGE":
        il, sl = ev.get("instruction_level"), ev.get("source_level")
        for name, v in (("instruction_level", il), ("source_level", sl)):
            if v is not None and v not in _ILEVEL_RANK:
                errors.append(f"{name} must be one of {list(INSTRUCTION_LEVELS)}, got {v!r}")
        if il in _ILEVEL_RANK and sl in _ILEVEL_RANK and _ILEVEL_RANK[il] < _ILEVEL_RANK[sl]:
            errors.append(f"instruction-privilege escalation: content at level {il!r} "
                          f"originated at {sl!r} (MessageRole-CPE, arXiv:2608.27299)")
    if kind == "STEP" and ev.get("phase") not in ("open", "close"):
        errors.append("STEP.phase must be 'open' or 'close'")
    if kind == "CLAIM":
        roots = ev.get("evidence_roots")
        if not isinstance(roots, list) or not roots:
            errors.append("CLAIM.evidence_roots must be a non-empty list")
    if kind in ("TOOL_CALL", "TOOL_RESULT") and "token_cost" in ev:
        tc = ev["token_cost"]
        if not isinstance(tc, dict) or not {"in", "out"} <= set(tc):
            errors.append("token_cost must be {'in': int, 'out': int}")
    return errors


def validate_trace(path):
    """Validate a JSONL trace file. Returns (n_events, errors)."""
    errors = []
    seen_ids = set()
    n = 0
    with Path(path).open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: bad JSON ({exc})")
                continue
            for err in validate_event(ev):
                errors.append(f"line {lineno}: {err}")
            eid = ev.get("event_id")
            if eid in seen_ids:
                errors.append(f"line {lineno}: duplicate event_id {eid}")
            seen_ids.add(eid)
    return n, errors


# --- recorder ------------------------------------------------------------

class Recorder:
    """Append-only trace writer. One instance per run.

    Every public method returns the event dict it wrote, so a caller can link
    events (a TOOL_RESULT to its TOOL_CALL, a close STEP to its open).
    """

    def __init__(self, run_id=None, layer="swarm", language="en",
                 trace_dir=TRACE_DIR, sink=None, harness_manifest=None):
        self.run_id = run_id or f"run-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        self.layer = layer
        self.language = language
        self._sink = sink
        self._own_sink = False
        self._seq = 0
        if sink is None:
            trace_dir = Path(trace_dir)
            trace_dir.mkdir(parents=True, exist_ok=True)
            self._path = trace_dir / f"{self.run_id}.jsonl"
            self._sink = self._path.open("a", encoding="utf-8")
            self._own_sink = True
        else:
            self._path = None
        # tie the run to a harness state (Phase 1): stamp the manifest hash so a
        # result can be attributed to the exact component versions that produced it
        if harness_manifest is not None:
            self.emit("NOTE", actor="harness", text="harness manifest",
                      harness_manifest=harness_manifest)

    # -- low level --
    def emit(self, kind, actor, **fields):
        ev = {
            "event_id": uuid.uuid4().hex,
            "seq": self._seq,          # monotonic per run — the reliable order key
            "ts": round(time.time(), 6),
            "schema": SCHEMA_VERSION,
            "kind": kind,
            "run_id": self.run_id,
            "actor": actor,
            "layer": fields.pop("layer", self.layer),
            "language": fields.pop("language", self.language),
        }
        ev.update({k: v for k, v in fields.items() if v is not None})
        ev = scrub(ev)
        errs = validate_event(ev)
        if errs:
            raise ValueError(f"invalid {kind} event: {errs}")
        self._sink.write(json.dumps(ev, ensure_ascii=False) + "\n")
        self._sink.flush()
        self._seq += 1
        return ev

    # -- Five-W message --
    def message(self, sender, receiver, content_class, declared_purpose,
                channel, body=None, **extra):
        return self.emit(
            "MESSAGE", actor=sender, sender=sender, receiver=receiver,
            content_class=content_class, declared_purpose=declared_purpose,
            channel=channel, body=body, **extra,
        )

    def tool_call(self, actor, tool, declared_purpose, args=None, **extra):
        call_id = uuid.uuid4().hex
        self.emit("TOOL_CALL", actor=actor, call_id=call_id, tool=tool,
                  declared_purpose=declared_purpose, args=args, **extra)
        return call_id

    def tool_result(self, actor, call_id, ok, summary=None, token_cost=None, **extra):
        return self.emit("TOOL_RESULT", actor=actor, call_id=call_id, ok=bool(ok),
                         summary=summary, token_cost=token_cost, **extra)

    def step(self, actor, step_id, phase, **extra):
        return self.emit("STEP", actor=actor, step_id=step_id, phase=phase, **extra)

    def claim(self, actor, claim, evidence_roots, **extra):
        return self.emit("CLAIM", actor=actor, claim=claim,
                         evidence_roots=list(evidence_roots), **extra)

    def artifact(self, actor, path, op, **extra):
        return self.emit("ARTIFACT", actor=actor, path=path, op=op, **extra)

    def spawn(self, actor, child_actor, **extra):
        return self.emit("SPAWN", actor=actor, child_actor=child_actor, **extra)

    def note(self, actor, text, **extra):
        return self.emit("NOTE", actor=actor, text=text, **extra)

    def close(self):
        if self._own_sink and self._sink:
            self._sink.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# --- cli ---------------------------------------------------------------

def _cli(argv=None):
    parser = argparse.ArgumentParser(description="Phase 0 trace substrate.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="validate a JSONL trace file")
    v.add_argument("path")
    sub.add_parser("selftest", help="write a tiny trace to a memory buffer and validate it")
    args = parser.parse_args(argv)

    if args.cmd == "validate":
        n, errors = validate_trace(args.path)
        if errors:
            print(f"INVALID ({n} events, {len(errors)} problems)")
            for e in errors[:50]:
                print("  " + e)
            return 1
        print(f"VALID ({n} events)")
        return 0

    if args.cmd == "selftest":
        import io
        buf = io.StringIO()
        rec = Recorder(run_id="selftest", sink=buf)
        s = rec.step("planner", "s1", "open", phase_note="split the task")
        rec.message("planner", "worker-a", "task", "delegate subtask 1", "direct",
                    body="compute the VAT for invoice 42; secret=hunter2")
        cid = rec.tool_call("worker-a", "python", "run the VAT calc")
        rec.tool_result("worker-a", cid, ok=True, summary="VAT=8.40",
                        token_cost={"in": 1200, "out": 40})
        rec.claim("worker-a", "VAT for invoice 42 is 8.40", ["invoice-42.pdf"])
        rec.message("worker-a", "planner", "result", "report subtask 1 done", "direct")
        rec.step("planner", "s1", "close")
        rec.close()
        text = buf.getvalue()
        # validate from the buffer
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text)
            tmp = fh.name
        n, errors = validate_trace(tmp)
        os.unlink(tmp)
        redacted = "[REDACTED]" in text and "hunter2" not in text

        # instruction-privilege-escalation check (run 200): a clean level pair
        # validates; a promoted one is flagged
        clean_ok = validate_event({
            "event_id": "x", "seq": 0, "ts": 1.0, "kind": "MESSAGE", "run_id": "r", "actor": "a",
            "layer": "harness", "language": "en", "sender": "a", "receiver": "b",
            "content_class": "task", "declared_purpose": "p", "channel": "direct",
            "instruction_level": "user", "source_level": "user"}) == []
        cpe_flagged = any("privilege escalation" in e for e in validate_event({
            "event_id": "x", "seq": 0, "ts": 1.0, "kind": "MESSAGE", "run_id": "r", "actor": "a",
            "layer": "harness", "language": "en", "sender": "a", "receiver": "b",
            "content_class": "task", "declared_purpose": "p", "channel": "direct",
            "instruction_level": "system", "source_level": "retrieved"}))

        print(text.rstrip())
        print("---")
        print(f"events: {n}  errors: {len(errors)}  secret_scrubbed: {redacted}  "
              f"cpe_check: clean_ok={clean_ok} flagged={cpe_flagged}")
        ok = not errors and redacted and n == 7 and clean_ok and cpe_flagged
        print("SELFTEST", "GREEN" if ok else "RED")
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    sys.exit(_cli())
