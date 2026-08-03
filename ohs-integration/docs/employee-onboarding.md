# OHS AI — Employee quick-start (one-pager)

**URL:** https://ai.optimalhealthsystems.com/
**What it is:** a private AI workspace for our practice. Chat, document editor, email triage, calendar, deep research, and your own private memory. Everything you do is private to you.

---

## Sign in (first time)

1. Open **https://ai.optimalhealthsystems.com/** in Chrome or Safari.
2. The first screen is a Cloudflare login. Click **Sign in with Google** and use your `@optimalhealthsystems.com` work account. (Until Google sign-in is configured, use the username + password your manager gave you.)
3. After the Cloudflare screen you'll see the Odysseus login. Sign in with the **same credentials** your manager gave you (or with your Google account if it's been linked).
4. On the **first login only**, change your password: **top-right avatar → Settings → Change password**.

---

## The three things you'll use most

### 1. Chat (the main work surface)

The middle of the screen is the chat. Type a question or task. Pick a model in the dropdown:

- **MiniMax-M3** (default) — fast, cheap, fine for almost everything.
- **claude-haiku-4-5** (or whichever Anthropic model is shown) — better for careful reasoning.
- **gemma-4-12b** — the **local** model, runs on our own box, never leaves the building. **Use this for anything patient-related or otherwise sensitive.**

Type `Enter` to send, `Shift+Enter` for a new line. The model answers in a streaming bubble.

### 2. Skills (slash commands)

Type `/` in the chat box to see a list of available skills. For example:

- `/ohs-internal-kb` — searches our internal knowledge base (policies, product info, procedures).
- `/ohs-product-catalog` — looks up OHS product specs, pricing, SKUs.
- More will appear as we add them. Just type `/` to see the current list.

### 3. Documents (left sidebar → "Documents")

A Markdown editor with AI suggestions. Click **+ New**, write, the AI can suggest edits / fill in sections / rewrite. Files save automatically. Only **you** can see your documents.

---

## Other tabs in the left sidebar

| Tab | What it's for |
|---|---|
| **Chat** | What you're looking at now. New chat = top-left **+**. |
| **Compare** | Blind A/B: ask the same question to two models, vote on which answer is better. |
| **Research** | "Deep research" — the agent will spend 2-10 minutes reading multiple sources and write you a cited report. |
| **Documents** | Your private document workspace (Markdown editor with AI). |
| **Email** | Triage: connect your IMAP/SMTP in **Settings → Email**. |
| **Calendar** | Connect a CalDAV calendar (Radicale runs on this box). |
| **Notes** | Quick notes; AI can search and reference them. |
| **Memory** | What the AI has remembered about you. You can edit / delete entries. |
| **Tasks** | To-do items; the AI can act on them when you ask. |
| **Gallery** | Image generation / editing. |

---

## What's safe to share with the AI

- Internal policies, procedures, drafts, brainstorming
- Product specs, pricing questions
- Marketing copy, templates, code
- General research (the AI uses public web search)

## What's NOT safe to share (use the **local** model = `gemma-4-12b`)

- Anything that identifies a specific patient, even indirectly
- PHI (Protected Health Information) of any kind
- Anything that would be a HIPAA violation if it left the building

The **local model** (`gemma-4-12b`) processes everything on our own Mac — the prompt and the response never go to any external server. **For anything patient-related, always pick the local model.**

---

## Common questions

- **"Can my manager see my chats?"** No. Chats, documents, and memory are scoped per user. Admins can see user *accounts* (Settings → Users) but not their content.
- **"Where is my data stored?"** On the Mac mini in the office, in `/Users/ai/odysseus/data/`. Backed up nightly to `/Users/ai/backups/odysseus/`. Not uploaded to any cloud.
- **"What if I forget my password?"** Ask your manager to reset it. (Soon: you'll be able to reset it yourself from the login screen.)
- **"Can I use this on my phone?"** Yes — the URL works in any browser. There's no native app; bookmark the URL on your home screen.
- **"Something's broken / a model gave a bad answer / the AI is stuck"** Ping `ohs-admin` in Slack. The whole system has a health endpoint and we get alerts when it's down.

---

## Tips for better answers

- **Be specific.** "Write a 200-word patient-recall letter for Mrs. Smith, age 72, who missed her annual physical" beats "write a recall letter."
- **Tell the model what to ignore.** "Don't make up sources, just say if you don't know."
- **For long tasks, break them up.** "First, outline the answer. Then expand each section." Two messages > one 5000-word prompt.
- **For sensitive work, switch the model dropdown to `gemma-4-12b` first.** The output stays on this box.
- **Use skills (`/`)** for repeated tasks. Once a skill is set up right, you can re-run the same workflow in one slash.
