# Epoch AI GPU Clusters - Batch Data Pipeline

## Project Overview
This project is an end-to-end batch data pipeline that ingests, cleans, and stores the Epoch AI GPU Clusters dataset. It is designed to support an AI Infrastructure Analyst who needs to track global AI compute capacity to predict hardware bottlenecks and analyze competitor resources.

The pipeline extracts the data, transforms it by filtering out anonymized systems and missing data (ensuring verified attribution for market share analysis), and loads it into a local PostgreSQL database. The workflow is fully orchestrated using Kestra.

## Prerequisites
This pipeline is fully containerized. To run it, you only need:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Running in the background)

## Step 1: Build and Run the Infrastructure
This project is fully containerized. To spin up the database, pgAdmin, and Kestra, open your terminal in the root of this repository and run:

```bash
docker compose up -d --build
```

*Wait about 30 seconds for the database and Kestra server to fully initialize.*

## Step 2: Run the Orchestration (Kestra)
We use Kestra to orchestrate the batch ingestion script.

1. Open your browser and navigate to the Kestra UI: http://localhost:8081
2. *Note: If prompted to create an admin user, enter any dummy email and password.*
3. On the left menu, click **Flows**.
4. Click **Create** and paste the contents of the `orchestration/kestra_flow.yaml` file located in this repository.
5. Click **Save**, then click the **Execute** button at the top right.
6. The flow will trigger the Docker container, run the Python ingestion script, and push the cleaned data to PostgreSQL. Wait for the green **SUCCESS** status.

## Step 3: Verify the Data in PostgreSQL (pgAdmin)
1. Open your browser and navigate to pgAdmin: http://localhost:8080
2. Log in with the following credentials:
    * **Email:** `admin@admin.com`
    * **Password:** `adminpassword`
3. In the top left, right-click **Servers** > **Register** > **Server...**
4. Name it `Local Pipeline`.
5. Switch to the **Connection** tab and enter:
    * **Host name/address:** `postgres`
    * **Port:** `5432`
    * **Maintenance database:** `gpu_database`
    * **Username:** `admin`
    * **Password:** `adminpassword`
6. Click **Save**.
7. In the left menu, expand: **Servers** > **Local Pipeline** > **Databases** > **gpu_database** > **Schemas** > **public** > **Tables**.
8. Right-click the `gpu_clusters_cleaned` table, select **View/Edit Data** > **All Rows** to verify the ingested data.

## Step 4: Shut Down
To clean up your environment, run:

```bash
docker compose down
```
