import logging

from src.fetch_from_gcs import GCSFetcher
from src.pipeline_utils import PipelineUtils
from src.transform_data import Transformer
from src.write_to_big_query import BigQueryWriter

class DataWarehouseTransformation:
    """Read the lake CSV, transform it, and replace the BigQuery analytics table."""

    LAKE_OBJECT_PATH = "raw/gpu_clusters/gpu_clusters.csv"
    CLUSTER_FIELDS = ["country"]
    REQUIRED_ENV_VARS = ("GCS_BUCKET", "GCP_PROJECT_ID", "BQ_DATASET", "BQ_TABLE")

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Configure logging, load the environment, and construct collaborators."""
        self.utils = PipelineUtils()
        self.utils.configure_logging()
        environment = self.utils.get_environment_variables(self.REQUIRED_ENV_VARS)
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

        raw_csv = self.fetcher.download_csv(self.bucket_name, self.LAKE_OBJECT_PATH)
        df = self.fetcher.load_dataframe(raw_csv)
        df = self.transformer.clean(df)

        table_id = self.writer.load_dataframe(
            df,
            table=self.table,
            cluster_fields=self.CLUSTER_FIELDS,
        )

        self.logger.info(f"Warehouse transformation completed: {table_id}")
        return table_id

def main() -> None:
    DataWarehouseTransformation().run()

if __name__ == "__main__":
    main()
