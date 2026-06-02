# Superstore Data Warehouse — Project Plan

## Goal
Build an end-to-end data warehouse portfolio piece using the classic Superstore dataset.
Demonstrates: data ingestion, layered SQL modeling with dbt, and business dashboards — all for free.

---

## Tech Stack (100% Free)

| Layer | Tool | Cost |
|---|---|---|
| Raw data | Superstore CSV (Kaggle) | Free |
| Data warehouse | Google BigQuery (free tier) | Free — 10 GB storage, 1 TB queries/month |
| Transformation | dbt Core (CLI) | Free |
| Dashboards | Looker Studio | Free — shareable public URLs |
| Python loader | Python 3.11 + google-cloud-bigquery | Free |

**Why this stack:**
- BigQuery has a permanent free tier (not a trial) — no credit card surprises
- dbt has a native BigQuery adapter, well-documented and widely used together
- Looker Studio connects to BigQuery natively with zero config — no localhost tunnel needed
- Both BigQuery and Looker Studio are on your resume already (Google ecosystem)
- Dashboard links are shareable URLs — anyone clicking your GitHub can view your live dashboards

---

## Dataset

**Tableau Superstore** — download from Kaggle:
https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

Contains ~9,994 rows across: Orders, Customers, Products, Geography, Shipping.
Fields: Order ID, Order Date, Ship Date, Ship Mode, Customer, Segment, Region,
Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit.

---

## Project Structure

```
superstore-data-warehouse/
├── .gitignore
├── requirements.txt                  # google-cloud-bigquery, pandas, db-dtypes
├── .env.example                      # GCP project ID, dataset names
├── scripts/
│   └── load_data.py                  # CSV → BigQuery raw dataset
├── data/
│   └── superstore.csv                # gitignored — download manually from Kaggle
└── dbt/
    ├── dbt_project.yml
    ├── profiles.yml                  # BigQuery connection config
    └── models/
        ├── staging/                  # 1-to-1 with raw tables, light cleaning only
        │   ├── schema.yml
        │   ├── stg_orders.sql
        │   ├── stg_customers.sql
        │   └── stg_products.sql
        └── marts/                    # business-ready tables for dashboards
            ├── schema.yml
            ├── fct_orders.sql
            ├── dim_customers.sql
            ├── dim_products.sql
            └── dim_geography.sql
```

---

## Execution Phases

### Phase 1 — GCP + Environment Setup (Day 1, ~1.5 hours)

**Google Cloud setup (one-time):**
1. Go to console.cloud.google.com — sign in with your Google account
2. Create a new project: `superstore-dw`
3. Enable the BigQuery API (search "BigQuery API" → Enable)
4. Create a Service Account:
   - IAM & Admin → Service Accounts → Create
   - Role: `BigQuery Admin`
   - Download the JSON key file → save as `gcp-key.json` in project root (gitignored)
5. Create two BigQuery datasets in the UI:
   - `raw` — for the loaded CSV
   - `dbt_superstore` — for dbt output models

