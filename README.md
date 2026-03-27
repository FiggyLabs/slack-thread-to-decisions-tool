*Part of [Figgy Labs](https://github.com/FiggyLabs/figgy-labs)*

# ✅ Settled

**Your team makes decisions in Slack. Settled captures them.**

Paste a thread. Get a clean decision record — owner, rationale, action items — in seconds.
Runs on your machine. No Slack account needed. No data leaves your machine.

---

## The problem

Your team spent 15 messages debating a tech choice. Somewhere in the middle, a decision was made. Three days later nobody can find it, nobody agrees on what was decided, and the debate starts again.

Decisions buried in Slack threads aren't decisions — they're liabilities.

---

## Demo

### Input — a real Slack thread

```
Maya:    so are we going with Stripe or Paddle for billing? we need to decide this week
Tom:     I looked at both — Paddle handles VAT automatically which is huge for EU customers
Maya:    yeah but Stripe has way better docs and we already have a test account
Tom:     true, the VAT thing is a real headache though, we'd have to handle it ourselves
Priya:   can we just decide? we're burning time
Tom:     fine, I'd go Stripe if someone owns the VAT compliance piece
Maya:    @Priya can you look into what VAT compliance actually needs from us?
Priya:   yeah I can do that, give me until Friday
Maya:    ok Stripe it is. @Tom set up the live account and get us keys by EOD Thursday
Tom:     on it
Maya:    once we have keys @Priya can you add them to the secrets manager?
Priya:   yep
```

### Command

```bash
python settled.py --file thread.txt
```

### Output

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

12 messages → 1 decision, 3 action items, 2 owners, 1 open question. Logged in under 5 seconds. No one reruns this debate on Monday.

---

## Try it now

```bash
git clone https://github.com/FiggyDev/slack-thread-to-decisions-tool
cd slack-thread-to-decisions-tool
python settled.py --file examples/billing_thread.txt
```

No install. No environment setup. No account. Just Python 3.8+.

> **First time?** You'll need Ollama for local AI — [download here](https://ollama.com), then:
> ```bash
> ollama pull llama3.2:3b
> ```
> Settled routes to it automatically.

---

## Install

```bash
git clone https://github.com/FiggyDev/slack-thread-to-decisions-tool
cd slack-thread-to-decisions-tool
```

That's it. No `pip install`. No build step. Pure Python stdlib for local use.

Optional cloud backends:

```bash
pip install openai       # for OpenAI fallback
pip install anthropic    # for Anthropic fallback
```

---

## CLI usage

```bash
# From a file
python settled.py --file thread.txt

# From stdin
cat thread.txt | python settled.py

# Inline
python settled.py "Alice: Let's use Postgres. Bob: Agreed. Alice: @Bob owns migration."

# Raw JSON — pipe into other tools
python settled.py --file thread.txt --json

# Specific model
python settled.py --file thread.txt --model gemma3:4b

# Web UI — paste in browser, Cmd+Enter to extract
python settled.py --web
```

### JSON output

```bash
python settled.py --file examples/billing_thread.txt --json
```

```json
{
  "summary": "The team chose Stripe over Paddle for billing.",
  "decisions": [
    {
      "decision": "Use Stripe as the billing provider",
      "owner": "Maya",
      "rationale": "Better docs, existing test account, team familiarity",
      "confidence": "high",
      "action_items": [
        "Tom: set up live Stripe account and deliver API keys by Thursday EOD",
        "Priya: research VAT compliance requirements by Friday",
        "Priya: add Stripe keys to secrets manager once received"
      ],
      "open_questions": [
        "VAT compliance scope — pending Priya's Friday research"
      ]
    }
  ],
  "participants": ["Maya", "Tom", "Priya"]
}
```

---

## Web UI

```bash
python settled.py --web
```

Opens at `http://localhost:5100`. Paste your thread, press **Cmd+Enter**.

---

## LLM backends

Settled tries these in order — first available wins:

| Backend       | Setup                        | Privacy                     |
|---------------|------------------------------|-----------------------------|
| Ollama (local)| `ollama serve` running       | ✅ Stays on your machine    |
| OpenAI        | `OPENAI_API_KEY` env var     | Sent to OpenAI              |
| Anthropic     | `ANTHROPIC_API_KEY` env var  | Sent to Anthropic           |

For local use: `ollama pull llama3.2:3b` (fast) or `ollama pull gemma3:4b` (better quality).

---

## Why local-first

Most AI tools send your data to external servers. Settled doesn't.

When you run it with Ollama, your Slack thread text stays on your machine. It never touches a cloud API. That matters when threads contain engineering decisions, business strategy, or anything confidential.

Cloud backends (OpenAI, Anthropic) are available if you prefer, using your own keys.

---

## Free vs paid

### Free — this repo, forever

| Feature | |
|---|---|
| CLI with Markdown and JSON output | ✅ |
| Local web UI | ✅ |
| Local LLM via Ollama — fully private | ✅ |
| Cloud LLM fallbacks with your own API keys | ✅ |
| Unlimited use, no account | ✅ |

### Settled Pro — coming soon

For teams who want decisions to live inside Slack itself:

| Feature | Description |
|---|---|
| `/settled` slash command | Extract decisions without leaving Slack |
| Decision log | Searchable history across all channels |
| Team workspace | Shared log your whole team can access |
| Weekly digest | Decisions summary delivered to your channel |
| Reminders | Ping action item owners when things go stale |
| Export | Push to Notion, Confluence, or Linear |

→ [Join the waitlist](https://github.com/FiggyDev/slack-thread-to-decisions-tool/issues/1)

---

## Requirements

Python 3.8+. No required packages for local use.

---

## Contributing

PRs welcome. The goal is to keep this zero-dependency for local use — please don't add frameworks or build steps to the core path.

---

## License

MIT
