"""
utils.py
"""

import json
from urllib.parse import urlencode

import pandas as pd
import requests
import streamlit as st

BASE_URL = 'https://data.gov.sg/api/action/datastore_search'
DATASET_ID = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"

@st.cache_data(show_spinner=False)
def load_resale_data(town=None , flat_type=None, limit=10_000) -> pd.DataFrame:
    """
    Download HDB resale data from the Data.gov.sg API.
    """

    # Encode the filters dictionary into URL-encoded string
    filters = {}
    if town:
        filters['town'] = town
    if flat_type:
        filters['flat_type'] = flat_type
    
    encoded_filters = urlencode({"filters": json.dumps(filters)})

    # Complete URL with query parameters
    url = f"{BASE_URL}?resource_id={DATASET_ID}&{encoded_filters}&limit={limit}"

    # Making the HTTP GET request
    response = requests.get(url, timeout=30)

    # Parsing the JSON response
    dataframe = response.json()['result']['records']

    # Converting to a Pandas DataFrame
    df = pd.DataFrame(dataframe)

    return df

@st.cache_resource(show_spinner=False)
def ask_llm(prompt: str) -> str:
    """
    Ask a question and return the answer.
    """
    return prompt