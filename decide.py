#!/usr/bin/env python3
"""
decide.py — Slack Thread → Decision Extractor
Paste a Slack thread, get back a clean decision record.

Usage:
  CLI:   python decide.py "paste your thread here"
         cat thread.txt | python decide.py
  Web:   python decide.py --web           (opens http://localhost:5100)
  File:  python decide.py --file thread.txt

LLM backends (in priority order):
  1. Ollama local  (default, free, private)
  2. OpenAI        (set OPENAI_API_KEY)
  3. Anthropic     (set ANTHROPIC_API_KEY)
"""

import json
import os
import sys
import argparse
import textwrap
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ── LLM Config ────────────────────────────────────────────────────────────────

OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OPENAI_KEY   = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_KEY= os.getenv("ANTHROPIC_API_KEY", "")

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a decision extraction assistant.
Given a Slack thread, extract every clear decision, agreement, or commitment made.
Return ONLY a valid JSON object — no markdown, no commentary, nothing else.

JSON schema:
{
  "decisions": [
    {
      "decision": "one clear sentence stating what was decided",
      "owner": "person responsible, or null if unknown",
      "rationale": "why this was decided, or null if not stated",
      "action_items": ["specific next steps, if any"],
      "date_mentioned": "date referenced in thread, or null",
      "confidence": "high | medium | low"
    }
  ],
  "summary": "one sentence summary of the whole thread",
  "participants": ["names or handles mentioned"],
  "thread_date": "date of thread if detectable, or null"
}

