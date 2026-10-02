# Suki Mart Sandbox — Schema Reference

> Auto-generated from `data/store.db`. All businesses, people and data are **fictional**.

- **Database:** SQLite, single file `data/store.db`
- **Sandbox "now":** `2026-09-30 21:00` — treat this as *today* (history starts `2026-04-01`)
- **Currency:** PHP (₱). Timestamps are `YYYY-MM-DD HH:MM:SS`, local Manila time.
- **Reset:** `python data/seed.py` recreates the exact same database.

## Tables at a glance

| Area | Table | Rows | What's in it |
|---|---|---:|---|
| Stores & supply | `branches` | 12 | 12 stores across Metro Manila (flagship / standard / express). Two don't offer delivery. |
| Stores & supply | `suppliers` | 18 | Vendors per category, with their *promised* lead time and payment terms. |
| Stores & supply | `products` | 133 | Catalog with cost and retail price, category, supplier, and shelf life for perishables. |
| Stores & supply | `inventory` | 1,596 | Stock per branch × product: on hand, reorder point/qty, average daily sales, nearest expiry. |
| Stores & supply | `purchase_orders` | 778 | Restock orders to suppliers: expected vs. actual receipt, partial deliveries, cancellations. |
| Customers & sales | `customers` | 2,670 | Shoppers with contact info, home branch, marketing opt-in and preferred channel. |
| Customers & sales | `loyalty_accounts` | 1,387 | Suki card per member: tier, points balance, points about to expire. |
| Customers & sales | `loyalty_transactions` | 16,737 | Points ledger: earn, redeem, expire, manual adjustments. |
| Customers & sales | `promos` | 16 | Campaigns with type, value, minimum spend, target category, channel, dates and budget. |
| Customers & sales | `orders` | 35,203 | Six months of transactions (in-store, delivery, pickup) with discounts, fees, payment method, points. |
| Customers & sales | `order_items` | 129,846 | Line items with unit price AND unit cost — so you can compute margin. |
| Delivery | `riders` | 48 | Delivery riders, their vehicle, home branch, status and rating. |
| Delivery | `deliveries` | 9,397 | One row per delivery order: promised vs. delivered time, distance, area, failures. |
| People & operations | `staff` | 223 | Employees per branch (cashiers, stock clerks, pickers, supervisors, managers) + central CSR team. |
| People & operations | `staffing_targets` | 336 | Minimum staff required per branch, day of week (0=Sunday … 6=Saturday) and time block. |
| People & operations | `shifts` | 17,887 | 8 weeks of shift history + 2 weeks scheduled ahead, with no-shows and sick calls. |
| Customer experience | `support_tickets` | 1,650 | Customer service tickets by channel and category, with response/resolution times and CSAT. |
| Customer experience | `reviews` | 3,200 | Public reviews (Google, Facebook, app) with rating, text, topic, and whether the store replied. |
| Meta | `sandbox_info` | 5 | Key/value facts about the sandbox — including `sandbox_now`, the current date inside the data. |

## Relationships

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

## Columns

### `sandbox_info`

| Column | Type | Notes |
|---|---|---|
| `key` | TEXT | PK |
| `value` | TEXT | required |

### `branches`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `code` | TEXT | required |
| `name` | TEXT | required |
| `city` | TEXT | required |
| `area` | TEXT | required |
| `branch_type` | TEXT | required |
| `latitude` | REAL |  |
| `longitude` | REAL |  |
| `has_delivery` | INTEGER | required |
| `opened_on` | TEXT | required |
| `opening_time` | TEXT | required |
| `closing_time` | TEXT | required |
| `phone` | TEXT |  |

### `suppliers`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `name` | TEXT | required |
| `category_focus` | TEXT | required |
| `contact_person` | TEXT |  |
| `phone` | TEXT |  |
| `email` | TEXT |  |
| `promised_lead_time_days` | INTEGER | required |
| `payment_terms` | TEXT | required |
| `is_active` | INTEGER | required |

### `products`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `sku` | TEXT | required |
| `name` | TEXT | required |
| `category` | TEXT | required |
| `unit` | TEXT | required |
| `cost_price` | REAL | required |
| `retail_price` | REAL | required |
| `supplier_id` | INTEGER | → `suppliers.id` · required |
| `is_perishable` | INTEGER | required |
| `shelf_life_days` | INTEGER |  |
| `is_active` | INTEGER | required |

