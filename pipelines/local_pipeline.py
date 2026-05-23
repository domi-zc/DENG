"""Local pipeline: download source data, clean it, and load it into the local PostgreSQL database."""

import logging
import os
import sys

from dotenv import load_dotenv

from src.fetch_data import DataFetcher
from src.transform_data import Transformer
from src.write_to_postgresql import PostgreSQLWriter


class LocalPipeline:
    """Fetch the source dataset, clean it, and write it to the local PostgreSQL database."""

    DATASET_URL = "https://epoch.ai/data/gpu_clusters.zip"
    CSV_FILENAME = "gpu_clusters.csv"
    TARGET_TABLE = "gpu_clusters_cleaned"
    REQUIRED_ENV_VARS = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Configure logging, load the environment, and construct collaborators."""
        self.configure_logging()
        environment = self.get_environment_variables()
        self.fetcher = DataFetcher()
        self.transformer = Transformer()
        self.writer = PostgreSQLWriter(self.build_engine_url(environment))

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
        environment = {var: os.environ.get(var, "") for var in self.REQUIRED_ENV_VARS}
        missing_vars = [name for name, value in environment.items() if not value]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
        return environment

    def build_engine_url(self, environment: dict[str, str]) -> str:
        """Compose the SQLAlchemy URL from validated environment variables."""
        return (
            f"postgresql://{environment['DB_USER']}:{environment['DB_PASSWORD']}"
            f"@{environment['DB_HOST']}:{environment['DB_PORT']}/{environment['DB_NAME']}"
        )

    def run(self) -> None:
        """Execute the local pipeline."""
        raw_csv = self.fetcher.fetch_csv_from_url(self.DATASET_URL, self.CSV_FILENAME)
        df = self.fetcher.load_dataframe(raw_csv)
        df = self.transformer.clean(df)

        self.writer.write_dataframe(df, self.TARGET_TABLE)
        self.logger.info("Local pipeline completed successfully")

def main() -> None:
    LocalPipeline().run()


if __name__ == "__main__":
    main()
