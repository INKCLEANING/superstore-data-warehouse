# Superstore Data Warehouse

End-to-end data warehouse and analytics project built on the classic Tableau Superstore dataset.
Demonstrates ELT pipeline design, layered dbt modeling, data quality testing, and business dashboards.

**[View Live Dashboard →](ADD_LOOKER_STUDIO_URL_HERE)**

---

## Architecture

```
superstore.csv  (Kaggle)
      │
      ▼  Python loader (scripts/load_data.py)
BigQuery: raw.orders  (9,994 rows)
      │
      ▼  dbt staging layer  (views)
BigQuery: dbt_superstore_staging
      ├── stg_orders
      ├── stg_customers
      └── stg_products
      │
      ▼  dbt marts layer  (tables)
BigQuery: dbt_superstore_marts
      ├── fct_orders       (10k rows — one per order line item)
      ├── dim_customers    (793 customers)
      ├── dim_products     (1,894 products)
      └── dim_geography    (632 locations)
      │
      ▼  Looker Studio (native BigQuery connector)
Dashboards: Sales Overview · Product Performance · Customer Segments
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data warehouse | Google BigQuery (free tier) |
| Transformation | dbt Core 1.8 |
| Dashboards | Looker Studio |
| Data ingestion | Python 3.9 + google-cloud-bigquery |
| Dataset | Tableau Superstore (Kaggle) |

---

## dbt Models

### Staging Layer — `dbt_superstore_staging`

Views that sit directly on top of raw data. No business logic — only cleaning and renaming.

| Model | Description |
|---|---|
| `stg_orders` | Cleaned order line items. Casts types, normalizes column names to snake_case, derives `days_to_ship` and `profit_margin`. |
| `stg_customers` | Deduplicated customer list with segment, extracted from the orders table. |
| `stg_products` | Deduplicated product catalog with category and sub-category hierarchy. |

### Marts Layer — `dbt_superstore_marts`

Materialized tables ready for dashboards and ad-hoc analysis.

| Model | Rows | Description |
|---|---|---|
| `fct_orders` | 9,994 | One row per order line item. Contains all measures (sales, profit, discount, quantity) and foreign keys to all dimensions. |
| `dim_customers` | 793 | One row per customer with segment, first/last order dates, lifetime sales, and lifetime profit. |
| `dim_products` | 1,894 | One row per product with category hierarchy, total units sold, and aggregate profit. |
| `dim_geography` | 632 | Unique city/state/region/country combinations. |

### Data Quality Tests

27 tests run on every `dbt test` execution — all passing.

| Test type | Count | Examples |
|---|---|---|
| `not_null` | 11 | All primary keys, sales, profit |
| `unique` | 7 | `row_id`, `customer_id`, `product_id` |
| `accepted_values` | 5 | segment, region, ship_mode |
| `relationships` | 2 | fct_orders → dim_customers, dim_products |

---

## How to Run Locally

**Prerequisites:** Python 3.9+, a Google Cloud account, BigQuery API enabled.

```bash
# 1. Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/superstore-data-warehouse
cd superstore-data-warehouse
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Add credentials
cp .env.example .env
# Fill in GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS in .env

# 3. Download dataset
kaggle datasets download -d vivek468/superstore-dataset-final -p data/ --unzip
mv "data/Sample - Superstore.csv" data/superstore.csv

# 4. Load raw data into BigQuery
python scripts/load_data.py

# 5. Run dbt models and tests
cd dbt
dbt run
dbt test

# 6. View model lineage docs
dbt docs generate && dbt docs serve
```

---

## Key Insights

- **Discounting hurts**: orders with a discount > 20% have a negative average profit margin — the deeper the discount, the worse the outcome
- **Technology leads revenue but Furniture leads losses**: the Furniture category, specifically Tables, is the biggest profit drain in the product catalog
- **The West region drives the most revenue** but the Central region has the lowest profit margins
- **Consumer segment** accounts for ~51% of revenue but Corporate has higher average order value

---

## Project Structure

```
superstore-data-warehouse/
├── scripts/
│   └── load_data.py          # CSV → BigQuery raw.orders
├── data/                     # gitignored — download via kaggle CLI
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/          # stg_orders, stg_customers, stg_products
│       └── marts/            # fct_orders, dim_customers, dim_products, dim_geography
├── requirements.txt
├── .env.example
└── plan.md
```
