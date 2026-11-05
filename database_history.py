# database_history.py
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def _get_mongo_uri():
    """Read MONGODB_URI from Streamlit secrets, falling back to env / .env."""
    try:
        if "MONGODB_URI" in st.secrets:
            return st.secrets["MONGODB_URI"]
    except Exception:
        pass  # no secrets.toml locally
    return os.getenv("MONGODB_URI")


@st.cache_resource
def _get_history_collection():
    """Connect once (lazily) and reuse the client across reruns."""
    uri = _get_mongo_uri()
    if not uri:
        raise RuntimeError("MONGODB_URI is not set")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return client["futureGoalAI"]["history"]


def save_history(name, school, goal, phone, gender):
    """
    Save student details to MongoDB (images are not stored).
    """
    _get_history_collection().insert_one({
        "name": name,
        "school": school,
        "goal": goal,
        "phone": phone,
        "gender": gender,
        "timestamp": datetime.now()
    })
