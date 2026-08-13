{% test not_null_if(model, column_name, condition_column, condition_value) %}

{#
  Custom generic test: when condition_column equals condition_value,
  column_name must not be null.

  Example: delivered orders must have order_delivered_customer_date.
#}

SELECT *
FROM {{ model }}
WHERE {{ condition_column }} = '{{ condition_value }}'
  AND {{ column_name }} IS NULL

{% endtest %}
