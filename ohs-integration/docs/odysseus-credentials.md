# OHS AI — User credentials (Odysseus deployment)

**Server:** `http://127.0.0.1:7860`  (start with `./start-macos.sh` in `/Users/ai/odysseus`)
**Admin URL:** same — log in as `ohs-admin`, then go to **Settings → Users** to manage accounts.
**Network access:** to expose to the LAN, set `APP_BIND=0.0.0.0` in `/Users/ai/odysseus/.env` and (recommended) put the box behind Cloudflare Access / Tailscale / your reverse proxy. Do **not** expose 7860 directly to the public internet.

**Default model:** `MiniMax-M3` (OpenAI-compatible endpoint, base URL `https://api.minimax.io/v1`)
**Backup model:** `gemma-4-12b` (local llama.cpp on `http://127.0.0.1:8080/v1` — point any agent at this model for PHI-safe prompts)

---

## Current state (2026-08-02, mid-afternoon)

The operator (`ohs-admin`) cleared all 25 placeholder employees via the UI
on 2026-08-02 and created a personal admin user `skyler-beals`. Real users
will be added back as the rollout progresses.

| Username | Password | Role |
|---|---|---|
| `ohs-admin` | `OHS-Admin-Pass-2026-Changeme` | super-admin |
| `skyler-beals` | (set at creation; see `/Users/ai/odysseus/data/auth.json`) | admin (operator) |

**Both passwords must be rotated before going live:**

- `ohs-admin` still ends in `-Changeme` (the hint that it's the default)
- `skyler-beals` was auto-generated when created — copy it from
  `auth.json` (it's a bcrypt hash; you can't recover the plaintext from
  the hash, so reset it via the admin UI or the API)

To get the live user list at any time:

```bash
python3 -c "import json; print('\n'.join(sorted(json.load(open('/Users/ai/odysseus/data/auth.json'))['users'].keys())))"
```

---

## Original Day-2 deployment (historical reference)

The original deployment (Aug 2 morning) created 1 admin + 25 employees
with predictable placeholder passwords (`OHS-User-NN-2026-Changeme`).
That credential list is preserved in the git history of this repo
(commit `2872ac1`) if you need it for reference — but those users were
deleted from the live `auth.json` and the passwords were never rotated
to anything else. **Don't use those passwords for any real account.**

The pre-deletion backup at `~/backups/odysseus/20260802-0752/auth.json`
has the original 26-user `auth.json` if you need to recover user01–
user25's bcrypt hashes (note: re-adding them means re-running the
bulk-create script with NEW passwords — see "Bulk-creating new users"
below).

---

## Per-user data — where it lives

Each user has their own:

- login (username + password)
- conversation history (SQLite, `data/app.db`)
- uploaded files (`data/uploads/<username>/`)
- personal documents (`data/personal_docs/<username>/`)
- vector memory (ChromaDB collection per user)
- email account (configure per-user in Settings → Email)
- calendar (configure per-user in Settings → Calendar)

---

## Bulk-creating new users (admin only)

```bash
COOKIE_JAR=/tmp/admin-cookies.txt
curl -sS -c "$COOKIE_JAR" -X POST 'http://127.0.0.1:7860/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ohs-admin","password":"OHS-Admin-Pass-2026-Changeme"}' -o /dev/null

# Add a single new user:
curl -sS -b "$COOKIE_JAR" -X POST 'http://127.0.0.1:7860/api/auth/users' \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice-temp-pass-2026","is_admin":false}'
rm -f "$COOKIE_JAR"
```

Or generate strong random passwords and create users in a loop:

```bash
cd /Users/ai/odysseus
./venv/bin/python <<'EOF'
import secrets, string
from core.auth import AuthManager
am = AuthManager()
for i in range(1, 26):
    uname = f"user{i:02d}"
    pw = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    try:
        am.create_user(uname, pw, is_admin=False)
        print(f"{uname} {pw}")
    except Exception as e:
        print(f"{uname} SKIPPED ({e})")
EOF
```

For a real onboarding flow, the recommended path is OAuth (Google) — set
`GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in
`/Users/ai/odysseus/.env`, then users can sign in with their Google
accounts and you'll never have to hand out passwords.

---

## Backup (whole data tree, nightly)

```bash
cd /Users/ai
tar czf odysseus-data-$(date +%Y%m%d).tgz \
  --exclude='odysseus/.venv' \
  --exclude='odysseus/data/huggingface' \
  --exclude='odysseus/data/odysseus_models' \
  odysseus/data odysseus/.env odysseus/data/auth.json
```

`data/app.db` has the user table + sessions + messages. The ChromaDB
collection is the per-user vector memory. Both are standard sqlite and
can be restored by unpacking the tarball into the original location.

---

## Verifying the deployment

```bash
# 1. Server up?
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:7860/

# 2. Admin login + list users
COOKIE_JAR=/tmp/c.txt
curl -sS -c "$COOKIE_JAR" -X POST 'http://127.0.0.1:7860/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ohs-admin","password":"OHS-Admin-Pass-2026-Changeme"}' -o /dev/null
curl -sS -b "$COOKIE_JAR" 'http://127.0.0.1:7860/api/auth/users' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'  {len(d.get(\"users\",[]))} users')"
rm -f "$COOKIE_JAR"

# 3. MiniMax reachable from the box
curl -sS --max-time 5 -o /dev/null -w 'MiniMax: %{http_code}\n' \
  https://api.minimax.io/v1/models
```

---

## What was verified (cumulative across sessions)

**Day 2 cutover (2026-08-02 morning)** — the original 26-user deployment:

- ✅ Odysseus installed natively on Mac mini M4 (port 7860)
- ✅ Admin user `ohs-admin` + 25 employees (`user01`-`user25`) created
- ✅ Per-user data isolation: `user02` could not access `user01`'s session (HTTP 404)
- ✅ MiniMax endpoint added (8 models)
- ✅ Chat end-to-end worked for all 25 users
- ✅ Login rate limiter works (a feature, not a bug)

**Session 2 (2026-08-02 midday)** — fixes + shared KB:

- ✅ MiniMax endpoint re-enabled (had been disabled — `is_enabled=0 → 1`)
- ✅ Shared KB mechanism added (`shared: true` on SKILL.md → visible to all users)
- ✅ All 3 placeholder skills visible to all 25 users
- ✅ All 5 Local models in llama.cpp work end-to-end via Odysseus
- ✅ All 26 users default to `MiniMax-M3` (`share_defaults_with_users=true`)
- ✅ 29-check battletest passes in ~3 min
- ✅ 3 placeholder skills removed (moved to `~/odysseus/data/.skills-archived/placeholder-20260802-174142/`)

**Session 3 (2026-08-02 afternoon)** — operator cleanup:

- ✅ Operator (`ohs-admin`) deleted all 25 placeholder users via UI
- ✅ Created `skyler-beals` as new admin
- ✅ Removed 3 inaccurate placeholder skills (clinical-practice content)
- ⚠️ **Real OHS shared KB still needs to be built** — see `docs/KB-BUILD-SESSION.md`