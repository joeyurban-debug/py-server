"""
Local Test Server - Flask + embedded UI
Double-click the .exe, browser opens automatically.
"""

import threading
import webbrowser
import time
import json
import sys
import os
from datetime import datetime
from flask import Flask, jsonify, request, Response

app = Flask(__name__)
REQUEST_LOG = []

# --- Embedded UI --------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Local Test Server</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #0f1117;
    --surface:  #181c27;
    --border:   #272c3d;
    --accent:   #5b8dee;
    --accent2:  #3ecf8e;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --danger:   #f87171;
    --mono:     'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    line-height: 1.5;
    min-height: 100vh;
  }

  /* -- Layout -- */
  header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }
  .logo { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; color: var(--text); }
  .logo span { color: var(--accent); }
  .badge {
    background: #1a2e1a;
    color: var(--accent2);
    border: 1px solid #2a4a2a;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  .port-badge {
    margin-left: auto;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--muted);
  }
  .port-badge strong { color: var(--accent); }

  main { display: grid; grid-template-columns: 340px 1fr; height: calc(100vh - 53px); }

  /* -- Left Panel -- */
  .panel {
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-header {
    padding: 14px 18px 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .clear-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    cursor: pointer;
    transition: all 0.15s;
    text-transform: none;
    letter-spacing: 0;
  }
  .clear-btn:hover { border-color: var(--danger); color: var(--danger); }

  .log-list { overflow-y: auto; flex: 1; }
  .log-item {
    padding: 10px 18px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.1s;
    display: grid;
    grid-template-columns: 52px 1fr;
    gap: 8px;
    align-items: start;
  }
  .log-item:hover { background: var(--surface); }
  .log-item.active { background: #1a2035; }
  .method {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    text-align: center;
    letter-spacing: 0.3px;
  }
  .GET    { background: #1a3a2a; color: var(--accent2); }
  .POST   { background: #1e2f4a; color: var(--accent); }
  .PUT    { background: #2e2a12; color: #f5c542; }
  .DELETE { background: #2e1a1a; color: var(--danger); }
  .PATCH  { background: #2a1e35; color: #c084fc; }

  .log-meta { min-width: 0; }
  .log-path {
    font-family: var(--mono);
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
  }
  .log-time { font-size: 10px; color: var(--muted); margin-top: 2px; }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 8px;
    color: var(--muted);
    font-size: 13px;
  }
  .empty-icon { font-size: 32px; opacity: 0.4; }

  /* -- Right Panel -- */
  .detail { display: flex; flex-direction: column; overflow: hidden; }

  .tabs {
    display: flex;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    padding: 0 18px;
    gap: 2px;
  }
  .tab {
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    transition: color 0.15s;
  }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  .tab:hover:not(.active) { color: var(--text); }

  /* -- Try It -- */
  .try-panel { flex: 1; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }

  .field-label { font-size: 11px; font-weight: 600; color: var(--muted); letter-spacing: 0.5px; margin-bottom: 5px; }

  .input-row { display: flex; gap: 8px; }
  .method-select {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 8px 10px;
    border-radius: 6px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    outline: none;
    width: 90px;
  }
  .url-input, .body-input, .headers-input {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 8px 12px;
    border-radius: 6px;
    font-family: var(--mono);
    font-size: 12px;
    outline: none;
    width: 100%;
    transition: border-color 0.15s;
  }
  .url-input:focus, .body-input:focus, .headers-input:focus {
    border-color: var(--accent);
  }
  .body-input { resize: vertical; min-height: 100px; }
  .headers-input { resize: vertical; min-height: 60px; }

  .send-btn {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 9px 22px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: opacity 0.15s;
    align-self: flex-start;
  }
  .send-btn:hover { opacity: 0.85; }
  .send-btn:active { opacity: 0.7; }

  /* -- Response -- */
  .response-section { display: flex; flex-direction: column; gap: 8px; }
  .response-meta {
    display: flex;
    gap: 12px;
    align-items: center;
    font-size: 12px;
  }
  .status-ok  { color: var(--accent2); font-weight: 700; font-family: var(--mono); }
  .status-err { color: var(--danger);  font-weight: 700; font-family: var(--mono); }
  .resp-time  { color: var(--muted); font-family: var(--mono); }

  .code-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    font-family: var(--mono);
    font-size: 12px;
    overflow: auto;
    max-height: 300px;
    white-space: pre-wrap;
    color: var(--text);
  }

  /* -- Request detail -- */
  .detail-content { flex: 1; overflow-y: auto; padding: 20px 24px; display: none; flex-direction: column; gap: 14px; }
  .detail-content.visible { display: flex; }

  .kv-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 12px; }
  .kv-table tr { border-bottom: 1px solid var(--border); }
  .kv-table td { padding: 7px 0; vertical-align: top; }
  .kv-table td:first-child { color: var(--muted); width: 140px; padding-right: 12px; }

  .placeholder-detail {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--muted);
    gap: 8px;
  }
  .placeholder-detail .icon { font-size: 28px; opacity: 0.3; }

  scrollbar-width: thin;
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
</head>
<body>

<header>
  <div class="logo">local<span>.</span>dev</div>
  <div class="badge">* RUNNING</div>
  <div class="port-badge">http://localhost:<strong id="port-display">3000</strong></div>
</header>

<main>
  <!-- Left: request log -->
  <div class="panel">
    <div class="panel-header">
      Requests
      <button class="clear-btn" onclick="clearLog()">Clear</button>
    </div>
    <div class="log-list" id="log-list">
      <div class="empty-state" id="empty-state">
        <div class="empty-icon"></div>
        <div>Waiting for requests...</div>
      </div>
    </div>
  </div>

  <!-- Right: detail + try it -->
  <div class="detail">
    <div class="tabs">
      <div class="tab active" onclick="switchTab('try')">Try It</div>
      <div class="tab" onclick="switchTab('detail')">Request Detail</div>
    </div>

    <!-- Try It panel -->
    <div class="try-panel" id="tab-try">
      <div>
        <div class="field-label">METHOD & URL</div>
        <div class="input-row">
          <select class="method-select" id="req-method">
            <option>GET</option><option>POST</option><option>PUT</option>
            <option>PATCH</option><option>DELETE</option>
          </select>
          <input class="url-input" id="req-url" placeholder="/api/hello" value="/api/hello">
        </div>
      </div>

      <div>
        <div class="field-label">HEADERS (JSON, optional)</div>
        <textarea class="headers-input" id="req-headers" placeholder='{"Content-Type": "application/json"}'></textarea>
      </div>

      <div>
        <div class="field-label">BODY (JSON, optional)</div>
        <textarea class="body-input" id="req-body" placeholder='{"key": "value"}'></textarea>
      </div>

      <button class="send-btn" onclick="sendRequest()">Send Request</button>

      <div class="response-section" id="response-section" style="display:none">
        <div class="field-label">RESPONSE</div>
        <div class="response-meta" id="response-meta"></div>
        <div class="code-block" id="response-body"></div>
      </div>
    </div>

    <!-- Detail panel -->
    <div class="detail-content" id="tab-detail">
      <div class="placeholder-detail" id="detail-placeholder">
        <div class="icon"></div>
        <div>Click a request to inspect it</div>
      </div>
      <div id="detail-data" style="display:none">
        <div class="field-label">REQUEST INFO</div>
        <table class="kv-table" id="detail-table"></table>
        <div class="field-label" style="margin-top:14px">BODY</div>
        <div class="code-block" id="detail-body">-</div>
      </div>
    </div>
  </div>
</main>

<script>
let logs = [];
let selectedId = null;
let activeTab = 'try';

// -- Tab switching ----------------------------------------------------------
function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', ['try','detail'][i] === tab);
  });
  document.getElementById('tab-try').style.display    = tab === 'try'    ? 'flex'  : 'none';
  document.getElementById('tab-detail').style.display = tab === 'detail' ? 'flex'  : 'none';
  document.getElementById('tab-detail').classList.toggle('visible', tab === 'detail');
}

