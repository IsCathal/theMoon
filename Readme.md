# BigBrain Semantic Search

This project demonstrates a full-stack semantic search application using OpenSearch, FastAPI, and Streamlit. It includes:

- **Docker OpenSearch cluster**: Two-node OpenSearch cluster with OpenSearch Dashboards, preconfigured for semantic search and RAG capabilities.
- **Backend (FastAPI)**: A Python API that indexes CSV data into OpenSearch and provides semantic search endpoints.
- **Frontend (Streamlit)**: A web UI for uploading CSV files and performing semantic searches.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
   - [OpenSearch Cluster](#opensearch-cluster)
   - [Backend (FastAPI)](#backend-fastapi)
   - [Frontend (Streamlit)](#frontend-streamlit)
3. [Usage](#usage)
   - [Uploading CSV Data](#uploading-csv-data)
   - [Performing Semantic Search](#performing-semantic-search)
   - [Conversational RAG (Optional)](#conversational-rag-optional)
4. [Environment Variables](#environment-variables)
5. [Troubleshooting](#troubleshooting)
6. [License](#license)

---

## Prerequisites

- Docker & Docker Compose
- Python 3.9+ and `pip`
- (Optional) `.env` file support via `python-dotenv`

---

## Setup

### OpenSearch Cluster

1. **Edit `.env`** in this folder to include your OpenSearch admin password:
   ```dotenv
   OPENSEARCH_INITIAL_ADMIN_PASSWORD=YourStrongPassword
   ```
2. **Start the cluster**:
   ```bash
   docker compose up -d
   ```
3. **Verify**:
   - OpenSearch at https://localhost:9200 (Basic Auth: `admin` / your password)
   - Dashboards at https://localhost:5601

### Backend (FastAPI)

1. **Navigate** to the backend directory:
   ```bash
   cd backend
   ```
2. **Create & activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install fastapi "uvicorn[standard]" httpx pandas python-dotenv
   ```
4. **Create `.env`** in `backend/`:
   ```dotenv
   OPENSEARCH_URL=https://localhost:9200
   OPENSEARCH_USER=admin
   OPENSEARCH_INITIAL_ADMIN_PASSWORD=YourStrongPassword
   VERIFY_SSL=false
   INDEX_NAME=csv-index
   ```
5. **Run the API**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend (Streamlit)

1. **Navigate** to the frontend directory:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   pip install streamlit requests pandas python-dotenv
   ```
3. **Create `.env`** in `frontend/`:
   ```dotenv
   API_URL=http://localhost:8000
   ```
4. **Run Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```
5. **Open** http://localhost:8501 in your browser.

---

## Usage

### Uploading CSV Data

1. In Streamlit, go to the **Upload CSV** tab.
2. Select a CSV file (any columns) and click **Upload to API**.
3. The backend will create `csv-index` if missing and index every row.

### Performing Semantic Search

1. Switch to the **Search** tab in Streamlit.
2. Enter a query and select the number of results.
3. Click **Search** to view the top-k semantically similar rows.

### Conversational RAG (Optional)

To enable RAG and conversational search:

1. Apply dynamic cluster settings:
   ```bash
   curl -k -u admin:$OPENSEARCH_INITIAL_ADMIN_PASSWORD -XPUT      https://localhost:9200/_cluster/settings      -H "Content-Type: application/json"      -d '{"persistent":{"plugins.ml_commons.memory_feature_enabled":true,"plugins.ml_commons.rag_pipeline_feature_enabled":true}}'
   ```
2. Provision the workflow template:
   ```bash
   curl -k -u admin:$OPENSEARCH_INITIAL_ADMIN_PASSWORD -XPOST      https://localhost:9200/_plugins/_flow_framework/workflow?use_case=conversational_search_with_llm_deploy&provision=true      -H 'Content-Type: application/json'      -d '{"create_connector.credential.key":"<YOUR_OPENAI_KEY>"}'
   ```
3. Wait for the workflow to complete (check `_status`).
4. In your FastAPI or Streamlit code, call the RAG pipeline APIs with `ext.generative_qa_parameters`.

---

## Environment Variables

| Variable                             | Description                                                  | Default                  |
|--------------------------------------|--------------------------------------------------------------|--------------------------|
| `OPENSEARCH_INITIAL_ADMIN_PASSWORD`  | Password for OpenSearch `admin` user                         | **(required)**           |
| `OPENSEARCH_URL`                     | URL of the OpenSearch cluster                                | `https://localhost:9200` |
| `OPENSEARCH_USER`                    | Admin username                                               | `admin`                  |
| `VERIFY_SSL`                         | Whether to verify TLS certificates (`true`/`false`)          | `false`                  |
| `INDEX_NAME`                         | Name of the index for CSV data                               | `csv-index`              |
| `API_URL` (frontend)                 | URL of the backend FastAPI service                           | `http://localhost:8000`  |

---

## Troubleshooting

- **Connection errors**: Ensure `VERIFY_SSL` matches your cert setup and the cluster is up.
- **Port conflicts**: FastAPI runs on 8000, Streamlit on 8501, Dashboards on 5601.
- **Missing dependencies**: Activate the correct venv and run `pip install -r requirements.txt`.

---

## License

MIT © Your Name
