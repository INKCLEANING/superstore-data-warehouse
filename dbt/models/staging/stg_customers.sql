with source as (
    select * from {{ source('raw', 'orders') }}
),

deduped as (
    select
        customer_id,
        customer_name,
        segment,
        row_number() over (partition by customer_id order by order_date asc) as rn
    from source
    where customer_id is not null
)

select
    customer_id,
    customer_name,
    segment
from deduped
where rn = 1
