# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]  # only so we can import mcp-server/server.py unchanged
# ///
"""
Kuya Hermes website: landing page + live read-only dashboard.

    uv run web/app.py            # → http://localhost:8787

The JSON API calls the SAME functions as the suki MCP server
(mcp-server/server.py), so the website, Hermes Desktop and Telegram all see
identical numbers. Read-only on purpose: writes (purchase orders, shift
covers) go through Kuya Hermes, which asks for confirmation first.
"""
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "mcp-server"))
import server as suki  # noqa: E402

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "hermes")
HERMES_API = os.environ.get("HERMES_API", "http://127.0.0.1:8642")


def _hermes_key() -> str:
    """API_SERVER_KEY from Hermes' .env. Read server-side only; never sent to the browser."""
    if os.environ.get("API_SERVER_KEY"):
        return os.environ["API_SERVER_KEY"]
    try:
        with open(os.path.join(HERMES_HOME, ".env"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("API_SERVER_KEY="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


def _playbook() -> str:
    """Kuya's skill + data rules, sent as `instructions` on every turn.

    The public API-server agent is locked to the suki MCP toolset only (no
    skills/terminal/files), so the playbook travels with the request instead.
    """
    skill_dir = os.path.join(REPO, "skills", "kuya-hermes-ops")
    parts = []
    for name in ("SKILL.md", os.path.join("references", "data-rules.md")):
        try:
            with open(os.path.join(skill_dir, name), encoding="utf-8") as f:
                parts.append(f.read())
        except OSError:
            pass
    parts.append(
        "You are answering on the public Kuya Hermes website. Only discuss Suki Mart operations "
        "using the suki tools. Refuse anything else briefly and politely. Tools appear as "
        "mcp__suki__<tool> (same as mcp_suki_<tool> in the playbook).\n\n"
        "OUTPUT FORMATTING RULES:\n"
        "- Always format multi-item or comparative data (sweeps, stockout alerts, shift gaps, purchase orders) "
        "using standard Markdown tables with leading and trailing pipes:\n"
        "  | Branch | Risk | Stockouts | Dup POs | Staff Short | Tickets | Deliveries |\n"
        "  |:---|:---|---:|---:|---:|---:|---:|\n"
        "  | ERM | high | 14 | 2 | 3 | 6 | 4 |\n"
        "- Use standard separators:\n"
        "  ━━━━━━━━━━━━━━━━━━━━ (section break)\n"
        "  ────────────────────── (minor break / before footer)\n"
        "- Format next actions as a clean numbered list (1., 2., 3.).\n"
        "- When proposing a purchase order or shift cover, always end with a clear question asking for confirmation (e.g. 'I-file ko na ba?')."
    )
    return "\n\n---\n\n".join(parts)


_CHAT_LOCK = __import__("threading").Semaphore(2)  # cap concurrent agent turns from the public site


def _ask_kuya(body: dict) -> dict:
    """Forward one chat turn to the real Hermes agent (Responses API).

    `conversation` keeps multi-turn context server-side, so a confirm
    ("oo, i-file mo na") lands in the same session as the proposal.
    """
    import urllib.error
    import urllib.request

    message = str(body.get("message", "")).strip()[:2000]
    if not message:
        return {"error": "Message cannot be empty. Please enter a question or command.", "_status": 400}
    conversation = str(body.get("conversation") or "kuya-web")[:80]
    req = urllib.request.Request(
        f"{HERMES_API}/v1/responses",
        data=json.dumps({"model": "hermes-agent", "input": message, "conversation": conversation,
                         "instructions": _playbook(), "store": True}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {_hermes_key()}"},
        method="POST",
    )
    if not _CHAT_LOCK.acquire(timeout=5):
        return {"error": "Kuya is currently busy handling another request. Please try again in a few seconds.", "_status": 429}
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
            err_json = json.loads(err_body)
            if isinstance(err_json, dict) and "error" in err_json:
                err_body = err_json["error"]
        except Exception:
            pass
        detail = f": {err_body}" if err_body else f" (HTTP {e.code})"
        return {"error": f"Hermes gateway returned an error{detail}. Is the agent configured correctly?", "_status": 502}
    except urllib.error.URLError as e:
        return {"error": f"Cannot connect to Hermes gateway at {HERMES_API}: {e.reason}. Ensure the agent gateway is running.", "_status": 502}
    except TimeoutError:
        return {"error": "Kuya response timed out. The agent gateway took too long to answer.", "_status": 504}
    finally:
        _CHAT_LOCK.release()

    if isinstance(data, dict) and data.get("error"):
        return {"error": str(data["error"]), "_status": 500}

    text, tools = [], []
    for item in data.get("output", []):
        if item.get("type") == "function_call":
            name = item.get("name", "")
            # Hermes routes MCP tools through a generic wrapper:
            #   tool_call {"calls": [{"name": "mcp__suki__branch_pulse", ...}]}
            # tool_describe only reads schemas, so it isn't a real action.
            if name == "tool_describe":
                continue
            if name == "tool_call":
                try:
                    calls = json.loads(item.get("arguments") or "{}").get("calls") or []
                    tools.extend(c.get("name", "") for c in calls if isinstance(c, dict))
                except (ValueError, AttributeError):
                    tools.append(name)
                continue
            tools.append(name)
        elif item.get("type") == "message" and item.get("phase") != "commentary":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text.append(c.get("text", ""))
    reply = "\n\n".join(t for t in text if t).strip()
    if not reply and not tools:
        reply = "(No response received from agent)"
    return {"reply": reply, "tools": tools, "id": data.get("id")}

STATIC = os.path.join(ROOT, "static")
ASSETS = os.path.join(REPO, "assets")
PORT = int(os.environ.get("PORT", "8787"))

PAGES = {"/": "index.html", "/dashboard": "dashboard.html"}


def _overview() -> dict:
    """Network totals for the landing page's live problem stats."""
    sweep = suki.network_sweep()
    rows = sweep.get("branches", [])
    dup_res = suki.query(
        "SELECT COUNT(*) AS n FROM (SELECT 1 FROM purchase_orders "
        "WHERE status IN ('pending','in_transit','partially_received') "
        "GROUP BY branch_id, product_id HAVING COUNT(*) > 1)"
    )
    dup_pairs = dup_res[0]["n"] if dup_res else 0

    oos_res = suki.query("SELECT COUNT(*) AS n FROM inventory WHERE on_hand = 0")
    oos = oos_res[0]["n"] if oos_res else 0

    unanswered_res = suki.query(
        "SELECT COUNT(*) AS n FROM support_tickets WHERE status IN ('open','pending') AND first_response_at IS NULL"
    )
    unanswered = unanswered_res[0]["n"] if unanswered_res else 0

    lead_res = suki.query(
        "SELECT s.name, s.promised_lead_time_days AS promised, "
        "ROUND(AVG(julianday(po.received_at) - julianday(po.ordered_at)), 1) AS actual "
        "FROM purchase_orders po JOIN suppliers s ON s.id = po.supplier_id "
        "WHERE po.received_at IS NOT NULL GROUP BY s.id "
        "ORDER BY actual - s.promised_lead_time_days DESC LIMIT 1"
    )
    lead = lead_res[0] if lead_res else {"name": "N/A", "promised": 0, "actual": 0}
    return {
        "as_of": "2026-09-30",
        "out_of_stock": oos,
        "duplicate_po_pairs": dup_pairs,
        "tickets_never_answered": unanswered,
        "worst_supplier": lead,
        "worst_branch": sweep.get("worst", "ALB"),
        "branches": len(rows),
    }


API = {
    "/api/overview": lambda _: _overview(),
    "/api/sweep": lambda _: suki.network_sweep(),
    "/api/branches": lambda _: suki.list_branches(),
}


SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")  # set when exposing the site through a tunnel


class Handler(BaseHTTPRequestHandler):
    def _authorized(self) -> bool:
        """HTTP Basic auth gate (any username) when SITE_PASSWORD is set."""
        if not SITE_PASSWORD:
            return True
        import base64
        import hmac

        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                _, _, pw = base64.b64decode(header[6:]).decode("utf-8").partition(":")
                if hmac.compare_digest(pw, SITE_PASSWORD):
                    return True
            except ValueError:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Kuya Hermes demo"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass
    def _json(self, obj, code: int = 200) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _file(self, path: str) -> None:
        if not os.path.isfile(path):
            return self._json({"error": f"File not found: {os.path.basename(path)}"}, 404)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        try:
            with open(path, "rb") as f:
                self._send(200, f.read(), ctype)
        except (IOError, OSError) as e:
            sys.stderr.write(f"[kuya-web] File read error {path}: {e}\n")
            self._json({"error": f"Error reading file: {e}"}, 500)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        if not self._authorized():
            return
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            if path in PAGES:
                return self._file(os.path.join(STATIC, PAGES[path]))
            if path in API:
                return self._json(API[path](path))
            if path.startswith("/api/pulse/"):
                branch_code = path.rsplit("/", 1)[-1]
                if not branch_code:
                    return self._json({"error": "Missing branch code in URL"}, 400)
                return self._json(suki.branch_pulse(branch_code))
            if path.startswith("/assets/"):
                return self._file(os.path.join(ASSETS, os.path.basename(path)))
            if path.startswith("/static/"):
                return self._file(os.path.join(STATIC, os.path.basename(path)))
            return self._json({"error": "not found"}, 404)
        except ValueError as e:  # unknown branch code etc.
            sys.stderr.write(f"[kuya-web] GET {path} client error: {e}\n")
            return self._json({"error": str(e)}, 400)
        except Exception as e:
            sys.stderr.write(f"[kuya-web] GET {path} internal error: {e}\n")
            return self._json({"error": f"Internal server error: {e}"}, 500)

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        if not self._authorized():
            return
        path = urlparse(self.path).path.rstrip("/")
        if path != "/api/chat":
            return self._json({"error": "not found"}, 404)
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 20000)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw or b"{}")
            except (json.JSONDecodeError, ValueError) as e:
                return self._json({"error": f"Invalid JSON payload: {e}"}, 400)
            res = _ask_kuya(body)
            code = res.pop("_status", 200) if isinstance(res, dict) else 200
            return self._json(res, code)
        except Exception as e:  # Hermes down, timeout, bad JSON — show it in the chat
            sys.stderr.write(f"[kuya-web] POST /api/chat error: {e}\n")
            return self._json({"error": f"Kuya is unavailable: {e}. Is the Hermes gateway running?"}, 502)
    def log_message(self, fmt, *args) -> None:
        sys.stderr.write("[kuya-web] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"Kuya Hermes web → http://localhost:{PORT}  (dashboard: /dashboard)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
