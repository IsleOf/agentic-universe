#!/usr/bin/env python3
"""commit_guard.py — scan the staged diff and commit message for credential-
shaped content before `git commit` runs, and refuse if it finds any.

Closes run 477's own "Next": secret_scan.py existed but nothing called it.
This is the natural boundary — right before a commit makes something permanent
in history — and it is REPORT-only like orphan_scan/kill_reconcile, not
auto-redact like secret_scan.redact(): a git diff is structured (hunks, line
numbers) and rewriting it post-hoc risks producing a diff that no longer
applies. The right fix for a diff with a secret in it is to fix the SOURCE FILE
and re-stage, not to patch the diff text. So this refuses and names the file.

Usage (before every `git commit -F <msgfile>`):
    python tools/commit_guard.py check --message-file <msgfile>
exit 0 = clean, proceed. exit 3 = blocked, findings printed.

PORTABILITY_CLASS: fixed-schema
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from secret_scan import scan  # noqa: E402


def staged_diff(cwd="."):
    """The exact content about to become a permanent commit. Returns None if
    git is unavailable (an instrument that can't measure must say so)."""
    try:
        r = subprocess.run(["git", "-C", str(cwd), "diff", "--cached"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def check(cwd=".", message="", diff=None):
    """(ok, reason, findings). ok=False iff the staged diff or the commit
    message contains a credential-shaped string. `diff` can be injected for
    testing without a real git repo.
    """
    d = staged_diff(cwd) if diff is None else diff
    if d is None:
        return False, "could not read staged diff — cannot confirm clean", []
    findings = scan(d) + [dict(f, in_="message") for f in scan(message)]
    if not findings:
        return True, "clean", []
    by_pattern = {}
    for f in findings:
        by_pattern.setdefault(f["pattern"], 0)
        by_pattern[f["pattern"]] += 1
    summary = ", ".join("%s x%d" % (k, v) for k, v in sorted(by_pattern.items()))
    return False, ("BLOCKED: credential-shaped content in the staged diff or "
                   "message (%s) — fix the source file and re-stage, do not "
                   "just edit the commit message" % summary), findings


def _selftest():
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    fake_oauth = "ya29." + "A" * 40

    ok, why, found = check(diff="+ hello world\n+ print('fine')\n", message="normal commit")
    ck("clean diff + message -> ok", ok and why == "clean")

    ok, why, found = check(
        diff="+  access_token: %s\n" % fake_oauth, message="normal commit")
    ck("secret in diff -> blocked", not ok and "BLOCKED" in why)
    ck("blocked reason names the pattern", "google_oauth_access_token" in why)
    # the line also matches generic_api_key_kv ("access_token: <20+ chars>") -
    # both real findings on the same secret, not a bug; assert non-empty and
    # that the specific pattern fired, not an exact count.
    ck("findings are returned", len(found) >= 1)
    ck("finding never carries the raw secret", fake_oauth not in str(found))

    ok, why, found = check(diff="+ fine\n", message="oops token=%s" % fake_oauth)
    ck("secret in MESSAGE (not diff) also blocked", not ok)
    ck("message-origin finding tagged in_=message",
       any(f.get("in_") == "message" for f in found))

    # multiple findings summarised, not just the first
    two = "+ %s\n+ AKIA%s\n" % (fake_oauth, "Q" * 16)
    ok, why, found = check(diff=two, message="")
    ck("multiple distinct patterns all counted", len(found) == 2)
    ck("summary names both patterns",
       "google_oauth_access_token" in why and "aws_access_key_id" in why)

    # git unreadable -> blocked, not a silent pass
    import unittest.mock as mock
    with mock.patch("commit_guard.staged_diff", return_value=None):
        ok, why, found = check(cwd="/definitely/not/a/repo")
    ck("git unreadable -> blocked, not a silent pass",
       not ok and "cannot confirm clean" in why)

    ok_all = all(c for _, c in checks)
    for name, c in checks:
        print("  %-56s %s" % (name, "ok" if c else "FAIL"))
    print("commit_guard selftest: %d/%d %s"
          % (sum(1 for _, c in checks if c), len(checks),
             "GREEN" if ok_all else "RED"))
    return 0 if ok_all else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    if len(argv) > 1 and argv[1] == "check":
        msg = ""
        if "--message-file" in argv:
            mf = argv[argv.index("--message-file") + 1]
            msg = Path(mf).read_text(encoding="utf-8", errors="replace")
        ok, why, found = check(message=msg)
        print(why)
        for f in found:
            print("   %s at %d-%d (%s): %s" % (
                f["pattern"], f["start"], f["end"], f.get("in_", "diff"), f["masked"]))
        return 0 if ok else 3
    print(__doc__.strip().splitlines()[0])
    print("usage: commit_guard.py [check [--message-file F]|selftest]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
