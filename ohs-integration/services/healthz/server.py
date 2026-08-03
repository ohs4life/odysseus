#!/usr/bin/env python3
"""healthz.py - combined health endpoint for monitoring.

Returns 200 with JSON when everything is healthy, 503 when any
dependency is down. Single endpoint, no auth, intended for Uptime
Kuma or a curl-based watchdog.

Checks: Odysseus (local + public), MiniMax API, llama.cpp.
Stats: user count from data/auth.json, session/message counts from app.db.
"""
import asyncio
import json
import os
import sqlite3
import time
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

ODYSSEUS = os.environ.get("ODYSSEUS_URL", "http://127.0.0.1:7860")
MINIMAX = os.environ.get("MINIMAX_URL", "https://api.minimax.io/v1")
LLAMACPP = os.environ.get("LLAMACPP_URL", "http://127.0.0.1:8080")
DB_PATH = os.environ.get("ODYSSEUS_DB", "/Users/ai/odysseus/data/app.db")
AUTH_PATH = Path("/Users/ai/odysseus/data/auth.json")
PUBLIC_URL = os.environ.get("ODYSSEUS_PUBLIC", "https://ai.optimalhealthsystems.com")

app = FastAPI(title="OHS AI healthz", version="0.1.0")


async def _check(name, coro_fn, timeout=5):
    started = time.monotonic()
    try:
        ok, detail = await asyncio.wait_for(coro_fn(), timeout=timeout)
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"[:120]
    return {
        "name": name, "ok": ok,
        "ms": int((time.monotonic() - started) * 1000),
        "detail": str(detail)[:120],
    }


async def _ok_odysseus(c):
    r = await c.get(f"{ODYSSEUS}/")
    return r.status_code < 500, f"HTTP {r.status_code}"


async def _ok_minimax(c):
    r = await c.get(f"{MINIMAX}/models", headers={"Authorization": "Bearer ignore"})
    return r.status_code in (200, 401), f"HTTP {r.status_code}"


async def _ok_llama(c):
    r = await c.get(f"{LLAMACPP}/v1/models")
    return r.status_code < 500, f"HTTP {r.status_code} ({len(r.json().get('data',[]))} models)"


async def _ok_public(c):
    r = await c.get(f"{PUBLIC_URL}/", follow_redirects=False)
    return r.status_code in (200, 302), f"HTTP {r.status_code}"


def _stats():
    extras = {}
    # User count from auth.json (where Odysseus stores its user table)
    try:
        if AUTH_PATH.exists():
            data = json.loads(AUTH_PATH.read_text())
            extras["users"] = len(data.get("users", {}))
    except Exception as e:
        extras["auth_error"] = str(e)[:100]
    # Session / message counts from app.db
    for tbl in ("sessions", "chat_messages"):
        try:
            db = sqlite3.connect(DB_PATH, timeout=2)
            extras[tbl] = db.execute(
                f"SELECT COUNT(*) FROM {tbl}"
            ).fetchone()[0]
        except Exception:
            pass
    return extras


@app.get("/healthz")
async def healthz():
    async with httpx.AsyncClient() as c:
        checks = await asyncio.gather(
            _check("odysseus_local",   lambda: _ok_odysseus(c)),
            _check("odysseus_public",  lambda: _ok_public(c)),
            _check("minimax_api",      lambda: _ok_minimax(c)),
            _check("llamacpp_local",   lambda: _ok_llama(c)),
        )
    all_ok = all(c["ok"] for c in checks)
    body = {
        "ok": all_ok,
        "ts": time.time(),
        "service": "ohs-ai-healthz",
        "version": "0.1.0",
        "checks": checks,
        "stats": _stats(),
    }
    return JSONResponse(body, status_code=200 if all_ok else 503)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7870, log_level="info")
