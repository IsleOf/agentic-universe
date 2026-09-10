#!/usr/bin/env python3
"""orphan_scan.py - find sessions that outlived whatever should have ended them.

Built after 2026-09-10, when four independent instances of one failure appeared on a
single machine within hours (see docs/CONSOLIDATION_PLAN.md 6.4):

  1. a CLI agent outlived its PARENT   (front-end closed; child kept running ~8.4h CPU)
  2. three sessions outlived their PROMPT ("reply READY only, do nothing" -> 213% CPU)
  3. four browser daemons outlived their TASK (52-60 chrome children, ~5h)
  4. a killed agent's file writes outlived their PROCESS

None was a crash. Nothing errored, nothing alerted. They were found only by manual
/proc inspection during a resource crisis. This module makes that inspection repeatable.

DESIGN, following the house rules:

* **REPORT, never block or kill.** Same posture as tools/gates.py: this returns signals
  for a human or a supervisor to act on. It has no kill path and never will - a scanner
  that can reap is a scanner whose false positives are unrecoverable.
* **Pure function + separate collector.** `classify()` takes a list of plain dicts, so it
  is testable without a real /proc. `collect_linux()` is the only part that touches the
  system, and it is not exercised by the selftest.
* **Rates, not absolutes.** Context switches are scored per-second, because an absolute
  count is just a function of uptime (the run-385 hazard: a threshold on an aggregate is
  a function of every parameter the aggregate depends on - scale it, don't fix it).
* **An instrument that cannot measure must say so.** A process missing the fields a
  signal needs yields UNKNOWN for that signal, never a confident default.

PORTABILITY_CLASS: fixed-schema
"""
import json
import os
import sys

# --- signal names -----------------------------------------------------------------
ORPHANED = "orphaned"            # parent is gone; reparented to init
STALE = "stale"                  # older than the age budget for its kind
SPINNING = "spinning"            # context-switch rate far above its cohort
IDLE_PROMPTED_BUT_BUSY = "idle_prompted_but_busy"  # told to do nothing; using real CPU
UNKNOWN = "unknown"              # required fields absent - say so, don't guess

# Phrases that mark a session whose prompt forbids work. Matched case-insensitively.
_DO_NOTHING_MARKERS = (
    "reply ready only",
    "do not research",
    "session bootstrap",
    "do nothing",
)

DEFAULTS = {
    "max_age_s": 3600.0,      # a session older than this is stale unless whitelisted
    "spin_ctx_per_s": 20.0,   # voluntary ctx switches/sec above which we call it spinning
    "idle_cpu_pct": 5.0,      # CPU% above which a do-nothing session is contradicting itself
}


def _has(p, *keys):
    return all(k in p and p[k] is not None for k in keys)


def in_scope(p, session_patterns):
    """Is this process a CLAIMED SESSION, or just something running on the box?

    Added after the module's own first live run flagged systemd, cron, dbus-daemon,
    agetty, tailscaled and rsyslogd as orphaned+stale. They are none of those things:
    ppid=1 is correct for a daemon and 12h uptime is its job.

    That failure IS the run-386/387 hazard (the fix for a defect carrying the defect):
    a tool for finding "sessions that should have ended" that cannot tell a session
    from a daemon has no concept of *should*. The scope is therefore not a filter
    bolted on afterwards - it is the definition the signals depend on. Every signal
    below is meaningful ONLY inside it.

    Related: concept_an_instrument_must_declare_which_corpus_it_measured. `report()`
    prints the scope it used, so the output always says what it looked at.
    """
    blob = ((p.get("cmdline") or "") + " " + (p.get("comm") or "")).lower()
    return any(pat.lower() in blob for pat in session_patterns)


# Processes that count as agent sessions. Deliberately explicit: an empty or
# over-broad scope is how this module produced its first, useless output.
SESSION_PATTERNS = (
    "agy", "agy-real", "claude", "codex", "opencode", "gemini",
    "browser_use", "skill_cli.daemon", "hermes", "ollama",
)

