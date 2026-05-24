variable "gcp_project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  description = "The GCP region"
  default     = "europe-west6"
}

variable "gcp_bucket_name" {
  type        = string
  description = "The unique name of the GCS bucket"
}

variable "bq_dataset_name" {
  type        = string
  description = "The name of the BigQuery dataset"
}

variable "credentials_path" {
  type        = string
  description = "Path to the GCP Service Account JSON key"
  default     = "../.secrets/gcp-key-terraform.json" 
}