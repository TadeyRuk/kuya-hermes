"""Sari-sari store ledger CLI backed by a Google Sheet.

Reuses the google-workspace skill's OAuth token, so no extra auth is needed.
Every command prints JSON so the agent can read the result directly.

Sheet layout (created once by the setup script):
  Inventory    A Item | B Unit | C Price | D Initial stock | E Restocked | F Sold
               G On hand | H Reorder at | I Status        (E:G and I are formulas)
  Transactions A Timestamp | B Type | C Customer | D Item | E Qty | F Unit price
               G Total | H Note                           (append-only ledger)
  Utang        live QUERY of balances per customer        (read-only)

Types: sale (cash), utang (on credit), bayad (customer pays down utang),
restock (stock delivered). bayad rows store a NEGATIVE total so that
sum(Total) over utang+bayad rows is the customer's outstanding balance.
"""
import argparse
import difflib
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

GWS_SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "google-workspace", "scripts",
)
sys.path.insert(0, GWS_SCRIPTS)
import google_api  # noqa: E402

SHEET_ID_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sheet_id.txt")


def _load_sheet_id():
    """SARISARI_SHEET_ID env var wins; otherwise sheet_id.txt written by setup/install.ps1."""
    sid = os.environ.get("SARISARI_SHEET_ID", "").strip()
    if not sid and os.path.exists(SHEET_ID_FILE):
        with open(SHEET_ID_FILE, encoding="utf-8") as f:
            sid = f.read().strip()
    return sid


SHEET_ID = _load_sheet_id()
PH_TZ = timezone(timedelta(hours=8))  # Asia/Manila, no DST
TYPES = ("sale", "utang", "bayad", "restock")


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def fail(msg, **extra):
    out({"ok": False, "error": msg, **extra})
    sys.exit(1)


def svc():
    return google_api.build_service("sheets", "v4").spreadsheets().values()


def read(rng):
    return svc().get(spreadsheetId=SHEET_ID, range=rng).execute().get("values", [])


def num(v, default=0.0):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return default


def load_inventory():
    rows = read("Inventory!A2:I")
    items = []
    for r in rows:
        r = r + [""] * (9 - len(r))
        if not r[0]:
            continue
        items.append({
            "item": r[0], "unit": r[1], "price": num(r[2]),
            "on_hand": num(r[6]), "reorder_at": num(r[7]), "status": r[8],
        })
    return items


def load_transactions():
    rows = read("Transactions!A2:H")
    txns = []
    for r in rows:
        r = r + [""] * (8 - len(r))
        txns.append({
            "timestamp": r[0], "type": r[1], "customer": r[2], "item": r[3],
            "qty": num(r[4]), "unit_price": num(r[5]), "total": num(r[6]), "note": r[7],
        })
    return txns


def resolve_item(query, items):
    """Exact, then substring, then fuzzy match. Fails with candidates if unclear."""
    q = query.strip().lower()
    names = [i["item"] for i in items]
    exact = [i for i in items if i["item"].lower() == q]
    if exact:
        return exact[0]
    sub = [i for i in items if q in i["item"].lower() or i["item"].lower() in q]
    if len(sub) == 1:
        return sub[0]
    if len(sub) > 1:
        fail(f"'{query}' matches several items", candidates=[i["item"] for i in sub])
    close = difflib.get_close_matches(query, names, n=3, cutoff=0.5)
    if len(close) == 1:
        return next(i for i in items if i["item"] == close[0])
    fail(f"No inventory item matches '{query}'", candidates=close or names)


def balances(txns):
    bal = defaultdict(float)
    for t in txns:
        if t["type"] in ("utang", "bayad") and t["customer"]:
            bal[t["customer"]] += t["total"]
    return {c: round(b, 2) for c, b in bal.items() if abs(b) > 0.004}


def match_customer(name, txns):
    """Reuse an existing customer's exact spelling when the name matches loosely."""
    known = sorted({t["customer"] for t in txns if t["customer"]})
    for k in known:
        if k.lower() == name.strip().lower():
            return k
    return name.strip()


def cmd_inventory(_args):
    items = load_inventory()
    out({"ok": True, "items": items, "low_stock": [i["item"] for i in items if i["status"] == "LOW"]})


