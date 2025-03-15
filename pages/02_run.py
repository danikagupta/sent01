import os
import uuid
from datetime import datetime

import streamlit as st
import pandas as pd

from utils import (
    PROMPT_FILE,
    initialize_models,
    apply_model,
    save_results,
    get_current_date
)
from firebase_config import initialize_firebase, upload_to_firestore

st.set_page_config(page_title="Run Models", page_icon="🚀")
st.title("Run Models")

# Initialize models
if 'models' not in st.session_state:
    st.session_state.models = initialize_models()

def upload_result_to_firestore(model_name, prompt, response, elapsed_time):
    data = {
        'id': str(uuid.uuid4()),
        'model': model_name,
        'prompt': prompt,
        'response': response,
        'time_seconds': elapsed_time,
        'timestamp': datetime.now().isoformat(),
        'date': get_current_date()
    }
    return upload_to_firestore(data)

def run_models(df, selected_models, run_count):
    current_count = 0
    total_count = run_count * len(selected_models) * df.shape[0]
    progress_bar = st.progress(0)
    results = []
    
    # Initialize Firebase
    firebase_enabled = initialize_firebase()
    if firebase_enabled:
        st.sidebar.success("Firebase connection established")
    else:
        st.sidebar.warning("Firebase connection not available")
    
    with st.status("Running models...", expanded=True) as status:
        for i in range(1, run_count + 1):
            for model_name in selected_models:
                for _, row in df.iterrows():
                    user_input = row['Prompt']
                    status.write(f"Run {i}: Processing {model_name} - {user_input[:50]}...")
                    
                    rsp, elapsed_time = apply_model(st.session_state.models[model_name], user_input)
                    results.append({
                        'model': model_name,
                        'prompt': user_input,
                        'response': rsp,
                        'time_seconds': elapsed_time,
                        'current_date': get_current_date()
                    })
                    
                    if firebase_enabled:
                        upload_result_to_firestore(model_name, user_input, rsp, elapsed_time)
                    
                    current_count += 1
                    progress_bar.progress(current_count / total_count)
        
        status.update(label="Complete!", state="complete")
    
    return pd.DataFrame(results)

# Main interface
if os.path.exists(PROMPT_FILE):
    df = pd.read_csv(PROMPT_FILE)
    st.info(f"Found {len(df)} prompts ready to process")
    
    with st.form("run_config"):
        st.subheader("Configure Run")
        
        # Model selection
        available_models = list(st.session_state.models.keys())
        selected_models = st.multiselect(
            "Select models to run",
            available_models,
            default=available_models
        )
        
        # Run count
        run_count = st.number_input("Number of runs per prompt", min_value=1, value=1)
        
        submitted = st.form_submit_button("Start Run")
        
        if submitted and selected_models:
            result_df = run_models(df, selected_models, run_count)
            
            if not result_df.empty:
                st.subheader("Results")
                st.dataframe(result_df, hide_index=True)
                save_results(result_df)
                st.success("Results saved successfully!")
else:
    st.error("No prompts file found. Please upload prompts in the Upload page first.")
