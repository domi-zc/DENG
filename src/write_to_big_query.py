import logging

import pandas as pd
from google.api_core.exceptions import GoogleAPIError
from google.cloud import bigquery


class BigQueryWriter:
    """Load DataFrames into BigQuery with clustering."""

    DEFAULT_LOCATION = "europe-west6"
    WRITE_DISPOSITION = bigquery.WriteDisposition.WRITE_TRUNCATE

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

    def load_dataframe(
        self,
        df: pd.DataFrame,
        *,
        table: str,
        cluster_fields: list[str],
    ) -> str:
        """Replace a BigQuery table with the DataFrame, applying clustering."""
        if df is None or df.empty:
            raise ValueError("Input DataFrame must not be empty")
        if not table:
            raise ValueError("table must be a non-empty string")
        if not cluster_fields:
            raise ValueError("cluster_fields must contain at least one column name")

        client = self.get_client()
        table_id = f"{self.project}.{self.dataset}.{table}"


        job_config = bigquery.LoadJobConfig(
            write_disposition=self.WRITE_DISPOSITION,
            clustering_fields=list(cluster_fields),
        )

        # Load to BigQuery table
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

    def get_client(self) -> bigquery.Client:
        """Return a cached BigQuery client, creating it on first use."""
        if self.client is None:
            self.client = bigquery.Client(project=self.project, location=self.location)
        return self.client
