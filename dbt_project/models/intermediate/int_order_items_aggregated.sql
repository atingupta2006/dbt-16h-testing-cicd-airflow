SELECT
    order_id,
    SUM(price) AS total_order_value,
    SUM(freight_value) AS total_freight_value
FROM {{ ref('stg_order_items') }}
GROUP BY order_id