# Long-lived infrastructure that MATCHES a session pattern but is not a session.
# 2026-09-10: three VS Code Codex extension servers (.vscode-server/extensions/
# openai.chatgpt-*) were reaped by hand because they matched "codex" and were
# flagged `stale` - which means nothing but "older than the age budget", which is
# normal for an editor language server. They were the live working agents for
# poster-studio and poly-bot. Both editors died.
#
# `stale` alone is NEVER grounds to reap. It is an age fact, not a fault.
NEVER_REAP_MARKERS = (
    ".vscode-server/extensions",   # editor language/extension servers
    "vscode-server/bin",
    "--type=extensionHost",
    "language-server",
    "lsp-server",
)

# Signals that indicate an actual fault, as opposed to mere age. A reaper MUST
# require at least one of these; see is_reapable().
FAULT_SIGNALS = (SPINNING, IDLE_PROMPTED_BUT_BUSY)


def is_reapable(entry, min_age_s=7200.0):
    """Would a reaper be justified in killing this? Conservative by construction.

    Requires ALL of:
      - at least one FAULT signal (spinning / idle-prompted-but-busy) - age alone
        is never enough, that is the 2026-09-10 mistake
      - STALE as well (a fault in a young process may just be startup)
      - age > min_age_s
      - not matching NEVER_REAP_MARKERS

    Returns (bool, reason).
    """
    cmd = (entry.get("cmdline") or "") + " " + (entry.get("comm") or "")
    for m in NEVER_REAP_MARKERS:
        if m in cmd:
            return False, "protected: matches %r" % m
    sig = entry.get("signals", [])
    faults = [s for s in sig if s in FAULT_SIGNALS]
    if not faults:
        return False, "no fault signal (stale alone is an age fact, not a fault)"
    if STALE not in sig:
        return False, "fault present but not stale - may be starting up"
    age = entry.get("detail", {}).get("age_s")
    if age is None:
        return False, "age unknown - refusing to reap"
    if age <= min_age_s:
        return False, "age %.0fs <= %.0fs budget" % (age, min_age_s)
    return True, "stale + %s + age %.0fs" % (",".join(faults), age)


def classify(procs, now_s, max_age_s=None, spin_ctx_per_s=None, idle_cpu_pct=None,
             session_patterns=SESSION_PATTERNS):
    """Classify a list of process dicts. Returns {pid: {signals, detail}}.

    Each proc dict may carry: pid, ppid, comm, cmdline, start_s, cpu_pct,
    voluntary_ctxt, rss_kb. Missing fields degrade that signal to UNKNOWN rather
    than producing a confident wrong answer.

    Only processes matching `session_patterns` are classified; everything else is
    returned with signals=[] and detail={"out_of_scope": True}. See in_scope().
    """
    max_age_s = DEFAULTS["max_age_s"] if max_age_s is None else max_age_s
    spin = DEFAULTS["spin_ctx_per_s"] if spin_ctx_per_s is None else spin_ctx_per_s
    idle_cpu = DEFAULTS["idle_cpu_pct"] if idle_cpu_pct is None else idle_cpu_pct

    out = {}
    for p in procs:
        if not in_scope(p, session_patterns):
            out[p["pid"]] = {"signals": [], "detail": {"out_of_scope": True},
                             "comm": p.get("comm"), "cmdline": p.get("cmdline")}
            continue

        signals, detail = [], {}

        # --- orphaned: reparented to init while still running.
        # Only meaningful in scope: a daemon SHOULD have ppid=1.
        if _has(p, "ppid"):
            if p["ppid"] == 1:
                signals.append(ORPHANED)
                detail["orphaned"] = "ppid=1 (reparented; original parent exited)"
        else:
            signals.append(UNKNOWN + ":orphaned")

        # --- stale: outlived its age budget
        if _has(p, "start_s"):
            age = now_s - p["start_s"]
            detail["age_s"] = age
            if age > max_age_s:
                signals.append(STALE)
        else:
            signals.append(UNKNOWN + ":stale")

        # --- spinning: ctx-switch RATE, not count (count is a function of uptime)
        if _has(p, "voluntary_ctxt", "start_s"):
            age = max(now_s - p["start_s"], 1.0)
            rate = p["voluntary_ctxt"] / age
            detail["ctx_per_s"] = rate
            if rate > spin:
                signals.append(SPINNING)
        else:
            signals.append(UNKNOWN + ":spinning")

        # --- a do-nothing prompt burning real CPU contradicts itself
        # NOTE the elif chain here was a silent gap in the first version: with a
        # cmdline present but cpu_pct None, it emitted neither a signal nor an
        # UNKNOWN - the exact "instrument that can't measure its input returns
        # nothing and says nothing" failure this module claims to detect. Now the
        # do-nothing prompt is recorded whenever cmdline is readable, and the
        # verdict degrades to UNKNOWN whenever the CPU reading it needs is absent.
        if _has(p, "cmdline"):
            low = p["cmdline"].lower()
            if any(m in low for m in _DO_NOTHING_MARKERS):
                detail["do_nothing_prompt"] = True
                if _has(p, "cpu_pct"):
                    if p["cpu_pct"] > idle_cpu:
                        signals.append(IDLE_PROMPTED_BUT_BUSY)
                else:
                    signals.append(UNKNOWN + ":idle_prompted")
        else:
            signals.append(UNKNOWN + ":idle_prompted")

        out[p["pid"]] = {"signals": signals, "detail": detail,
                         "comm": p.get("comm"), "cmdline": p.get("cmdline")}
    return out


