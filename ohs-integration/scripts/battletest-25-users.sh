#!/bin/bash
# 25-user battletest for OHS AI / Odysseus.
#
# Verifies:
#   1. All 25 users + admin can log in (rate-limit aware: sleeps between batches)
#   2. Each user can see the 3 shared KB skills
#   3. Each user can create a MiniMax session and complete a chat round-trip
#   4. Per-user session isolation (user A doesn't see user B's sessions)
#   5. Public URL is reachable
#   6. Healthz is green
#
# Output: per-user PASS/FAIL + summary stats.

set -u

BASE="${BASE:-http://127.0.0.1:7860}"
HEALTHZ="${HEALTHZ:-http://127.0.0.1:7870/healthz}"
PUBLIC="${PUBLIC:-https://ai.optimalhealthsystems.com/}"

PASS=0
FAIL=0
FAILS=()
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

# ----- phase 0: system-level checks -----
echo "=== phase 0: system ==="
http=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "$HEALTHZ" 2>/dev/null)
[ "$http" = "200" ] && { echo "  ✓ healthz HTTP 200"; PASS=$((PASS+1)); } || { echo "  ✗ healthz HTTP $http"; FAIL=$((FAIL+1)); FAILS+=("healthz"); }

http=$(curl -sS -L -o /dev/null -w '%{http_code}' --max-time 15 "$PUBLIC" 2>/dev/null)
[ "$http" = "200" ] && { echo "  ✓ public URL HTTP 200"; PASS=$((PASS+1)); } || { echo "  ✗ public URL HTTP $http"; FAIL=$((FAIL+1)); FAILS+=("public"); }

# Login one user to bootstrap cookie + warm limiter
bootstrap_login() {
    local user="$1" pw="$2" jar="$3"
    curl -sS -c "$jar" -X POST "$BASE/api/auth/login" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$user\",\"password\":\"$pw\"}" -o /dev/null
}

# ----- phase 1+2: per-user login + shared KB + chat -----
test_user() {
    local user="$1" pw="$2"
    local jar="$TMP/jar.${user}"
    local out="$TMP/out.${user}"

    # wait for rate-limit reset if we've been hitting it
    sleep 4

    # login
    local code
    code=$(curl -sS -c "$jar" -X POST "$BASE/api/auth/login" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$user\",\"password\":\"$pw\"}" \
        -o /dev/null -w '%{http_code}')
    if [ "$code" != "200" ]; then
        echo "  ✗ $user: login HTTP $code"
        FAIL=$((FAIL+1)); FAILS+=("$user-login"); return
    fi

    # shared KB
    local skills_count
    skills_count=$(curl -sS -b "$jar" "$BASE/api/skills" 2>/dev/null | \
        python3 -c "import json,sys; print(json.load(sys.stdin).get('count',-1))" 2>/dev/null)
    if [ "$skills_count" != "3" ]; then
        echo "  ✗ $user: shared KB count=$skills_count (want 3)"
        FAIL=$((FAIL+1)); FAILS+=("$user-kb"); return
    fi

    # session create (MiniMax)
    local sid
    sid=$(curl -sS -b "$jar" -X POST "$BASE/api/session" \
        --data-urlencode "name=bt-$user-$(date +%s)" \
        --data-urlencode "endpoint_url=https://api.minimax.io/v1" \
        --data-urlencode "model=MiniMax-M3" \
        --data-urlencode "endpoint_id=4aded1be" \
        --data-urlencode "rag=false" \
        --data-urlencode "skip_validation=true" 2>/dev/null | \
        python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
    if [ -z "$sid" ] || [ "$sid" = "None" ]; then
        echo "  ✗ $user: session create failed (sid='$sid')"
        FAIL=$((FAIL+1)); FAILS+=("$user-session"); return
    fi

    # chat round-trip (small message, expect a quick reply)
    local reply
    reply=$(curl -sS -b "$jar" -X POST "$BASE/api/chat" \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"Reply with exactly: PONG from $user\",\"session\":\"$sid\",\"model\":\"MiniMax-M3\"}" \
        -m 45 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response',''))" 2>/dev/null)
    if echo "$reply" | grep -q "$user"; then
        echo "  ✓ $user: login + shared KB (3) + chat round-trip ($user in reply)"
        PASS=$((PASS+1))
    else
        echo "  ✗ $user: chat reply missing username marker (got: ${reply:0:80})"
        FAIL=$((FAIL+1)); FAILS+=("$user-chat")
    fi

    rm -f "$jar"
}

echo
echo "=== phase 1+2: 25 users (login + shared KB + chat) ==="
test_user "ohs-admin" "OHS-Admin-Pass-2026-Changeme"
for n in $(seq -w 1 25); do
    test_user "user${n}" "OHS-User-${n}-2026-Changeme"
done

# ----- phase 3: per-user isolation -----
echo
echo "=== phase 3: per-user isolation ==="
# create a session as user01 with a marker name, verify user02 doesn't see it
J1="$TMP/jar.iso1"; J2="$TMP/jar.iso2"
sleep 4
bootstrap_login "user01" "OHS-User-01-2026-Changeme" "$J1"
sleep 4
bootstrap_login "user02" "OHS-User-02-2026-Changeme" "$J2"
MARKER="iso-test-$(date +%s)-$$"
sleep 4
curl -sS -b "$J1" -X POST "$BASE/api/session" \
    --data-urlencode "name=$MARKER" \
    --data-urlencode "endpoint_url=https://api.minimax.io/v1" \
    --data-urlencode "model=MiniMax-M3" \
    --data-urlencode "endpoint_id=4aded1be" \
    --data-urlencode "rag=false" \
    --data-urlencode "skip_validation=true" -o /dev/null

LEAKED=$(curl -sS -b "$J2" "$BASE/api/sessions" 2>/dev/null | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for s in d if '$MARKER' in s.get('name','')))" 2>/dev/null)
if [ "$LEAKED" = "0" ]; then
    echo "  ✓ user02 does NOT see user01's marker session"
    PASS=$((PASS+1))
else
    echo "  ✗ user02 sees $LEAKED sessions matching user01's marker"
    FAIL=$((FAIL+1)); FAILS+=("isolation-leak")
fi
rm -f "$J1" "$J2"

# ----- summary -----
echo
echo "=== summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -gt 0 ]; then
    echo "FAILURES: ${FAILS[@]}"
    exit 1
fi
exit 0