// -- Log polling ------------------------------------------------------------
async function pollLogs() {
  try {
    const r = await fetch('/api/__log__');
    const data = await r.json();
    if (data.length !== logs.length) {
      logs = data;
      renderLog();
    }
  } catch(e) {}
  setTimeout(pollLogs, 800);
}

function renderLog() {
  const list = document.getElementById('log-list');
  const empty = document.getElementById('empty-state');
  if (!logs.length) { empty.style.display = 'flex'; return; }
  empty.style.display = 'none';

  // Only re-render if needed
  list.innerHTML = '';
  logs.slice().reverse().forEach(entry => {
    const el = document.createElement('div');
    el.className = 'log-item' + (entry.id === selectedId ? ' active' : '');
    el.onclick = () => selectEntry(entry.id);
    el.innerHTML = `
      <span class="method ${entry.method}">${entry.method}</span>
      <div class="log-meta">
        <div class="log-path">${entry.path}</div>
        <div class="log-time">${entry.time} . ${entry.status}</div>
      </div>`;
    list.appendChild(el);
  });
}

function selectEntry(id) {
  selectedId = id;
  renderLog();
  const entry = logs.find(l => l.id === id);
  if (!entry) return;

  document.getElementById('detail-placeholder').style.display = 'none';
  document.getElementById('detail-data').style.display = 'block';

  const rows = [
    ['Method',  entry.method],
    ['Path',    entry.path],
    ['Time',    entry.time],
    ['Status',  entry.status],
    ['IP',      entry.ip],
  ];
  if (entry.query) rows.push(['Query', entry.query]);

  document.getElementById('detail-table').innerHTML = rows
    .map(([k,v]) => `<tr><td>${k}</td><td>${v || '-'}</td></tr>`)
    .join('');

  const body = entry.body ? JSON.stringify(JSON.parse(entry.body), null, 2) : '-';
  document.getElementById('detail-body').textContent = body;

  switchTab('detail');
}

