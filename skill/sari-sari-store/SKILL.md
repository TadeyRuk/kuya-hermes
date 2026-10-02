---
name: sari-sari-store
description: "Run a sari-sari store ledger from chat: log sales, utang (credit), bayad (payments), restocks; check stock and balances; daily summary. Google Sheet backend. Use for any Taglish/English message about selling, utang, bayad, stock, or store sales."
version: 1.0.0
author: Paul Dacalan
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Store, Inventory, Utang, Ledger, Sheets, Taglish, Philippines]
    related_skills: [google-workspace]
---

# Sari-Sari Store Ledger

The owner talks in Taglish or English. Turn each message into ledger commands,
run them, and confirm back in one or two short lines.

Backend: Google Sheet "Sari-Sari Store (Hermes)"
{{SHEET_URL}}
Auth comes from the google-workspace skill. If a command fails with an auth
error, run that skill's `setup.py --check`.

## Command

Run in the terminal (Git Bash). Every command prints JSON.

```bash
STORE='"{{PYTHON}}" "{{STORE_PY}}"'
eval $STORE inventory
```

| Action | Command |
|---|---|
| Stock + prices | `eval $STORE inventory` |
| Cash sale | `eval $STORE log --type sale --item "Ligo Sardinas" --qty 2` |
| Utang (credit) | `eval $STORE log --type utang --customer "Aling Nena" --item "Lucky Me Pancit Canton" --qty 3` |
| Bayad (payment) | `eval $STORE log --type bayad --customer "Aling Nena" --amount 50` |
| Restock | `eval $STORE log --type restock --item "Kopiko 3in1" --qty 30` |
| All balances | `eval $STORE utang` |
| One customer | `eval $STORE utang --customer "Aling Nena"` |
| Daily summary | `eval $STORE summary` (or `--date 2026-10-02`) |
| Undo last entry | `eval $STORE undo` |

Optional on `log`: `--price N` (override unit price), `--note "text"`.

## Reading Taglish

- Words for credit: `utang`, `ilista`, `palista`, `sa lista`, `babayaran mamaya/bukas` → `--type utang`
- Words for payment: `bayad`, `nagbayad`, `hulog`, `nagbigay ng ___ pambayad` → `--type bayad --amount`
- Plain buying with no credit word (`bumili`, `kumuha`, `binili`) → `--type sale`
- Delivery or added stock (`dumating`, `nag-restock`, `dagdag stock`) → `--type restock`
- Colloquial item names: canton/pancit → Lucky Me Pancit Canton, sardinas/ligo → Ligo Sardinas,
  kape/kopiko → Kopiko 3in1, coke → Coke Mismo, itlog/egg → Itlog, bigas/rice → Bigas,
  mantika/oil → Mantika (maliit), sabon/safeguard → Safeguard, asukal/sugar → Asukal (1/4),
  load → Load (Smart/Globe) (qty = peso amount).
- Number words: isa=1, dalawa=2, tatlo=3, apat=4, lima=5, anim=6, pito=7, walo=8, siyam=9, sampu=10.
- One message can contain several items. Log each item as its own command.
- If `ok` is false with `candidates`, pick the obvious one, or ask the owner with the options listed.
- Keep customer names as the owner says them, with honorifics ("Aling Nena", "Mang Jose").
  The script reuses an existing spelling when the name matches.

## Replying

Short and in the owner's language. Include what was logged, the total, and
whatever changed: stock left, the customer's new balance, or a LOW stock warning.

Example: *"Nailista ✅ Aling Nena: 3 Pancit Canton (₱54). Utang niya ngayon: ₱54."*

## Rules

1. Log simple sales, utang, bayad, and restocks right away. They are easy to undo, and the owner is busy.
2. Ask first when a message is ambiguous: unclear item, missing qty, or not clear whether it is utang or a cash sale.
3. Always confirm before `undo`. Say which row will be removed.
4. Never edit the Inventory tab's formula columns (Restocked, Sold, On hand, Status).
   Add new products or change prices only when the owner explicitly asks.
5. Never contact customers. Reminders about utang go only to the owner.
6. Money is in pesos (₱). Totals come from the sheet's prices, so don't invent prices.
