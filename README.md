# Epoch AI GPU Clusters - Batch Data Pipeline

## Project Overview

This project is an end-to-end batch data pipeline that ingests, cleans and stores the Epoch AI GPU Clusters dataset. It is designed to support an AI Infrastructure Analyst at an AI factory currently conceptualizing the company's newest AI data center in Switerland. Since the company is not a hyperscaler, and given that capital expenditures (CapEx) for 1 MW of an AI data center capacity amount to approximately 55 million CHF - coupled with the current gobal memory shortage - chip selection and infrastructure design carry significant financial consequences. By benchmarking against comparable facilities in the dataset, this information supports the busines case for the project's high CapEx and aids in the chip selection strategy.

The pipeline features two completely independent execution tracks:
1. **Local Track:** Extracts data, transforms it, and loads it into a local PostgreSQL database.
2. **Cloud Track:** Extracts data, loads raw data into a Google Cloud Storage (GCS) Data Lake, transforms it, and loads the structured data into a Google BigQuery Data Warehouse.

Both tracks are fully containerized using Docker and orchestrated using Kestra. Infrastructure for the cloud track is provisioned as code (IaC) using Terraform.

---

## Prerequisites

To run this pipeline on a fresh machine, you need the following installed:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Running in the background)
* [Terraform CLI](https://developer.hashicorp.com/terraform/install)
* [Google Cloud Platform](https://console.cloud.google.com/) (GCP) Account

---

## Setup Guide

This pipeline can be executed in two different environments: Cloud or Local. The Cloud Setup requires a Google Cloud project and Terraform to provision the infrastructure. If you prefer to test the pipeline locally without configuring cloud accounts or hitting external APIs, you can scroll down directly to the **Local Setup** heading.

---

## Cloud Setup

### Step 1: Google Cloud Project Initialization
1. Log into the Google Cloud Console.
2. Click the project dropdown at the top of the screen and select **New Project**.
3. **Project Name:** You can name this anything (e.g., `Epoch GPU Clusters`).
4. **Project ID:** Google will auto-generate an ID under the name. **This ID must be globally unique across all of Google Cloud.** You can edit it to something like `epoch-gpu-pipeline-12345`. Note this ID down.
5. Click **Create**.

### Step 2: Check Required APIs
You must ensure Google Cloud has activated the services we need.
1. In the top search bar of the GCP Console, type **APIs & Services** and select **Library**.
2. Search for **Cloud Storage API**. Click it, and check if it is enabled (if the button says "Manage", it is already active; otherwise, click "Enable").
3. Go back to the Library search bar, search for **BigQuery API**, and check if it is enabled.

### Step 3: Service Accounts & Keys
To ensure strict security and the Principle of Least Privilege, this project uses two separate service accounts. 

**1. Create the Terraform Service Account:**
* Go to **IAM & Admin** > **Service Accounts** and click **Create Service Account**.
* Name it `terraform-runner` and click **Create and continue**.
* Grant the following roles:
  * BigQuery Admin
  * Storage Admin
* Click **Done**. 
* Back on the Service Accounts table, click the **Actions dots** (three vertical dots) on the right side of the `terraform-runner` row and select **Manage keys**.
* Click **Add Key** > **Create new key** (JSON).
* Download the key, rename it to `gcp-key-terraform.json`, and move it directly into the `.secrets/` folder in your repository.

**2. Create the Pipeline Service Account:**
* Go back to **Service Accounts** and click **Create Service Account**.
* Name it `pipeline-runner` and click **Create and continue**.
* Grant the following roles:
  * BigQuery Data Editor
  * BigQuery Job User
  * Storage Bucket Viewer
  * Storage Object Admin
* Click **Done**.
* Back on the Service Accounts table, click the **Actions dots** on the right side of the `pipeline-runner` row and select **Manage keys**.
* Click **Add Key** > **Create new key** (JSON).
* Download the key, rename it to `gcp-key-pipeline.json`, and move it into the `.secrets/` folder.

### Step 4: Configure Environment Variables
Before provisioning infrastructure, you must set up your local environment file. 
1. In the root of the repository, copy the `.env.example` file and rename the copy to `.env`.
2. **Local Variables:** The local database and orchestration variables are already pre-filled for you. You can leave these exactly as they are. If you choose to change them, note that Kestra requires strict password complexity (at least 8 characters, 1 uppercase, 1 lowercase, 1 number).
3. **Cloud Variables:** Update the bottom section with your specific Google Cloud details:
   * `GCP_PROJECT_ID`: Enter the globally unique Project ID you created in Step 1.
   * `GCS_BUCKET`: Enter a name for your data lake. **This must also be globally unique** (e.g., `epoch-data-lake-12345`).
   * `BQ_DATASET`: Enter a standard name for your dataset (e.g., `epoch_ai_gpu_clusters_dw`).
   * `BQ_TABLE`: Enter a standard name for your table (e.g., `gpu_clusters_cleaned`).

### Step 5: Provision Infrastructure (Terraform)
We use Terraform to deploy the Data Lake and Data Warehouse. Just like the `.env` file, Terraform needs to be configured with your specific cloud values before it can run.
1. Navigate to the `terraform/` directory.
2. Copy the `terraform.tfvars.example` file and rename it to `terraform.tfvars`.
3. Open `terraform.tfvars` and fill in the exact same **GCP project ID**, **bucket name**, and **dataset name** that you used in your `.env` file.
4. Once the variables are saved, run the following commands to provision the infrastructure:

```bash
terraform init
terraform apply
```
*Type `yes` when prompted to build the infrastructure.*

### Step 6: Run the Cloud Pipeline
Navigate back to the project root and spin up the cloud orchestration environment:

```bash
cd ..
docker compose -f docker-compose.cloud.yaml up -d --build
```
1. Open Kestra at http://localhost:8081 and log in with the following credentials:
    - Email: `admin@admin.com`
    - Password: `Adminpassword1`
2. Navigate to **Flows** > `orchestrate_cloud_pipeline`.
3. Click **Execute**.
4. **Verify:** Open the GCP Console, navigate to BigQuery, expand your project and the dataset, and preview your newly populated table.

---

## Local Setup

If you wish to test the pipeline locally without hitting Google Cloud APIs, you can run the isolated local track.

### Step 1: Run the Local Infrastructure
In the project root, spin up the local database, pgAdmin, and Kestra:

```bash
docker compose -f docker-compose.local.yaml up -d --build
```

### Step 2: Run the Local Pipeline
1. Open Kestra at http://localhost:8081 and log in with the following credentials:
    - Email: `admin@admin.com`
    - Password: `Adminpassword1`
2. Navigate to **Flows** > `orchestrate_local_pipeline`.
3. Click **Execute**.

### Step 3: Verify the Data (pgAdmin)
1. Open pgAdmin at http://localhost:8080 and log in with the following credentials:
    - Email: `admin@admin.com`
    - Password: `adminpassword`
2. Expand **Servers** > **Local Pipeline** (Password: `adminpassword`).
3. Navigate to **Databases** > **gpu_database** > **Schemas** > **public** > **Tables**.
4. Right-click `gpu_clusters_cleaned` > **View/Edit Data** > **All Rows**.

---

## Teardown & Clean Up

To avoid incurring Google Cloud costs and to free up local resources, tear down the project when finished.

**1. Destroy Cloud Infrastructure:**
```bash
cd terraform
terraform destroy
```
*Type `yes` to delete the BigQuery dataset and GCS bucket.*

**2. Stop Docker Containers:**
```bash
# To stop the cloud environment
docker compose -f docker-compose.cloud.yaml down -v

# To stop the local environment
docker compose -f docker-compose.local.yaml down -v
```
*(Note: The `-v` flag permanently wipes the local PostgreSQL data and Kestra history).*