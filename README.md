# 🔍 Elastic ML Anomaly Detection Pipeline

[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-005571.svg?logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![Kibana](https://img.shields.io/badge/Kibana-8.x-005571.svg?logo=kibana&logoColor=white)](https://www.elastic.co/kibana)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)

This repository contains a complete, automated end-to-end pipeline for **Log Generation, Ingestion, and Machine Learning (ML) Anomaly Detection** using the Elastic Stack (ELK) and Python. 

The project demonstrates how to simulate realistic application logs with injected anomalies, process them via Beats/Logstash, store them in Elasticsearch, and automatically verify the findings of Elasticsearch Machine Learning jobs.

## 📌 Project Overview

The primary goal of this project is to showcase unsupervised machine learning capabilities within Elasticsearch. The system simulates a microservice environment, generates structured logs, and identifies operational and security anomalies without relying on static thresholds.

### ⚙️ Core Architecture & Data Flow

1. **Data Generation (`generate_logs.py`):** A custom Python script generates thousands of structured log lines simulating 4 services, random users, and IPs. It intentionally injects anomalies (approx. 3%) such as:
   - Error/Fatal spikes
   - Suspicious user behavior (e.g., abnormally high request volumes)
   - Rare/Unusual IP addresses
   - Access outside of normal business hours (night shifts)
   - Extremely slow response times
2. **Ingestion (Filebeat & Logstash):** - **Filebeat** tails the generated JSON logs, extracts timestamps, maps IPs, and streams them directly into an Elasticsearch Data Stream (`filebeat-structured`).
   - **Logstash** is available as an alternative or supplementary ingestion node for complex Grok parsing.
3. **Storage & ML (Elasticsearch):** Data is securely indexed. Pre-configured ML Jobs (e.g., `population-user`) continuously analyze the data streams to baseline normal behavior and score outliers.
4. **Monitoring (Metricbeat):** Monitors the health and performance of the Elasticsearch cluster, Docker containers, and the host system.
5. **Verification (`verify_anomalies.py`):** A Python automation script that queries Elasticsearch's `.ml-anomalies-shared` index to programmatically validate and extract the anomalies found by the ML jobs.

---

## 🛠️ Technology Stack

* **Infrastructure:** Docker & Docker Compose (Self-managed Elastic Stack with SSL/TLS enabled)
* **Elastic Stack:** Elasticsearch, Kibana, Filebeat, Metricbeat, Logstash
* **Automation & Scripting:** Python (Libraries: `elasticsearch`, `datetime`, `random`)

---

## 📂 Repository Structure

```text
├── docker-compose.yml         # Defines the Elastic Stack (es01, kibana, beats, logstash)
├── filebeat.yml               # Filebeat config for NDJSON parsing & Data Stream routing
├── metricbeat.yml             # Metricbeat config for ES, Kibana, and Docker monitoring
├── logstash.conf              # Logstash pipeline configuration (optional grok parsing)
├── generate_logs.py           # Python script to generate normal and anomalous log data
├── verify_anomalies.py        # Python script to query ES and validate ML Job findings
└── README.md                  # Project documentation

```

---

## 🚀 Installation & Setup

### 1. Prerequisites

* **Docker & Docker Compose** installed.
* **Python 3.9+** installed.
* Ensure your Docker engine has at least **4GB RAM** allocated (Elasticsearch requirement).

### 2. Environment Configuration

Create a `.env` file in the root directory to define required stack variables:

```env
STACK_VERSION=8.11.0
CLUSTER_NAME=ml-cluster
LICENSE=trial
ELASTIC_PASSWORD=YourSecurePassword123
KIBANA_PASSWORD=YourSecurePassword123
ES_PORT=9200
KIBANA_PORT=5601
ENCRYPTION_KEY=Your32CharSecureEncryptionKeyHere!

```

### 3. Spin up the Elastic Stack

Start the infrastructure using Docker Compose. The `setup` container will automatically generate SSL certificates and configure passwords.

```bash
docker-compose up -d

```

*Wait a few minutes for Elasticsearch and Kibana to become healthy. You can access Kibana at `https://localhost:5601`.*

---

## 🔬 Execution Workflow

To see the Anomaly Detection in action, follow these steps:

### Step 1: Create the ML Job (in Kibana)

1. Log in to Kibana (`elastic` / `ELASTIC_PASSWORD`).
2. Navigate to **Machine Learning > Anomaly Detection**.
3. Create a new job (e.g., named `population-user`) pointing to the `filebeat-structured*` index pattern.
4. Start the Datafeed.

### Step 2: Start the Verification Script

In your first terminal, start the verification script. It will connect to Elasticsearch and wait for new data to be processed.

```bash
pip install elasticsearch
python verify_anomalies.py

```

### Step 3: Generate Anomalous Logs

While the verification script is waiting (you have ~45 seconds), open a second terminal and trigger the log generator:

```bash
python generate_logs.py

```

*This will create files like `logdata_10000.log` which Filebeat will immediately detect and ship to Elasticsearch.*

### Step 4: View Results

Watch the terminal running `verify_anomalies.py`. Once the wait time is over, it will output the findings directly from the ML engine:

```text
==================================================
🔬 SCIENTIFIC PROOF: 14 ANOMALIES DETECTED
==================================================
Timestamp: 2023-10-25T03:14:00 | Anomaly Score: 98.40 | Description: Unusual Access Time
Timestamp: 2023-10-25T14:22:15 | Anomaly Score: 85.12 | Description: Rare IP (5.5.5.3)
...

```

---

## 🛡️ Security & Best Practices Implemented

* **Zero-Trust Network:** All intra-cluster communication (HTTP & Transport) is secured via TLS/SSL.
* **Least Privilege:** Services (like Kibana) use dedicated built-in service accounts (`kibana_system`).
* **Data Streams & ILM:** Filebeat uses Index Lifecycle Management (ILM) and Data Streams for scalable time-series data storage.

```

```
