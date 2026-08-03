# Cloudflare Access setup for ai.optimalhealthsystems.com

**What this does:** every visitor to `https://ai.optimalhealthsystems.com/` is redirected to a Cloudflare-hosted login page first. They must authenticate (Google, email link, or a one-time PIN) before they reach Odysseus. The Cloudflare Tunnel already exposes the app; this adds the login wall in front.

**Time:** 10-15 min. **You** do this in the Cloudflare dashboard — I don't have an API token. After it's set up, no code change on the box is needed; Cloudflare handles it at the edge.

## Steps

1. Go to https://one.dash.cloudflare.com/ (Zero Trust dashboard).
2. If first time: pick your account, accept the terms, set an org name (e.g. "OHS"). The **Free plan is fine** for up to 50 users.
3. **Access → Applications → Add an application → Self-hosted**.
4. Fill in:
   - **Name:** `Odysseus OHS AI`
   - **Session duration:** 24 hours
   - **Application domain:** `ai.optimalhealthsystems.com`
   - **Path:** (leave blank — covers all paths)
   - **Service type:** HTTP
   - **Destination URL:** `http://localhost:7860`  (this is the address Cloudflare's edge connects to from inside the tunnel; our existing cloudflared config does the actual loopback to Odysseus)
5. **Identity providers**: at minimum, add **Google** (one-click, your team probably already has Google Workspace). Optional: add a one-time PIN email policy for vendors/contractors.
6. **Access policies**: by default, "Allow" for everyone in your org. If you want to restrict to specific emails (e.g. only @optimalhealthsystems.com), add an **Allow** policy with an **Email ending in** selector set to `@optimalhealthsystems.com`. For a tighter policy, add an **Allow** rule with **Email** set to specific addresses.
7. Click **Save**. Cloudflare will deploy the policy to the edge within ~30 seconds.
8. Visit `https://ai.optimalhealthsystems.com/` in a private/incognito window — you should see a Cloudflare login screen, not the Odysseus login.
9. After you sign in (Google), you should be redirected to the Odysseus UI as usual.

## What to test
- [ ] Unauthenticated request to `https://ai.optimalhealthsystems.com/` is redirected to the Cloudflare login.
- [ ] Logging in with a `@optimalhealthsystems.com` Google account grants access.
- [ ] Logging in with a non-allowlisted Google account is denied.
- [ ] After sign-in, the Odysseus session is the same as before (you can use your existing Odysseus credentials inside Odysseus).
- [ ] The Cloudflare session cookie persists across all users' browsers (one Cloudflare login per device, not per request).

## Optional hardening
- **Device posture** (in Cloudflare Access → Settings): require a specific OS, require WARP, etc. Strong but adds friction.
- **Country allowlist**: if all users are in the US, allow only US. Restricts drive-by access from random IPs.
- **App Launcher** (Cloudflare Zero Trust → Access → App Launcher): pin Odysseus to the launcher so employees can reach it from a single dashboard.

## What this does NOT do
- It does **not** replace Odysseus's own auth. Users still need their Odysseus credentials inside Odysseus. Cloudflare Access is the front door; Odysseus login is the second door.
- It does **not** encrypt traffic inside the tunnel — the cloudflared tunnel already does that.
- It does **not** prevent a compromised employee from accessing their own data. That needs the in-app privilege controls Odysseus already has.
