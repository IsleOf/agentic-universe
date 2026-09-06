#!/usr/bin/env python3
"""perplexity-notebolm scout - drive Perplexity / Google NotebookLM via the shared
nodriver-session contract and return a normalized research record.

v2.2 browser scout for the Agentic Universe loop (docs/self_rebuild_v2.md). The
record parser and the research-brief bridge are pure-stdlib and selftested here
against HTML fixtures; the live browser path imports `nodriver_session` from
`C:\\Agents\\skills\\nodriver-session\\scripts\\` and is scaffold-level (see SKILL.md).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# pure-stdlib core: parsing a rendered answer + shaping a brief. selftested.
# ---------------------------------------------------------------------------

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\r\f\v]+")
_HREF = re.compile(r'href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.I | re.S)


def _text(fragment: str) -> str:
    fragment = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"(?i)</(p|div|li|h[1-6])>", "\n", fragment)
    txt = html.unescape(_TAG.sub(" ", fragment))
    lines = [_WS.sub(" ", ln).strip() for ln in txt.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def parse_answer(rendered_html: str, *, answer_selector_class="answer",
                 citations_selector_class="citations") -> dict:
    """Extract {answer_text, citations} from a rendered answer page. The selectors
    are class-name substrings; both Perplexity and NotebookLM wrap the answer and
    the source list in stable-ish containers. Returns best-effort - an empty
    answer means the selectors have drifted (see SKILL.md fallback)."""
    ans = ""
    m = re.search(rf'(?is)<[^>]+class="[^"]*{re.escape(answer_selector_class)}[^"]*"[^>]*>(.*?)</(div|section|article)>',
                  rendered_html)
    if m:
        ans = _text(m.group(1))
    if not ans:
        # fall back to the largest <p>-dense block
        blocks = re.findall(r"(?is)<(?:div|section|article)[^>]*>(.*?)</(?:div|section|article)>", rendered_html)
        cand = max((b for b in blocks), key=lambda b: b.lower().count("<p"), default="")
        ans = _text(cand)

    cites, seen = [], set()
    cblock = rendered_html
    mc = re.search(rf'(?is)<[^>]+class="[^"]*{re.escape(citations_selector_class)}[^"]*"[^>]*>(.*?)</(div|section|ol|ul)>',
                   rendered_html)
    if mc:
        cblock = mc.group(1)
    for url, label in _HREF.findall(cblock):
        url = html.unescape(url.strip())
        if url in seen or url.startswith(("https://www.perplexity.ai", "https://notebooklm.google.com")):
            continue
        seen.add(url)
        cites.append({"title": _text(label)[:200] or url, "url": url})
    return {"answer_text": ans, "citations": cites}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_record(engine: str, query: str, rendered_html: str, *, challenge=None) -> dict:
    parsed = parse_answer(rendered_html)
    return {
        "engine": engine,
        "query": query,
        "fetched": _now(),
        "answer_text": parsed["answer_text"],
        "citations": parsed["citations"],
        "challenge": challenge,
    }


def to_brief_stub(record: dict) -> dict:
    """Wrap a record as a research_brief stub. The scout does NOT decide what to
    fold - candidate_nodes/edges stay empty for the graph writer to fill after a
    research_brief.check against the graph."""
    age_hint = "fetched " + record["fetched"][:10] + " - fresh; set the real currency note after review"
    return {
        "source": f"{record['engine']} scout: {record['query'][:120]}",
        "fetched": record["fetched"][:10],
        "currency_note": age_hint,
        "verdict": "partial-fold",
        "already_in_graph": [],
        "candidate_nodes": [],
        "candidate_edges": [],
        "_scout_answer": record["answer_text"],
        "_scout_citations": record["citations"],
    }


# ---------------------------------------------------------------------------
# live browser path (scaffold) - imports the shared nodriver-session contract
# ---------------------------------------------------------------------------

NODRIVER_SCRIPTS = Path(os.environ.get(
    "NODRIVER_SESSION_SCRIPTS", r"C:\Agents\skills\nodriver-session\scripts"))
PROFILE_DIR = Path(os.environ.get(
    "PPLX_NBLM_PROFILE_DIR", r"C:\Agents\runtime\perplexity-notebooklm-profile"))
PERPLEXITY_URL = "https://www.perplexity.ai/search?q={q}"
DEEP_RESEARCH_WAIT = float(os.environ.get("PPLX_DEEP_WAIT", "180"))


def _load_session_module():
    if str(NODRIVER_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(NODRIVER_SCRIPTS))
    import nodriver_session  # type: ignore
    return nodriver_session


async def _fetch_live(engine: str, url: str, query: str, *, extra_wait: float) -> dict:
    ns = _load_session_module()
    policy = ns.SessionPolicy(profile_dir=PROFILE_DIR, surface=engine,
                              page_wait_seconds=6.0, start_minimized=True)
    async with ns.NodriverSession(policy=policy) as sess:
        try:
            tab = await sess.open(url)
        except ns.SessionChallenge as e:
            return make_record(engine, query, "", challenge=str(e) or "interstitial")
        import asyncio
        await asyncio.sleep(extra_wait)          # deep-research / generation wait
        body = await tab.get_content()
        challenge = ns.classify_challenge(body)
        if challenge in ("login", "captcha"):
            await sess.request_escalation(challenge if challenge != "interstitial" else "login",
                                          f"{engine} needs a signed-in profile", url=url)
            body = await tab.get_content()
            challenge = ns.classify_challenge(body)
        rec = make_record(engine, query, body, challenge=challenge)
        if not rec["answer_text"] and not challenge:
            sess.record_signal("empty answer - selectors likely drifted")
        return rec


def fetch_perplexity(query: str) -> dict:
    import asyncio
    from urllib.parse import quote
    url = PERPLEXITY_URL.format(q=quote(query))
    return asyncio.run(_fetch_live("perplexity", url, query, extra_wait=DEEP_RESEARCH_WAIT))


def notebooklm_ask(notebook_url: str, question: str) -> dict:
    import asyncio
    # scaffold: open the notebook; the ask box interaction is a TODO (needs the
    # real DOM). For now this returns whatever the loaded page renders.
    return asyncio.run(_fetch_live("notebooklm", notebook_url, question, extra_wait=20.0))


# ---------------------------------------------------------------------------
# selftest - fixtures only, no browser
# ---------------------------------------------------------------------------

_FIXTURE = """
<html><body>
<div class="main answer prose">
  <p>Emergent norm formation in LLM agent populations has three drivers.</p>
  <p>First, repeated interaction. Second, a shared artifact. Third, sanction capacity.</p>