def collect_linux(proc_root="/proc", clk_tck=None, boot_s=0.0, now_s=None):
    """Read /proc into the dict shape classify() expects. Linux/WSL only.

    Not covered by selftest: it touches the real filesystem. Its output shape is
    what the selftest exercises, via synthetic dicts.
    """
    if clk_tck is None:
        clk_tck = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
    procs = []
    for name in os.listdir(proc_root):
        if not name.isdigit():
            continue
        d = os.path.join(proc_root, name)
        try:
            with open(os.path.join(d, "stat")) as f:
                stat = f.read()
            rp = stat.rfind(")")
            fields = stat[rp + 2:].split()
            ppid = int(fields[1])
            utime = int(fields[11])
            stime = int(fields[12])
            starttime = int(fields[19])
            with open(os.path.join(d, "cmdline")) as f:
                cmdline = f.read().replace("\0", " ").strip()
            with open(os.path.join(d, "comm")) as f:
                comm = f.read().strip()
            vol = None
            with open(os.path.join(d, "status")) as f:
                for line in f:
                    if line.startswith("voluntary_ctxt_switches:"):
                        vol = int(line.split()[1])
                        break
        except (IOError, OSError, IndexError, ValueError):
            continue
        start_s = boot_s + starttime / float(clk_tck)
        # Lifetime-average CPU%, not instantaneous. Added after the first live scan
        # reported unknown:idle_prompted for the single worst process on the box
        # (213.9% CPU): the signal that would have caught it needed a CPU reading
        # this collector was not taking. A lifetime average understates a recent
        # burst and overstates a finished one - it is the cheap single-read
        # approximation, and `cpu_pct_kind` says so rather than letting a caller
        # assume otherwise.
        age = max((now_s or 0.0) - start_s, 1.0) if now_s else None
        cpu_pct = None
        if age:
            cpu_pct = 100.0 * ((utime + stime) / float(clk_tck)) / age
        procs.append({
            "pid": int(name), "ppid": ppid, "comm": comm, "cmdline": cmdline,
            "start_s": start_s, "voluntary_ctxt": vol,
            "cpu_pct": cpu_pct, "cpu_pct_kind": "lifetime_average",
            "rss_kb": None,
        })
    return procs


