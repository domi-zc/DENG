import logging
import os
import sys

from dotenv import load_dotenv


class PipelineUtils:
    """Shared helpers for configuring logging and validating environment variables."""

    LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

    logger = logging.getLogger(__name__)

    def configure_logging(self) -> None:
        """Load .env and force INFO logging to stdout for Kestra."""
        load_dotenv()
        logging.basicConfig(
            level=logging.INFO,
            format=self.LOG_FORMAT,
            stream=sys.stdout,
        )

    def get_environment_variables(self, required_vars: tuple[str, ...]) -> dict[str, str]:
        """Validate and return all required environment variables as a dictionary."""
        if not required_vars:
            raise ValueError("required_vars must not be empty")
        environment = {name: os.environ.get(name, "") for name in required_vars}
        missing = [name for name, value in environment.items() if not value]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {missing}")
        return environment
