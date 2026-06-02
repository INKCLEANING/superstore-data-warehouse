with customers as (
    select * from {{ ref('stg_customers') }}
),

order_stats as (
    select
        customer_id,
        min(order_date)         as first_order_date,
        max(order_date)         as last_order_date,
        count(distinct order_id) as total_orders,
        round(sum(sales), 2)    as lifetime_sales,
        round(sum(profit), 2)   as lifetime_profit
    from {{ ref('stg_orders') }}
    group by customer_id
)

select
    c.customer_id,
    c.customer_name,
    c.segment,
    s.first_order_date,
    s.last_order_date,
    s.total_orders,
    s.lifetime_sales,
    s.lifetime_profit,
    round(s.lifetime_profit / nullif(s.lifetime_sales, 0), 4) as lifetime_margin
from customers c
left join order_stats s using (customer_id)