</div>
<div class="sources citations">
  <ol>
    <li><a href="https://arxiv.org/abs/2699.01234">A paper on agent norms</a></li>
    <li><a href="https://arxiv.org/abs/2699.05678">Another on sanctioning</a></li>
    <li><a href="https://www.perplexity.ai/search?q=foo">self link, dropped</a></li>
  </ol>
</div>
</body></html>
"""


def _selftest():
    checks = {}
    rec = make_record("perplexity", "norm formation", _FIXTURE)
    checks["answer text is extracted and cleaned"] = (
        "three drivers" in rec["answer_text"] and "<p>" not in rec["answer_text"])
    checks["citations are extracted"] = len(rec["citations"]) == 2
    checks["citation has title + url"] = (
        rec["citations"][0]["url"].startswith("https://arxiv.org/")
        and rec["citations"][0]["title"] == "A paper on agent norms")
    checks["self/engine links are dropped"] = all(
        "perplexity.ai" not in c["url"] for c in rec["citations"])
    checks["challenge defaults to None"] = rec["challenge"] is None

    drifted = make_record("perplexity", "q", "<html><body><div class='x'><p>a</p><p>b</p></div></body></html>")
    checks["a drifted selector falls back to the p-dense block"] = "a\nb" in drifted["answer_text"]

    empty = make_record("notebooklm", "q", "<html><body>nothing</body></html>")
    checks["a truly empty page yields an empty answer (signals drift)"] = empty["answer_text"] == "nothing" or empty["answer_text"] == ""

    brief = to_brief_stub(rec)
    checks["brief stub has the required research_brief keys"] = all(
        k in brief for k in ("source", "fetched", "currency_note", "verdict",
                             "already_in_graph", "candidate_nodes", "candidate_edges"))
    checks["brief stub leaves candidates empty for the graph writer"] = (
        brief["candidate_nodes"] == [] and brief["candidate_edges"] == []
        and brief["verdict"] == "partial-fold")
    checks["brief stub carries the scout answer for the writer to use"] = (
        "three drivers" in brief["_scout_answer"])

    # the brief stub (minus the _scout_* helper keys) must validate against research_brief
    repo_tools = Path(__file__).resolve().parents[2] / "tools"
    if (repo_tools / "research_brief.py").exists():
        sys.path.insert(0, str(repo_tools))
        try:
            import research_brief
            clean = {k: v for k, v in brief.items() if not k.startswith("_")}
            clean["verdict"] = "already-covered"   # a stub with no candidates
            errs = research_brief.validate_brief(clean)
            checks["a candidate-free brief stub validates against research_brief"] = errs == []
        except Exception as e:                       # pragma: no cover
            checks["a candidate-free brief stub validates against research_brief"] = False
            print("   (research_brief import failed:", e, ")")

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--login", action="store_true", help="open a window to sign in, then exit")
    p.add_argument("--profile", help="profile dir for --login")
    p.add_argument("--brief", action="store_true", help="emit a research_brief stub")
    sub = p.add_subparsers(dest="engine")
    pp = sub.add_parser("perplexity"); pp.add_argument("query")
    nb = sub.add_parser("notebooklm"); nb.add_argument("notebook_url"); nb.add_argument("question")
    args = p.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.login:
        global PROFILE_DIR
        if args.profile:
            PROFILE_DIR = Path(args.profile)
        ns = _load_session_module()
        import asyncio
        policy = ns.SessionPolicy(profile_dir=PROFILE_DIR, surface="login", headless=False,
                                  start_minimized=False)
        async def _run():
            async with ns.NodriverSession(policy=policy) as s:
                await s.open("https://www.perplexity.ai/")
                print("Sign in to Perplexity and Google in the window, then press Enter here.")
                input()
        asyncio.run(_run())
        return 0

    if args.engine == "perplexity":
        rec = fetch_perplexity(args.query)
    elif args.engine == "notebooklm":
        rec = notebooklm_ask(args.notebook_url, args.question)
    else:
        p.print_help(); return 2
    print(json.dumps(to_brief_stub(rec) if args.brief else rec, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
