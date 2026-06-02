with source as (
    select * from {{ source('raw', 'orders') }}
)

select
    row_id,
    order_id,
    order_date,
    ship_date,
    date_diff(ship_date, order_date, day)   as days_to_ship,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region,
    product_id,
    category,
    sub_category,
    product_name,
    round(sales, 4)                         as sales,
    quantity,
    round(discount, 4)                      as discount,
    round(profit, 4)                        as profit,
    round(profit / nullif(sales, 0), 4)     as profit_margin
from source
where order_id is not null
