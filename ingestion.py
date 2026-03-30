import requests
import zipfile
import os
import pandas as pd
from dbgpu import GPUDatabase
import re

url = "https://epoch.ai/data/gpu_clusters.zip"
zip_path = "/Users/noahzemljic/Documents/HSLU/DENG/gpu_clusters.zip"
extraction_path = "/Users/noahzemljic/Documents/HSLU/DENG/data"

db = GPUDatabase.default()


rename_dict = {
    'Name': 'name',
    'Status': 'status',
    'Certainty': 'certainty',
    'Single cluster?': 'single_cluster',
    'Max OP/s (log)': 'max_ops_log',
    'H100 equivalents': 'h100_equivalents',
    'Chip type (primary)': 'chip_type_primary',
    'Chip quantity (primary)': 'chip_quantity_primary',
    'Country': 'country',
    'Owner': 'owner',
    'First Operational Date': 'first_operational_date',
    'Note': 'note',
    'Sector': 'sector',
    'Power Capacity (MW)': 'power_capacity_mw',
    'Hardware Cost': 'hardware_cost',
    'Location': 'location',
    'Users': 'users',
    'Hardware note': 'hardware_note',
    'Quote': 'quote',
    'First Operational Date Note': 'first_operational_date_note',
    'Certainty Note': 'certainty_note',
    'Energy Efficiency (log)': 'energy_efficiency_log',
    'Builds Upon': 'builds_upon',
    'Superseded by': 'superseded_by',
    'Possible Duplicate': 'possible_duplicate',
    'Possible Duplicate Of': 'possible_duplicate_of',
    'Chip type (secondary)': 'chip_type_secondary',
    'Chip quantity (secondary)': 'chip_quantity_secondary',
    'Total number of AI chips': 'total_number_of_ai_chips',
    'GPU Supplier (primary)': 'gpu_supplier_primary',
    'GPU supplier (secondary)': 'gpu_supplier_secondary',
    'Include in Standard Analysis': 'include_in_standard_analysis',
    'Exclude': 'exclude',
    'Rank when first operational': 'rank_when_first_operational',
    '16-bit OP/s (log)': '16bit_ops_log',
    'Max OP/s': 'max_ops',
    '8-bit OP/s': '8bit_ops',
    '16-bit OP/s': '16bit_ops',
    '32-bit OP/s': '32bit_ops',
    'Calculated Power Capacity (MW)': 'calculated_power_capacity_mw',
    'Reported Power Capacity (MW)': 'reported_power_capacity_mw',
    'Energy Efficiency': 'energy_efficiency',
    'Calculated Cost': 'calculated_cost',
    'Reported Cost': 'reported_cost',
    'Reported Cost (Inflation adjusted)': 'reported_cost_inflation_adjusted',
    'Cost Quote': 'cost_quote',
    'Noteworthy': 'noteworthy',
    'Decommissioned Date (if applicable)': 'decommissioned_date_if_applicable',
    'Largest existing cluster when first operational': 'largest_existing_cluster_when_first_operational',
    '% of largest cluster when first operational': 'percent_of_largest_cluster_when_first_operational',
    'Source 1': 'source_1',
    'Source 2': 'source_2',
    'Source 3': 'source_3',
    'Source 4': 'source_4',
    'Source 5': 'source_5'
}

def download_data(url, zip_path, extraction_path):
    print("------ DOWNLOADING DATA ------")

    # Download the dataset
    response = requests.get(url)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract the dataset
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(extraction_path, ["gpu_clusters.csv"])

    # Remove the .zip file from the file system
    os.remove(zip_path)

def load_data(path):
    print("------ LOADING DATA ------")
    df = pd.read_csv(path)
    df.rename(columns=rename_dict, inplace=True)

    # Remove unncessary columns
    df.drop(['include_in_standard_analysis', 'exclude', 'noteworthy', 'gpu_supplier_primary', 'gpu_supplier_secondary', 'source_1', 'source_2', 'source_3', 'source_4', 'source_5'], axis=1, inplace=True)

    return df

def enrich_data(df):
    print("------ ENRICHING DATA WITH POWER/MEMORY SPECS ------")
    specs_df = pd.read_csv('./gpu_specs.csv', index_col="gpu")

    # Get the unique primary and secondary chip types of the facility
    primary_chips =  set(df['chip_type_primary'].unique())
    secondary_chips = set(df['chip_type_secondary'].unique())
    all_unique_chips = pd.Series(list(primary_chips | secondary_chips), index=None, name="chip_specs")

    specs_df.merge(all_unique_chips, left_on='gpu', right_on="chip_specs", how="left")

    specs_df.to_csv('df.csv')

    # Get the chip specifications
    for prefix in ["primary", "secondary"]:
        # Get the chip column
        chip_col = f'chip_type_{prefix}'

        df[f'{prefix}_tdp_w'] = df[chip_col].map(specs_df['tdp_w']).fillna(0)
        df[f'{prefix}_vram_gb'] = df[chip_col].map(specs_df['memory_size_gb']).fillna(0)

    df.to_csv('./df.csv')

    # # Append the specifications to the dataframe for primary and secondary chips
    # for prefix in ['primary', 'secondary']:
    #     chip_col = f"chip_type_{prefix}"
    #     qty_col = f"chip_quantity_{prefix}"

    #     df[f"{prefix}_tdp_kw"] = df[chip_col].map(lambda x: chip_specs.get(x, {}).get("tdp_kw", 0))
    #     df[f"{prefix}_vram_gb"] = df[chip_col].map(lambda x: chip_specs.get(x, {}).get("vram_gb", 0))

    # # Calculate the Aggregated Weighted Efficiency
    # df['total_cluster_vram_gb'] = (df["chip_quantity_primary"] * df['primary_vram_gb']) + (df["chip_quantity_secondary"] * df['secondary_vram_gb'])
    # df['total_cluster_power_kw'] =  (df["chip_quantity_primary"] * df['primary_tdp_kw']) + (df["chip_quantity_secondary"] * df['secondary_tdp_kw'])

    # df['awe_gb_per_kw'] = df['total_cluster_vram_gb'] / df['total_cluster_power_kw']




def main():
    # Download the dataset
    download_data(url=url,
                  zip_path = zip_path,
                  extraction_path = extraction_path)

    # Load the data
    cluster_df = load_data(f"{extraction_path}/gpu_clusters.csv")

    enrich_data(cluster_df)

if __name__ == "__main__":
    main()
