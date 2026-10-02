# Suki Mart data rules (for the skill)

Source of truth: `data/SCHEMA.md` (generated from `data/store.db`). Re-read it
before naming any column. Do not guess column names.

## Time
- Sandbox "now" is `2026-09-30 21:00:00` (`sandbox_info.sandbox_now`). Never use
  the real clock. History starts `2026-04-01`.
- Timestamps are `YYYY-MM-DD HH:MM:SS`, Manila local time.
- `staffing_targets.day_of_week` and `shifts` use 0 = Sunday ... 6 = Saturday.
- `shifts` covers 8 weeks of history plus 2 weeks scheduled ahead.

## Money
- Currency is PHP. Always show the symbol: ₱.
- `order_items` has unit price AND unit cost, so margin is computable.

## Joins
```
branches ─┬─< inventory >── products >── suppliers
          ├─< purchase_orders >── products / suppliers
          ├─< orders ──< order_items >── products
          │     ├── customers ── loyalty_accounts ──< loyalty_transactions
          │     ├── promos
          │     └── deliveries >── riders
          ├─< staff ──< shifts        staffing_targets
          ├─< support_tickets (→ customers, orders, staff)
          └─< reviews (→ customers, orders)
```

## Enumerated values (use these exact strings)
- `orders.channel`: delivery, in_store, pickup
- `orders.status`: cancelled, completed, out_for_delivery, pending, refunded
- `deliveries.status`: delivered, failed, in_transit, pending_assignment, returned
- `purchase_orders.status`: cancelled, in_transit, partially_received, pending, received
- `support_tickets.status`: closed, open, pending, resolved
- `support_tickets.priority`: high, low, medium, urgent
- `loyalty_accounts.tier`: Bronze, Silver, Gold, Platinum
- `shifts.status`: called_in_sick, completed, no_show, scheduled, swapped

## Known data traps (the sandbox is messy on purpose)
- Suppliers carry a *promised* lead time; actual receipts differ. Compare
  `purchase_orders` expected vs actual dates, do not trust the promise.
- Duplicate purchase orders exist. Check for an existing `pending` / `in_transit`
  / `partially_received` PO before recommending a reorder.
- Two branches do not offer delivery. Do not suggest delivery fixes there.
- Some tickets are open, old and never responded to.
- Some customers have no marketing opt-in. Never include them in outreach lists.

Add every new quirk the team finds here.