def report(classified, only_flagged=True, session_patterns=SESSION_PATTERNS):
    """Render classify() output as text lines, declaring the corpus it measured.

    The header is not decoration: this module's first live output was useless
    precisely because its scope was everything. An instrument must declare which
    corpus it measured.
    """
    n_scope = sum(1 for c in classified.values()
                  if not c["detail"].get("out_of_scope"))
    lines = ["scope: %d/%d processes matched session patterns %s"
             % (n_scope, len(classified), ",".join(session_patterns))]
    if n_scope == 0 and classified:
        lines.append("  (nothing in scope - this is a statement about the scope, "
                     "not evidence that the box is clean)")
    for pid in sorted(classified):
        c = classified[pid]
        if c["detail"].get("out_of_scope"):
            continue
        real = [s for s in c["signals"] if not s.startswith(UNKNOWN)]
        if only_flagged and not real:
            continue
        det = c["detail"]
        bits = []
        if "age_s" in det:
            bits.append("age=%.0fs" % det["age_s"])
        if "ctx_per_s" in det:
            bits.append("ctx/s=%.1f" % det["ctx_per_s"])
        lines.append("pid %-7s %-16s [%s] %s" % (
            pid, (c["comm"] or "?")[:16], ",".join(c["signals"]), " ".join(bits)))
    return lines


# --- selftest ---------------------------------------------------------------------

