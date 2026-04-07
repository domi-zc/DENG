# Epoch AI GPU Clusters - Batch Data Pipeline

## Project Overview

This project is an end-to-end batch data pipeline that ingests, cleans, and stores the Epoch AI GPU Clusters dataset. It is designed to support an AI Infrastructure Analyst at an AI factory currently conceptualizing the company's newest AI data center in Switerland. Since the company is not a hyperscaler, and given that capital expenditures (CapEx) for 1 MW of an AI data center capacity amount to approximately 55 million CHF - coupled with the current gobal memory shortage - chip selection and infrastructure design carry significant financial consequences. By benchmarking against comparable facilities in the dataset, this information supports the busines case for the project's high CapEx and aids in the chip selection strategy.

The pipeline extracts the data, transforms it by filtering out anonymized systems and missing data and loads it into a local PostgreSQL database. The workflow is fully orchestrated using Kestra.

## Prerequisites

This pipeline is fully containerized. To run it, you only need:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Running in the background)

## Pipeline Configuration & Rubric Highlights

To assist with the peer review evaluation, here is an overview of the key pipeline components:

### Environment Variables Explained
The pipeline relies on environment variables defined in the `docker-compose.yaml` to securely pass credentials between the Python ingestion container and the PostgreSQL database container without hardcoding them into the Python script:
* `POSTGRES_USER` & `POSTGRES_PASSWORD`: Sets the root credentials for the PostgreSQL database instance.
* `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`: Injected into the Python `ingestion` container so SQLAlchemy knows exactly how to route the cleaned dataframe to the database. 
* `PGADMIN_DEFAULT_EMAIL` & `PGADMIN_DEFAULT_PASSWORD`: Sets the initial login credentials for the pgAdmin web interface.

### Workflow Visibility
The workflow orchestration code is visible and version-controlled in this repository under `orchestration/kestra_flow.yaml`. During the Docker Compose build, a setup container automatically imports this flow into the Kestra UI for immediate visibility.

### Backfill Logic Explained
This pipeline supports historical backfills. In the Kestra workflow (`kestra_flow.yaml`), the schedule trigger includes a `backfill` property starting from `2026-03-01T00:00:00Z`. If the pipeline experiences downtime or a scheduled run is missed, Kestra's backfill logic allows the user to manually trigger the pipeline for those specific historical dates to ensure no gaps exist in the dataset.

## Step 1: Build and Run the Infrastructure

This project is fully containerized. To spin up the database, pgAdmin, and Kestra, open your terminal in the root of this repository and run:

```bash
docker compose up -d --build
```

_Wait about 30 seconds for the database and Kestra server to fully initialize._

## Step 2: Run the Orchestration (Kestra)

We use Kestra to orchestrate the batch ingestion script. The setup is fully automated.

1. Open your browser and navigate to the Kestra UI: http://localhost:8081
2. Log in using the default pre-configured credentials:
    * **Email:** admin@admin.com
    * **Password:** adminpassword
3. On the left menu, click **Flows**. You will see the `orchestrate_gpu_pipeline` flow has been automatically imported.
4. Click on the flow, then click the **Execute** button at the top right.
5. Wait for the green **SUCCESS** status. The pipeline has now ingested and pushed the data to PostgreSQL.

## Step 3: Verify the Data in PostgreSQL (pgAdmin)

1. Open your browser and navigate to pgAdmin: http://localhost:8080
2. Log in with the following credentials:
    * **Email:** admin@admin.com
    * **Password:** adminpassword
3. In the left menu, expand **Servers** > **Local Pipeline**.
4. When prompted, enter the database password: `adminpassword`
5. Navigate to **Databases** > **gpu_database** > **Schemas** > **public** > **Tables**.
6. Right-click the `gpu_clusters_cleaned` table, select **View/Edit Data** > **All Rows** to verify the ingested data.

## Step 4: Shut Down

To clean up your environment, run:

```bash
docker compose down
```
