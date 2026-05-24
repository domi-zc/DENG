import logging

import pandas as pd

class Transformer:
    """Apply rename/drop/filter/reorder rules to the raw GPU clusters DataFrame."""

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

    COLUMNS_TO_DROP: list[str] = [
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

    FINAL_COLUMN_ORDER: list[str] = [
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

    ANONYMIZED_NAME = "Anonymized Chinese System"
    PRIMARY_CHIP_REQUIRED_COLUMNS = ("chip_type_primary", "chip_quantity_primary")
    # Cast to float because values can exceed PostgreSQL bigint range (~9.2 × 10¹⁸)
    OPS_COLUMNS = ("max_ops", "8bit_ops", "16bit_ops", "32bit_ops")

    logger = logging.getLogger(__name__)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename, drop, filter, and reorder columns for the analyst use case."""
        if df is None or df.empty:
            raise ValueError("Input DataFrame must not be empty")

        df = df.rename(columns=self.COLUMN_RENAME_MAP)

        # Drop unnecessary columns
        columns_to_drop_present = [
            column for column in self.COLUMNS_TO_DROP if column in df.columns
        ]
        df = df.drop(columns=columns_to_drop_present)

        # Drop anonymized entries the analyst cannot benchmark against
        cleaned_df = df[df["name"] != self.ANONYMIZED_NAME]

        # Drop rows missing primary chip data since they are unusable for chip-selection benchmarking
        cleaned_df = cleaned_df.dropna(subset=list(self.PRIMARY_CHIP_REQUIRED_COLUMNS))

        final_df = cleaned_df[self.FINAL_COLUMN_ORDER].copy()
        for col in self.OPS_COLUMNS:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors="coerce").astype("float64")
        final_df["first_operational_date"] = pd.to_datetime(
            final_df["first_operational_date"], errors="coerce"
        ).dt.date
        if final_df.empty:
            raise ValueError("Cleaned DataFrame is empty after filtering")

        self.logger.info(
            f"Cleaned DataFrame contains {len(final_df)} rows and {len(final_df.columns)} columns"
        )
        return final_df
