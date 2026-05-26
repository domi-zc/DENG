import io
import logging
import zipfile

import pandas as pd
import requests

class DataFetcher:
    """Download a ZIP from a URL and parse the contained CSV into a DataFrame."""

    DEFAULT_HTTP_TIMEOUT_SECONDS = 60

    logger = logging.getLogger(__name__)

    def __init__(self, http_timeout_seconds: int = DEFAULT_HTTP_TIMEOUT_SECONDS) -> None:
        """Store the HTTP timeout."""
        if http_timeout_seconds <= 0:
            raise ValueError("http_timeout_seconds must be positive")
        self.http_timeout_seconds = http_timeout_seconds

    def fetch_csv_from_url(self, url: str, file_name: str) -> bytes:
        """Download a ZIP from a URL and return the bytes of the named CSV member."""
        if not url:
            raise ValueError("url must be a non-empty string")
        if not file_name:
            raise ValueError("file_name must be a non-empty string")

        self.logger.info(f"Downloading ZIP from {url}")
        response = requests.get(url, timeout=self.http_timeout_seconds)
        response.raise_for_status()

        if not response.content:
            raise ValueError(f"Empty response body from {url}")

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            available_files = archive.namelist()
            if file_name not in available_files:
                raise FileNotFoundError(
                    f"{file_name} not found in ZIP; available files: {available_files}"
                )
            csv_bytes = archive.read(file_name)

        self.logger.info(f"Fetched {file_name} ({len(csv_bytes)} bytes) from {url}")
        return csv_bytes

    def load_dataframe(self, csv_bytes: bytes) -> pd.DataFrame:
        """Parse CSV bytes into a pandas DataFrame."""
        if not csv_bytes:
            raise ValueError("csv_bytes must not be empty")

        df = pd.read_csv(io.BytesIO(csv_bytes))
        if df.empty:
            raise ValueError("Parsed DataFrame is empty")

        self.logger.info(f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df
