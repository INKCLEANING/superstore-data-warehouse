with source as (
    select * from {{ source('raw', 'orders') }}
),

deduped as (
    select
        product_id,
        product_name,
        category,
        sub_category,
        row_number() over (partition by product_id order by order_date asc) as rn
    from source
    where product_id is not null
)

select
    product_id,
    product_name,
    category,
    sub_category
from deduped
where rn = 1
