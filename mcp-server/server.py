# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]  # pinned: v1 API (FastMCP) — what most docs & AI assistants use
# ///
"""
LAYER 1 — MCP SERVER (the hands) · Kuya Hermes for Suki Mart

Branch-operations tools over the Suki Mart sandbox (data/store.db). The same
tools serve two surfaces: HQ in Hermes Desktop (Branch Pulse pane) and branch
managers on Telegram reporting problems from the floor in Taglish.

Run standalone to check it starts (Ctrl+C to stop):
    uv run mcp-server/server.py

Register with Hermes (use the ABSOLUTE path to this file):
    hermes mcp add suki --command uv --args run /ABSOLUTE/PATH/TO/mcp-server/server.py
    hermes mcp test suki
"""
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

# Resolved relative to THIS file — Hermes launches MCP servers from its own folder.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "store.db")

# "Today" inside the sandbox. Never use the real clock.
SANDBOX_NOW = datetime(2026, 9, 30, 21, 0, 0)
OPEN_PO_STATUSES = ("pending", "in_transit", "partially_received")

mcp = FastMCP("suki")


def query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Read helper: returns rows as dicts."""
    con = sqlite3.connect(f"file:{os.path.abspath(DB_PATH)}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, params).fetchall()]
    finally:
        con.close()


def execute(sql: str, params: tuple = ()) -> int:
    """Write helper: returns affected row count. Reset data with `python data/seed.py`."""
    con = sqlite3.connect(os.path.abspath(DB_PATH))
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.rowcount
    finally:
        con.close()


def _branch(branch_code: str) -> dict:
    rows = query("SELECT id, code, name, has_delivery FROM branches WHERE code = ? COLLATE NOCASE", (branch_code.strip(),))
    if not rows:
        codes = ", ".join(r["code"] for r in query("SELECT code FROM branches ORDER BY code"))
        raise ValueError(f"Unknown branch '{branch_code}'. Valid codes: {codes}")
    return rows[0]


def _supplier_actual_lead_days() -> dict[int, float]:
    """Average real lead time per supplier, from received purchase orders."""
    rows = query(
        "SELECT supplier_id, AVG(julianday(received_at) - julianday(ordered_at)) AS d "
        "FROM purchase_orders WHERE received_at IS NOT NULL GROUP BY supplier_id"
    )
    return {r["supplier_id"]: round(r["d"], 1) for r in rows}


def _open_pos(branch_id: int, product_id: int) -> list[dict]:
    return query(
        f"SELECT po_number, quantity, status, ordered_at, expected_at FROM purchase_orders "
        f"WHERE branch_id = ? AND product_id = ? AND status IN ({','.join('?' * len(OPEN_PO_STATUSES))}) "
        f"ORDER BY ordered_at DESC",
        (branch_id, product_id, *OPEN_PO_STATUSES),
    )


def _shift_gaps(branch_id: int, day: str) -> list[dict]:
    """Staffing blocks on `day` where scheduled headcount is below target."""
    dow = int(datetime.strptime(day, "%Y-%m-%d").strftime("%w"))  # 0 = Sunday, matches staffing_targets
    gaps = []
    for t in query(
        "SELECT start_hour, end_hour, min_staff FROM staffing_targets "
        "WHERE branch_id = ? AND day_of_week = ? ORDER BY start_hour",
        (branch_id, dow),
    ):
        start, end = f"{t['start_hour']:02d}:00", f"{t['end_hour']:02d}:00"
        scheduled = query(
            "SELECT COUNT(*) AS n FROM shifts WHERE branch_id = ? AND shift_date = ? "
            "AND status IN ('scheduled', 'swapped') AND start_time < ? AND end_time > ?",
            (branch_id, day, end, start),
        )[0]["n"]
        if scheduled < t["min_staff"]:
            gaps.append({"date": day, "block": f"{start}-{end}", "scheduled": scheduled,
                         "target": t["min_staff"], "short_by": t["min_staff"] - scheduled})
    return gaps


# --------------------------------------------------------------------------
# Starter-kit helpers (kept)
# --------------------------------------------------------------------------
@mcp.tool()
def describe_sandbox() -> dict:
    """Describe the Suki Mart sandbox: business context, the current date
    inside the data ("sandbox_now"), and every table with its columns and
    row count. Call this only when you need to understand the raw data model."""
    info = {r["key"]: r["value"] for r in query("SELECT key, value FROM sandbox_info")}
    tables = {}
    for t in query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        name = t["name"]
        cols = [f'{c["name"]} {c["type"]}' for c in query(f"PRAGMA table_info({name})")]
        count = query(f"SELECT COUNT(*) AS n FROM {name}")[0]["n"]
        tables[name] = {"rows": count, "columns": cols}
    return {"info": info, "tables": tables}


@mcp.tool()
def list_branches(city: str | None = None) -> list[dict]:
    """List Suki Mart branches with their code, name, type, city, area and
    whether they offer delivery. Use it to turn a branch name a manager says
    ("Alabang", "BGC", "Katipunan") into its branch code."""
    sql = "SELECT code, name, branch_type, city, area, has_delivery FROM branches"
    if city:
        return query(sql + " WHERE city = ? ORDER BY code", (city,))
    return query(sql + " ORDER BY code")


# --------------------------------------------------------------------------
# Kuya Hermes domain tools
# --------------------------------------------------------------------------
@mcp.tool()
def branch_pulse(branch_code: str) -> dict:
    """One-call health check of a branch as of the sandbox date (2026-09-30):
    the most urgent stock problems (with whether a purchase order is already
    open), staffing gaps for the next two days versus targets, overdue support
    tickets, and late or failed deliveries in the last 7 days. Use this first
    whenever HQ or a manager asks how a branch is doing or for a morning brief."""
    return _pulse(branch_code, top=8)


def _pulse(branch_code: str, top: int | None = 8) -> dict:
    """branch_pulse body; top=None keeps every stock alert and gap (used by network_sweep)."""
    b = _branch(branch_code)
    lead = _supplier_actual_lead_days()

    stock = []
    for r in query(
        "SELECT p.id, p.sku, p.name, p.supplier_id, i.on_hand, i.reorder_point, i.avg_daily_sales "
        "FROM inventory i JOIN products p ON p.id = i.product_id "
        "WHERE i.branch_id = ? AND p.is_active = 1 AND i.on_hand <= i.reorder_point",
        (b["id"],),
    ):
        cover = round(r["on_hand"] / r["avg_daily_sales"], 1) if r["avg_daily_sales"] else None
        open_po = _open_pos(b["id"], r["id"])
        stock.append({
            "sku": r["sku"], "product": r["name"], "on_hand": r["on_hand"],
            "days_of_cover": cover, "supplier_real_lead_days": lead.get(r["supplier_id"]),
            "open_po": open_po[0]["po_number"] if open_po else None,
            "duplicate_open_pos": max(len(open_po) - 1, 0),
        })
    stock.sort(key=lambda s: (s["days_of_cover"] if s["days_of_cover"] is not None else 999))

    day1 = (SANDBOX_NOW + timedelta(days=1)).strftime("%Y-%m-%d")
    day2 = (SANDBOX_NOW + timedelta(days=2)).strftime("%Y-%m-%d")
    gaps = _shift_gaps(b["id"], day1) + _shift_gaps(b["id"], day2)

    tickets = query(
        "SELECT COUNT(*) AS open_tickets, "
        "SUM(first_response_at IS NULL) AS never_answered, "
        "SUM(julianday(?) - julianday(created_at) > 7) AS older_than_7d "
        "FROM support_tickets WHERE branch_id = ? AND status IN ('open', 'pending')",
        (SANDBOX_NOW.strftime("%Y-%m-%d %H:%M:%S"), b["id"]),
    )[0]

    deliveries = None
    if b["has_delivery"]:
        deliveries = query(
            "SELECT COUNT(*) AS total, SUM(delivered_at > promised_by) AS late, "
            "SUM(status IN ('failed', 'returned')) AS failed "
            "FROM deliveries WHERE branch_id = ? AND promised_by >= ?",
            (b["id"], (SANDBOX_NOW - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")),
        )[0]

    return {
        "branch": f"{b['code']} · {b['name']}",
        "as_of": "2026-09-30",
        "stock_alerts": stock[:top],
        "stock_alerts_total": len(stock),
        "out_of_stock": sum(1 for s in stock if s["on_hand"] == 0),
        "shift_gaps_next_2_days": gaps[:top],
        "tickets": tickets,
        "deliveries_last_7d": deliveries if deliveries else "branch has no delivery",
    }


@mcp.tool()
def network_sweep() -> dict:
    """Score ALL 12 branches in one call and rank them worst-first. Per branch:
    out-of-stock items with no open PO, items below reorder point, products
    with duplicate open POs, staff short for tomorrow, tickets never answered,
    and late/failed deliveries in the last 7 days, combined into a risk score.
    Use for "run full sweep", "which branch needs help most", or a network-wide
    morning brief; then drill into the worst branches with branch_pulse."""
    rows = []
    for b in query("SELECT code FROM branches ORDER BY code"):
        p = _pulse(b["code"], top=None)
        alerts_all = p["stock_alerts_total"]
        oos_no_po = sum(1 for s in p["stock_alerts"] if s["on_hand"] == 0 and not s["open_po"])
        dup_pos = sum(1 for s in p["stock_alerts"] if s["duplicate_open_pos"])
        tomorrow = (SANDBOX_NOW + timedelta(days=1)).strftime("%Y-%m-%d")
        short = sum(g["short_by"] for g in p["shift_gaps_next_2_days"] if g["date"] == tomorrow)
        unanswered = p["tickets"]["never_answered"] or 0
        d = p["deliveries_last_7d"]
        late = (d["late"] or 0) + (d["failed"] or 0) if isinstance(d, dict) else 0
        score = oos_no_po * 3 + dup_pos * 2 + short * 3 + unanswered * 2 + alerts_all * 0.5 + late * 0.2
        rows.append({"branch": b["code"], "risk_score": round(score, 1), "out_of_stock_no_po": oos_no_po,
                     "below_reorder": alerts_all, "duplicate_po_items": dup_pos,
                     "staff_short_tomorrow": short, "tickets_never_answered": unanswered,
                     "late_or_failed_deliveries_7d": late})
    rows.sort(key=lambda r: -r["risk_score"])
    return {"as_of": "2026-09-30", "branches": rows, "worst": rows[0]["branch"]}


@mcp.tool()
def check_restock(branch_code: str, product: str) -> dict:
    """Decide whether a branch should reorder a product. `product` can be a
    SKU or part of the name in English or Filipino shorthand the manager used
    (e.g. "sardines", "canton"). Returns stock on hand, days of cover, any
    purchase orders already open (the sandbox has duplicate POs — never reorder
    on top of one), the supplier's PROMISED vs REAL lead time, and a
    recommendation. Use before create_purchase_order."""
    b = _branch(branch_code)
    like = f"%{product.strip()}%"
    matches = query(
        "SELECT p.id, p.sku, p.name, p.unit, p.supplier_id, s.name AS supplier, s.promised_lead_time_days, "
        "i.on_hand, i.reorder_point, i.reorder_qty, i.avg_daily_sales "
        "FROM products p JOIN inventory i ON i.product_id = p.id AND i.branch_id = ? "
        "JOIN suppliers s ON s.id = p.supplier_id "
        "WHERE p.is_active = 1 AND (p.sku = ? OR p.name LIKE ?) ORDER BY i.on_hand LIMIT 5",
        (b["id"], product.strip(), like),
    )
    if not matches:
        return {"found": False, "message": f"No active product matching '{product}' at {b['code']}."}
    if len(matches) > 1:
        return {"found": False, "message": "Several products match — ask which one.",
                "candidates": [{"sku": m["sku"], "name": m["name"], "on_hand": m["on_hand"]} for m in matches]}

    m = matches[0]
    real_lead = _supplier_actual_lead_days().get(m["supplier_id"], m["promised_lead_time_days"])
    cover = round(m["on_hand"] / m["avg_daily_sales"], 1) if m["avg_daily_sales"] else None
    open_po = _open_pos(b["id"], m["id"])

    if open_po:
        rec = f"Do NOT reorder: {len(open_po)} open PO(s) already ({open_po[0]['po_number']}, {open_po[0]['status']})."
        if len(open_po) > 1:
            rec += f" {len(open_po) - 1} look like duplicates — flag them to purchasing."
    elif m["on_hand"] <= m["reorder_point"] or (cover is not None and cover <= real_lead):
        rec = (f"Reorder {m['reorder_qty']} {m['unit']}: {cover} days of cover vs "
               f"{real_lead} days real supplier lead time.")
    else:
        rec = f"No reorder needed yet: {cover} days of cover."

    return {
        "found": True, "branch": b["code"], "sku": m["sku"], "product": m["name"],
        "on_hand": m["on_hand"], "reorder_point": m["reorder_point"], "reorder_qty": m["reorder_qty"],
        "avg_daily_sales": m["avg_daily_sales"], "days_of_cover": cover,
        "supplier": m["supplier"], "promised_lead_days": m["promised_lead_time_days"],
        "real_lead_days": real_lead, "open_purchase_orders": open_po, "recommendation": rec,
    }


@mcp.tool()
def create_purchase_order(branch_code: str, sku: str, quantity: int | None = None) -> dict:
    """WRITE ACTION. Create a restock purchase order for one product at one
    branch. Refuses if an open PO (pending / in_transit / partially_received)
    already exists. Quantity defaults to the branch's reorder quantity. The
    expected date uses the supplier's REAL average lead time, not its promise.
    Only call after the user has confirmed."""
    b = _branch(branch_code)
    rows = query(
        "SELECT p.id, p.name, p.cost_price, p.supplier_id, i.reorder_qty FROM products p "
        "JOIN inventory i ON i.product_id = p.id AND i.branch_id = ? WHERE p.sku = ?",
        (b["id"], sku.strip()),
    )
    if not rows:
        return {"created": False, "message": f"SKU '{sku}' not stocked at {b['code']}."}
    p = rows[0]
    if _open_pos(b["id"], p["id"]):
        return {"created": False, "message": "An open purchase order already exists — not creating a duplicate.",
                "open_purchase_orders": _open_pos(b["id"], p["id"])}

    qty = quantity or p["reorder_qty"]
    lead = _supplier_actual_lead_days().get(p["supplier_id"], 3)
    new_id = query("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM purchase_orders")[0]["n"]
    po_number = f"PO-2026-{new_id:05d}"
    ordered = SANDBOX_NOW.strftime("%Y-%m-%d %H:%M:%S")
    expected = (SANDBOX_NOW + timedelta(days=lead)).strftime("%Y-%m-%d %H:%M:%S")
    execute(
        "INSERT INTO purchase_orders (id, po_number, supplier_id, branch_id, product_id, quantity, unit_cost, "
        "status, ordered_at, expected_at, notes) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)",
        (new_id, po_number, p["supplier_id"], b["id"], p["id"], qty, p["cost_price"], ordered, expected,
         "Created by Kuya Hermes"),
    )
    return {"created": True, "po_number": po_number, "branch": b["code"], "product": p["name"],
            "quantity": qty, "est_cost_php": round(qty * p["cost_price"], 2), "expected_at": expected}


@mcp.tool()
def find_staff_shifts(branch_code: str, staff_name: str, date: str | None = None) -> list[dict]:
    """Find a staff member's upcoming shifts at a branch, by first or last
    name (e.g. "Juan", "Santos"). `date` is YYYY-MM-DD; defaults to the next
    two days after the sandbox date. Use when a manager reports that someone
    is absent, sick, or a no-show, to get the shift_id to cover."""
    b = _branch(branch_code)
    like = f"%{staff_name.strip()}%"
    if date:
        dates = (date,)
    else:
        dates = ((SANDBOX_NOW + timedelta(days=1)).strftime("%Y-%m-%d"),
                 (SANDBOX_NOW + timedelta(days=2)).strftime("%Y-%m-%d"))
    return query(
        f"SELECT sh.id AS shift_id, st.employee_number, st.first_name || ' ' || st.last_name AS staff, "
        f"sh.role, sh.shift_date, sh.start_time, sh.end_time, sh.status FROM shifts sh "
        f"JOIN staff st ON st.id = sh.staff_id WHERE sh.branch_id = ? "
        f"AND (st.first_name LIKE ? OR st.last_name LIKE ?) "
        f"AND sh.shift_date IN ({','.join('?' * len(dates))}) ORDER BY sh.shift_date, sh.start_time LIMIT 10",
        (b["id"], like, like, *dates),
    )


@mcp.tool()
def find_shift_cover(shift_id: int, limit: int = 5) -> dict:
    """Rank replacement staff for a shift: same branch, same role, active,
    not already working an overlapping shift that day. Most reliable first
    (fewest no-shows and sick calls in the last 8 weeks), then fewest hours
    already booked that week. Use after find_staff_shifts or for a staffing
    gap from branch_pulse."""
    rows = query("SELECT * FROM shifts WHERE id = ?", (shift_id,))
    if not rows:
        return {"found": False, "message": f"No shift {shift_id}."}
    s = rows[0]
    week_start = (datetime.strptime(s["shift_date"], "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")
    candidates = query(
        "SELECT st.employee_number, st.first_name || ' ' || st.last_name AS staff, "
        "(SELECT COUNT(*) FROM shifts x WHERE x.staff_id = st.id AND x.status IN ('no_show', 'called_in_sick') "
        " AND x.shift_date BETWEEN '2026-08-05' AND '2026-09-30') AS absences_8w, "
        "(SELECT COALESCE(SUM((CAST(substr(x.end_time,1,2) AS INT) - CAST(substr(x.start_time,1,2) AS INT))), 0) "
        " FROM shifts x WHERE x.staff_id = st.id AND x.shift_date BETWEEN ? AND ? "
        " AND x.status IN ('scheduled','completed','swapped')) AS hours_this_week "
        "FROM staff st WHERE st.branch_id = ? AND st.role = ? AND st.status = 'active' AND st.id != ? "
        "AND NOT EXISTS (SELECT 1 FROM shifts y WHERE y.staff_id = st.id AND y.shift_date = ? "
        " AND y.status IN ('scheduled','swapped') AND y.start_time < ? AND y.end_time > ?) "
        "ORDER BY absences_8w, hours_this_week LIMIT ?",
        (week_start, s["shift_date"], s["branch_id"], s["role"], s["staff_id"],
         s["shift_date"], s["end_time"], s["start_time"], limit),
    )
    return {"found": True,
            "shift": {k: s[k] for k in ("id", "shift_date", "start_time", "end_time", "role", "status")},
            "candidates": candidates}


@mcp.tool()
def assign_cover(shift_id: int, cover_employee_number: str) -> dict:
    """WRITE ACTION. Cover an absent staff member's shift: marks the original
    shift as called_in_sick and books the replacement on the same date, time
    and role. Only call after the user has confirmed the replacement."""
    rows = query("SELECT * FROM shifts WHERE id = ?", (shift_id,))
    if not rows:
        return {"assigned": False, "message": f"No shift {shift_id}."}
    s = rows[0]
    if s["status"] not in ("scheduled", "swapped"):
        return {"assigned": False, "message": f"Shift {shift_id} is '{s['status']}', not an upcoming shift."}
    cover = query(
        "SELECT id, first_name || ' ' || last_name AS name FROM staff "
        "WHERE employee_number = ? AND branch_id = ? AND role = ? AND status = 'active'",
        (cover_employee_number.strip(), s["branch_id"], s["role"]),
    )
    if not cover:
        return {"assigned": False, "message": "Cover must be an active staff member with the same branch and role."}
    absent = query("SELECT first_name || ' ' || last_name AS name FROM staff WHERE id = ?", (s["staff_id"],))[0]["name"]

    execute("UPDATE shifts SET status = 'called_in_sick' WHERE id = ?", (shift_id,))
    execute(
        "INSERT INTO shifts (staff_id, branch_id, shift_date, start_time, end_time, role, status) "
        "VALUES (?, ?, ?, ?, ?, ?, 'scheduled')",
        (cover[0]["id"], s["branch_id"], s["shift_date"], s["start_time"], s["end_time"], s["role"]),
    )
    return {"assigned": True, "absent": absent, "cover": cover[0]["name"], "role": s["role"],
            "date": s["shift_date"], "time": f"{s['start_time']}-{s['end_time']}"}


if __name__ == "__main__":
    mcp.run()
