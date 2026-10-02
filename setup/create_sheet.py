"""Create the "Sari-Sari Store (Hermes)" Google Sheet and print its id.

Needs the Hermes google-workspace skill to be authenticated first
(setup.py --check prints AUTHENTICATED). Run with Hermes' venv python:

    python setup/create_sheet.py

Tabs:
  Inventory    - item master + live stock formulas (agent reads, rarely writes)
  Transactions - append-only ledger the agent writes to
  Utang        - live per-customer credit balance (QUERY over Transactions)
"""
import json
import os
import sys

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.join(os.environ["LOCALAPPDATA"], "hermes")
sys.path.insert(0, os.path.join(HERMES_HOME, "skills", "productivity", "google-workspace", "scripts"))
import google_api  # noqa: E402  (reuses Hermes' token loading/refresh)

# Demo catalogue: Item, Unit, Price (PHP), Initial stock, Reorder at.
INVENTORY = [
    ["Lucky Me Pancit Canton", "pack", 18, 40, 10],
    ["Ligo Sardinas", "can", 28, 30, 8],
    ["Kopiko 3in1", "sachet", 9, 60, 15],
    ["Coke Mismo", "bottle", 20, 24, 6],
    ["Itlog", "piraso", 9, 60, 12],
    ["Bigas", "kilo", 52, 25, 5],
    ["Mantika (maliit)", "bote", 32, 12, 4],
    ["Safeguard", "bar", 45, 15, 4],
    ["Asukal (1/4)", "pack", 22, 20, 5],
    ["Load (Smart/Globe)", "peso", 1, 1000, 100],
]

UTANG_FORMULA = (
    '=IFERROR(QUERY(Transactions!A:H,"select C, sum(G) where B=\'utang\' or B=\'bayad\' group by C '
    'label C \'Customer\', sum(G) \'Balance (PHP)\'",1),{"Customer","Balance (PHP)"})'
)


def main():
    sheets = google_api.build_service("sheets", "v4").spreadsheets()

    ss = sheets.create(body={
        # Sheets API rejects en_PH; en_US keeps comma separators in formulas.
        "properties": {"title": "Sari-Sari Store (Hermes)", "locale": "en_US", "timeZone": "Asia/Manila"},
        "sheets": [
            {"properties": {"title": t, "gridProperties": {"frozenRowCount": 1}}}
            for t in ("Inventory", "Transactions", "Utang")
        ],
    }).execute()
    sid = ss["spreadsheetId"]

    inv_rows = [["Item", "Unit", "Price", "Initial stock", "Restocked", "Sold", "On hand", "Reorder at", "Status"]]
    for i, (item, unit, price, initial, reorder) in enumerate(INVENTORY, start=2):
        inv_rows.append([
            item, unit, price, initial,
            f'=SUMIFS(Transactions!E:E,Transactions!D:D,A{i},Transactions!B:B,"restock")',
            f'=SUMIFS(Transactions!E:E,Transactions!D:D,A{i},Transactions!B:B,"sale")'
            f'+SUMIFS(Transactions!E:E,Transactions!D:D,A{i},Transactions!B:B,"utang")',
            f"=D{i}+E{i}-F{i}",
            reorder,
            f'=IF(G{i}<=H{i},"LOW","OK")',
        ])

    sheets.values().batchUpdate(spreadsheetId=sid, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Inventory!A1", "values": inv_rows},
            {"range": "Transactions!A1", "values": [["Timestamp", "Type", "Customer", "Item", "Qty", "Unit price", "Total", "Note"]]},
            {"range": "Utang!A1", "values": [[UTANG_FORMULA]]},
        ],
    }).execute()

    sheets.batchUpdate(spreadsheetId=sid, body={"requests": [
        {"repeatCell": {
            "range": {"sheetId": s["properties"]["sheetId"], "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold",
        }}
        for s in ss["sheets"]
    ]}).execute()

    print(json.dumps({"spreadsheetId": sid, "url": ss["spreadsheetUrl"]}, indent=2))


if __name__ == "__main__":
    main()
