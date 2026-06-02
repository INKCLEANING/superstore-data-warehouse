import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
RAW_DATASET = os.environ.get("BQ_RAW_DATASET", "raw")
LOCATION = os.environ.get("BQ_LOCATION", "US")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "superstore.csv")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )
    return df


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=False).dt.date
    df["ship_date"] = pd.to_datetime(df["ship_date"], dayfirst=False).dt.date
    df["sales"] = df["sales"].astype(float)
    df["profit"] = df["profit"].astype(float)
    df["discount"] = df["discount"].astype(float)
    df["quantity"] = df["quantity"].astype(int)
    df["postal_code"] = df["postal_code"].astype(str)
    return df


def load_to_bigquery(df: pd.DataFrame, client: bigquery.Client) -> None:
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.orders"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=[
            bigquery.SchemaField("row_id", "INTEGER"),
            bigquery.SchemaField("order_id", "STRING"),
            bigquery.SchemaField("order_date", "DATE"),
            bigquery.SchemaField("ship_date", "DATE"),
            bigquery.SchemaField("ship_mode", "STRING"),
            bigquery.SchemaField("customer_id", "STRING"),
            bigquery.SchemaField("customer_name", "STRING"),
            bigquery.SchemaField("segment", "STRING"),
            bigquery.SchemaField("country", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("state", "STRING"),
            bigquery.SchemaField("postal_code", "STRING"),
            bigquery.SchemaField("region", "STRING"),
            bigquery.SchemaField("product_id", "STRING"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("sub_category", "STRING"),
            bigquery.SchemaField("product_name", "STRING"),
            bigquery.SchemaField("sales", "FLOAT64"),
            bigquery.SchemaField("quantity", "INTEGER"),
            bigquery.SchemaField("discount", "FLOAT64"),
            bigquery.SchemaField("profit", "FLOAT64"),
        ],
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df):,} rows into {table_id}")


def main():
    print(f"Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, encoding="windows-1252")

    df = normalize_columns(df)
    df = cast_types(df)

    print(f"Rows: {len(df):,} | Columns: {list(df.columns)}")

    client = bigquery.Client(project=PROJECT_ID)
    load_to_bigquery(df, client)
    print("Done.")


if __name__ == "__main__":
    main()
