# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]
# ///
"""Build a static snapshot of the website for Vercel → web/dist/.

    uv run web/build_static.py && cd web/dist && vercel --prod

Every /api/* GET is pre-rendered to JSON from store.db (same functions as the
suki MCP server) and wired up with rewrites in vercel.json. Nothing in the
deployed site reaches back to a laptop; the live Kuya chat stays on the
local demo and Telegram.
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
import app  # noqa: E402  (reuses _overview + the suki functions)

DIST = os.path.join(ROOT, "dist")


def dump(name: str, obj) -> None:
    with open(os.path.join(DIST, "data", name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(os.path.join(DIST, "data"))
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(DIST, "static"))
    shutil.copy(os.path.join(ROOT, "static", "index.html"), os.path.join(DIST, "index.html"))
    shutil.copy(os.path.join(ROOT, "static", "dashboard.html"), os.path.join(DIST, "dashboard.html"))
    os.makedirs(os.path.join(DIST, "assets"))
    for f in ("kuya-hermes-avatar-160.png", "kuya-hermes-fullbody.png"):
        shutil.copy(os.path.join(REPO, "assets", f), os.path.join(DIST, "assets", f))

    dump("overview.json", app._overview())
    dump("sweep.json", app.suki.network_sweep())
    dump("branches.json", app.suki.list_branches())
    for b in app.suki.list_branches():
        dump(f"pulse-{b['code']}.json", app.suki.branch_pulse(b["code"]))

    vercel = {
        "cleanUrls": True,
        "rewrites": [
            {"source": "/api/overview", "destination": "/data/overview.json"},
            {"source": "/api/sweep", "destination": "/data/sweep.json"},
            {"source": "/api/branches", "destination": "/data/branches.json"},
            {"source": "/api/pulse/:code", "destination": "/data/pulse-:code.json"},
        ],
    }
    with open(os.path.join(DIST, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump(vercel, f, indent=2)
    print(f"built {DIST}")


if __name__ == "__main__":
    main()
