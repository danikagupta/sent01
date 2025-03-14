import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    if not firebase_admin._apps:
        # Check if credentials exist in Streamlit secrets
        if "FIREBASE_PROJECT_ID" in st.secrets:
            # Use credentials from Streamlit secrets
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": st.secrets["FIREBASE_PROJECT_ID"],
                "private_key_id": st.secrets["FIREBASE_PRIVATE_KEY_ID"],
                "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
                "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
                "client_id": st.secrets["FIREBASE_CLIENT_ID"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": st.secrets["FIREBASE_CLIENT_X509_CERT_URL"]
            })
            firebase_admin.initialize_app(cred)
            return True
        else:
            st.warning("Firebase credentials not found in secrets. Firestore upload functionality will be disabled.")
            return False
    return True

def upload_to_firestore(data):
    """Upload data to Firestore"""
    if not firebase_admin._apps:
        return False
    
    try:
        db = firestore.client()
        # Create a collection for LLM responses
        collection_ref = db.collection('llm_responses')
        # Add the document with auto-generated ID
        collection_ref.add(data)
        return True
    except Exception as e:
        st.error(f"Error uploading to Firestore: {e}")
        return False