### `inventory`

| Column | Type | Notes |
|---|---|---|
| `branch_id` | INTEGER | PK · → `branches.id` |
| `product_id` | INTEGER | PK · → `products.id` |
| `on_hand` | INTEGER | required |
| `reorder_point` | INTEGER | required |
| `reorder_qty` | INTEGER | required |
| `avg_daily_sales` | REAL | required |
| `nearest_expiry_date` | TEXT |  |
| `last_restocked_at` | TEXT |  |
| `last_counted_at` | TEXT |  |

### `purchase_orders`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `po_number` | TEXT | required |
| `supplier_id` | INTEGER | → `suppliers.id` · required |
| `branch_id` | INTEGER | → `branches.id` · required |
| `product_id` | INTEGER | → `products.id` · required |
| `quantity` | INTEGER | required |
| `unit_cost` | REAL | required |
| `status` | TEXT | required |
| `ordered_at` | TEXT | required |
| `expected_at` | TEXT | required |
| `received_at` | TEXT |  |
| `received_quantity` | INTEGER |  |
| `notes` | TEXT |  |

### `customers`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `first_name` | TEXT | required |
| `last_name` | TEXT | required |
| `email` | TEXT |  |
| `phone` | TEXT |  |
| `birthdate` | TEXT |  |
| `city` | TEXT |  |
| `home_branch_id` | INTEGER | → `branches.id` |
| `created_at` | TEXT | required |
| `marketing_opt_in` | INTEGER | required |
| `preferred_channel` | TEXT |  |

### `loyalty_accounts`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `customer_id` | INTEGER | → `customers.id` · required |
| `card_number` | TEXT | required |
| `tier` | TEXT | required |
| `points_balance` | INTEGER | required |
| `lifetime_points` | INTEGER | required |
| `points_expiring` | INTEGER | required |
| `points_expiry_date` | TEXT |  |
| `joined_at` | TEXT | required |
| `status` | TEXT | required |

### `loyalty_transactions`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `loyalty_account_id` | INTEGER | → `loyalty_accounts.id` · required |
| `order_id` | INTEGER | → `orders.id` |
| `txn_type` | TEXT | required |
| `points` | INTEGER | required |
| `created_at` | TEXT | required |
| `note` | TEXT |  |

### `promos`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `code` | TEXT | required |
| `name` | TEXT | required |
| `promo_type` | TEXT | required |
| `value` | REAL | required |
| `min_spend` | REAL | required |
| `target_category` | TEXT |  |
| `channel` | TEXT | required |
| `starts_on` | TEXT | required |
| `ends_on` | TEXT | required |
| `budget_php` | REAL |  |
| `description` | TEXT |  |

### `orders`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `order_number` | TEXT | required |
| `customer_id` | INTEGER | → `customers.id` |
| `branch_id` | INTEGER | → `branches.id` · required |
| `channel` | TEXT | required |
| `status` | TEXT | required |
| `created_at` | TEXT | required |
| `subtotal` | REAL | required |
| `discount` | REAL | required |
| `delivery_fee` | REAL | required |
| `total` | REAL | required |
| `promo_id` | INTEGER | → `promos.id` |
| `payment_method` | TEXT | required |
| `points_earned` | INTEGER | required |
| `points_redeemed` | INTEGER | required |

### `order_items`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `order_id` | INTEGER | → `orders.id` · required |
| `product_id` | INTEGER | → `products.id` · required |
| `quantity` | INTEGER | required |
| `unit_price` | REAL | required |
| `unit_cost` | REAL | required |
| `line_total` | REAL | required |

### `riders`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `first_name` | TEXT | required |
| `last_name` | TEXT | required |
| `phone` | TEXT |  |
| `vehicle` | TEXT | required |
| `home_branch_id` | INTEGER | → `branches.id` · required |
| `hired_on` | TEXT | required |
| `status` | TEXT | required |
| `rating` | REAL |  |

### `deliveries`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `order_id` | INTEGER | → `orders.id` · required |
| `rider_id` | INTEGER | → `riders.id` |
| `branch_id` | INTEGER | → `branches.id` · required |
| `delivery_area` | TEXT | required |
| `distance_km` | REAL | required |
| `assigned_at` | TEXT |  |
| `picked_up_at` | TEXT |  |
| `promised_by` | TEXT | required |
| `delivered_at` | TEXT |  |
| `status` | TEXT | required |
| `failure_reason` | TEXT |  |

