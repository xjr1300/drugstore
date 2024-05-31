-- 売上と売上明細テーブルに行を挿入
-- 売上1: 徳川家康
INSERT INTO
    sales (
        id,
        customer_id,
        sold_at,
        subtotal,
        discount_rate,
        discount_amount,
        taxable_amount,
        consumption_tax_rate,
        consumption_tax_amount,
        total
    )
VALUES
    (
        '08dcad6d-5abd-4d49-9742-e91af99aeace',
        'a67cd437-50fd-4667-a54e-5a5f09025359',
        '2024-05-31T14:34:11+09:00',
        1100,
        500,
        55,
        1045,
        1000,
        104,
        1149
    );

-- 売上1: 正露丸
INSERT INTO
    sale_details (sale_id, item_id, quantities, amount)
VALUES
    (
        '08dcad6d-5abd-4d49-9742-e91af99aeace',
        '6e0d4fbe-cafe-4af7-bc95-a564b5029322',
        2,
        600
    );

-- 売上1: バファリン
INSERT INTO
    sale_details (sale_id, item_id, quantities, amount)
VALUES
    (
        '08dcad6d-5abd-4d49-9742-e91af99aeace',
        '0734980b-ca7e-4bf4-81df-39ac95920ce0',
        1,
        500
    );

-- 売上2: 徳川慶喜
INSERT INTO
    sales (
        id,
        customer_id,
        sold_at,
        subtotal,
        discount_rate,
        discount_amount,
        taxable_amount,
        consumption_tax_rate,
        consumption_tax_amount,
        total
    )
VALUES
    (
        'a16cbeba-f3cc-482a-9d41-194bd0a5f14a',
        '830f842f-4822-4f73-adf8-3243c71ca0a7',
        '2024-06-01T09:32:02+09:00',
        4100,
        2000,
        820,
        3280,
        1000,
        328,
        3608
    );

-- 売上2: バファリン
INSERT INTO
    sale_details (sale_id, item_id, quantities, amount)
VALUES
    (
        'a16cbeba-f3cc-482a-9d41-194bd0a5f14a',
        '0734980b-ca7e-4bf4-81df-39ac95920ce0',
        3,
        1500
    );

-- 売上2: 太田胃酸
INSERT INTO
    sale_details (sale_id, item_id, quantities, amount)
VALUES
    (
        'a16cbeba-f3cc-482a-9d41-194bd0a5f14a',
        'ef2d7dab-02e7-4680-8e8e-55070f695d8b',
        2,
        2000
    );

-- 売上2: 正露丸
INSERT INTO
    sale_details (sale_id, item_id, quantities, amount)
VALUES
    (
        'a16cbeba-f3cc-482a-9d41-194bd0a5f14a',
        '6e0d4fbe-cafe-4af7-bc95-a564b5029322',
        2,
        600
    );
