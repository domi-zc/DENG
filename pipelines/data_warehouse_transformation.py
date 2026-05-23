"""Warehouse transformation: read the lake CSV, clean it, and load it into BigQuery."""

import logging
import os
import sys

from dotenv import load_dotenv

from src.fetch_from_gcs import GCSFetcher
from src.transform_data import Transformer
from src.write_to_big_query import BigQueryWriter


class DataWarehouseTransformation:
    """Read the lake CSV, transform it, and replace the BigQuery analytics table."""

    LAKE_OBJECT_PATH = "raw/gpu_clusters/gpu_clusters.csv"
    CLUSTER_FIELDS = ["country", "owner"]
    REQUIRED_ENV_VARS = ("GCS_BUCKET", "GCP_PROJECT_ID", "BQ_DATASET", "BQ_TABLE")

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Configure logging, load the environment, and construct collaborators."""
        self.configure_logging()
        environment = self.get_environment_variables()
        self.bucket_name = environment["GCS_BUCKET"]
        self.table = environment["BQ_TABLE"]
        self.fetcher = GCSFetcher()
        self.transformer = Transformer()
        self.writer = BigQueryWriter(
            project=environment["GCP_PROJECT_ID"],
            dataset=environment["BQ_DATASET"],
        )

    def run(self) -> str:
        """Execute the warehouse transformation and return the loaded BigQuery table id."""
        self.logger.info("Starting warehouse transformation")

        # Fetch the CSV from the GCS bucket and clean it
        raw_csv = self.fetcher.download_csv(self.bucket_name, self.LAKE_OBJECT_PATH)
        df = self.fetcher.load_dataframe(raw_csv)
        df = self.transformer.clean(df)


        # Load into Google BigQuery
        table_id = self.writer.load_dataframe(
            df,
            table=self.table,
            cluster_fields=self.CLUSTER_FIELDS,
        )

        self.logger.info(f"Warehouse transformation completed: {table_id}")
        return table_id

    def configure_logging(self) -> None:
        """Force INFO logging to stdout for Kestra."""
        load_dotenv()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            stream=sys.stdout,
        )

    def get_environment_variables(self) -> dict[str, str]:
        """Validate and return all required environment variables as a dictionary."""
        environment = {name: os.environ.get(name, "") for name in self.REQUIRED_ENV_VARS}
        missing = [name for name, value in environment.items() if not value]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {missing}")
        return environment


def main() -> None:
    DataWarehouseTransformation().run()


if __name__ == "__main__":
    main()
