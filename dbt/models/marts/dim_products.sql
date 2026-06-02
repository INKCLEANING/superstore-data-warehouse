with products as (
    select * from {{ ref('stg_products') }}
),

order_stats as (
    select
        product_id,
        count(distinct order_id)    as total_orders,
        sum(quantity)               as total_units_sold,
        round(sum(sales), 2)        as total_sales,
        round(sum(profit), 2)       as total_profit
    from {{ ref('stg_orders') }}
    group by product_id
)

select
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    s.total_orders,
    s.total_units_sold,
    s.total_sales,
    s.total_profit,
    round(s.total_profit / nullif(s.total_sales, 0), 4) as profit_margin
from products p
left join order_stats s using (product_id)