def cmd_log(args):
    t = args.type
    items = load_inventory()
    txns = load_transactions()
    customer = match_customer(args.customer, txns) if args.customer else ""

    if t in ("utang", "bayad") and not customer:
        fail(f"'{t}' needs --customer")

    if t == "bayad":
        if args.amount is None or args.amount <= 0:
            fail("bayad needs a positive --amount")
        row = ["", t, customer, "", "", "", -round(args.amount, 2), args.note or ""]
        item = None
    else:
        if not args.item or not args.qty or args.qty <= 0:
            fail(f"'{t}' needs --item and a positive --qty")
        item = resolve_item(args.item, items)
        price = item["price"] if args.price is None else args.price
        total = 0 if t == "restock" else round(price * args.qty, 2)
        if t in ("sale", "utang") and args.qty > item["on_hand"]:
            fail(f"Only {item['on_hand']:g} {item['unit']} of {item['item']} on hand",
                 on_hand=item["on_hand"])
        row = ["", t, customer, item["item"], args.qty, price, total, args.note or ""]

    row[0] = datetime.now(PH_TZ).strftime("%Y-%m-%d %H:%M")
    svc().append(
        spreadsheetId=SHEET_ID, range="Transactions!A:H",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    result = {"ok": True, "logged": dict(zip(
        ["timestamp", "type", "customer", "item", "qty", "unit_price", "total", "note"], row))}
    if item:
        fresh = resolve_item(item["item"], load_inventory())
        result["on_hand_now"] = fresh["on_hand"]
        result["low_stock"] = fresh["status"] == "LOW"
    if customer:
        result["customer_balance"] = balances(load_transactions()).get(customer, 0)
    out(result)


def cmd_utang(args):
    bal = balances(load_transactions())
    if args.customer:
        name = next((c for c in bal if c.lower() == args.customer.lower()), args.customer)
        out({"ok": True, "customer": name, "balance": bal.get(name, 0)})
    else:
        out({"ok": True, "balances": dict(sorted(bal.items(), key=lambda kv: -kv[1])),
             "total_outstanding": round(sum(bal.values()), 2)})


def cmd_summary(args):
    day = args.date or datetime.now(PH_TZ).strftime("%Y-%m-%d")
    txns = load_transactions()
    today = [t for t in txns if t["timestamp"].startswith(day)]
    sold = defaultdict(float)
    cash = credit = paid = 0.0
    for t in today:
        if t["type"] == "sale":
            cash += t["total"]
            sold[t["item"]] += t["qty"]
        elif t["type"] == "utang":
            credit += t["total"]
            sold[t["item"]] += t["qty"]
        elif t["type"] == "bayad":
            paid += -t["total"]
    items = load_inventory()
    out({
        "ok": True, "date": day, "transactions": len(today),
        "cash_sales": round(cash, 2), "utang_given": round(credit, 2),
        "utang_collected": round(paid, 2),
        "top_items": sorted(sold.items(), key=lambda kv: -kv[1])[:5],
        "low_stock": [f"{i['item']} ({i['on_hand']:g} {i['unit']} left)" for i in items if i["status"] == "LOW"],
        "outstanding_utang": balances(txns),
    })


def cmd_undo(_args):
    """Delete the most recent Transactions row."""
    rows = read("Transactions!A2:H")
    if not rows:
        fail("No transactions to undo")
    last_idx = len(rows)  # 0-based row index of the last data row (header is row 0)
    meta = google_api.build_service("sheets", "v4").spreadsheets()
    sheet_id = next(s["properties"]["sheetId"]
                    for s in meta.get(spreadsheetId=SHEET_ID).execute()["sheets"]
                    if s["properties"]["title"] == "Transactions")
    meta.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"deleteDimension": {
        "range": {"sheetId": sheet_id, "dimension": "ROWS",
                  "startIndex": last_idx, "endIndex": last_idx + 1}}}]}).execute()
    out({"ok": True, "removed": rows[-1]})


def main():
    p = argparse.ArgumentParser(description="Sari-sari store ledger")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("inventory", help="Items, prices, stock on hand")

    lg = sub.add_parser("log", help="Record a transaction")
    lg.add_argument("--type", required=True, choices=TYPES)
    lg.add_argument("--item")
    lg.add_argument("--qty", type=float)
    lg.add_argument("--customer")
    lg.add_argument("--amount", type=float, help="bayad amount in PHP")
    lg.add_argument("--price", type=float, help="override unit price")
    lg.add_argument("--note")

    ut = sub.add_parser("utang", help="Outstanding credit balances")
    ut.add_argument("--customer")

    sm = sub.add_parser("summary", help="Daily summary")
    sm.add_argument("--date", help="YYYY-MM-DD (default: today, PH time)")

    sub.add_parser("undo", help="Delete the last transaction")

    args = p.parse_args()
    if not SHEET_ID:
        fail("No sheet configured. Set SARISARI_SHEET_ID or run setup/install.ps1.")
    {"inventory": cmd_inventory, "log": cmd_log, "utang": cmd_utang,
     "summary": cmd_summary, "undo": cmd_undo}[args.cmd](args)


if __name__ == "__main__":
    main()
