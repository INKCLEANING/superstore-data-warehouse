with source as (
    select distinct
        postal_code,
        city,
        state,
        region,
        country
    from {{ ref('stg_orders') }}
    where postal_code is not null
)

select * from source
