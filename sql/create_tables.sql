-- 商品テーブル
CREATE TABLE IF NOT EXISTS items (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    unit_price INTEGER NOT NULL,
    CONSTRAINT pk_items PRIMARY KEY (id),
    CONSTRAINT ck_items_unit_price CHECK (unit_price >= 0)
);

-- 会員区分テーブル
CREATE TABLE IF NOT EXISTS membership_types (
    code INTEGER NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT pk_membership_types PRIMARY KEY (code)
);

-- 顧客テーブル
CREATE TABLE IF NOT EXISTS customers (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    membership_type_code INTEGER NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (id),
    CONSTRAINT fk_customers__membership_type_code FOREIGN KEY (membership_type_code) REFERENCES membership_types (code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 消費税テーブル
-- 消費税率は10,000倍して記録
CREATE TABLE IF NOT EXISTS consumption_taxes (
    id TEXT NOT NULL,
    begin_dt TEXT NOT NULL,
    end_dt TEXT NOT NULL,
    rate INTEGER NOT NULL,
    CONSTRAINT pk_consumption_taxes PRIMARY KEY (id),
    CONSTRAINT uq_consumption_taxes_begin_dt UNIQUE (begin_dt),
    CONSTRAINT uq_consumption_taxes_end_dt UNIQUE (end_dt),
    CONSTRAINt ck_consumption_taxes_rate CHECK (
        rate >= 0
        AND rate < 10000
    )
);

-- 売上テーブル
-- 割引率は10,000倍して記録
-- 消費税率は10,000倍して記録
CREATE TABLE if NOT EXISTS sales (
    id TEXT NOT NULL,
    customer_id TEXT NULL,
    sold_at TEXT NOT NULL,
    subtotal INTEGER NOT NULL,
    discount_rate INTEGER NOT NULL,
    discount_amount INTEGER NOT NULL,
    taxable_amount INTEGER NOT NULL,
    consumption_tax_rate INTEGER NOT NULL,
    consumption_tax_amount INTEGER NOT NULL,
    total INTEGER NOT NULL,
    CONSTRAINT pk_sales PRIMARY KEY (id),
    CONSTRAINT fk_sales__customers FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_sales_subtotal CHECK (subtotal >= 0),
    CONSTRAINT ck_sales_discount_rate CHECK (discount_rate >= 0),
    CONSTRAINT ck_sales_discount_amount CHECK (discount_amount >= 0),
    CONSTRAINT ck_sales_taxable_amount CHECK (taxable_amount >= 0),
    CONSTRAINT ck_sales_consumption_tax_rate CHECK (
        consumption_tax_rate >= 0
        AND consumption_tax_rate < 10000
    ),
    CONSTRAINT ck_sales_consumption_tax_amount CHECK (consumption_tax_amount >= 0),
    CONSTRAINT ck_sales_total CHECK (total >= 0)
);

-- 売上明細テーブル
CREATE TABLE IF NOT EXISTS sale_details (
    sale_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantities INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    CONSTRAINT pk_sale_details PRIMARY KEY (sale_id, item_id),
    CONSTRAINT fk_sale_details__sales FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sale_details__items FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_sale_details_sale_id_item_id UNIQUE (sale_id, item_id),
    CONSTRAINT ck_sale_details_quantities CHECK (quantities >= 0) CONSTRAINT ck_sale_details_amount CHECK (amount > 0)
);
