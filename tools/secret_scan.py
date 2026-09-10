#!/usr/bin/env python3
"""secret_scan.py — detect and redact credential-shaped strings in text before
it is persisted (a log, a commit message, a board file, a sweep doc).

The gap this closes (run 476, folding arXiv:2604.18658 "Owner-Harm"): every
check this project has built (gates.py, orphan_scan, kill_reconcile) verifies
whether an ACTION is permitted. None of them look at what a *permitted* action's
OUTPUT contains. On 2026-09-10 a legitimate, requested `cat config.yaml` printed
a live OAuth access token and refresh token into a diagnostic session's own tool
output — no policy violated, harm was in the output of a permitted action.

Design differs from orphan_scan/kill_reconcile on purpose: those are REPORT-only
(a caller decides). This one defaults to ACT (redact), because the asymmetry is
different — a false positive costs a few masked characters in a log; a false
negative costs a leaked credential. `scan()` alone is still pure/read-only for
callers who want to decide themselves.

PORTABILITY_CLASS: fixed-schema
"""
import re
import sys
from pathlib import Path

# Each pattern: (name, compiled regex). Deliberately specific prefixes/shapes
# over generic high-entropy heuristics — a named pattern gives an operator a
# specific "why", a bare entropy score does not (the ≥8-instance instrument
# rule: say what you found, not just that something looks suspicious).
_PATTERNS = [
    ("google_oauth_access_token", r"\bya29\.[A-Za-z0-9_-]{20,}\b"),
    ("google_oauth_refresh_token", r"\b1//0[A-Za-z0-9_-]{15,}\b"),
    ("google_api_key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("aws_access_key_id", r"\bAKIA[0-9A-Z]{16}\b"),
    ("github_token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("slack_token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ("bearer_header", r"\bBearer\s+[A-Za-z0-9._-]{20,}\b"),
    ("jwt_like", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    ("private_key_block", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ("generic_api_key_kv", r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]\s*"
                          r"['\"]?[A-Za-z0-9_\-\.]{20,}['\"]?"),
]
COMPILED = [(name, re.compile(pat)) for name, pat in _PATTERNS]


def _mask(s, keep=4):
    """Show enough to identify the finding without reproducing the secret."""
    if len(s) <= keep * 2:
        return "*" * len(s)
    return s[:keep] + ("*" * max(3, len(s) - keep * 2)) + s[-keep:]


def scan(text):
    """Pure, read-only. Returns a list of {pattern, start, end, masked}.
    Never returns the raw matched text — even the caller only sees a mask."""
    if not text:
        return []
    findings = []
    for name, rx in COMPILED:
        for m in rx.finditer(text):
            findings.append({
                "pattern": name,
                "start": m.start(),
                "end": m.end(),
                "masked": _mask(m.group(0)),
            })
    findings.sort(key=lambda f: f["start"])
    return findings


def redact(text, placeholder_fmt="[REDACTED:{name}]"):
    """Returns (clean_text, findings). Default action for anything that will be
    persisted. Overlap-safe: rebuilds left-to-right from non-overlapping spans.
    """
    findings = scan(text)
    if not findings:
        return text, []
    # drop any finding fully inside an earlier one (overlapping patterns)
    kept = []
    last_end = -1
    for f in findings:
        if f["start"] >= last_end:
            kept.append(f)
            last_end = f["end"]
    out, cursor = [], 0
    for f in kept:
        out.append(text[cursor:f["start"]])
        out.append(placeholder_fmt.format(name=f["pattern"]))
        cursor = f["end"]
    out.append(text[cursor:])
    return "".join(out), kept


def redact_file(path, in_place=False):
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    clean, findings = redact(text)
    if in_place and findings:
        p.write_text(clean, encoding="utf-8")
    return clean, findings


def _selftest():
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    # Fake-shaped but structurally realistic tokens, not any real credential.
    fake_oauth = "ya29." + "A" * 40
    fake_refresh = "1//0" + "b" * 30
    fake_ghp = "ghp_" + "x" * 40
    fake_aws = "AKIA" + "Q" * 16
    plain = "the quick brown fox jumps over the lazy dog, config.yaml line 12"

    # detection, one pattern at a time
    ck("detects google oauth access token",
       any(f["pattern"] == "google_oauth_access_token" for f in scan(fake_oauth)))
    ck("detects google oauth refresh token",
       any(f["pattern"] == "google_oauth_refresh_token" for f in scan(fake_refresh)))
    ck("detects github token", any(f["pattern"] == "github_token" for f in scan(fake_ghp)))
    ck("detects aws access key id", any(f["pattern"] == "aws_access_key_id" for f in scan(fake_aws)))

    # no false positive on ordinary text
    ck("plain text -> no findings", scan(plain) == [])

    # masking never reveals the full secret
    f = scan(fake_oauth)[0]
    ck("masked value is shorter than or equal to original and not equal to it",
       f["masked"] != fake_oauth and "*" in f["masked"])
    ck("masked value does not contain the full secret substring",
       fake_oauth not in f["masked"])

    # redact() removes the secret from the output text entirely
    mixed = "server:\n  host: 127.0.0.1\n  access_token: %s\n  refresh_token: %s\n" % (
        fake_oauth, fake_refresh)
    clean, found = redact(mixed)
    ck("redact() removes both secrets from the output text",
       fake_oauth not in clean and fake_refresh not in clean)
    ck("redact() reports what it found (2)", len(found) == 2)
    ck("redact() leaves non-secret structure intact",
       "host: 127.0.0.1" in clean and "server:" in clean)

    # multiple distinct secrets, overlapping-adjacent, all caught
    many = " ".join([fake_oauth, fake_ghp, fake_aws, fake_refresh])
    clean2, found2 = redact(many)
    ck("redact() catches 4 distinct secrets in one text", len(found2) == 4)
    ck("none of the 4 raw secrets survive redaction",
       not any(s in clean2 for s in (fake_oauth, fake_ghp, fake_aws, fake_refresh)))

    # idempotent: redacting already-redacted text finds nothing new
    clean3, found3 = redact(clean2)
    ck("redacting already-clean text finds nothing", found3 == [])

    # empty / None input never raises, never finds
    ck("empty string -> no findings, no crash", scan("") == [])
    ck("None input -> no findings, no crash", scan(None) == [])

    # sweep: token length must not flip detection (a threshold-on-length bug
    # would fail short/long real tokens differently - run-385 hazard)
    lens = []
    for n in range(15, 61, 5):
        t = "ya29." + "Z" * n
        lens.append(len(scan(t)) == (1 if n >= 20 else 0))
    ck("access-token length boundary behaves as documented (>=20 chars after prefix)",
       all(lens))

    ok = all(c for _, c in checks)
    for name, c in checks:
        print("  %-68s %s" % (name, "ok" if c else "FAIL"))
    print("secret_scan selftest: %d/%d %s"
          % (sum(1 for _, c in checks if c), len(checks), "GREEN" if ok else "RED"))
    return 0 if ok else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    if len(argv) > 1 and argv[1] == "scan" and len(argv) > 2:
        text = Path(argv[2]).read_text(encoding="utf-8", errors="replace")
        found = scan(text)
        if not found:
            print("clean: no secret-shaped strings found")
            return 0
        for f in found:
            print("%s at %d-%d: %s" % (f["pattern"], f["start"], f["end"], f["masked"]))
        return 1
    if len(argv) > 1 and argv[1] == "redact" and len(argv) > 2:
        in_place = "--in-place" in argv
        clean, found = redact_file(argv[2], in_place=in_place)
        if in_place:
            print("redacted %d finding(s) in place" % len(found))
        else:
            sys.stdout.write(clean)
        return 0
    print(__doc__.strip().splitlines()[0])
    print("usage: secret_scan.py [scan <file>|redact <file> [--in-place]|selftest]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
