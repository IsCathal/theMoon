# main.py – FastAPI CSV uploader to csv-index
# ----------------------------------------------------
# Simple FastAPI app that:
#  • POST /upload_csv  – upload a CSV and index its rows into `csv-index`
#
# Prerequisites:
#  pip install fastapi uvicorn[standard] httpx pandas python-dotenv
#  Define .env with OPENSEARCH_URL, OPENSEARCH_USER, OPENSEARCH_INITIAL_ADMIN_PASSWORD
#
import os
import asyncio
import pandas as pd
import httpx
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment vars from .env
load_dotenv()
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "https://localhost:9200")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "admin")
OPENSEARCH_PASS = os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD", "admin")
INDEX_NAME = os.getenv("INDEX_NAME", "csv-index")
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

app = FastAPI(title="CSV → csv-index Uploader")
client: Optional[httpx.AsyncClient] = None

@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient(
        auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
        verify=VERIFY_SSL,
        timeout=30
    )
    # Wait for OpenSearch to be ready
    for attempt in range(10):
        try:
            resp = await client.head(f"{OPENSEARCH_URL}/{INDEX_NAME}")
            break
        except (httpx.RemoteProtocolError, httpx.ConnectError):
            print(f"Waiting for OpenSearch (attempt {attempt+1}/10)...")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("Cannot connect to OpenSearch after multiple attempts")

    # Create index if missing
    if resp.status_code == 404:
        mapping = {"properties": {col: {"type": "text"} for col in df.columns}} if 'df' in locals() else {"properties": {"text": {"type": "text"}}}
        body = {"mappings": mapping}
        r = await client.put(f"{OPENSEARCH_URL}/{INDEX_NAME}", json=body)
        r.raise_for_status()
        print(f"Created index {INDEX_NAME}")

@app.on_event("shutdown")
async def shutdown():
    global client
    if client:
        await client.aclose()

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV; index each row in csv-index"""
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    # Automatically map each column as a field
    success = 0
    for idx, row in df.iterrows():
        doc = row.to_dict()
        url = f"{OPENSEARCH_URL}/{INDEX_NAME}/_doc/{idx}?refresh=wait_for"
        res = await client.put(url, json=doc)
        if res.status_code in (200, 201):
            success += 1
    return JSONResponse({"indexed": success, "total": len(df)})

# Run with: uvicorn main:app --reload --port 8000
