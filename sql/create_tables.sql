-- 商品テーブル
CREATE TABLE IF NOT EXISTS items (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    unit_price INTEGER NOT NULL,
    PRIMARY KEY (id),
    CHECK (unit_price >= 0)
);

-- 会員区分テーブル
CREATE TABLE IF NOT EXISTS membership_types (
    code INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (code)
);

-- 顧客テーブル
CREATE TABLE IF NOT EXISTS customers (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    membership_type_code INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (membership_type_code) REFERENCES membership_types (code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 消費税テーブル
CREATE TABLE IF NOT EXISTS consumption_taxes (
    id TEXT NOT NULL,
    begin_dt TEXT NOT NULL,
    end_dt TEXT NOT NULL,
    rate REAL NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (begin_dt),
    UNIQUE (end_dt),
    CHECK (
        rate >= 0.0
        AND rate < 1.0
    )
);

-- 売上テーブル
CREATE TABLE if NOT EXISTS sales (
    id TEXT NOT NULL,
    customer_id TEXT NULL,
    sold_at TEXT NOT NULL,
    subtotal INTEGER NOT NULL,
    discount_rate REAL NOT NULL,
    discount_amount INTEGER NOT NULL,
    taxable_amount INTEGER NOT NULL,
    consumption_tax_rate REAL NOT NULL,
    consumption_tax_amount INTEGER NOT NULL,
    total INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (subtotal >= 0),
    CHECK (discount_rate >= 0.0),
    CHECK (discount_amount >= 0),
    CHECK (taxable_amount >= 0),
    CHECK (
        consumption_tax_rate >= 0.0
        AND consumption_tax_rate < 1.0
    ),
    CHECK (consumption_tax_amount >= 0),
    CHECK (total >= 0)
);

-- 売上明細テーブル
CREATE TABLE IF NOT EXISTS sale_details (
    sale_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantities INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    PRIMARY KEY (sale_id, item_id),
    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (sale_id, item_id),
    CHECK (quantities >= 0) CHECK (amount > 0)
);
