# streamlit_app.py – Streamlit frontend for FastAPI semantic CSV uploader/search
# ----------------------------------------------------
# Simple Streamlit UI to:
#  • Upload a CSV with a `text` column to the FastAPI backend
#  • Enter a search query and view semantic search results
#
# Prerequisites:
#  pip install streamlit requests pandas python-dotenv
#  Define .env with API_URL (e.g. http://localhost:8000)
#
import os
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


# Load environment
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="CSV Semantic Search", layout="wide")
st.title("CSV → OpenSearch Semantic Search")

# Sidebar: settings
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("FastAPI Endpoint URL", API_URL)

# Tab selection
tabs = st.tabs(["Upload CSV", "Search"])

with tabs[0]:
    st.header("Upload a CSV")
    st.write("Choose a CSV file with a `text` column to index its rows.")
    uploaded_file = st.file_uploader("Select CSV file", type=["csv"] )
    if uploaded_file is not None:
        if st.button("Upload to API"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                resp = requests.post(f"{api_url}/upload_csv", files=files)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Successfully indexed {data['indexed']} of {data['total']} rows.")
                else:
                    st.error(f"Upload failed ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Error during upload: {e}")

with tabs[1]:
    st.header("Semantic Search")
    st.write("Enter a query to perform semantic search on the indexed CSV data.")
    query = st.text_input("Search query")
    k = st.slider("Results (k)", min_value=1, max_value=20, value=5)
    if st.button("Search"):
        if not query:
            st.warning("Please enter a search query.")
        else:
            try:
                params = {"q": query, "k": k}
                resp = requests.get(f"{api_url}/search", params=params)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df)
                    else:
                        st.info("No results found.")
                else:
                    st.error(f"Search failed ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Error during search: {e}")

st.markdown("---")
st.write("Powered by FastAPI + OpenSearch Semantic Search")