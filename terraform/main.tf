terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  project     = var.gcp_project_id
  region      = var.region
  credentials = file(var.credentials_path)
}

resource "google_storage_bucket" "data_lake" {
  name          = var.gcp_bucket_name
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "data_warehouse" {
  dataset_id                  = var.bq_dataset_name
  location                    = var.region
  description                 = "Dataset for Epoch AI GPU Clusters benchmarking"
  delete_contents_on_destroy  = true
}