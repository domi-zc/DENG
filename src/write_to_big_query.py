import logging

import pandas as pd
from google.api_core.exceptions import GoogleAPIError
from google.cloud import bigquery


class BigQueryWriter:
    """Load DataFrames into BigQuery with an explicit schema, year partitioning, and clustering."""

    DEFAULT_LOCATION = "europe-west6"
    WRITE_DISPOSITION = bigquery.WriteDisposition.WRITE_TRUNCATE

    TABLE_SCHEMA = [
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("owner", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("power_capacity_mw", "FLOAT"),
        bigquery.SchemaField("first_operational_date", "DATE"),
        bigquery.SchemaField("calculated_cost", "FLOAT"),
        bigquery.SchemaField("reported_cost", "FLOAT"),
        bigquery.SchemaField("reported_cost_inflation_adjusted", "FLOAT"),
        bigquery.SchemaField("hardware_cost", "FLOAT"),
        bigquery.SchemaField("chip_type_primary", "STRING"),
        bigquery.SchemaField("chip_quantity_primary", "INTEGER"),
        bigquery.SchemaField("chip_type_secondary", "STRING"),
        bigquery.SchemaField("chip_quantity_secondary", "INTEGER"),
        bigquery.SchemaField("total_number_of_ai_chips", "INTEGER"),
        bigquery.SchemaField("energy_efficiency", "FLOAT"),
        bigquery.SchemaField("max_ops", "FLOAT"),
        bigquery.SchemaField("8bit_ops", "FLOAT"),
        bigquery.SchemaField("16bit_ops", "FLOAT"),
        bigquery.SchemaField("32bit_ops",  "FLOAT"),
    ]

    PARTITION_CONFIG = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.YEAR,
        field="first_operational_date",
    )

    logger = logging.getLogger(__name__)

    def __init__(self, project: str, dataset: str, location: str = DEFAULT_LOCATION) -> None:
        """Store target project, dataset, and location for every load."""
        if not project:
            raise ValueError("project must be a non-empty string")
        if not dataset:
            raise ValueError("dataset must be a non-empty string")
        if not location:
            raise ValueError("location must be a non-empty string")

        self.project = project
        self.dataset = dataset
        self.location = location
        self.client: bigquery.Client | None = None

    def get_client(self) -> bigquery.Client:
        """Return a cached BigQuery client, creating it on first use."""
        if self.client is None:
            self.client = bigquery.Client(project=self.project, location=self.location)
        return self.client

    def load_dataframe(
        self,
        df: pd.DataFrame,
        *,
        table: str,
        cluster_fields: list[str],
    ) -> str:
        """Ensure the table exists then replace its data with the DataFrame."""
        if df is None or df.empty:
            raise ValueError("Input DataFrame must not be empty")
        if not table:
            raise ValueError("table must be a non-empty string")
        if not cluster_fields:
            raise ValueError("cluster_fields must contain at least one column name")

        client = self.get_client()
        table_id = f"{self.project}.{self.dataset}.{table}"

        bq_table = bigquery.Table(table_id, schema=self.TABLE_SCHEMA)
        bq_table.time_partitioning = self.PARTITION_CONFIG
        bq_table.clustering_fields = list(cluster_fields)
        client.create_table(bq_table, exists_ok=True)

        job_config = bigquery.LoadJobConfig(
            schema=self.TABLE_SCHEMA,
            time_partitioning=self.PARTITION_CONFIG,
            write_disposition=self.WRITE_DISPOSITION,
            clustering_fields=list(cluster_fields),
        )

        self.logger.info(f"Loading {len(df)} rows into BigQuery table {table_id}")

        try:
            load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
            load_job.result()
        except GoogleAPIError as error:
            raise RuntimeError(f"BigQuery load job failed for {table_id}: {error}") from error

        if load_job.errors:
            raise RuntimeError(
                f"BigQuery load job reported errors for {table_id}: {load_job.errors}"
            )

        self.logger.info(f"Loaded {load_job.output_rows} rows into {table_id}")
        return table_id
