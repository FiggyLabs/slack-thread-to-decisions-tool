# 🧵 Slack Thread → Decisions

Paste a messy Slack thread. Get back a clean decision record.

No Slack account needed. No API keys needed. Runs locally.

---

## What it does

Remote teams make decisions in Slack threads and immediately lose them. This tool reads a thread and returns:

- **Decision** — what was actually decided, as one clear sentence
- **Owner** — who is responsible
- **Rationale** — why the decision was made
- **Action items** — specific next steps
- **Confidence** — how clearly the decision was stated

---

## Quickstart

```bash
git clone https://github.com/FiggyDev/slack-thread-to-decisions-tool
cd slack-thread-to-decisions-tool
pip install -r requirements.txt
```

**Web UI** (easiest):
```bash
python decide.py --web
# Opens http://localhost:5100
```

**CLI**:
```bash
python decide.py "Alice: Let's use Postgres. Bob: Agreed. Charlie: I'll update the docs."

# From a file
python decide.py --file thread.txt

# From stdin
cat thread.txt | python decide.py

# Raw JSON output
python decide.py --file thread.txt --json
```

---

## LLM options

The tool tries backends in this order. The first one available wins.

| Backend | Requirement | Privacy |
|---|---|---|
| **Ollama (local)** | `ollama serve` running | ✅ Fully local |
| **OpenAI** | `OPENAI_API_KEY` env var | Cloud |
| **Anthropic** | `ANTHROPIC_API_KEY` env var | Cloud |

### Local setup (recommended)

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2:3b     # fast, good quality
# or
ollama pull gemma3:4b       # higher quality, slower
```

### Use a specific model
```bash
python decide.py --model gemma3:4b "your thread"
# or
OLLAMA_MODEL=qwen2.5:3b python decide.py --web
```

### Cloud fallback
```bash
export OPENAI_API_KEY=sk-...
python decide.py "your thread"
```

---

## Example

**Input:**
```
Alice: Should we use Postgres or MySQL for the new service?
Bob: I've used both. Postgres has better JSON support and we'll need that for metadata.
Alice: That's a good point. Anyone disagree?
Charlie: No objections. Let's go with Postgres.
Alice: Agreed. @Charlie can you update the infra docs and add it to the ADR?
Charlie: On it. Will be done by Friday.
```

**Output:**
```markdown
# Decision Record

**Thread summary:** The team decided to use Postgres over MySQL for better JSON support.

## Decision 1
**Use Postgres for the new service instead of MySQL**

- **Owner:** Charlie
- **Rationale:** Postgres has better JSON support needed for metadata storage
- **Confidence:** 🟢 high
- **Action items:**
  - Update infrastructure documentation
  - Add decision to ADR
  - Complete by Friday
```

---

## Requirements

```
# requirements.txt — zero required deps for local Ollama
# Optional, for cloud fallbacks:
openai>=1.0       # pip install openai     (OpenAI only)
anthropic>=0.20   # pip install anthropic  (Anthropic only)
```

Pure stdlib for local Ollama. No `requests`, no frameworks.

---

## Free vs Paid

### Free (this repo — forever)

- ✅ CLI tool — unlimited use
- ✅ Web UI (local)
- ✅ Local LLM via Ollama
- ✅ Cloud LLM fallbacks (OpenAI / Anthropic — your own keys)
- ✅ JSON and Markdown output
- ✅ Single thread extraction

### Paid (coming — [slack-decisions.app](https://slack-decisions.app))

- 🔌 **Slack App** — slash command `/decide` inside Slack, no copy-paste
- 📚 **Decision log** — searchable history of all decisions across channels
- 👥 **Team workspace** — shared log across your whole team
- 📬 **Weekly digest** — decisions summary sent to your channel every Monday
- 📤 **Export** — push to Notion, Confluence, Linear
- 🔔 **Reminders** — ping owners when action items go stale

---

## Privacy

When running locally with Ollama: your thread text never leaves your machine.

Cloud backends (OpenAI/Anthropic) send thread text to those providers under their standard privacy policies.

---

## Contributing

PRs welcome. Keep it simple — this tool should stay zero-dependency for local use.

---

## License

MIT
