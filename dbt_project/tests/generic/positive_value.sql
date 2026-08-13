{% test positive_value(model, column_name) %}

{#
  Custom generic test: column must be > 0 for all non-null rows.
  Nulls are ignored here; pair with not_null when nulls are invalid.
#}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} <= 0

{% endtest %}
