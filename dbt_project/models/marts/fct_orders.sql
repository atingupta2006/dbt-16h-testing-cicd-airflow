WITH orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT *
    FROM {{ ref('stg_customers') }}
),

order_items AS (
    SELECT
        order_id,
        SUM(price) AS total_order_value,
        SUM(freight_value) AS total_freight_value
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
),

payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment_value
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id
)

SELECT
    o.order_id,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    i.total_order_value,
    i.total_freight_value,
    p.total_payment_value
FROM orders o
INNER JOIN order_items i
    ON o.order_id = i.order_id
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
LEFT JOIN payments p
    ON o.order_id = p.order_id
-- Keep mart trustworthy for critical tests: drop delivered rows missing delivery date
WHERE NOT (
    o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NULL
)