### `staff`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `employee_number` | TEXT | required |
| `first_name` | TEXT | required |
| `last_name` | TEXT | required |
| `role` | TEXT | required |
| `branch_id` | INTEGER | → `branches.id` |
| `hired_on` | TEXT | required |
| `status` | TEXT | required |
| `hourly_rate_php` | REAL | required |

### `staffing_targets`

| Column | Type | Notes |
|---|---|---|
| `branch_id` | INTEGER | PK · → `branches.id` |
| `day_of_week` | INTEGER | PK |
| `start_hour` | INTEGER | PK |
| `end_hour` | INTEGER | required |
| `min_staff` | INTEGER | required |

### `shifts`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `staff_id` | INTEGER | → `staff.id` · required |
| `branch_id` | INTEGER | → `branches.id` · required |
| `shift_date` | TEXT | required |
| `start_time` | TEXT | required |
| `end_time` | TEXT | required |
| `role` | TEXT | required |
| `status` | TEXT | required |

### `support_tickets`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `ticket_number` | TEXT | required |
| `customer_id` | INTEGER | → `customers.id` |
| `order_id` | INTEGER | → `orders.id` |
| `branch_id` | INTEGER | → `branches.id` |
| `channel` | TEXT | required |
| `category` | TEXT | required |
| `priority` | TEXT | required |
| `status` | TEXT | required |
| `subject` | TEXT | required |
| `description` | TEXT | required |
| `created_at` | TEXT | required |
| `first_response_at` | TEXT |  |
| `resolved_at` | TEXT |  |
| `assigned_staff_id` | INTEGER | → `staff.id` |
| `csat_score` | INTEGER |  |

### `reviews`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK |
| `customer_id` | INTEGER | → `customers.id` |
| `branch_id` | INTEGER | → `branches.id` · required |
| `order_id` | INTEGER | → `orders.id` |
| `source` | TEXT | required |
| `rating` | INTEGER | required |
| `title` | TEXT |  |
| `body` | TEXT | required |
| `topic` | TEXT |  |
| `created_at` | TEXT | required |
| `replied_at` | TEXT |  |
| `reply_text` | TEXT |  |

## Enumerated values

- **`orders.channel`:** `delivery`, `in_store`, `pickup`
- **`orders.status`:** `cancelled`, `completed`, `out_for_delivery`, `pending`, `refunded`
- **`orders.payment_method`:** `card`, `cash`, `cod`, `gcash`, `maya`
- **`deliveries.status`:** `delivered`, `failed`, `in_transit`, `pending_assignment`, `returned`
- **`purchase_orders.status`:** `cancelled`, `in_transit`, `partially_received`, `pending`, `received`
- **`support_tickets.category`:** `app_bug`, `damaged_item`, `late_delivery`, `loyalty_points`, `missing_item`, `payment`, `promo_code`, `refund_request`, `rider_behavior`, `store_experience`, `wrong_item`
- **`support_tickets.status`:** `closed`, `open`, `pending`, `resolved`
- **`support_tickets.priority`:** `high`, `low`, `medium`, `urgent`
- **`support_tickets.channel`:** `chat`, `email`, `facebook`, `phone`, `viber`
- **`loyalty_accounts.tier`:** `Bronze`, `Gold`, `Platinum`, `Silver`
- **`promos.promo_type`:** `bundle`, `fixed_off`, `free_delivery`, `percent_off`
- **`staff.role`:** `branch_manager`, `cashier`, `csr`, `picker`, `stock_clerk`, `supervisor`
- **`shifts.status`:** `called_in_sick`, `completed`, `no_show`, `scheduled`, `swapped`
- **`reviews.source`:** `app`, `facebook`, `google`
- **`reviews.topic`:** `app`, `cleanliness`, `delivery`, `freshness`, `loyalty`, `prices`, `staff`, `stock`
- **`products.category`:** `Baby & Kids`, `Bakery`, `Beverages`, `Canned & Packaged`, `Coffee & Breakfast`, `Condiments & Sauces`, `Dairy & Eggs`, `Frozen`, `Household`, `Meat & Seafood`, `Personal Care`, `Produce`, `Rice & Grains`, `Snacks`
