import logging
import os
import sys

from dotenv import load_dotenv

from src.fetch_data import DataFetcher
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
        self.configure_logging()
        environment = self.get_environment_variables()
        self.fetcher = DataFetcher()
        self.writer = DataLakeWriter(environment["GCS_BUCKET"])

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
