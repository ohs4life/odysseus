"""End-to-end verification of the KB grounding contract.

Exercises the post-processor against all the failure modes that could
allow the model to hallucinate:

  1. KB has answer, model cites           -> compliant
  2. KB has answer, model didn't cite     -> rewrite with citations
  3. KB no answer, model hallucinates     -> force refusal
  4. KB no answer, model refuses          -> compliant
  5. KB errored, model hallucinates       -> force refusal + KB-unavailable note
  6. KB errored, model refuses            -> compliant
  7. KB skipped (guide_only mode)         -> no enforcement (compliant)

Plus a live chat test against the running Odysseus service.

Run with:
    venv/bin/python tests/test_kb_grounding.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from src.knowledgebase import grounding, retriever  # noqa: E402

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"


def run(desc, response, status, ret) -> bool:
    check = grounding.enforce_grounding(response, ret, retrieval_status=status)
    ok = (
        (status == "ok_has_answer" and "citation:" in response and check.compliant)
        or (status == "ok_has_answer" and "citation:" not in response and not check.compliant)
        or (status == "ok_no_answer" and grounding.has_refusal(response) and check.compliant)
        or (status == "ok_no_answer" and not grounding.has_refusal(response) and not check.compliant)
        or (status == "error" and grounding.has_refusal(response) and check.compliant)
        or (status == "error" and not grounding.has_refusal(response) and not check.compliant)
        or (status == "skipped" and check.compliant)
    )
    marker = PASS if ok else FAIL
    print(f"  [{marker}] {desc}: compliant={check.compliant}, issue={check.issue}")
    return ok


def main() -> int:
    print("=== Unit tests for grounding.enforce_grounding ===")
    r_nano = retriever.retrieve("how does nanoblue work?", top_k=3)
    r_tokyo = retriever.retrieve("weather in Tokyo", top_k=3)

    cases = [
        ("1. KB has answer, model cites",
         "NanoBlue [citation: 1] works [citation: 2].", "ok_has_answer", r_nano),
        ("2. KB has answer, model didn't cite",
         "I'm not sure what NanoBlue is.", "ok_has_answer", r_nano),
        ("3. KB no answer, model hallucinates",
         "Tokyo is sunny.", "ok_no_answer", r_tokyo),
        ("4. KB no answer, model refuses",
         "I don't have that in my reference material. Would you like me to web-search?",
         "ok_no_answer", r_tokyo),
        ("5. KB errored, model hallucinates",
         "Tokyo is sunny.", "error", None),
        ("6. KB errored, model refuses",
         "I don't have that in my reference material.", "error", None),
        ("7. KB skipped (guide_only), model says anything",
         "Whatever I want.", "skipped", None),
    ]
    all_ok = all(run(*c) for c in cases)

    print("\n=== KB health check ===")
    h = grounding.check_kb_health()
    print(f"  healthy={h.healthy}, sources={h.sources_indexed}, chroma={h.chroma_items}, bm25={h.bm25_exists}")
    print(f"  issues: {h.issues}")
    if not h.healthy:
        print(f"  [{FAIL}] KB health issues detected")
        all_ok = False
    else:
        print(f"  [{PASS}] KB healthy")

    print("\n=== Live chat tests against running service ===")
    import requests
    base = os.environ.get("ODYSSEUS_BASE_URL", "http://127.0.0.1:7860")
    sess = requests.Session()
    try:
        r = sess.post(f"{base}/api/auth/login",
                      json={"username": "ohs-admin",
                            "password": "OHS-Admin-Pass-2026-Changeme"},
                      timeout=5)
        if r.status_code != 200:
            print(f"  [{FAIL}] login failed: {r.status_code}")
            return 1
        sess.cookies.update(r.cookies)
        sid = "test-kb-grounding-" + str(int(time.time()))
        r = sess.post(f"{base}/api/session",
                      data={"name": sid,
                            "endpoint_url": "https://api.minimax.io/v1",
                            "model": "MiniMax-M3",
                            "endpoint_id": "4aded1be",
                            "rag": "false",
                            "skip_validation": "true"},
                      timeout=10)
        sid = (r.json().get("id") or
               (r.json().get("session") or {}).get("id") or sid)
    except Exception as e:
        print(f"  [{FAIL}] login/setup failed: {e}")
        return 1

    def run_chat(q: str) -> tuple[str, str]:
        r = sess.post(f"{base}/api/chat_stream",
                      files={"mode": (None, "agent"),
                             "message": (None, q),
                             "session": (None, sid),
                             "model": (None, "MiniMax-M3")},
                      timeout=180, stream=True)
        text = ""
        err = ""
        for line in r.iter_lines():
            if not line:
                continue
            s = line.decode("utf-8", errors="replace")
            if not s.startswith("data: ") or "[DONE]" in s:
                continue
            try:
                data = json.loads(s[6:])
            except Exception:
                continue
            t = data.get("type", "delta")
            if t == "delta" and not data.get("thinking"):
                text += data.get("delta", "")
            elif t == "delta" and data.get("thinking") is None:
                # Some providers send thinking=None for visible text; treat
                # None as "not thinking" and include the delta.
                text += data.get("delta", "")
            elif t == "event" and s.startswith("event: error"):
                err = data.get("error", "")
        return text, err

    print("\n  Live: KB has answer")
    t, e = run_chat("how does nanoblue work?")
    if e:
        print(f"  [{FAIL}] chat errored: {e}")
        all_ok = False
    elif "citation:" not in t:
        print(f"  [{FAIL}] no citations in response")
        all_ok = False
    else:
        print(f"  [{PASS}] response ({len(t)} chars) has citations")
        print(f"    preview: {t[:120].replace(chr(10), ' ')}...")

    print("\n  Live: KB has no answer")
    t, e = run_chat("what is the weather in Tokyo?")
    if e:
        print(f"  [{FAIL}] chat errored: {e}")
        all_ok = False
    elif not (grounding.has_refusal(t) or "i don't have" in t.lower()):
        print(f"  [{FAIL}] model did not refuse: {t[:200]}")
        all_ok = False
    else:
        print(f"  [{PASS}] model refused correctly")
        print(f"    preview: {t[:200]}")

    print("\n" + ("=" * 30))
    print("RESULT: " + (PASS if all_ok else FAIL))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
