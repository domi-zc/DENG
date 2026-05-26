import logging

from src.fetch_data import DataFetcher
from src.pipeline_utils import PipelineUtils
from src.transform_data import Transformer
from src.write_to_postgresql import PostgreSQLWriter


class LocalPipeline:
    """Fetch the source dataset, clean it, and write it to the local PostgreSQL database."""

    DATASET_URL = "https://epoch.ai/data/gpu_clusters.zip"
    CSV_FILENAME = "gpu_clusters.csv"
    REQUIRED_ENV_VARS = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME", "LOCAL_DB_TABLE")

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Configure logging, load the environment, and construct collaborators."""
        self.utils = PipelineUtils()
        self.utils.configure_logging()
        self.environment = self.utils.get_environment_variables(self.REQUIRED_ENV_VARS)
        self.fetcher = DataFetcher()
        self.transformer = Transformer()
        self.writer = PostgreSQLWriter(self.build_engine_url(self.environment))

    def build_engine_url(self, environment: dict[str, str]) -> str:
        """Compose the SQLAlchemy URL from validated environment variables."""
        return (
            f"postgresql://{environment['DB_USER']}:{environment['DB_PASSWORD']}"
            f"@{environment['DB_HOST']}:{environment['DB_PORT']}/{environment['DB_NAME']}"
        )

    def run(self) -> None:
        """Execute the local pipeline."""
        target_table = self.environment["LOCAL_DB_TABLE"]

        raw_csv = self.fetcher.fetch_csv_from_url(self.DATASET_URL, self.CSV_FILENAME)
        df = self.fetcher.load_dataframe(raw_csv)
        df = self.transformer.clean(df)

        self.writer.write_dataframe(df, target_table)
        self.logger.info("Local pipeline completed successfully")

def main() -> None:
    LocalPipeline().run()


if __name__ == "__main__":
    main()
