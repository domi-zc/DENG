import logging

from src.fetch_data import DataFetcher
from src.pipeline_utils import PipelineUtils
from src.write_to_data_lake import DataLakeWriter


class DataLakeIngestion:
    """Download the source ZIP, extract the CSV, and upload it to the data lake."""

    DATASET_URL = "https://epoch.ai/data/gpu_clusters.zip"
    CSV_FILENAME = "gpu_clusters.csv"
    LAKE_OBJECT_PATH = "raw/gpu_clusters/gpu_clusters.csv"
    REQUIRED_ENV_VARS = ("GCS_BUCKET",)

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Configure logging, load the environment, and construct collaborators."""
        self.utils = PipelineUtils()
        self.utils.configure_logging()
        environment = self.utils.get_environment_variables(self.REQUIRED_ENV_VARS)
        self.fetcher = DataFetcher()
        self.writer = DataLakeWriter(environment["GCS_BUCKET"])

    def run(self) -> str:
        """Execute the ingestion pipeline and return the resulting gs:// URI."""
        self.logger.info("Starting data lake ingestion")

        raw_csv = self.fetcher.fetch_csv_from_url(self.DATASET_URL, self.CSV_FILENAME)
        uri = self.writer.upload_bytes(self.LAKE_OBJECT_PATH, raw_csv)

        self.logger.info(f"Data lake ingestion completed: {uri}")
        return uri

def main() -> None:
    DataLakeIngestion().run()

if __name__ == "__main__":
    main()
