#!/usr/bin/env python3
"""
Suki Mart sandbox generator — CAMP/RUN with Hermes Agent.

Creates data/store.db: a fictional Metro Manila grocery + delivery chain.
Standard library only. Deterministic: every run produces identical data,
so this script is also the RESET command:

    python data/seed.py          # (re)create data/store.db

The data is intentionally messy. Real business problems are planted in it —
finding them is part of the challenge.
"""
import os
import random
import sqlite3
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "store.db")

R = random.Random(2026)
TODAY = datetime(2026, 9, 30, 21, 0)       # "now" inside the sandbox
START = datetime(2026, 4, 1)               # six months of history


def ts(d):
    return d.strftime("%Y-%m-%d %H:%M:%S") if d else None


def ds(d):
    return d.strftime("%Y-%m-%d") if d else None


def rand_dt(a, b):
    return a + timedelta(seconds=R.randint(0, int((b - a).total_seconds())))


def wchoice(pairs):
    items, weights = zip(*pairs)
    return R.choices(items, weights=weights, k=1)[0]


# ---------------------------------------------------------------- reference data
FIRST = """Juan Maria Jose Ana Mark Kristine John Angelica Paolo Camille Miguel Patricia Carlo Nicole
Rafael Bea Gabriel Joyce Joshua Andrea Christian Jasmine Kevin Denise Adrian Hazel Francis Katrina
Renz Aira Jerome Pauline Ramon Liza Enrique Grace Vincent Trisha Arvin Lovely Nathaniel Shiela Kyle
Rhea Bryan Mae Dominic Czarina Ivan Danica Lorenzo Ella Marco Frances Jericho Clarisse Aldrin Joanna
Emil Kathleen Oliver Precious Rodel Maricel Noel Jennifer Allan Rowena Cedric Abigail Jayson Janine""".split()
LAST = """Santos Reyes Cruz Bautista Ocampo Garcia Mendoza Torres Tomas Andrada Castillo Flores Villanueva
Ramos Castro Rivera Aquino Navarro Salazar Mercado Dela Cruz Gonzales Lopez Hernandez Perez Morales
Del Rosario Aguilar Pascual Soriano Manalo Dizon Pineda Valdez Lim Tan Co Sy Chua Gatchalian Yap Ong
Macaraeg Lacson Samonte Bernardo Buenaventura Evangelista Fernandez Galang Ilagan Javier Lagman""".replace("Dela Cruz", "Dela_Cruz").replace("Del Rosario", "Del_Rosario").split()
LAST = [x.replace("_", " ") for x in LAST]

BRANCHES = [
    # code, name, city, area, type, lat, lng, delivery
    ("BGC", "Suki Mart BGC High Street", "Taguig", "BGC", "flagship", 14.5509, 121.0503, 1),
    ("MKT", "Suki Mart Makati Legazpi", "Makati", "Legazpi Village", "flagship", 14.5547, 121.0169, 1),
    ("ORT", "Suki Mart Ortigas Center", "Pasig", "Ortigas", "standard", 14.5866, 121.0614, 1),
    ("KPT", "Suki Mart Kapitolyo", "Pasig", "Kapitolyo", "standard", 14.5700, 121.0590, 1),
    ("CUB", "Suki Mart Cubao", "Quezon City", "Cubao", "standard", 14.6190, 121.0540, 1),
    ("KAT", "Suki Mart Katipunan", "Quezon City", "Loyola Heights", "standard", 14.6380, 121.0740, 1),
    ("TMR", "Suki Mart Tomas Morato", "Quezon City", "South Triangle", "express", 14.6330, 121.0340, 1),
    ("MAN", "Suki Mart Mandaluyong Shaw", "Mandaluyong", "Shaw", "express", 14.5810, 121.0450, 0),
    ("ALB", "Suki Mart Alabang", "Muntinlupa", "Alabang", "flagship", 14.4230, 121.0400, 1),
    ("PQE", "Suki Mart Parañaque BF", "Parañaque", "BF Homes", "standard", 14.4520, 121.0180, 1),
    ("MKN", "Suki Mart Marikina", "Marikina", "Concepcion", "standard", 14.6500, 121.1030, 1),
    ("ERM", "Suki Mart Ermita", "Manila", "Ermita", "express", 14.5830, 120.9840, 0),
]

SUPPLIERS = [
    # name, focus, lead_days, terms
    ("Luzon Fresh Produce Co.", "Produce", 1, "COD"),
    ("Benguet Highland Farms", "Produce", 2, "Net 15"),
    ("Pampanga Poultry & Meats", "Meat & Seafood", 1, "Net 7"),
    ("Navotas Seafood Traders", "Meat & Seafood", 1, "COD"),
    ("Isla Dairy Cooperative", "Dairy & Eggs", 2, "Net 15"),
    ("Kusina Bakeshop Supply", "Bakery", 1, "Net 7"),
    ("Metro Beverage Distributors", "Beverages", 3, "Net 30"),
    ("Tropika Juice Corp.", "Beverages", 4, "Net 30"),
    ("Pinoy Snack Makers Inc.", "Snacks", 3, "Net 30"),
    ("Visayas Canning Corp.", "Canned & Packaged", 5, "Net 30"),
    ("Golden Grain Rice Mill", "Rice & Grains", 3, "Net 15"),
    ("Mindanao Coffee Traders", "Coffee & Breakfast", 5, "Net 30"),
    ("CleanHome Distributors", "Household", 4, "Net 45"),
    ("Kalinga Personal Care Supply", "Personal Care", 4, "Net 45"),
    ("Frostline Frozen Foods", "Frozen", 3, "Net 30"),
    ("Sari-Sari Wholesale Hub", "Canned & Packaged", 2, "Net 15"),
    ("Baby & Mom Essentials PH", "Baby & Kids", 5, "Net 45"),
    ("Condimento Manila", "Condiments & Sauces", 4, "Net 30"),
]
LATE_SUPPLIERS = {"Tropika Juice Corp.", "Visayas Canning Corp."}   # planted: chronically late