function clearLog() {
  fetch('/api/__log__/clear', { method: 'POST' });
  logs = [];
  selectedId = null;
  renderLog();
  document.getElementById('empty-state').style.display = 'flex';
}

// -- Try It ----------------------------------------------------------------
async function sendRequest() {
  const method  = document.getElementById('req-method').value;
  const url     = document.getElementById('req-url').value || '/';
  const rawHdr  = document.getElementById('req-headers').value.trim();
  const rawBody = document.getElementById('req-body').value.trim();

  let headers = { 'Content-Type': 'application/json' };
  if (rawHdr) { try { headers = { ...headers, ...JSON.parse(rawHdr) }; } catch(e) { alert('Invalid headers JSON'); return; } }

  const opts = { method, headers };
  if (rawBody && method !== 'GET') {
    try { JSON.parse(rawBody); opts.body = rawBody; } catch(e) { alert('Invalid body JSON'); return; }
  }

  const t0 = performance.now();
  try {
    const r = await fetch(url, opts);
    const elapsed = Math.round(performance.now() - t0);
    const text = await r.text();
    let pretty = text;
    try { pretty = JSON.stringify(JSON.parse(text), null, 2); } catch(e) {}

    const meta = document.getElementById('response-meta');
    const ok = r.status < 400;
    meta.innerHTML = `<span class="${ok ? 'status-ok' : 'status-err'}">${r.status} ${r.statusText}</span>
                      <span class="resp-time">${elapsed}ms</span>`;
    document.getElementById('response-body').textContent = pretty;
    document.getElementById('response-section').style.display = 'flex';
  } catch(e) {
    document.getElementById('response-meta').innerHTML = `<span class="status-err">Network error</span>`;
    document.getElementById('response-body').textContent = e.message;
    document.getElementById('response-section').style.display = 'flex';
  }
}

// set port display
fetch('/api/__meta__').then(r => r.json()).then(d => {
  document.getElementById('port-display').textContent = d.port;
}).catch(() => {});

pollLogs();
switchTab('try');
</script>
</body>
</html>
"""


# --- Internal API -------------------------------------------------------------

_log_lock = threading.Lock()
_log_counter = 0

def _add_log(method, path, status, ip, body=None, query=None):
    global _log_counter
    with _log_lock:
        _log_counter += 1
        REQUEST_LOG.append({
            "id":     _log_counter,
            "method": method,
            "path":   path,
            "status": str(status),
            "ip":     ip,
            "time":   datetime.now().strftime("%H:%M:%S"),
            "body":   body,
            "query":  query,
        })
        if len(REQUEST_LOG) > 200:
            REQUEST_LOG.pop(0)


@app.route("/api/__log__")
def get_log():
    return jsonify(REQUEST_LOG)


@app.route("/api/__log__/clear", methods=["POST"])
def clear_log():
    with _log_lock:
        REQUEST_LOG.clear()
    return jsonify({"ok": True})


@app.route("/api/__meta__")
def meta():
    return jsonify({"port": PORT})


@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")


# --- Your API routes (edit these) ---------------------------------------------

@app.route("/api/hello", methods=["GET"])
def hello():
    _add_log("GET", "/api/hello", 200, request.remote_addr)
    return jsonify({"message": "Hello from local.dev!", "timestamp": datetime.now().isoformat()})


@app.route("/api/echo", methods=["POST"])
def echo():
    body = request.get_json(silent=True) or {}
    raw  = json.dumps(body)
    _add_log("POST", "/api/echo", 200, request.remote_addr, body=raw)
    return jsonify({"echo": body, "received_at": datetime.now().isoformat()})


@app.route("/api/items", methods=["GET", "POST"])
def items():
    if request.method == "GET":
        _add_log("GET", "/api/items", 200, request.remote_addr,
                 query=request.query_string.decode())
        return jsonify({"items": ["alpha", "beta", "gamma"], "count": 3})
    else:
        body = request.get_json(silent=True) or {}
        _add_log("POST", "/api/items", 201, request.remote_addr, body=json.dumps(body))
        return jsonify({"created": True, "item": body}), 201


# Catch-all: log unknown routes
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def catch_all(path):
    body = None
    if request.method not in ("GET", "DELETE"):
        raw = request.get_data(as_text=True)
        if raw:
            body = raw
    full_path = "/" + path
    if request.query_string:
        full_path += "?" + request.query_string.decode()
    _add_log(request.method, "/" + path, 404, request.remote_addr,
             body=body, query=request.query_string.decode())
    return jsonify({"error": "Not found", "path": "/" + path}), 404


# --- Entry point --------------------------------------------------------------

PORT = 3000

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()
    print(f"  local.dev running -> http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
