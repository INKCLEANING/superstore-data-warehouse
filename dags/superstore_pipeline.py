from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    dag_id="superstore_pipeline",
    default_args=default_args,
    description="Load Superstore CSV into BigQuery and run dbt transformations",
    schedule_interval="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["superstore", "dbt", "bigquery"],
) as dag:

    def run_load_data():
        import sys
        sys.path.insert(0, "/opt/airflow/scripts")
        from load_data import main
        main()

    load_data = PythonOperator(
        task_id="load_data",
        python_callable=run_load_data,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir /opt/airflow/dbt",
    )

    load_data >> dbt_run >> dbt_test
