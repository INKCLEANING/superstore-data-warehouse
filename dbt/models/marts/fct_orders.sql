with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

geography as (
    select * from {{ ref('dim_geography') }}
)

select
    o.row_id,
    o.order_id,
    o.order_date,
    o.ship_date,
    o.days_to_ship,
    o.ship_mode,

    -- customer dims
    o.customer_id,
    c.customer_name,
    c.segment,

    -- product dims
    o.product_id,
    p.product_name,
    p.category,
    p.sub_category,

    -- geography dims
    o.postal_code,
    g.city,
    g.state,
    g.region,
    g.country,

    -- measures
    o.sales,
    o.quantity,
    o.discount,
    o.profit,
    o.profit_margin

from orders o
left join customers c using (customer_id)
left join products p using (product_id)
left join geography g using (postal_code, city, state)
