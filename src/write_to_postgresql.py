import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


class PostgreSQLWriter:
    """Write DataFrames into a local PostgreSQL table, replacing the target on each run."""

    logger = logging.getLogger(__name__)

    def __init__(self, engine_url: str) -> None:
        """Store the SQLAlchemy URL used for every write."""
        if not engine_url:
            raise ValueError("engine_url must be a non-empty string")
        self.engine_url = engine_url

    def write_dataframe(self, df: pd.DataFrame, table_name: str) -> None:
        """Replace a PostgreSQL table with the contents of the DataFrame."""
        if df is None or df.empty:
            raise ValueError("Input DataFrame must not be empty")
        if not table_name:
            raise ValueError("table_name must be a non-empty string")

        self.logger.info(f"Writing {len(df)} rows to PostgreSQL table {table_name}")
        engine = create_engine(self.engine_url)

        try:
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
            )
        except SQLAlchemyError as error:
            raise RuntimeError(
                f"Failed to write to PostgreSQL table {table_name}: {error}"
            ) from error
        finally:
            engine.dispose()

        self.logger.info(f"Successfully wrote {len(df)} rows to {table_name}")
