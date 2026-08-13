SELECT
    order_id,
    SUM(payment_value) AS total_payment_value
FROM {{ ref('stg_payments') }}
GROUP BY order_id