def _selftest():
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    now = 100000.0
    # every in-scope fixture must match SESSION_PATTERNS; "x" would be out of scope
    S = "agy-real"

    # 0. SCOPE - the regression that motivated this module's rewrite.
    # Its first live run flagged systemd/cron/dbus-daemon/agetty/tailscaled as
    # orphaned+stale. They must now be silent, and for the right reason.
    daemons = [
        {"pid": 100, "ppid": 1, "comm": "systemd", "cmdline": "/sbin/init",
         "start_s": now - 45818, "voluntary_ctxt": 18000, "cpu_pct": 0.4},
        {"pid": 101, "ppid": 1, "comm": "cron", "cmdline": "/usr/sbin/cron -f",
         "start_s": now - 45816, "voluntary_ctxt": 20, "cpu_pct": 0.0},
        {"pid": 102, "ppid": 1, "comm": "dbus-daemon", "cmdline": "dbus-daemon --system",
         "start_s": now - 45816, "voluntary_ctxt": 4500, "cpu_pct": 0.1},
        {"pid": 103, "ppid": 1, "comm": "tailscaled", "cmdline": "/usr/sbin/tailscaled",
         "start_s": now - 45816, "voluntary_ctxt": 467000, "cpu_pct": 1.5},
    ]
    rd = classify(daemons, now)
    ck("system daemons are out of scope, not flagged",
       all(rd[p]["signals"] == [] for p in (100, 101, 102, 103)))
    ck("out-of-scope is stated, not silent",
       all(rd[p]["detail"].get("out_of_scope") for p in (100, 101, 102, 103)))
    ck("a long-lived high-ctx daemon is still not 'spinning'",
       SPINNING not in rd[103]["signals"])

    # 1. orphan detection (in scope)
    r = classify([{"pid": 1, "ppid": 1, "comm": S, "cmdline": S,
                   "start_s": now - 10, "voluntary_ctxt": 5, "cpu_pct": 0.0}], now)
    ck("orphan flagged on ppid=1 in scope", ORPHANED in r[1]["signals"])

    r = classify([{"pid": 2, "ppid": 42, "comm": S, "cmdline": S,
                   "start_s": now - 10, "voluntary_ctxt": 5, "cpu_pct": 0.0}], now)
    ck("live parent not flagged orphan", ORPHANED not in r[2]["signals"])

    # 2. stale on age budget
    r = classify([{"pid": 3, "ppid": 9, "comm": S, "cmdline": S,
                   "start_s": now - 7200, "voluntary_ctxt": 1, "cpu_pct": 0.0}],
                 now, max_age_s=3600)
    ck("stale flagged past budget", STALE in r[3]["signals"])

    # 3. the do-nothing prompt contradiction (the poly-bot case)
    busy = {"pid": 4, "ppid": 9, "comm": "agy-real",
            "cmdline": "agy-real --prompt-interactive Reply READY only. This is a "
                       "session bootstrap; do not research, edit files, or dispatch.",
            "start_s": now - 20000, "voluntary_ctxt": 700000, "cpu_pct": 213.9}
    r = classify([busy], now)
    ck("do-nothing prompt + high CPU flagged", IDLE_PROMPTED_BUT_BUSY in r[4]["signals"])
    ck("same process also flagged spinning", SPINNING in r[4]["signals"])

    quiet = dict(busy, pid=5, cpu_pct=0.1, voluntary_ctxt=100)
    r = classify([quiet], now)
    ck("do-nothing prompt at rest not flagged",
       IDLE_PROMPTED_BUT_BUSY not in r[5]["signals"])

    # 4. an instrument that cannot measure must SAY SO, not default
    r = classify([{"pid": 6, "comm": S, "cmdline": S}], now)
    sig = r[6]["signals"]
    ck("missing ppid -> unknown:orphaned", UNKNOWN + ":orphaned" in sig)
    ck("missing start_s -> unknown:stale", UNKNOWN + ":stale" in sig)
    ck("missing fields never yield a real signal",
       not [s for s in sig if not s.startswith(UNKNOWN)])

    # 4b. the SILENT GAP found by reading v1 back: a do-nothing prompt with no CPU
    # reading emitted neither a signal nor an UNKNOWN - the very failure this
    # module exists to detect, committed by this module.
    nocpu = {"pid": 61, "ppid": 9, "comm": S,
             "cmdline": S + " --prompt-interactive Reply READY only. do nothing",
             "start_s": now - 100, "voluntary_ctxt": 10}
    r = classify([nocpu], now)
    ck("do-nothing prompt with no CPU reading -> unknown, not silence",
       UNKNOWN + ":idle_prompted" in r[61]["signals"])
    ck("...and the prompt itself is still recorded",
       r[61]["detail"].get("do_nothing_prompt") is True)

    # 5. ctx-switch scoring is a RATE, so uptime alone must not flip it
    #    (run-385 hazard: scale a threshold, don't fix it). Sweep uptime widely at a
    #    constant rate and assert the verdict is invariant.
    flips = set()
    for age in range(100, 40001, 250):
        p = {"pid": 7, "ppid": 9, "comm": S, "cmdline": S,
             "start_s": now - age, "voluntary_ctxt": int(2.0 * age), "cpu_pct": 0.0}
        flips.add(SPINNING in classify([p], now, spin_ctx_per_s=20.0)[7]["signals"])
    ck("constant ctx RATE gives one verdict across uptime 100..40000s", flips == {False})

    flips_hi = set()
    for age in range(100, 40001, 250):
        p = {"pid": 8, "ppid": 9, "comm": S, "cmdline": S,
             "start_s": now - age, "voluntary_ctxt": int(50.0 * age), "cpu_pct": 0.0}
        flips_hi.add(SPINNING in classify([p], now, spin_ctx_per_s=20.0)[8]["signals"])
    ck("a high constant rate is flagged at every uptime", flips_hi == {True})

    # 6. threshold sweep: verdict must be monotone in the threshold
    p = {"pid": 9, "ppid": 9, "comm": S, "cmdline": S,
         "start_s": now - 1000, "voluntary_ctxt": 30000, "cpu_pct": 0.0}  # 30/s
    seen = [SPINNING in classify([p], now, spin_ctx_per_s=t)[9]["signals"]
            for t in range(1, 60)]
    ck("spin verdict monotone as threshold rises",
       seen == sorted(seen, reverse=True))

    # 6b. is_reapable - the 2026-09-10 regression. Three VS Code Codex extension
    # servers were reaped by hand on `stale` alone. `stale` is an age fact, not a
    # fault. Editors died. These checks must never both pass again.
    editor = {"pid": 20, "ppid": 9, "comm": "codex",
              "cmdline": "/home/dev/.vscode-server/extensions/openai.chatgpt-26.5901/server",
              "start_s": now - 69000, "voluntary_ctxt": 10, "cpu_pct": 0.0}
    e = classify([editor], now)[20]
    ck("editor server is stale", STALE in e["signals"])
    ok_r, why = is_reapable(dict(e, cmdline=editor["cmdline"], comm=editor["comm"]))
    ck("...but NOT reapable (protected marker)", ok_r is False and "protected" in why)

    plain_stale = {"pid": 21, "ppid": 9, "comm": "agy-real", "cmdline": "agy-real --serve",
                   "start_s": now - 69000, "voluntary_ctxt": 10, "cpu_pct": 0.0}
    e2 = classify([plain_stale], now)[21]
    ok_r2, why2 = is_reapable(dict(e2, cmdline=plain_stale["cmdline"], comm="agy-real"))
    ck("stale-only is never reapable", ok_r2 is False and "no fault signal" in why2)

    stuck = {"pid": 22, "ppid": 9, "comm": "agy-real",
             "cmdline": "agy-real --prompt-interactive Reply READY only. do nothing",
             "start_s": now - 20000, "voluntary_ctxt": 700000, "cpu_pct": 213.9}
    e3 = classify([stuck], now)[22]
    ok_r3, why3 = is_reapable(dict(e3, cmdline=stuck["cmdline"], comm="agy-real"))
    ck("stale + fault + old IS reapable", ok_r3 is True)

    young = dict(stuck, pid=23, start_s=now - 60)
    e4 = classify([young], now)[23]
    ok_r4, _ = is_reapable(dict(e4, cmdline=young["cmdline"], comm="agy-real"))
    ck("a young process with a fault is not reapable", ok_r4 is False)

    # age-budget sweep: reapability must be monotone in age, never flip back
    seen_r = []
    for age in range(1000, 40001, 500):
        p = dict(stuck, pid=24, start_s=now - age,
                 voluntary_ctxt=int(35.0 * age))
        ee = classify([p], now)[24]
        seen_r.append(is_reapable(dict(ee, cmdline=p["cmdline"], comm="agy-real"))[0])
    ck("reapability monotone in age", seen_r == sorted(seen_r))

    # 7. report() hides clean processes but shows flagged ones
    mixed = [{"pid": 10, "ppid": 9, "comm": "clean", "cmdline": S,
              "start_s": now - 5, "voluntary_ctxt": 1, "cpu_pct": 0.0},
             {"pid": 11, "ppid": 1, "comm": "orphan", "cmdline": S,
              "start_s": now - 5, "voluntary_ctxt": 1, "cpu_pct": 0.0}]
    lines = report(classify(mixed, now))
    ck("report shows only flagged, after the scope header",
       len(lines) == 2 and lines[0].startswith("scope:") and "orphan" in lines[1])
    ck("report header declares the corpus", "2/2" in lines[0])

    ok = all(c for _, c in checks)
    for name, c in checks:
        print("  %-58s %s" % (name, "ok" if c else "FAIL"))
    print("orphan_scan selftest: %d/%d %s"
          % (sum(1 for _, c in checks if c), len(checks), "GREEN" if ok else "RED"))
    return 0 if ok else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    if len(argv) > 1 and argv[1] == "scan":
        if not os.path.isdir("/proc"):
            print("scan requires /proc (Linux/WSL); nothing measured", file=sys.stderr)
            return 2
        import time
        now = time.time()
        procs = collect_linux(boot_s=now - _uptime(), now_s=now)
        cl = classify(procs, now)
        lines = report(cl)
        print("\n".join(lines) if lines else "no flagged sessions")
        return 0
    if len(argv) > 1 and argv[1] == "json":
        data = json.load(sys.stdin)
        print(json.dumps(classify(data["procs"], data["now_s"]), indent=1))
        return 0
    print(__doc__.strip().splitlines()[0])
    print("usage: orphan_scan.py [selftest|scan|json]")
    return 0


def _uptime():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
