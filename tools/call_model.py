#!/usr/bin/env python3
"""call_model - the single model seam for the whole loop (v2.0 connective piece).

Every probe adapter and `loop_conductor.run_worker` want the same thing:
`call_model(prompt: str) -> str`. This module is that seam, with a pluggable
backend so v2.0 ("provision a call_model budget") becomes one env var, not a
wiring project:

    AU_MODEL_BACKEND = fake      (default) - deterministic, offline, for tests + dry runs
                     = cli       - shell out to the local CLI-agent pool
                                  (C:\\Agents\\skills\\CLI-AGENT-CONTROL\\agentctl.sh),
                                  AU_MODEL_AGENT picks the agent (default agy3)
                     = callable  - a Python callable registered via register()/set_backend()

`judge(a, b, criterion)` is built on `call_model` for `probe_rho_holdout`.

The `fake` and `callable` paths are pure stdlib and never touch the network or a
subprocess - the selftest only exercises those. The `cli` path uses `subprocess`
to call an already-installed, already-authed local tool; it is strictly opt-in.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys

_REGISTERED: dict[str, object] = {}
_ACTIVE: object | None = None   # a callable set by set_backend(); overrides the env


def register(name: str, fn) -> None:
    """Register a named callable backend (e.g. an API-key client)."""
    _REGISTERED[str(name)] = fn


def set_backend(name_or_callable) -> None:
    """Force a backend for this process. Pass a name ('fake'/'cli'/a registered
    name) or a callable(prompt)->str. `None` reverts to the AU_MODEL_BACKEND env."""
    global _ACTIVE
    if name_or_callable is None:
        _ACTIVE = None
    elif callable(name_or_callable):
        _ACTIVE = name_or_callable
    else:
        _ACTIVE = _resolve(str(name_or_callable))


def _fake(prompt: str) -> str:
    """Deterministic offline stand-in. Echoes a short digest + a canned shape so
    downstream parsers get *something* structured without any model."""
    h = hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8]
    p = (prompt or "").lower()
    if "yes" in p and "no" in p and "?" in p:
        return "no"                       # relay adapters: fail safe = don't forward
    if "which is better" in p or "\na:" in p and "\nb:" in p:
        return "A"                        # judge default
    if "{" in prompt and "}" in prompt:
        return "[]"                       # proposer: empty list -> heuristic fallback
    return f"[fake:{h}] no action"        # idle-agent: unparseable -> idle_noop


def _cli_backend(prompt: str) -> str:
    agent = os.environ.get("AU_MODEL_AGENT", "agy3")
    script = os.environ.get(
        "AU_AGENTCTL", r"C:\Agents\skills\CLI-AGENT-CONTROL\agentctl.sh")
    model = os.environ.get("AU_MODEL_NAME", "")
    cmd = ["bash", script, "run", agent]
    if model:
        cmd += ["--model", model]
    cmd += [prompt]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=float(os.environ.get("AU_MODEL_TIMEOUT", "180")))
        return (r.stdout or "").strip() or (r.stderr or "").strip()
    except Exception as e:                 # pragma: no cover - opt-in path
        return f"[cli-error: {e}]"


def _resolve(name: str):
    name = (name or "fake").strip().lower()
    if name in _REGISTERED:
        return _REGISTERED[name]
    if name == "cli":
        return _cli_backend
    return _fake


def _backend():
    if _ACTIVE is not None:
        return _ACTIVE
    return _resolve(os.environ.get("AU_MODEL_BACKEND", "fake"))


def call_model(prompt: str) -> str:
    """The seam. Routes to the active backend; any backend error is returned as a
    string starting with '[' so downstream fail-safe parsers treat it as garbage."""
    try:
        out = _backend()(prompt)
        return out if isinstance(out, str) else str(out)
    except Exception as e:
        return f"[call_model-error: {e}]"


def judge(text_a: str, text_b: str, *, criterion: str = "which is the better response") -> str:
    """`judge(a, b) -> "A" | "B"` for probe_rho_holdout. Built on call_model; a
    non-A/B reply defaults to 'A' (the incumbent), matching the adapter's tie rule."""
    prompt = (f"{criterion}? Answer with exactly 'A' or 'B'.\n\n"
              f"A:\n{text_a}\n\nB:\n{text_b}\n")
    reply = (call_model(prompt) or "").strip().upper()
    m = re.search(r"\b([AB])\b", reply)
    return m.group(1) if m else "A"


class scripted:
    """Context manager: `with scripted(['a', 'b']): ...` or
    `with scripted(lambda p: ...): ...` forces a backend for the block."""
    def __init__(self, replies):
        if callable(replies):
            self._fn = replies
        else:
            self._it = iter(replies)
            self._fn = lambda _p: next(self._it, "")
        self._prev = None

    def __enter__(self):
        global _ACTIVE
        self._prev = _ACTIVE
        _ACTIVE = self._fn
        return self

    def __exit__(self, *exc):
        global _ACTIVE
        _ACTIVE = self._prev


def _selftest():
    checks = {}
    set_backend(None)
    checks["default backend is the offline fake"] = call_model("hello").startswith("[fake:")
    checks["fake is deterministic"] = call_model("x") == call_model("x")
    checks["fake fails safe on a yes/no forward question"] = call_model("forward? yes or no?") == "no"

    with scripted(["B", "A", "not-a-letter"]):
        checks["scripted replies are consumed in order"] = (
            call_model("1") == "B" and call_model("2") == "A")
        checks["judge parses a scripted A/B"] = judge("x", "y") == "A"  # next reply "not-a-letter" -> "A"
    checks["scripted context restores the previous backend"] = call_model("z").startswith("[fake:")

    register("myapi", lambda p: f"echo:{p[:3]}")
    set_backend("myapi")
    checks["a registered callable backend is used"] = call_model("hello") == "echo:hel"
    set_backend(lambda p: 12345)
    checks["a non-str backend result is coerced to str"] = call_model("q") == "12345"
    set_backend(lambda p: (_ for _ in ()).throw(RuntimeError("boom")))
    checks["a backend exception becomes a '[' string, not a crash"] = (
        call_model("q").startswith("[call_model-error:"))
    set_backend(None)

    # judge default when the backend gives nothing usable
    with scripted(lambda p: "maybe"):
        checks["judge defaults to A (the incumbent) on an unparseable reply"] = judge("a", "b") == "A"

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    a = sub.add_parser("ask"); a.add_argument("prompt")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "ask":
        print(call_model(args.prompt))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
