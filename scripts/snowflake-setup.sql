-- Trainer-only Snowflake bootstrap (Olist). Not a student topic.
-- Account used in dry-run: EQWZHBW-CD46277 / ACCOUNTADMIN

USE ROLE ACCOUNTADMIN;

CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE ACCOUNTADMIN;
GRANT OPERATE ON WAREHOUSE COMPUTE_WH TO ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS OLIST_DB;
USE DATABASE OLIST_DB;

CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS ANALYTICS_DEV;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;

USE SCHEMA RAW;

CREATE OR REPLACE TABLE customers (
    customer_id STRING,
    customer_unique_id STRING,
    customer_zip_code_prefix STRING,
    customer_city STRING,
    customer_state STRING
);

CREATE OR REPLACE TABLE orders (
    order_id STRING,
    customer_id STRING,
    order_status STRING,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE OR REPLACE TABLE order_items (
    order_id STRING,
    order_item_id INTEGER,
    product_id STRING,
    seller_id STRING,
    shipping_limit_date TIMESTAMP,
    price NUMBER(10,2),
    freight_value NUMBER(10,2)
);

CREATE OR REPLACE TABLE payments (
    order_id STRING,
    payment_sequential INTEGER,
    payment_type STRING,
    payment_installments INTEGER,
    payment_value NUMBER(10,2)
);

CREATE OR REPLACE TABLE products (
    product_id STRING,
    product_category_name STRING,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

CREATE OR REPLACE FILE FORMAT csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('');

CREATE OR REPLACE STAGE olist_stage
  FILE_FORMAT = csv_format;