Rules:
- Extract only real decisions — not questions, brainstorming, or casual chat
- If no decisions were made, return decisions: []
- Keep decision statements concise and specific
- confidence=high means unambiguous; low means inferred"""

# ── LLM Backends ─────────────────────────────────────────────────────────────

def _post_json(url: str, payload: dict, headers: dict = {}) -> dict:
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json", **headers
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def _call_ollama(thread: str) -> str:
    payload = {
        "model":  OLLAMA_MODEL,
        "prompt": f"<system>\n{SYSTEM_PROMPT}\n</system>\n\nSlack thread:\n{thread}",
        "stream": False,
    }
    result = _post_json(f"{OLLAMA_URL}/api/generate", payload)
    return result.get("response", "")


def _call_openai(thread: str) -> str:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": f"Slack thread:\n{thread}"},
        ],
        "response_format": {"type": "json_object"},
    }
    result = _post_json(
        "https://api.openai.com/v1/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
    )
    return result["choices"][0]["message"]["content"]


def _call_anthropic(thread: str) -> str:
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": f"Slack thread:\n{thread}"}],
    }
    result = _post_json(
        "https://api.anthropic.com/v1/messages",
        payload,
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
    )
    return result["content"][0]["text"]


def call_llm(thread: str) -> str:
    """Try Ollama first, fall back to OpenAI, then Anthropic."""
    # Try Ollama (local, no API key required)
    try:
        out = _call_ollama(thread)
        if out.strip():
            return out, "ollama"
    except Exception:
        pass

    # Try OpenAI
    if OPENAI_KEY:
        try:
            out = _call_openai(thread)
            if out.strip():
                return out, "openai"
        except Exception:
            pass

    # Try Anthropic
    if ANTHROPIC_KEY:
        try:
            out = _call_anthropic(thread)
            if out.strip():
                return out, "anthropic"
        except Exception:
            pass

    raise RuntimeError(
        "No LLM available.\n"
        "Options:\n"
        "  • Run Ollama locally:  ollama serve\n"
        "  • Set OPENAI_API_KEY env var\n"
        "  • Set ANTHROPIC_API_KEY env var"
    )


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_response(raw: str) -> dict:
    """Extract JSON from LLM response, tolerating common formatting issues."""
    text = raw.strip()
    # Strip markdown fences
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    # Find first { ... }
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    return json.loads(text)


# ── Formatter ─────────────────────────────────────────────────────────────────

def format_markdown(result: dict, backend: str = "") -> str:
    lines = []
    now   = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Decision Record\n*Extracted {now}*")
    if backend:
        lines.append(f"*LLM: {backend}*")
    lines.append("")

    if result.get("summary"):
        lines.append(f"**Thread summary:** {result['summary']}\n")

    decisions = result.get("decisions", [])
    if not decisions:
        lines.append("*No decisions found in this thread.*")
        return "\n".join(lines)

    for i, d in enumerate(decisions, 1):
        lines.append(f"## Decision {i}")
        lines.append(f"**{d.get('decision','(no text)')}**\n")
        if d.get("owner"):
            lines.append(f"- **Owner:** {d['owner']}")
        if d.get("rationale"):
            lines.append(f"- **Rationale:** {d['rationale']}")
        if d.get("date_mentioned"):
            lines.append(f"- **Date referenced:** {d['date_mentioned']}")
        conf = d.get("confidence", "")
        if conf:
            icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(conf, "")
            lines.append(f"- **Confidence:** {icon} {conf}")
        actions = d.get("action_items", [])
        if actions:
            lines.append("- **Action items:**")
            for a in actions:
                lines.append(f"  - {a}")
        lines.append("")

    if result.get("participants"):
        lines.append(f"**Participants:** {', '.join(result['participants'])}")

    return "\n".join(lines)


# ── Core ──────────────────────────────────────────────────────────────────────

def extract(thread: str) -> tuple[dict, str]:
    """Extract decisions from thread text. Returns (result_dict, backend_name)."""
    if not thread or not thread.strip():
        raise ValueError("Thread text is empty.")
    raw, backend = call_llm(thread)
    result = parse_response(raw)
    return result, backend


# ── Web UI ────────────────────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slack → Decisions</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#0f172a;color:#e2e8f0;min-height:100vh;padding:32px 16px}
  .wrap{max-width:780px;margin:0 auto}
  h1{font-size:24px;font-weight:700;margin-bottom:4px;color:#f8fafc}
  .sub{font-size:14px;color:#64748b;margin-bottom:32px}
  label{font-size:12px;font-weight:600;color:#94a3b8;
        text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:6px}
  textarea{width:100%;height:200px;padding:14px;border-radius:10px;
           border:1px solid #1e293b;background:#1e293b;color:#e2e8f0;
           font-size:14px;resize:vertical;outline:none;line-height:1.6}
  textarea:focus{border-color:#6366f1}
  textarea::placeholder{color:#475569}
  .row{display:flex;gap:12px;margin:16px 0;align-items:center}
  select{padding:8px 12px;border-radius:8px;border:1px solid #1e293b;
         background:#1e293b;color:#e2e8f0;font-size:13px;outline:none}
  button{padding:10px 24px;background:#6366f1;color:#fff;border:none;
         border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;transition:.15s}
  button:hover{background:#4f46e5}
  button:disabled{opacity:.5;cursor:default}
  .out{margin-top:24px;display:none}
  .out.show{display:block}
  .card{background:#1e293b;border:1px solid #2d3f55;border-radius:10px;padding:20px;margin-bottom:12px}
  .d-title{font-size:16px;font-weight:700;color:#f1f5f9;margin-bottom:10px}
  .meta{font-size:12px;color:#64748b;display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px}
  .badge{padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600}
  .high{background:rgba(34,197,94,.15);color:#22c55e}
  .medium{background:rgba(234,179,8,.15);color:#eab308}
  .low{background:rgba(239,68,68,.15);color:#ef4444}
  .actions-list{margin-top:8px;padding-left:16px}
  .actions-list li{font-size:13px;color:#94a3b8;margin:3px 0}
  .summary-bar{background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
               border-radius:8px;padding:12px 16px;margin-bottom:16px;
               font-size:14px;color:#a5b4fc}
  .empty{color:#475569;font-size:14px;padding:24px;text-align:center}
  .err{color:#f87171;font-size:13px;margin-top:8px}
  .copy-btn{float:right;padding:4px 10px;font-size:11px;background:#334155;
            border-radius:5px;cursor:pointer;border:none;color:#94a3b8}
  .copy-btn:hover{background:#475569;color:#e2e8f0}
  .backend{font-size:11px;color:#334155;margin-left:auto}
  pre{background:#0f172a;padding:14px;border-radius:8px;font-size:12px;
      overflow-x:auto;white-space:pre-wrap;margin-top:12px;color:#94a3b8;display:none}
  .show-json{font-size:11px;color:#475569;cursor:pointer;margin-top:8px;
             background:none;border:none;padding:0;text-decoration:underline}
  .show-json:hover{color:#94a3b8}
</style>
</head>
<body>
<div class="wrap">
  <h1>🧵 Slack → Decisions</h1>
  <div class="sub">Paste a Slack thread. Get back a clean decision record.</div>

  <label for="thread">Slack thread</label>
  <textarea id="thread" placeholder="Paste your Slack thread here...

Example:
Alice: Should we use Postgres or MySQL for this?
Bob: I've worked with both. Postgres has better JSON support.
Alice: Makes sense, let's go with Postgres.
Charlie: Agreed. I'll update the infra docs.
Alice: @Charlie owns the DB setup. Target: end of sprint."></textarea>

  <div class="row">
    <button id="btn" onclick="run()">Extract decisions</button>
    <span class="backend" id="backend-lbl"></span>
  </div>
  <div class="err" id="err"></div>

  <div class="out" id="out"></div>
</div>

<script>
async function run() {
  const thread = document.getElementById('thread').value.trim();
  const btn = document.getElementById('btn');
  const errEl = document.getElementById('err');
  const outEl = document.getElementById('out');
  errEl.textContent = '';
  if (!thread) { errEl.textContent = 'Paste a thread first.'; return; }

  btn.disabled = true; btn.textContent = 'Extracting…';
  outEl.className = 'out';

  try {
    const r = await fetch('/extract', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({thread})
    });
    const d = await r.json();
    if (!d.ok) { errEl.textContent = d.error; return; }
    renderResult(d);
  } catch(e) {
    errEl.textContent = 'Request failed: ' + e.message;
  } finally {
    btn.disabled = false; btn.textContent = 'Extract decisions';
  }
}

function renderResult(d) {
  const outEl = document.getElementById('out');
  const backEl = document.getElementById('backend-lbl');
  backEl.textContent = 'via ' + (d.backend||'llm');

  const decisions = d.result?.decisions || [];
  const summary   = d.result?.summary || '';

  let html = '';
  if (summary) html += `<div class="summary-bar">💬 ${esc(summary)}</div>`;

  if (!decisions.length) {
    html += '<div class="card"><div class="empty">No decisions found in this thread.</div></div>';
  } else {
    decisions.forEach((dec, i) => {
      const conf = dec.confidence || 'medium';
      const actions = (dec.action_items||[]).map(a=>`<li>${esc(a)}</li>`).join('');
      html += `<div class="card">
        <button class="copy-btn" onclick="copyDec(${i})">Copy</button>
        <div class="d-title">${esc(dec.decision||'')}</div>
        <div class="meta">
          ${dec.owner      ? `<span>👤 ${esc(dec.owner)}</span>` : ''}
          ${dec.date_mentioned ? `<span>📅 ${esc(dec.date_mentioned)}</span>` : ''}
          <span class="badge ${conf}">${conf} confidence</span>
        </div>
        ${dec.rationale ? `<div style="font-size:13px;color:#94a3b8;margin-bottom:6px">${esc(dec.rationale)}</div>` : ''}
        ${actions ? `<ul class="actions-list">${actions}</ul>` : ''}
      </div>`;
    });
  }

  const raw = JSON.stringify(d.result, null, 2);
  html += `<button class="show-json" onclick="toggleJson(this)">show JSON</button>
           <pre id="raw-json">${esc(raw)}</pre>`;

  outEl.innerHTML = html;
  outEl.className = 'out show';

  // Store decisions for copy
  window._decisions = decisions;
  window._rawResult = d.result;
}

function copyDec(i) {
  const d = window._decisions[i];
  if (!d) return;
  let text = `Decision: ${d.decision}`;
  if (d.owner)     text += `\nOwner: ${d.owner}`;
  if (d.rationale) text += `\nRationale: ${d.rationale}`;
  if (d.action_items?.length) text += `\nActions:\n${d.action_items.map(a=>'  - '+a).join('\n')}`;
  navigator.clipboard.writeText(text);
}

function toggleJson(btn) {
  const pre = document.getElementById('raw-json');
  const show = pre.style.display === 'block';
  pre.style.display = show ? 'none' : 'block';
  btn.textContent   = show ? 'show JSON' : 'hide JSON';
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

document.getElementById('thread').addEventListener('keydown', e => {
  if ((e.metaKey||e.ctrlKey) && e.key === 'Enter') run();
});
</script>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress access log

    def _send(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", _HTML.encode())
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        if self.path != "/extract":
            self._send(404, "text/plain", b"Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length).decode())
        thread = body.get("thread", "").strip()
        try:
            result, backend = extract(thread)
            resp = json.dumps({"ok": True, "result": result, "backend": backend})
            self._send(200, "application/json", resp.encode())
        except Exception as e:
            resp = json.dumps({"ok": False, "error": str(e)})
            self._send(200, "application/json", resp.encode())


# ── CLI ───────────────────────────────────────────────────────────────────────

def cli_main():
    parser = argparse.ArgumentParser(
        description="Extract decisions from a Slack thread.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python decide.py "Alice: Let's go with Postgres. Bob: Agreed."
          cat thread.txt | python decide.py
          python decide.py --file thread.txt
          python decide.py --file thread.txt --json
          python decide.py --web
        """),
    )
    parser.add_argument("thread", nargs="?", help="Thread text (or use --file / stdin)")
    parser.add_argument("--file",    "-f", help="Read thread from file")
    parser.add_argument("--web",     "-w", action="store_true", help="Start web UI")
    parser.add_argument("--port",    "-p", type=int, default=5100, help="Web port (default 5100)")
    parser.add_argument("--json",    "-j", action="store_true", help="Output raw JSON")
    parser.add_argument("--model",   "-m", help=f"Ollama model (default: {OLLAMA_MODEL})")
    args = parser.parse_args()

    if args.model:
        import decide as _self
        _self.OLLAMA_MODEL = args.model
        globals()["OLLAMA_MODEL"] = args.model

    # Web mode
    if args.web:
        server = HTTPServer(("0.0.0.0", args.port), _Handler)
        url = f"http://localhost:{args.port}"
        print(f"🧵 Slack → Decisions  |  {url}")
        print("   Paste a thread in the browser. Cmd+Enter to extract.")
        print("   Press Ctrl+C to stop.\n")
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
        return

    # Determine thread input
    thread = ""
    if args.file:
        with open(args.file) as f:
            thread = f.read()
    elif args.thread:
        thread = args.thread
    elif not sys.stdin.isatty():
        thread = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(0)

    # Extract
    try:
        result, backend = extract(thread)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown(result, backend))


if __name__ == "__main__":
    cli_main()