CATALOG = {
    "Produce": [("Tomatoes", "kg", 80), ("Red Onions", "kg", 140), ("Garlic", "kg", 160), ("Potatoes", "kg", 90),
                ("Carrots", "kg", 85), ("Kangkong", "bundle", 25), ("Pechay", "bundle", 30), ("Calamansi", "250g", 45),
                ("Saba Bananas", "kg", 70), ("Carabao Mangoes", "kg", 180), ("Pineapple", "pc", 95), ("Ampalaya", "kg", 110),
                ("Talong (Eggplant)", "kg", 90), ("Sitaw", "bundle", 35), ("Lettuce", "head", 75), ("Ginger", "kg", 150)],
    "Meat & Seafood": [("Pork Liempo", "kg", 360), ("Pork Kasim", "kg", 320), ("Whole Chicken", "kg", 210),
                       ("Chicken Thighs", "kg", 230), ("Ground Beef", "kg", 420), ("Bangus (Milkfish)", "kg", 220),
                       ("Tilapia", "kg", 160), ("Shrimp (Suahe)", "kg", 480), ("Galunggong", "kg", 240), ("Beef Brisket", "kg", 460)],
    "Dairy & Eggs": [("Fresh Eggs Large", "tray-30", 260), ("Fresh Milk", "1L", 105), ("Evaporated Milk", "370ml", 38),
                     ("Condensed Milk", "300ml", 55), ("Cheddar Cheese", "200g", 95), ("Butter", "225g", 140),
                     ("Plain Yogurt", "500g", 120), ("Salted Eggs", "6pc", 70), ("Quail Eggs", "24pc", 65)],
    "Bakery": [("Pandesal", "10pc", 45), ("Ensaymada", "4pc", 120), ("Monay", "6pc", 50), ("Loaf Bread", "600g", 85),
               ("Spanish Bread", "6pc", 55), ("Ube Cheese Pandesal", "6pc", 95), ("Banana Cake", "loaf", 150)],
    "Beverages": [("Bottled Water", "500ml", 18), ("Bottled Water", "6L", 95), ("Cola", "1.5L", 75), ("Lemon Soda", "1.5L", 70),
                  ("Iced Tea Powder", "1L pack", 25), ("Mango Juice", "1L", 90), ("Pineapple Juice", "1L", 85),
                  ("Calamansi Juice", "1L", 95), ("Energy Drink", "250ml", 40), ("Chocolate Malt Drink", "1kg", 380)],
    "Snacks": [("Banana Chips", "200g", 60), ("Chicharon", "100g", 55), ("Corn Snacks", "100g", 35), ("Cassava Chips", "150g", 50),
               ("Polvoron", "12pc", 95), ("Otap", "200g", 85), ("Dried Mangoes", "100g", 110), ("Peanuts Adobo", "200g", 65),
               ("Chocolate Wafer", "10pc", 70), ("Crackers", "10pack", 75)],
    "Canned & Packaged": [("Corned Beef", "260g", 95), ("Sardines in Tomato Sauce", "155g", 26), ("Tuna Flakes", "180g", 42),
                          ("Meat Loaf", "150g", 38), ("Vienna Sausage", "130g", 45), ("Instant Pancit Canton", "60g", 17),
                          ("Instant Noodles Beef", "55g", 12), ("Spaghetti Pasta", "1kg", 95), ("Spaghetti Sauce Sweet", "1kg", 120),
                          ("Coconut Milk", "400ml", 55), ("Liver Spread", "85g", 30), ("Pork and Beans", "230g", 32)],
    "Rice & Grains": [("Premium Rice Dinorado", "5kg", 380), ("Well-Milled Rice", "25kg", 1250), ("Jasmine Rice", "5kg", 340),
                      ("Brown Rice", "2kg", 190), ("Glutinous Rice", "1kg", 90), ("Oatmeal", "800g", 150), ("Brown Sugar", "1kg", 85),
                      ("Refined Sugar", "1kg", 95), ("All-Purpose Flour", "1kg", 70)],
    "Coffee & Breakfast": [("3-in-1 Coffee", "30 sachets", 210), ("Barako Ground Coffee", "250g", 180), ("Instant Coffee", "100g", 130),
                           ("Hot Chocolate Tablea", "10pc", 120), ("Corn Flakes", "500g", 175), ("Peanut Butter", "340g", 110),
                           ("Coco Jam", "250g", 85), ("Hotdog Jumbo", "1kg", 290), ("Longganisa", "500g", 175), ("Tocino", "450g", 165)],
    "Household": [("Laundry Powder", "1kg", 120), ("Fabric Conditioner", "1L", 110), ("Dishwashing Liquid", "500ml", 85),
                  ("Bleach", "1L", 60), ("Toilet Paper", "12 rolls", 190), ("Trash Bags Large", "10pc", 75),
                  ("Insect Spray", "600ml", 250), ("Floor Wax", "500g", 95), ("Kitchen Towel", "2 rolls", 70)],
    "Personal Care": [("Bath Soap", "3x90g", 110), ("Shampoo", "340ml", 185), ("Toothpaste", "150g", 125), ("Toothbrush", "3pc", 95),
                      ("Deodorant", "40ml", 150), ("Sanitary Napkins", "8pc", 55), ("Alcohol 70%", "500ml", 90), ("Lotion", "200ml", 195)],
    "Frozen": [("Chicken Nuggets", "500g", 210), ("Frozen Siomai", "20pc", 180), ("Lumpiang Shanghai", "30pc", 230),
               ("Ice Cream Ube", "1.3L", 290), ("Ice Cream Mango", "1.3L", 290), ("Frozen Mixed Veggies", "500g", 130),
               ("Tapa", "500g", 240), ("Embutido", "2 rolls", 220)],
    "Baby & Kids": [("Diapers Medium", "40pc", 650), ("Baby Wipes", "80pc", 95), ("Infant Formula", "900g", 1150),
                    ("Baby Cereal", "250g", 180), ("Kids Vitamins Syrup", "120ml", 160)],
    "Condiments & Sauces": [("Soy Sauce", "1L", 55), ("Cane Vinegar", "1L", 45), ("Fish Sauce (Patis)", "750ml", 60),
                            ("Banana Ketchup", "550g", 50), ("Oyster Sauce", "405g", 85), ("Cooking Oil", "2L", 230),
                            ("Iodized Salt", "1kg", 30), ("Ground Black Pepper", "50g", 45), ("Shrimp Paste (Bagoong)", "250g", 90),
                            ("Sinigang Mix", "40g", 22)],
}
PERISHABLE = {"Produce": 5, "Meat & Seafood": 4, "Dairy & Eggs": 14, "Bakery": 3, "Frozen": 120}

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sandbox_info (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE branches (
  id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, city TEXT NOT NULL, area TEXT NOT NULL,
  branch_type TEXT NOT NULL CHECK (branch_type IN ('flagship','standard','express')),
  latitude REAL, longitude REAL, has_delivery INTEGER NOT NULL, opened_on TEXT NOT NULL,
  opening_time TEXT NOT NULL, closing_time TEXT NOT NULL, phone TEXT
);

CREATE TABLE suppliers (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, category_focus TEXT NOT NULL, contact_person TEXT, phone TEXT, email TEXT,
  promised_lead_time_days INTEGER NOT NULL, payment_terms TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY, sku TEXT UNIQUE NOT NULL, name TEXT NOT NULL, category TEXT NOT NULL, unit TEXT NOT NULL,
  cost_price REAL NOT NULL, retail_price REAL NOT NULL, supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  is_perishable INTEGER NOT NULL, shelf_life_days INTEGER, is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE inventory (
  branch_id INTEGER NOT NULL REFERENCES branches(id), product_id INTEGER NOT NULL REFERENCES products(id),
  on_hand INTEGER NOT NULL, reorder_point INTEGER NOT NULL, reorder_qty INTEGER NOT NULL,
  avg_daily_sales REAL NOT NULL, nearest_expiry_date TEXT, last_restocked_at TEXT, last_counted_at TEXT,
  PRIMARY KEY (branch_id, product_id)
);

CREATE TABLE purchase_orders (
  id INTEGER PRIMARY KEY, po_number TEXT UNIQUE NOT NULL, supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  branch_id INTEGER NOT NULL REFERENCES branches(id), product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL, unit_cost REAL NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending','in_transit','received','partially_received','cancelled')),
  ordered_at TEXT NOT NULL, expected_at TEXT NOT NULL, received_at TEXT, received_quantity INTEGER, notes TEXT
);

CREATE TABLE customers (
  id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT, phone TEXT, birthdate TEXT,
  city TEXT, home_branch_id INTEGER REFERENCES branches(id), created_at TEXT NOT NULL,
  marketing_opt_in INTEGER NOT NULL DEFAULT 0, preferred_channel TEXT
);

CREATE TABLE loyalty_accounts (
  id INTEGER PRIMARY KEY, customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(id), card_number TEXT UNIQUE NOT NULL,
  tier TEXT NOT NULL CHECK (tier IN ('Bronze','Silver','Gold','Platinum')), points_balance INTEGER NOT NULL,
  lifetime_points INTEGER NOT NULL, points_expiring INTEGER NOT NULL DEFAULT 0, points_expiry_date TEXT,
  joined_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE promos (
  id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  promo_type TEXT NOT NULL CHECK (promo_type IN ('percent_off','fixed_off','free_delivery','bundle')),
  value REAL NOT NULL, min_spend REAL NOT NULL DEFAULT 0, target_category TEXT, channel TEXT NOT NULL,
  starts_on TEXT NOT NULL, ends_on TEXT NOT NULL, budget_php REAL, description TEXT
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY, order_number TEXT UNIQUE NOT NULL, customer_id INTEGER REFERENCES customers(id),
  branch_id INTEGER NOT NULL REFERENCES branches(id),
  channel TEXT NOT NULL CHECK (channel IN ('in_store','delivery','pickup')),
  status TEXT NOT NULL CHECK (status IN ('completed','cancelled','refunded','pending','out_for_delivery')),
  created_at TEXT NOT NULL, subtotal REAL NOT NULL, discount REAL NOT NULL DEFAULT 0, delivery_fee REAL NOT NULL DEFAULT 0,
  total REAL NOT NULL, promo_id INTEGER REFERENCES promos(id), payment_method TEXT NOT NULL, points_earned INTEGER NOT NULL DEFAULT 0,
  points_redeemed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE order_items (
  id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL, unit_price REAL NOT NULL, unit_cost REAL NOT NULL, line_total REAL NOT NULL
);

CREATE TABLE loyalty_transactions (
  id INTEGER PRIMARY KEY, loyalty_account_id INTEGER NOT NULL REFERENCES loyalty_accounts(id),
  order_id INTEGER REFERENCES orders(id), txn_type TEXT NOT NULL CHECK (txn_type IN ('earn','redeem','expire','adjustment')),
  points INTEGER NOT NULL, created_at TEXT NOT NULL, note TEXT
);

CREATE TABLE riders (
  id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, phone TEXT,
  vehicle TEXT NOT NULL CHECK (vehicle IN ('motorcycle','bicycle','e-bike')), home_branch_id INTEGER NOT NULL REFERENCES branches(id),
  hired_on TEXT NOT NULL, status TEXT NOT NULL CHECK (status IN ('active','on_leave','inactive')), rating REAL
);

CREATE TABLE deliveries (
  id INTEGER PRIMARY KEY, order_id INTEGER UNIQUE NOT NULL REFERENCES orders(id), rider_id INTEGER REFERENCES riders(id),
  branch_id INTEGER NOT NULL REFERENCES branches(id), delivery_area TEXT NOT NULL, distance_km REAL NOT NULL,
  assigned_at TEXT, picked_up_at TEXT, promised_by TEXT NOT NULL, delivered_at TEXT,
  status TEXT NOT NULL CHECK (status IN ('delivered','failed','returned','in_transit','pending_assignment')),
  failure_reason TEXT
);

CREATE TABLE staff (
  id INTEGER PRIMARY KEY, employee_number TEXT UNIQUE NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
  role TEXT NOT NULL, branch_id INTEGER REFERENCES branches(id), hired_on TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active','on_leave','resigned')), hourly_rate_php REAL NOT NULL
);

CREATE TABLE staffing_targets (
  branch_id INTEGER NOT NULL REFERENCES branches(id), day_of_week INTEGER NOT NULL, start_hour INTEGER NOT NULL,
  end_hour INTEGER NOT NULL, min_staff INTEGER NOT NULL, PRIMARY KEY (branch_id, day_of_week, start_hour)
);

CREATE TABLE shifts (
  id INTEGER PRIMARY KEY, staff_id INTEGER NOT NULL REFERENCES staff(id), branch_id INTEGER NOT NULL REFERENCES branches(id),
  shift_date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, role TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('scheduled','completed','no_show','called_in_sick','swapped'))
);

CREATE TABLE support_tickets (
  id INTEGER PRIMARY KEY, ticket_number TEXT UNIQUE NOT NULL, customer_id INTEGER REFERENCES customers(id),
  order_id INTEGER REFERENCES orders(id), branch_id INTEGER REFERENCES branches(id), channel TEXT NOT NULL,
  category TEXT NOT NULL, priority TEXT NOT NULL CHECK (priority IN ('low','medium','high','urgent')),
  status TEXT NOT NULL CHECK (status IN ('open','pending','resolved','closed')),
  subject TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL, first_response_at TEXT,
  resolved_at TEXT, assigned_staff_id INTEGER REFERENCES staff(id), csat_score INTEGER
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), branch_id INTEGER NOT NULL REFERENCES branches(id),
  order_id INTEGER REFERENCES orders(id), source TEXT NOT NULL, rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  title TEXT, body TEXT NOT NULL, topic TEXT, created_at TEXT NOT NULL, replied_at TEXT, reply_text TEXT
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_branch_date ON orders(branch_id, created_at);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
CREATE INDEX idx_deliveries_branch ON deliveries(branch_id, promised_by);
CREATE INDEX idx_tickets_status ON support_tickets(status, created_at);
CREATE INDEX idx_reviews_branch ON reviews(branch_id, created_at);
CREATE INDEX idx_shifts_branch_date ON shifts(branch_id, shift_date);
CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id, status);
"""


def phone():
    return "09" + str(R.choice([17, 18, 19, 20, 21, 27, 28, 38, 45, 55, 56, 61, 66, 77, 95, 98])) + f"{R.randint(0, 9999999):07d}"


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    c = con.cursor()

    c.executemany("INSERT INTO sandbox_info VALUES (?,?)", [
        ("business", "Suki Mart — fictional Metro Manila grocery & delivery chain"),
        ("sandbox_now", ts(TODAY)),
        ("history_start", ds(START)),
        ("currency", "PHP"),
        ("note", "All people, businesses and data are fictional. The data contains planted problems."),
    ])

    # ------------------------------------------------------------ branches
    for i, (code, name, city, area, btype, lat, lng, dlv) in enumerate(BRANCHES, 1):
        opened = date(R.randint(2012, 2023), R.randint(1, 12), R.randint(1, 28))
        close = "22:00" if btype != "express" else "23:00"
        c.execute("INSERT INTO branches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (i, code, name, city, area, btype, lat, lng, dlv, ds(opened), "07:00", close,
                   "(02) 8" + f"{R.randint(0, 9999999):07d}"))
    branch_ids = list(range(1, len(BRANCHES) + 1))
    code_to_id = {b[0]: i for i, b in enumerate(BRANCHES, 1)}
    delivery_branches = [code_to_id[b[0]] for b in BRANCHES if b[7]]
    branch_weight = {code_to_id[b[0]]: {"flagship": 1.6, "standard": 1.0, "express": 0.6}[b[4]] for b in BRANCHES}

    # ------------------------------------------------------------ suppliers
    sup_by_focus = {}
    for i, (name, focus, lead, terms) in enumerate(SUPPLIERS, 1):
        cp = f"{R.choice(FIRST)} {R.choice(LAST)}"
        email = name.lower().split()[0].replace(".", "").replace("&", "") + "@example.ph"
        c.execute("INSERT INTO suppliers VALUES (?,?,?,?,?,?,?,?,?)", (i, name, focus, cp, phone(), email, lead, terms, 1))
        sup_by_focus.setdefault(focus, []).append(i)
    sup_name = {i: s[0] for i, s in enumerate(SUPPLIERS, 1)}

    # ------------------------------------------------------------ products
    products = []  # (id, category, price, cost, perishable)
    pid = 0
    for cat, items in CATALOG.items():
        for (name, unit, price) in items:
            pid += 1
            margin = R.uniform(0.12, 0.35) if cat not in ("Rice & Grains", "Baby & Kids") else R.uniform(0.06, 0.14)
            cost = round(price * (1 - margin), 2)
            sup = R.choice(sup_by_focus.get(cat, sup_by_focus["Canned & Packaged"]))
            per = cat in PERISHABLE
            sku = f"SM-{cat[:3].upper()}-{pid:04d}"
            c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (pid, sku, f"{name} {unit}", cat, unit, cost, float(price), sup, int(per), PERISHABLE.get(cat), 1))
            products.append((pid, cat, float(price), cost, per))
    prod_by_id = {p[0]: p for p in products}
    popularity = {p[0]: R.uniform(0.3, 3.0) * (2.2 if p[1] in ("Canned & Packaged", "Beverages", "Condiments & Sauces", "Bakery") else 1)
                  for p in products}

    # ------------------------------------------------------------ inventory (+ planted stock imbalance)
    imbalance_products = R.sample([p[0] for p in products if not p[4]], 14)
    for b in branch_ids:
        for p in products:
            p_id, cat, price, cost, per = p
            ads = round(popularity[p_id] * branch_weight[b] * R.uniform(0.6, 1.4), 2)
            rp = max(5, int(ads * R.uniform(3, 6)))
            rq = max(12, int(ads * R.uniform(10, 18)))
            on_hand = int(ads * R.uniform(5, 20))
            expiry = None
            if per:
                expiry = TODAY.date() + timedelta(days=R.randint(1, PERISHABLE[cat]))
            if p_id in imbalance_products:
                if b % 3 == 0:
                    on_hand = R.choice([0, 0, R.randint(1, max(1, rp // 3))])      # stocking out here…
                elif b % 3 == 1:
                    on_hand = int(ads * R.uniform(70, 120))                         # …while overstocked here
            elif R.random() < 0.03:
                on_hand = R.randint(0, max(1, rp - 1))                              # random low stock
            if per and R.random() < 0.06:
                expiry = TODAY.date() + timedelta(days=R.randint(0, 2))            # expiring soon
                on_hand = max(on_hand, int(ads * R.uniform(6, 14)))
            restocked = TODAY - timedelta(days=R.randint(0, 20), hours=R.randint(0, 12))
            counted = TODAY - timedelta(days=R.choice([0, 1, 2, 3, 7, 14, 30, 45]))
            c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?,?,?,?)",
                      (b, p_id, on_hand, rp, rq, ads, ds(expiry), ts(restocked), ts(counted)))

    # ------------------------------------------------------------ purchase orders (+ late suppliers, duplicates)
    po_rows = []
    po_n = 0
    for _ in range(760):
        p = R.choice(products)
        sup = con.execute("SELECT supplier_id FROM products WHERE id=?", (p[0],)).fetchone()[0]
        b = R.choice(branch_ids)
        ordered = rand_dt(START, TODAY - timedelta(hours=6))
        lead = SUPPLIERS[sup - 1][2]
        expected = ordered + timedelta(days=lead)
        late = sup_name[sup] in LATE_SUPPLIERS
        qty = R.randint(24, 240)
        if expected < TODAY - timedelta(days=1):
            if R.random() < 0.05:
                status, received, rq, notes = "cancelled", None, None, "Cancelled by branch"
            else:
                delay = R.randint(3, 11) if late and R.random() < 0.75 else (R.randint(1, 2) if R.random() < 0.12 else 0)
                received = expected + timedelta(days=delay, hours=R.randint(-6, 6))
                if received > TODAY:
                    status, received, rq, notes = "in_transit", None, None, "Supplier delayed"
                elif R.random() < (0.3 if late else 0.06):
                    status, rq, notes = "partially_received", int(qty * R.uniform(0.4, 0.85)), "Short delivery"
                else:
                    status, rq, notes = "received", qty, None
        else:
            status, received, rq, notes = R.choice(["pending", "in_transit"]), None, None, None
        po_n += 1
        po_rows.append((po_n, f"PO-2026-{po_n:05d}", sup, b, p[0], qty, p[3], status, ts(ordered), ts(expected), ts(received), rq, notes))
    # planted duplicate POs
    for _ in range(18):
        src = R.choice([r for r in po_rows if r[7] in ("pending", "in_transit")])
        po_n += 1
        dup_ordered = datetime.strptime(src[8], "%Y-%m-%d %H:%M:%S") + timedelta(hours=R.randint(1, 30))
        po_rows.append((po_n, f"PO-2026-{po_n:05d}", src[2], src[3], src[4], src[5], src[6], "pending",
                        ts(dup_ordered), src[9], None, None, None))
    c.executemany("INSERT INTO purchase_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", po_rows)

    # ------------------------------------------------------------ customers (+ duplicates)
    cities = [b[2] for b in BRANCHES]
    customers = []
    N_CUST = 2600
    for cid in range(1, N_CUST + 1):
        fn, ln = R.choice(FIRST), R.choice(LAST)
        created = rand_dt(datetime(2023, 1, 1), TODAY - timedelta(days=5))
        home = R.choices(branch_ids, weights=[branch_weight[b] for b in branch_ids])[0]
        email = f"{fn.lower()}.{ln.lower().replace(' ', '')}{R.randint(1, 999)}@{R.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'example.ph'])}"
        bd = date(R.randint(1960, 2006), R.randint(1, 12), R.randint(1, 28))
        customers.append([cid, fn, ln, email, phone(), ds(bd), BRANCHES[home - 1][2], home, ts(created),
                          int(R.random() < 0.55), R.choice(["sms", "email", "app_push", "viber"])])
    dup_rows = []
    for k in range(70):
        src = R.choice(customers[:2400])
        nid = N_CUST + k + 1
        ph = src[4]
        ph = R.choice(["+63" + ph[1:], ph[:4] + " " + ph[4:7] + " " + ph[7:], ph])
        em = src[3]
        em = R.choice([em.upper(), em.replace("gmail", "gmial"), em.replace(".", "", 1), em])
        fn = R.choice([src[1], src[1].upper(), src[1][:3] + "."]) if len(src[1]) > 3 else src[1]
        dup_rows.append([nid, fn, src[2], em, ph, src[5], src[6], src[7],
                         ts(datetime.strptime(src[8], "%Y-%m-%d %H:%M:%S") + timedelta(days=R.randint(30, 400))),
                         src[9], src[10]])
    all_customers = customers + dup_rows
    for row in all_customers:
        if row[8] > ts(TODAY):
            row[8] = ts(TODAY - timedelta(days=2))
    c.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?,?)", all_customers)
    cust_home = {r[0]: r[7] for r in all_customers}
    cust_ids = [r[0] for r in all_customers]

    # customer behaviour segments
    regulars = R.sample(cust_ids[:2400], 420)
    lapsed = set(R.sample(regulars, 90))     # planted: stopped buying ~2 months ago
    occasional = [x for x in cust_ids if x not in set(regulars)]

    # ------------------------------------------------------------ promos (+ money-losers)
    promos = [
        ("PAYDAY15", "Payday Treat 15% Off", "percent_off", 15, 1500, None, "all", "2026-04-15", "2026-09-30", 400000, "15% off on payday weekends"),
        ("FREESHIPQC", "Free Delivery QC", "free_delivery", 79, 800, None, "delivery", "2026-05-01", "2026-08-31", 120000, "Free delivery for QC branches"),
        ("RICE30", "Rice Rush 30% Off", "percent_off", 30, 0, "Rice & Grains", "all", "2026-07-01", "2026-09-30", 150000, "Deep discount on rice"),
        ("BABY20", "Baby Week 20% Off", "percent_off", 20, 1000, "Baby & Kids", "all", "2026-08-01", "2026-08-31", 90000, "Baby essentials sale"),
        ("SUKI100", "Suki ₱100 Off", "fixed_off", 100, 1000, None, "all", "2026-04-01", "2026-09-30", 250000, "Welcome back voucher"),
        ("FRESHAM", "Fresh Morning 10%", "percent_off", 10, 500, "Produce", "in_store", "2026-06-01", "2026-09-30", 60000, "7–10 AM produce discount"),
        ("SNACKBUNDLE", "Merienda Bundle", "bundle", 50, 300, "Snacks", "all", "2026-05-15", "2026-07-15", 40000, "Buy 3 snacks, save ₱50"),
        ("COFFEE2GO", "Kape Deal", "fixed_off", 40, 400, "Coffee & Breakfast", "all", "2026-06-15", "2026-09-15", 50000, "₱40 off coffee & breakfast"),
        ("RAINYDAY", "Tag-ulan Free Delivery", "free_delivery", 79, 1200, None, "delivery", "2026-07-01", "2026-09-30", 150000, "Rainy season delivery promo"),
        ("GOLDEXTRA", "Gold Member Extra 12%", "percent_off", 12, 2000, None, "all", "2026-04-01", "2026-09-30", 300000, "For Gold and Platinum members"),
        ("FROZEN25", "Freezer Fill-up 25%", "percent_off", 25, 800, "Frozen", "all", "2026-08-15", "2026-09-30", 70000, "Frozen food sale"),
        ("CLEANHOME", "Linis Bahay 15%", "percent_off", 15, 600, "Household", "all", "2026-05-01", "2026-06-30", 45000, "Household essentials"),
        ("APPFIRST", "First Delivery ₱150 Off", "fixed_off", 150, 700, None, "delivery", "2026-04-01", "2026-09-30", 200000, "New delivery customers"),
        ("BAYANIHAN", "Bayanihan 8%", "percent_off", 8, 500, None, "all", "2026-06-12", "2026-06-30", 80000, "Independence month"),
        ("MEATFEST", "Ihaw-Ihaw Meat Fest 20%", "percent_off", 20, 1500, "Meat & Seafood", "all", "2026-09-01", "2026-09-30", 120000, "Grilling season"),
        ("SEPT3X", "Triple Points September", "fixed_off", 0, 500, None, "all", "2026-09-01", "2026-09-30", 0, "Triple loyalty points"),
    ]
    for i, pr in enumerate(promos, 1):
        c.execute("INSERT INTO promos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (i,) + pr)
    promo_by_code = {p[0]: i for i, p in enumerate(promos, 1)}

    # ------------------------------------------------------------ loyalty accounts
    tiers = {}
    loyalty_ids = {}
    la_id = 0
    for cid in cust_ids:
        if R.random() < (0.95 if cid in regulars else 0.45):
            la_id += 1
            tier = wchoice([("Bronze", 50), ("Silver", 28), ("Gold", 16), ("Platinum", 6)]) if cid not in regulars else \
                wchoice([("Bronze", 15), ("Silver", 35), ("Gold", 35), ("Platinum", 15)])
            tiers[cid] = tier
            loyalty_ids[cid] = la_id
    loyalty_balance = {la: 0 for la in loyalty_ids.values()}
    loyalty_life = {la: 0 for la in loyalty_ids.values()}
    loy_txn = []

    # ------------------------------------------------------------ orders + items + deliveries
    riders = []
    for r in range(1, 49):
        home = R.choice(delivery_branches)
        riders.append((r, R.choice(FIRST), R.choice(LAST), phone(), wchoice([("motorcycle", 80), ("e-bike", 12), ("bicycle", 8)]),
                       home, ds(date(R.randint(2021, 2026), R.randint(1, 12), R.randint(1, 28))) if True else None,
                       wchoice([("active", 88), ("on_leave", 6), ("inactive", 6)]), round(R.uniform(3.9, 4.95), 2)))
    riders = [list(r) for r in riders]
    for r in riders:
        if r[6] > ds(TODAY):
            r[6] = "2026-01-15"
    bad_riders = {5, 23}                                 # planted: high failure / lateness
    for r in riders:
        if r[0] in bad_riders:
            r[8] = round(R.uniform(3.1, 3.5), 2)
            r[7] = "active"
    c.executemany("INSERT INTO riders VALUES (?,?,?,?,?,?,?,?,?)", riders)
    riders_by_branch = {}
    for r in riders:
        if r[7] == "active":
            riders_by_branch.setdefault(r[5], []).append(r[0])
    for b in delivery_branches:
        riders_by_branch.setdefault(b, [R.choice([r[0] for r in riders])])

    AREAS = {
        "BGC": ["Fort Bonifacio", "McKinley Hill", "Pinagsama", "Western Bicutan"],
        "MKT": ["Legazpi Village", "Salcedo Village", "Poblacion", "Bel-Air", "San Antonio"],
        "ORT": ["Ortigas Center", "San Antonio", "Ugong", "Wack-Wack"],
        "KPT": ["Kapitolyo", "Oranbo", "Bagong Ilog", "Ugong"],
        "CUB": ["Cubao", "Socorro", "Kamuning", "Project 4", "Horseshoe"],
        "KAT": ["Loyola Heights", "Teachers Village", "Diliman", "Blue Ridge"],
        "TMR": ["South Triangle", "Sacred Heart", "Laging Handa", "Kamuning"],
        "ALB": ["Alabang", "Ayala Alabang", "Cupang", "Sucat"],
        "PQE": ["BF Homes", "San Antonio Valley", "Moonwalk", "Don Bosco"],
        "MKN": ["Concepcion", "Marikina Heights", "Parang", "Sto. Niño"],
    }

    order_rows, item_rows, deliv_rows = [], [], []
    oid = iid = did = 0
    pay_methods = [("cash", 34), ("gcash", 30), ("maya", 12), ("card", 16), ("cod", 8)]
    prod_ids = [p[0] for p in products]
    prod_w = [popularity[p] for p in prod_ids]

    def make_order(created, cust, branch, channel):
        nonlocal oid, iid, did
        oid += 1
        n_items = R.randint(1, 4) if channel == "in_store" else R.randint(3, 9)
        chosen = R.choices(prod_ids, weights=prod_w, k=n_items)
        subtotal = 0.0
        lines = []
        for p_id in set(chosen):
            p = prod_by_id[p_id]
            qty = R.randint(1, 4)
            line = round(p[2] * qty, 2)
            subtotal += line
            iid += 1
            lines.append((iid, oid, p_id, qty, p[2], p[3], line))
        subtotal = round(subtotal, 2)
        # promo selection
        promo_id, discount = None, 0.0
        active = [(code, i) for code, i in promo_by_code.items()
                  if promos[i - 1][7] <= ds(created) <= promos[i - 1][8]
                  and (promos[i - 1][6] in ("all", channel))
                  and subtotal >= promos[i - 1][4]]
        if active and R.random() < 0.28:
            code, promo_id = R.choice(active)
            pr = promos[promo_id - 1]
            ptype, val, cat = pr[2], pr[3], pr[5]
            base = subtotal if not cat else sum(l[6] for l in lines if prod_by_id[l[2]][1] == cat)
            if ptype == "percent_off":
                discount = round(base * val / 100, 2)
            elif ptype == "fixed_off":
                discount = float(val) if base > 0 else 0.0
            elif ptype == "bundle":
                discount = float(val) if base >= 150 else 0.0
            if discount == 0 and ptype != "free_delivery" and code != "SEPT3X":
                promo_id = None
        fee = 0.0
        if channel == "delivery":
            fee = 79.0 if subtotal < 1500 else 49.0
            if promo_id and promos[promo_id - 1][2] == "free_delivery":
                fee = 0.0
        total = round(max(0, subtotal - discount) + fee, 2)
        status = wchoice([("completed", 93), ("cancelled", 4), ("refunded", 3)])
        if created > TODAY - timedelta(hours=3):
            status = "pending" if channel != "delivery" else "out_for_delivery"
        la = loyalty_ids.get(cust)
        earned = redeemed = 0
        if la and status == "completed":
            mult = 3 if (promo_id == promo_by_code["SEPT3X"]) else 1
            earned = int(total // 100) * mult
            if loyalty_balance[la] > 300 and R.random() < 0.12:
                redeemed = min(loyalty_balance[la], R.choice([100, 200, 300]))
                loyalty_balance[la] -= redeemed
                loy_txn.append((la, oid, "redeem", -redeemed, ts(created), "Redeemed at checkout"))
            loyalty_balance[la] += earned
            loyalty_life[la] += earned
            loy_txn.append((la, oid, "earn", earned, ts(created), "Triple points promo" if mult == 3 else None))
        order_rows.append((oid, f"SM-{created.strftime('%y%m')}-{oid:06d}", cust, branch, channel, status, ts(created),
                           subtotal, discount, fee, total, promo_id, wchoice(pay_methods if channel != "in_store" else pay_methods[:4]),
                           earned, redeemed))
        item_rows.extend(lines)
        if channel == "delivery":
            did += 1
            code = BRANCHES[branch - 1][0]
            area = R.choice(AREAS.get(code, ["Nearby"]))
            dist = round(R.uniform(0.8, 7.5), 1)
            promised = created + timedelta(minutes=R.choice([60, 90, 120]))
            rider = R.choice(riders_by_branch[branch])
            if R.random() < 0.06:
                rider = R.choice(list(bad_riders))
            assigned = created + timedelta(minutes=R.randint(3, 25))
            peak = created.weekday() in (4, 5) and 17 <= created.hour <= 20
            late_zone = code in ("CUB", "ORT") and peak                           # planted: late cluster
            base_min = R.randint(15, 40) + dist * 3
            if late_zone:
                base_min += R.randint(40, 110)
            elif peak:
                base_min += R.randint(0, 35)
            if rider in bad_riders:
                base_min += R.randint(20, 70)
            picked = assigned + timedelta(minutes=R.randint(5, 20))
            delivered = picked + timedelta(minutes=base_min)
            dstatus, reason = "delivered", None
            fail_p = 0.02 + (0.14 if rider in bad_riders else 0) + (0.05 if late_zone else 0)
            if status == "cancelled":
                dstatus, delivered, reason = "failed", None, "Order cancelled"
            elif R.random() < fail_p:
                dstatus, delivered = R.choice(["failed", "returned"]), None
                reason = R.choice(["Customer unreachable", "Wrong address", "Rider accident/vehicle issue", "Items damaged", "Customer refused"])
            if status in ("pending", "out_for_delivery"):
                dstatus, delivered, reason = ("in_transit" if R.random() < 0.7 else "pending_assignment"), None, None
                if dstatus == "pending_assignment":
                    rider, assigned, picked = None, None, None
            deliv_rows.append((did, oid, rider, branch, area, dist, ts(assigned), ts(picked), ts(promised), ts(delivered), dstatus, reason))

    day = START
    while day.date() <= TODAY.date():
        dow = day.weekday()
        payday = day.day in (15, 16, 30, 31, 1)
        for b in branch_ids:
            base = 13 * branch_weight[b] * (1.25 if dow >= 4 else 1.0) * (1.35 if payday else 1.0)
            n = max(1, int(R.gauss(base, base * 0.18)))
            for _ in range(n):
                hour = wchoice([(7, 4), (8, 6), (9, 6), (10, 7), (11, 10), (12, 10), (13, 7), (14, 5), (15, 5),
                                (16, 6), (17, 10), (18, 12), (19, 11), (20, 7), (21, 3)])
                created = day.replace(hour=hour, minute=R.randint(0, 59), second=R.randint(0, 59))
                if created > TODAY:
                    continue
                has_dlv = BRANCHES[b - 1][7]
                channel = wchoice([("in_store", 62), ("delivery", 28 if has_dlv else 0), ("pickup", 10)])
                cust = None
                if R.random() < 0.72:
                    pool = regulars if R.random() < 0.55 else occasional
                    cust = R.choice(pool)
                    if cust in lapsed and created > TODAY - timedelta(days=62):
                        cust = R.choice(occasional)
                    if cust_home.get(cust) != b and R.random() < 0.7:
                        cust = None if channel == "in_store" and R.random() < 0.3 else cust
                if channel != "in_store" and cust is None:
                    cust = R.choice(occasional)
                make_order(created, cust, b, channel)
        day += timedelta(days=1)

    # lapsed regulars get a dense history before they vanish
    for cid in lapsed:
        b = cust_home[cid]
        t = START + timedelta(days=R.randint(0, 10))
        stop = TODAY - timedelta(days=R.randint(63, 95))
        while t < stop:
            ch = "delivery" if BRANCHES[b - 1][7] and R.random() < 0.5 else "in_store"
            make_order(t.replace(hour=R.randint(8, 20), minute=R.randint(0, 59)), cid, b, ch)
            t += timedelta(days=R.randint(4, 9))

    c.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", order_rows)
    c.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?,?)", item_rows)
    c.executemany("INSERT INTO deliveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", deliv_rows)

    # loyalty accounts + expiring points (planted)
    la_rows = []
    for cid, la in loyalty_ids.items():
        bal = loyalty_balance[la]
        expiring, exp_date = 0, None
        if bal > 0 and R.random() < 0.3:
            expiring = int(bal * R.uniform(0.2, 0.8))
            exp_date = ds(TODAY.date() + timedelta(days=R.randint(1, 30)))
        created = next(r[8] for r in all_customers if r[0] == cid)
        la_rows.append((la, cid, f"SUKI-{la:08d}", tiers[cid], bal, loyalty_life[la] + R.randint(0, 3000), expiring, exp_date,
                        created, "active" if R.random() > 0.02 else "suspended"))
    c.executemany("INSERT INTO loyalty_accounts VALUES (?,?,?,?,?,?,?,?,?,?)", la_rows)
    for la in R.sample(list(loyalty_ids.values()), 120):
        loy_txn.append((la, None, "expire", -R.randint(50, 600), ts(rand_dt(START, TODAY)), "Points expired (12-month rule)"))
    for la in R.sample(list(loyalty_ids.values()), 25):
        loy_txn.append((la, None, "adjustment", R.choice([100, 200, 500, -150]), ts(rand_dt(START, TODAY)), "Manual adjustment by CSR"))
    c.executemany("INSERT INTO loyalty_transactions (loyalty_account_id, order_id, txn_type, points, created_at, note) VALUES (?,?,?,?,?,?)", loy_txn)

    # ------------------------------------------------------------ staff, targets, shifts
    staff_rows = []
    sid = 0
    ROLE_RATE = {"cashier": 78, "stock_clerk": 75, "picker": 76, "supervisor": 105, "branch_manager": 160, "csr": 95}
    for b in branch_ids:
        size = {"flagship": 22, "standard": 16, "express": 10}[BRANCHES[b - 1][4]]
        roles = ["branch_manager"] + ["supervisor"] * 2 + ["cashier"] * (size // 2) + ["stock_clerk"] * (size // 4) + ["picker"] * (size // 5)
        for role in roles:
            sid += 1
            staff_rows.append((sid, f"EMP-{sid:04d}", R.choice(FIRST), R.choice(LAST), role, b,
                               ds(date(R.randint(2016, 2026), R.randint(1, 9), R.randint(1, 28))),
                               wchoice([("active", 92), ("on_leave", 5), ("resigned", 3)]), ROLE_RATE[role] + R.randint(0, 20)))
    for k in range(10):   # central customer service team (no branch)
        sid += 1
        staff_rows.append((sid, f"EMP-{sid:04d}", R.choice(FIRST), R.choice(LAST), "csr", None,
                           ds(date(R.randint(2020, 2026), R.randint(1, 9), R.randint(1, 28))), "active", ROLE_RATE["csr"] + R.randint(0, 15)))
    c.executemany("INSERT INTO staff VALUES (?,?,?,?,?,?,?,?,?)", staff_rows)
    csr_ids = [s[0] for s in staff_rows if s[4] == "csr"]

    target_rows = []
    for b in branch_ids:
        mult = {"flagship": 1.5, "standard": 1.0, "express": 0.6}[BRANCHES[b - 1][4]]
        for dow in range(7):
            for (sh, eh, base) in [(7, 11, 4), (11, 15, 5), (15, 19, 6), (19, 23, 5)]:
                peak = 1.3 if dow >= 4 and sh >= 15 else 1.0
                target_rows.append((b, dow, sh, eh, max(2, round(base * mult * peak))))
    # stored with SQLite's convention: 0=Sunday … 6=Saturday (matches strftime('%w'))
    c.executemany("INSERT INTO staffing_targets VALUES (?,?,?,?,?)",
                  [(b, (d + 1) % 7, sh, eh, m) for (b, d, sh, eh, m) in target_rows])

    shift_rows = []
    shid = 0
    understaffed = {code_to_id["CUB"], code_to_id["KPT"], code_to_id["ALB"]}     # planted
    flaky = set(R.sample([s[0] for s in staff_rows if s[7] == "active" and s[5]], 9))  # planted no-show repeaters
    active_by_branch = {}
    for s in staff_rows:
        if s[7] == "active" and s[5]:
            active_by_branch.setdefault(s[5], []).append(s)
    d0 = (TODAY - timedelta(days=56)).date()
    for off in range(0, 56 + 14):
        dday = d0 + timedelta(days=off)
        dow = dday.weekday()
        for b, members in active_by_branch.items():
            for (sh, eh, base) in [(7, 11, 4), (11, 15, 5), (15, 19, 6), (19, 23, 5)]:
                tgt = next(t[4] for t in target_rows if t[0] == b and t[1] == dow and t[2] == sh)
                n = tgt
                if b in understaffed and dow >= 4 and sh >= 15:
                    n = max(1, tgt - R.randint(2, 3))
                elif R.random() < 0.08:
                    n = tgt - 1
                for s in R.sample(members, min(n, len(members))):
                    shid += 1
                    future = dday > TODAY.date()
                    if future:
                        st = "scheduled"
                    elif s[0] in flaky and R.random() < 0.22:
                        st = R.choice(["no_show", "called_in_sick"])
                    else:
                        st = wchoice([("completed", 95), ("called_in_sick", 2), ("no_show", 1), ("swapped", 2)])
                    shift_rows.append((shid, s[0], b, ds(dday), f"{sh:02d}:00", f"{eh:02d}:00", s[4], st))
    c.executemany("INSERT INTO shifts VALUES (?,?,?,?,?,?,?,?)", shift_rows)

    # ------------------------------------------------------------ support tickets
    order_lookup = {o[0]: o for o in order_rows}
    deliv_by_order = {d[1]: d for d in deliv_rows}
    delivery_orders = [d[1] for d in deliv_rows]
    late_orders = [d[1] for d in deliv_rows if d[9] and d[9] > d[8]]
    failed_orders = [d[1] for d in deliv_rows if d[10] in ("failed", "returned") and order_lookup[d[1]][5] != "cancelled"]
    rice_orders = [o[0] for o in order_rows if o[11] == promo_by_code["RICE30"]]
    TEMPL = {
        "late_delivery": ("Delivery arrived late", ["My order came {m} minutes late and the frozen items were soft.", "Rider was very late, order was promised within the hour.", "Still waiting for my delivery, nobody updates me."]),
        "missing_item": ("Missing item in my order", ["The {p} was not in the bag but I was charged for it.", "Two items missing from my delivery.", "Receipt shows {p} but it wasn't included."]),
        "wrong_item": ("Received wrong item", ["I ordered {p} but got a different size.", "Wrong brand was delivered, please replace."]),
        "damaged_item": ("Damaged / spoiled item", ["The eggs were cracked when they arrived.", "{p} was already spoiled on delivery.", "Packaging was torn and leaking."]),
        "refund_request": ("Refund request", ["Please refund my cancelled order, it's been a week.", "I was double-charged on GCash, requesting a refund."]),
        "loyalty_points": ("Loyalty points issue", ["My points from last week's purchase were not credited.", "My points expired without any notice.", "Triple points promo not reflected on my card."]),
        "promo_code": ("Promo code not working", ["Code {c} says invalid at checkout.", "Discount was not applied even though I met the minimum spend.", "Promo {c} applied the wrong amount."]),
        "payment": ("Payment problem", ["Card payment failed but money was deducted.", "GCash payment is stuck on pending."]),
        "app_bug": ("App issue", ["The app keeps logging me out.", "Cannot add items to cart on the app.", "Delivery tracking map is not loading."]),
        "store_experience": ("In-store experience", ["Long queue at the cashier, only one counter open.", "Staff was rude when I asked for help.", "Aisles were messy and prices were missing."]),
        "rider_behavior": ("Rider complaint", ["Rider was rude and asked for extra tip.", "Rider left the order at the gate without calling."]),
    }
    t_rows = []
    tid = 0
    for _ in range(1650):
        cat = wchoice([("late_delivery", 18), ("missing_item", 13), ("wrong_item", 7), ("damaged_item", 9), ("refund_request", 9),
                       ("loyalty_points", 10), ("promo_code", 9), ("payment", 7), ("app_bug", 8), ("store_experience", 6), ("rider_behavior", 4)])
        order_id = None
        if cat in ("late_delivery", "rider_behavior") and late_orders:
            order_id = R.choice(late_orders)
        elif cat in ("missing_item", "wrong_item", "damaged_item", "refund_request") and R.random() < 0.8:
            order_id = R.choice(delivery_orders + failed_orders * 3)
        elif cat == "promo_code" and rice_orders and R.random() < 0.5:
            order_id = R.choice(rice_orders)
        o = order_lookup.get(order_id)
        cust = o[2] if o else R.choice(cust_ids)
        branch = o[3] if o else (cust_home.get(cust) or R.choice(branch_ids))
        created = datetime.strptime(o[6], "%Y-%m-%d %H:%M:%S") + timedelta(hours=R.randint(1, 30)) if o else rand_dt(START, TODAY)
        if created > TODAY:
            created = TODAY - timedelta(hours=R.randint(1, 20))
        subj, bodies = TEMPL[cat]
        p_name = con.execute("SELECT name FROM products WHERE id=?", (R.choice(prod_ids),)).fetchone()[0]
        body = R.choice(bodies).format(m=R.randint(30, 120), p=p_name, c=R.choice(["RICE30", "PAYDAY15", "SUKI100", "FROZEN25"]))
        prio = wchoice([("low", 20), ("medium", 45), ("high", 27), ("urgent", 8)])
        age_days = (TODAY - created).days
        fr = created + timedelta(minutes=R.randint(10, 60 * 30))
        if age_days > 3:
            status = wchoice([("resolved", 55), ("closed", 30), ("pending", 8), ("open", 7)])
        else:
            status = wchoice([("open", 45), ("pending", 30), ("resolved", 25)])
        if fr > TODAY:
            fr = None
        resolved = None
        if status in ("resolved", "closed"):
            resolved = (fr or created) + timedelta(hours=R.randint(2, 96))
            if resolved > TODAY:
                resolved, status = None, "pending"
        csat = R.choice([1, 2, 3, 4, 4, 5, 5]) if resolved and R.random() < 0.6 else None
        tid += 1
        t_rows.append([tid, f"TKT-{tid:05d}", cust, order_id, branch, wchoice([("chat", 35), ("facebook", 25), ("email", 20), ("phone", 15), ("viber", 5)]),
                       cat, prio, status, subj, body, ts(created), ts(fr), ts(resolved), R.choice(csr_ids), csat])
    # planted: forgotten tickets — open, old, never responded to
    for row in R.sample([r for r in t_rows if r[8] in ("open", "pending")], 45):
        old = TODAY - timedelta(days=R.randint(8, 40), hours=R.randint(0, 20))
        row[11], row[12], row[13], row[8], row[15] = ts(old), None, None, "open", None
        row[14] = None if R.random() < 0.6 else row[14]
    c.executemany("INSERT INTO support_tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t_rows)

    # ------------------------------------------------------------ reviews
    POS = {
        "freshness": ["Fresh produce every time, the mangoes were sweet!", "Always fresh bread in the morning.", "Meat section is clean and fresh."],
        "delivery": ["Rider was fast and polite. Arrived early!", "Delivery was on time and items were well packed."],
        "staff": ["Cashiers are friendly and quick.", "Staff helped me find everything. Very accommodating."],
        "prices": ["Prices are fair and the payday promo is sulit.", "Good deals every week, cheaper than the mall."],
        "cleanliness": ["Store is clean and well organized.", "Neat aisles and air-conditioned, nice to shop here."],
        "app": ["App is easy to use and checkout is quick."],
    }
    NEG = {
        "delivery": ["Delivery was more than an hour late. Ice cream melted.", "Rider could not find our place and cancelled.", "Always late on Friday nights. Very frustrating."],
        "staff": ["Only one cashier open during rush hour. Long queue.", "Staff were chatting and ignored customers."],
        "cleanliness": ["Store smells bad and floors are sticky.", "Messy aisles, expired items still on the shelf."],
        "stock": ["Out of stock again. Third time this week.", "Items I need are never available here."],
        "freshness": ["Vegetables were wilted and the fish was not fresh.", "Bread was stale when I bought it."],
        "app": ["App crashed at checkout and I was charged twice."],
        "loyalty": ["My points disappeared. Customer service never replied."],
    }
    rv_rows = []
    rv_id = 0
    kpt = code_to_id["KPT"]
    for _ in range(3200):
        b = R.choices(branch_ids, weights=[branch_weight[x] for x in branch_ids])[0]
        created = rand_dt(START, TODAY)
        cust = R.choice(cust_ids) if R.random() < 0.85 else None
        order_id = None
        rating = wchoice([(5, 38), (4, 30), (3, 14), (2, 9), (1, 9)])
        if b == kpt and created > TODAY - timedelta(days=35):              # planted: branch in decline
            rating = wchoice([(5, 10), (4, 14), (3, 18), (2, 25), (1, 33)])
        if b in (code_to_id["CUB"], code_to_id["ORT"]) and R.random() < 0.25:
            late = [d for d in deliv_rows if d[3] == b and d[9] and d[9] > d[8]]
            if late:
                d = R.choice(late)
                order_id, rating = d[1], R.choice([1, 1, 2, 2, 3])
                created = datetime.strptime(d[9], "%Y-%m-%d %H:%M:%S") + timedelta(hours=R.randint(1, 20))
                cust = order_lookup[d[1]][2]
        if created > TODAY:
            created = TODAY - timedelta(hours=2)
        if rating >= 4:
            topic = R.choice(list(POS))
            body = R.choice(POS[topic])
            title = R.choice(["Sulit!", "Love this branch", "Great service", "Will shop again", "Solid"])
        else:
            topic = "delivery" if order_id else (R.choice(["staff", "cleanliness", "stock", "freshness"]) if b == kpt else R.choice(list(NEG)))
            body = R.choice(NEG[topic])
            title = R.choice(["Disappointed", "Needs improvement", "Not again", "Hay naku", "Please fix this"])
        replied = None
        reply = None
        if R.random() < (0.55 if rating >= 4 else 0.35):
            replied = created + timedelta(hours=R.randint(3, 120))
            if replied > TODAY:
                replied = None
            else:
                reply = "Salamat po for your feedback! We've shared this with our branch team." if rating >= 4 else \
                    "We're sorry about your experience. Our team will reach out to make this right."
        rv_id += 1
        rv_rows.append((rv_id, cust, b, order_id, wchoice([("google", 45), ("facebook", 30), ("app", 25)]), rating, title, body, topic,
                        ts(created), ts(replied), reply))
    c.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rv_rows)

    con.commit()
    con.execute("VACUUM")
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
              ["branches", "suppliers", "products", "inventory", "purchase_orders", "customers", "loyalty_accounts",
               "loyalty_transactions", "promos", "orders", "order_items", "riders", "deliveries", "staff",
               "staffing_targets", "shifts", "support_tickets", "reviews"]}
    con.close()
    print(f"Created {DB_PATH}")
    for k, v in counts.items():
        print(f"  {k:<22}{v:>8,}")


if __name__ == "__main__":
    main()
