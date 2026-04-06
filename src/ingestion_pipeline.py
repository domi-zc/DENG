import os
import logging
import zipfile
import pandas as pd
import requests

from pathlib import Path
from tempfile import TemporaryDirectory
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATASET_URL = "https://epoch.ai/data/gpu_clusters.zip"
CSV_FILENAME = "gpu_clusters.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "gpu_clusters.csv"

COLUMN_RENAME_MAP: dict[str, str] = {
    "Name": "name",
    "Status": "status",
    "Certainty": "certainty",
    "Single cluster?": "single_cluster",
    "Max OP/s (log)": "max_ops_log",
    "H100 equivalents": "h100_equivalents",
    "Chip type (primary)": "chip_type_primary",
    "Chip quantity (primary)": "chip_quantity_primary",
    "Country": "country",
    "Owner": "owner",
    "First Operational Date": "first_operational_date",
    "Note": "note",
    "Sector": "sector",
    "Power Capacity (MW)": "power_capacity_mw",
    "Hardware Cost": "hardware_cost",
    "Location": "location",
    "Users": "users",
    "Hardware note": "hardware_note",
    "Quote": "quote",
    "First Operational Date Note": "first_operational_date_note",
    "Certainty Note": "certainty_note",
    "Energy Efficiency (log)": "energy_efficiency_log",
    "Builds Upon": "builds_upon",
    "Superseded by": "superseded_by",
    "Possible Duplicate": "possible_duplicate",
    "Possible Duplicate Of": "possible_duplicate_of",
    "Chip type (secondary)": "chip_type_secondary",
    "Chip quantity (secondary)": "chip_quantity_secondary",
    "Total number of AI chips": "total_number_of_ai_chips",
    "GPU Supplier (primary)": "gpu_supplier_primary",
    "GPU supplier (secondary)": "gpu_supplier_secondary",
    "Include in Standard Analysis": "include_in_standard_analysis",
    "Exclude": "exclude",
    "Rank when first operational": "rank_when_first_operational",
    "16-bit OP/s (log)": "16bit_ops_log",
    "Max OP/s": "max_ops",
    "8-bit OP/s": "8bit_ops",
    "16-bit OP/s": "16bit_ops",
    "32-bit OP/s": "32bit_ops",
    "Calculated Power Capacity (MW)": "calculated_power_capacity_mw",
    "Reported Power Capacity (MW)": "reported_power_capacity_mw",
    "Energy Efficiency": "energy_efficiency",
    "Calculated Cost": "calculated_cost",
    "Reported Cost": "reported_cost",
    "Reported Cost (Inflation adjusted)": "reported_cost_inflation_adjusted",
    "Cost Quote": "cost_quote",
    "Noteworthy": "noteworthy",
    "Decommissioned Date (if applicable)": "decommissioned_date_if_applicable",
    "Largest existing cluster when first operational": "largest_existing_cluster_when_first_operational",
    "% of largest cluster when first operational": "percent_of_largest_cluster_when_first_operational",
    "Source 1": "source_1",
    "Source 2": "source_2",
    "Source 3": "source_3",
    "Source 4": "source_4",
    "Source 5": "source_5",
}

COLUMNS_TO_DROP = [
    "include_in_standard_analysis",
    "exclude",
    "noteworthy",
    "gpu_supplier_primary",
    "gpu_supplier_secondary",
    "source_1",
    "source_2",
    "source_3",
    "source_4",
    "source_5",
    "h100_equivalents",
    "note",
    "sector",
    "users",
    "hardware_note",
    "quote",
    "first_operational_date_note",
    "certainty_note",
    "builds_upon",
    "superseded_by",
    "possible_duplicate",
    "possible_duplicate_of",
    "cost_quote",
    "decommissioned_date_if_applicable",
    "largest_existing_cluster_when_first_operational",
    "percent_of_largest_cluster_when_first_operational",
    "location",
    "rank_when_first_operational",
    "certainty",
    "single_cluster",
    "calculated_power_capacity_mw",
    "reported_power_capacity_mw",
    "16bit_ops_log",
    "energy_efficiency_log",
]

FINAL_COLUMN_ORDER = [
    "name",
    "owner",
    "country",
    "power_capacity_mw",
    "first_operational_date",
    "calculated_cost",
    "reported_cost",
    "reported_cost_inflation_adjusted",
    "hardware_cost",
    "chip_type_primary",
    "chip_quantity_primary",
    "chip_type_secondary",
    "chip_quantity_secondary",
    "total_number_of_ai_chips",
    "energy_efficiency",
    "max_ops",
    "8bit_ops",
    "16bit_ops",
    "32bit_ops",
]


def download_and_extract(url: str, target_file: str) -> pd.DataFrame:
    """Download the GPU clusters ZIP and return the extracted CSV as a DataFrame."""
    logger.info("Downloading dataset from {url}")
    response = requests.get(url, timeout=60)
    # Raise an HTTP Error if one occured
    response.raise_for_status()

    with TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / "gpu_clusters.zip"
        zip_path.write_bytes(response.content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extract(target_file, tmp_dir)

        df = pd.read_csv(Path(tmp_dir) / target_file)

    logger.info("Loaded %d rows from %s", len(df), target_file)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns, drop unnecessary data, and reorder."""

    df = df.rename(columns=COLUMN_RENAME_MAP)
    df = df.drop(columns=COLUMNS_TO_DROP)

    # Drop rows with anonymized or missing data
    df = df[df["name"] != "Anonymized Chinese System"]
    df = df.dropna(subset=["chip_type_primary", "chip_quantity_primary"])

    return df[FINAL_COLUMN_ORDER]

def main() -> None:
    df = download_and_extract(DATASET_URL, CSV_FILENAME)
    df = clean(df)

    # Database credentials from the Docker environment
    user = os.getenv("DB_USER", "admin")
    password = os.getenv("DB_PASSWORD", "adminpassword")
    host = os.getenv("DB_HOST", "postgres")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "gpu_database")

    # Create the connection and push to PostgreSQL
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
    
    logger.info("Pushing data to PostgreSQL database...")
    df.to_sql(name="gpu_clusters_cleaned", con=engine, if_exists="replace", index=False)
    
    logger.info("Successfully wrote %d rows to the database.", len(df))

if __name__ == "__main__":
    main()
