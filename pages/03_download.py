import streamlit as st
import pandas as pd
from pathlib import Path
from utils import RESULT_FILE, load_results, clear_results
from firebase_config import initialize_firebase, get_all_firestore_records

st.set_page_config(page_title="Download Results", page_icon="📥")
st.title("Download Results")

def display_stats(df, source="Local"):
    """Display statistics about the results"""
    if df is not None and not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Results", len(df))
        with col2:
            if 'model' in df.columns:
                st.metric("Unique Models", df['model'].nunique())
        with col3:
            if 'date' in df.columns:
                st.metric("Unique Dates", df['date'].nunique())

# Create tabs for Local and Firestore downloads
local_tab, firestore_tab = st.tabs(["📂 Local Results", "☁️ Firestore Results"])

# Local Results Tab
with local_tab:
    results_df = load_results()
    
    if results_df is not None:
        display_stats(results_df)
        
        st.subheader("Preview")
        st.dataframe(results_df, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            custom_filename = st.text_input(
                "Local results filename", 
                value="complete_set.csv",
                help="Name of the file to save the results to"
            )
            st.download_button(
                label="📥 Download Local Results",
                data=results_df.to_csv(index=False),
                file_name=custom_filename,
                mime="text/csv",
                help="Download all local results as a CSV file"
            )
        
        with col2:
            st.button(
                "🗑️ Clear Local Results",
                help="Delete all local results. This action cannot be undone.",
                on_click=clear_results
            )
            st.caption("⚠️ This action cannot be undone")
    else:
        st.info("💡 No local results available. Run some models first!")

# Firestore Results Tab
with firestore_tab:
    load_button = st.button(
        "🔄 Load Firestore Records",
        help="Fetch the latest results from Firestore database"
    )
    
    if load_button:
        if initialize_firebase():
            with st.spinner("📡 Fetching records from Firestore..."):
                records = get_all_firestore_records()
                
                if records:
                    df = pd.DataFrame(records)
                    
                    # Convert timestamp to string for CSV export
                    if 'timestamp' in df.columns:
                        df['timestamp'] = df['timestamp'].astype(str)
                    
                    display_stats(df, "Firestore")
                    
                    # Create filter container
                    filter_container = st.container()
                    with filter_container:
                        st.markdown("### 🔍 Filter Options")
                        col1, col2 = st.columns(2)
                        
                        selected_dates = []
                        selected_models = []
                        
                        with col1:
                            if 'date' in df.columns:
                                selected_dates = st.multiselect(
                                    "📅 Filter by date",
                                    options=sorted(df['date'].unique()),
                                    help="Select one or more dates to filter results"
                                )
                        
                        with col2:
                            if 'model' in df.columns:
                                selected_models = st.multiselect(
                                    "🤖 Filter by model",
                                    options=sorted(df['model'].unique()),
                                    help="Select one or more models to filter results"
                                )
                    
                    # Apply filters
                    filtered_df = df.copy()
                    if selected_dates:
                        filtered_df = filtered_df[filtered_df['date'].isin(selected_dates)]
                    if selected_models:
                        filtered_df = filtered_df[filtered_df['model'].isin(selected_models)]
                    
                    # Show results
                    display_df = filtered_df if (selected_dates or selected_models) else df
                    
                    st.markdown("### 📊 Results Preview")
                    if selected_dates or selected_models:
                        st.caption(f"Showing {len(display_df)} filtered results out of {len(df)} total records")
                    st.dataframe(display_df, hide_index=True)
                    
                    # Download section
                    st.divider()
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        firebase_filename = st.text_input(
                            "Filename for download",
                            value="firestore_records.csv",
                            help="Name of the file to save the Firestore results to"
                        )
                    
                    with col2:
                        st.download_button(
                            label="📥 Download Results",
                            data=display_df.to_csv(index=False),
                            file_name=firebase_filename,
                            mime="text/csv",
                            help="Download filtered results as a CSV file"
                        )
                else:
                    st.warning("📭 No records found in Firestore database")
        else:
            st.error("❌ Failed to initialize Firebase. Please check your credentials.")
    else:
        st.info("💡 Click 'Load Firestore Records' to fetch data from Firestore")
