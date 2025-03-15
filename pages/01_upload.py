import streamlit as st
import pandas as pd
import os
from utils import PROMPT_FILE, ensure_data_directory

st.set_page_config(page_title="Upload Prompts", page_icon="📤")
st.title("Upload Prompts")

ensure_data_directory()

def validate_csv(df):
    if 'Prompt' not in df.columns:
        st.error("CSV file must contain a 'Prompt' column")
        return False
    return True

with st.container():
    uploaded_file = st.file_uploader("Upload a prompt file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if validate_csv(df):
            st.success("File uploaded successfully!")
            
            # Save the file
            df.to_csv(PROMPT_FILE, index=False)
            
            # Show preview
            st.subheader("Preview of Uploaded Prompts")
            st.dataframe(df, hide_index=True)
            
            # Display stats
            st.info(f"Total prompts: {len(df)}")
    else:
        if os.path.exists(PROMPT_FILE):
            st.info("Using existing prompts file")
            df = pd.read_csv(PROMPT_FILE)
            
            st.subheader("Current Prompts")
            st.dataframe(df, hide_index=True)
            
            if st.button("Clear Existing Prompts"):
                os.remove(PROMPT_FILE)
                st.experimental_rerun()
        else:
            st.warning("Please upload a CSV file containing prompts")