**Local environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dbt-bigquery google-cloud-bigquery pandas db-dtypes python-dotenv
```

**Verify dbt connects:**
```bash
cd dbt
dbt debug    # should show "All checks passed"
```

---

### Phase 2 — Data Ingestion (Day 1–2, ~1 hour)

1. Download `superstore.csv` from Kaggle, place in `data/`
2. Run `scripts/load_data.py`:
   - Reads CSV with pandas
   - Normalizes column names to snake_case
   - Loads into BigQuery table `raw.orders`
3. Verify in BigQuery console:
   ```sql
   SELECT COUNT(*) FROM `superstore-dw.raw.orders`;  -- expect 9,994
   ```

The loader script handles:
- Date parsing (Order Date, Ship Date → DATE type)
- Numeric types (Sales, Profit, Discount → FLOAT64)
- Encoding issues in product names

---

### Phase 3 — dbt Modeling (Days 2–5, ~4–6 hours)

**Layer 1 — Staging** (clean and rename, no business logic):
- `stg_orders` — cast types, rename to snake_case, parse dates, filter nulls
- `stg_customers` — deduplicate customers extracted from orders
- `stg_products` — deduplicate products, expose category/sub-category

**Layer 2 — Marts** (business-ready, joins and aggregations):
- `fct_orders` — one row per order line item, all metrics (sales, profit, discount, quantity, days_to_ship)
- `dim_customers` — one row per customer, segment, first/last order date, lifetime value
- `dim_products` — product catalog with category hierarchy
- `dim_geography` — city/state/region/country lookup

**Key dbt commands:**
```bash
dbt run           # build all models in BigQuery
dbt test          # run data quality tests
dbt docs generate # build lineage documentation
dbt docs serve    # open lineage graph in browser (great for README screenshot)
```

**Tests to include in schema.yml:**
- `not_null` + `unique` on all primary keys
- `accepted_values` — segment (Consumer/Corporate/Home Office), region, ship_mode
- `relationships` — fct_orders references dim_customers, dim_products, dim_geography
- `dbt_utils.expression_is_true` — profit can be negative, sales must be > 0

---

### Phase 4 — Dashboards in Looker Studio (Days 5–7, ~3–4 hours)

Go to lookerstudio.google.com → Create → Data Source → BigQuery.
Connect to your `dbt_superstore` dataset. Build 3 dashboards (can be pages in one report).

**Dashboard 1 — Sales Overview**
- Total Sales, Total Profit, Profit Margin %, Total Orders (scorecard KPIs)
- Monthly Sales Trend (time series line chart)
- Sales by Region (bar chart)
- Profit by Category (bar chart — shows which categories lose money)

**Dashboard 2 — Product Performance**
- Top 10 Sub-Categories by Revenue (horizontal bar)
- Discount vs. Profit relationship (scatter plot — shows discounting hurts profit)
- Products with Negative Profit (table — the "loss leaders" story)
- Sales vs. Profit by Category (combo chart)

**Dashboard 3 — Customer Segments**
- Revenue breakdown by Segment: Consumer / Corporate / Home Office (pie + bar)
- Top 20 Customers by Lifetime Value (table)
- Segment Profitability over Time (line chart)
- Average Order Value by Segment (scorecard)

**Portfolio tip:** Make the report publicly viewable (Share → Manage access → Anyone with link can view).
Paste the URL in your GitHub README — hiring managers can explore it live.

---

### Phase 5 — Portfolio Polish (Days 7–10, ~2 hours)

1. Take screenshots of each dashboard for the README
2. Run `dbt docs generate` and screenshot the lineage graph
3. Write `README.md`:
   - 2-sentence project summary
   - Architecture diagram (ASCII is fine)
   - Live dashboard link (Looker Studio public URL)
   - How to reproduce locally (5–6 commands)
   - Key insights found in the data (2–3 bullet points)
4. Confirm `.gitignore` covers: `data/`, `gcp-key.json`, `.env`, `.venv/`
5. Push to GitHub

---

## Data Flow Summary

```
superstore.csv
     │
     ▼  (scripts/load_data.py)
BigQuery: raw.orders
     │
     ▼  (dbt staging layer)
BigQuery: dbt_superstore.stg_orders
          dbt_superstore.stg_customers
          dbt_superstore.stg_products
     │
     ▼  (dbt marts layer)
BigQuery: dbt_superstore.fct_orders
          dbt_superstore.dim_customers
          dbt_superstore.dim_products
          dbt_superstore.dim_geography
     │
     ▼  (Looker Studio native connector)
Public Dashboard: Sales / Products / Customers
```

---

## Timeline

| Phase | Days | Output |
|---|---|---|
| GCP + Environment Setup | Day 1 | BigQuery datasets created, dbt connected |
| Data Ingestion | Day 1–2 | 9,994 rows loaded into BigQuery raw.orders |
| dbt Modeling | Day 2–5 | 7 models built + tested, lineage graph viewable |
| Dashboards | Day 5–7 | 3-page Looker Studio report, public URL |
| Portfolio Polish | Day 7–10 | README with screenshots and live link, pushed to GitHub |

**Total: 1–2 weeks part-time (~12–15 hours of actual work)**

---

## What This Demonstrates to Employers

- **ELT pipeline design** — raw ingestion → staging → marts (industry standard layering)
- **dbt proficiency** — models, tests, documentation, lineage graph
- **BigQuery** — cloud data warehouse, a top skill in modern data roles
- **SQL data modeling** — fact/dimension schema design
- **Looker Studio** — dashboard and reporting skills you already have
- **Python** — data loading and transformation scripting
- **Git hygiene** — clean repo, nothing sensitive committed, clear README
