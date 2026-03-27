# ✅ Settled

**Your team makes decisions in Slack. Settled captures them.**

Paste a thread. Get a clean decision record — owner, rationale, action items — in seconds. Runs on your machine. No Slack account needed.

---

## The problem

Your team spent 40 messages debating a tech stack choice. Somewhere in the middle, a decision was made. Three days later nobody can find it, nobody agrees on what was decided, and the debate starts again.

Decisions buried in threads aren't decisions — they're liabilities.

---

## The solution

Paste the thread. Settled reads it with a local AI model and hands you back:

- **What was decided** — one clear sentence
- **Who owns it** — the person responsible
- **Why** — the rationale, if it was stated
- **What happens next** — action items with owners
- **Confidence** — how clearly the decision was actually made

No Slack API. No login. No data leaving your machine.

---

## Demo

### The problem

This is a real-looking Slack thread. A decision got made somewhere in the middle. Can you find it? Can you find who owns what?

**thread.txt**

```
Maya:    so are we going with Stripe or Paddle for billing? we need to decide this week
Tom:     I looked at both — Paddle handles VAT automatically which is huge for EU customers
Maya:    yeah but Stripe has way better docs and we already have a test account
Tom:     true, the VAT thing is a real headache though, we'd have to handle it ourselves with Stripe
Priya:   can we just decide? we're burning time
Tom:     fine, I'd go Stripe if someone owns the VAT compliance piece
Maya:    @Priya can you look into what VAT compliance actually needs from us?
Priya:   yeah I can do that, give me until Friday
Maya:    ok Stripe it is. @Tom set up the live account and get us keys by EOD Thursday
Tom:     on it
Maya:    once we have keys @Priya can you add them to the secrets manager?
Priya:   yep
```

### The command

```bash
python settled.py --file thread.txt
```

### The output

```
# Decision Record

Thread summary: The team chose Stripe over Paddle for billing, with action
items to handle EU VAT compliance.

## Decision 1
**Use Stripe as the billing provider**

- Owner:      Maya
- Rationale:  Better documentation, existing test account, and team familiarity
              outweighed Paddle's automatic VAT handling
- Confidence: 🟢 high
- Action items:
  - Tom:   set up live Stripe account and deliver API keys by Thursday EOD
  - Priya: research VAT compliance requirements by Friday
  - Priya: add Stripe keys to secrets manager once received

## Open questions
  - VAT compliance scope is unresolved — Priya's Friday research will determine
    whether additional tooling is needed
```

### Why it matters

12 messages → 1 decision, 3 action items, 2 owners, 1 open question. Logged in under 5 seconds. No one has to reread the thread on Monday.

---

## Try it now

Copy this, save it as `thread.txt`, and run:

```bash
git clone https://github.com/FiggyDev/slack-thread-to-decisions-tool
cd slack-thread-to-decisions-tool
python settled.py --file thread.txt
```

That's the whole setup.

---

## CLI demos

```bash
# Standard output
python settled.py --file thread.txt

# JSON — pipe into other tools
python settled.py --file thread.txt --json

# Inline thread
python settled.py "Alice: Let's use Postgres. Bob: Agreed. Alice: @Bob own the migration."

# Web UI — paste and press Cmd+Enter
python settled.py --web
```

**JSON output** (`--json` flag):

```json
{
  "summary": "The team chose Stripe over Paddle for billing.",
  "decisions": [
    {
      "title": "Use Stripe as the billing provider",
      "owner": "Maya",
      "rationale": "Better docs, existing test account, team familiarity",
      "confidence": "high",
      "action_items": [
        "Tom: set up live account and deliver API keys by Thursday EOD",
        "Priya: research VAT compliance requirements by Friday",
        "Priya: add Stripe keys to secrets manager once received"
      ],
      "open_questions": [
        "VAT compliance scope — to be resolved after Priya's Friday research"
      ]
    }
  ]
}
```

Prefer the web UI? `python settled.py --web` — opens at `http://localhost:5100`, paste and press **Cmd+Enter**.

---

## Get started

```bash
git clone https://github.com/FiggyDev/slack-thread-to-decisions-tool
cd slack-thread-to-decisions-tool
python settled.py --web
```

Opens at `http://localhost:5100`. Paste your thread, press **Cmd+Enter**.

No install step. No environment setup. No account.

> **First time?** You'll need Ollama running locally — [download here](https://ollama.com), then:
> ```bash
> ollama pull llama3.2:3b
> ```
> That's it. Settled routes to it automatically.

---

## Why local-first

Most AI tools send your data to external servers. Settled doesn't.

When you run it with Ollama, your Slack thread text stays on your machine. It never touches a cloud API. That matters when threads contain engineering decisions, business strategy, or anything confidential.

Cloud fallbacks (OpenAI, Anthropic) are available if you prefer, using your own keys.

---

## CLI usage

```bash
# Paste a thread directly
python settled.py "Alice: Let's go with Postgres. Bob: Agreed."

# From a file
python settled.py --file thread.txt

# From stdin
cat thread.txt | python settled.py

# Raw JSON output (great for piping into other tools)
python settled.py --file thread.txt --json

# Use a specific model
python settled.py --model gemma3:4b --file thread.txt
```

---

## LLM backends

Settled tries these in order — first available wins:

| Backend | Setup | Privacy |
|---|---|---|
| Ollama (local) | `ollama serve` running | ✅ Stays on your machine |
| OpenAI | `OPENAI_API_KEY` env var | Sent to OpenAI |
| Anthropic | `ANTHROPIC_API_KEY` env var | Sent to Anthropic |

For local use: `ollama pull llama3.2:3b` (fast) or `ollama pull gemma3:4b` (better quality).

Zero required dependencies for local Ollama. Pure Python stdlib.

---

## Free vs paid

### Free — this repo, forever

- ✅ Web UI (local)
- ✅ CLI with JSON output
- ✅ Local LLM via Ollama — fully private
- ✅ Cloud LLM fallbacks with your own keys
- ✅ Unlimited use, no account

### Settled Pro — coming soon

For teams who want this to live inside Slack itself:

| Feature | Description |
|---|---|
| `/settled` slash command | Extract decisions without leaving Slack |
| Decision log | Searchable history across all channels |
| Team workspace | Shared log your whole team can access |
| Monday digest | Weekly decisions summary sent to your channel |
| Reminders | Ping action item owners when things go stale |
| Export | Push decisions to Notion, Confluence, or Linear |

→ [Join the waitlist](https://github.com/FiggyDev/slack-thread-to-decisions-tool/issues/1)

---

## Requirements

Python 3.8+. No required packages for local use.

Optional for cloud:
```bash
pip install openai       # OpenAI backend
pip install anthropic    # Anthropic backend
```

---

## Contributing

PRs welcome. The goal is to keep this zero-dependency for local use — please don't add frameworks or build steps to the core path.

---

## License

MIT
