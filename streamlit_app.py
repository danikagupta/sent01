import os
import streamlit as st
import uuid

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq

from pydantic.v1 import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage

import pandas as pd

import time
from datetime import datetime
from pathlib import Path

# Import Firebase configuration
from firebase_config import initialize_firebase, upload_to_firestore, get_all_firestore_records

PROMPT_FILE='data/prompts.csv'
RESULT_FILE='data/results.csv'
current_date = datetime.now().strftime("%Y-%m-%d")

def initialize_models():

    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    os.environ["GOOGLE_API_KEY"]=st.secrets["GEMINI_API_KEY"]
    os.environ["XAI_API_KEY"]=st.secrets["XAI_API_KEY"]
    os.environ["HUGGINGFACEHUB_API_TOKEN"]=st.secrets["HF_TOKEN"]
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

    models={

        "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini"),
        "claude-sonnet": ChatAnthropic(model="claude-3-5-sonnet-20240620"),
        "gemini-1.5-pro": ChatGoogleGenerativeAI(model="gemini-1.5-pro"),

        "grok-2-latest": ChatXAI(model="grok-2-latest"),
        #"llama": HuggingFaceEndpoint(repo_id="meta-llama/Llama-2-70b-chat-hf",task="text-generation",max_new_tokens=512,temperature=0.7),
        "llama":ChatGroq(model="llama-3.3-70b-versatile"),
        "deepseek":ChatGroq(model="deepseek-r1-distill-llama-70b"),
        
        #"gpt-4o": ChatOpenAI(model="gpt-4o"),
        #"claude-haiku": ChatAnthropic(model="claude-3-haiku-20240307"),

    }
    return models


def apply_model(model,user_input):
    try:
        start_time=time.time()
        user_message=HumanMessage(content=f"{user_input}")
        messages = [user_message]
        response=model.invoke(messages)
        end_time=time.time()
        elapsed_time=end_time-start_time
        return response.content, elapsed_time
    except Exception as e:
        return f"Error: {e}",0

def upload_result_to_firestore(model_name, prompt, response, elapsed_time):
    """Upload a single result to Firestore"""
    data = {
        'id': str(uuid.uuid4()),
        'model': model_name,
        'prompt': prompt,
        'response': response,
        'time_seconds': elapsed_time,
        'timestamp': datetime.now().isoformat(),
        'date': current_date
    }
    return upload_to_firestore(data)
    
def read_file_from_ui_or_fs():
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload a prompt file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df.to_csv(PROMPT_FILE,index=False)
        return df
    else:
        if os.path.exists(PROMPT_FILE):
            df=pd.read_csv(PROMPT_FILE)
            return df
    return None

def show_download_sidebar():
    file_path = Path(RESULT_FILE)

    with st.sidebar:
        st.divider()
        st.subheader("Downloads")
        
        # Local file download
        if file_path.exists():
            st.markdown("**Current Run Results**")
            custom_filename = st.text_input("Local results filename", value="complete_set.csv")
            with open(RESULT_FILE, "rb") as file:
                file_bytes = file.read()
            st.download_button(
                label="Download Local Results",
                data=file_bytes,
                file_name=custom_filename,
                mime="text/csv",
            )
            if st.button("Clear local file"):
                os.remove(RESULT_FILE)
        
        # Firestore records download
        st.markdown("**Firestore Database Records**")
        firebase_filename = st.text_input("Firestore results filename", value="firestore_records.csv")
        if st.button("Download Firestore Records"):
            # Initialize Firebase if not already initialized
            if initialize_firebase():
                records = get_all_firestore_records()
                if records:
                    df = pd.DataFrame(records)
                    # Convert timestamp to string for CSV export
                    if 'timestamp' in df.columns:
                        df['timestamp'] = df['timestamp'].astype(str)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Firestore CSV",
                        data=csv,
                        file_name=firebase_filename,
                        mime="text/csv",
                        key="firebase_download"
                    )
                    st.write("Preview of Firestore Records:")
                    st.dataframe(df, hide_index=True)
                else:
                    st.warning("No records found in Firestore database")
            else:
                st.error("Failed to initialize Firebase. Please check your credentials.")


def save_results(count,result_df):
    if count>0:
        if os.path.exists(RESULT_FILE):
            result_df.to_csv(RESULT_FILE,mode='a', index=False, header=False)
        else:
            result_df.to_csv(RESULT_FILE, index=False)

def run_all_models(df,model_list,run_count):
    update_ui.write(f"Starting run with {run_count=} for {models=}")
    current_count=0
    total_count=run_count*len(model_list)*df.shape[0]
    progress_bar=st.progress(current_count)
    results=[]
    total_start_time = time.time()
    
    # Initialize Firebase for Firestore uploads
    firebase_enabled = initialize_firebase()
    if firebase_enabled:
        st.sidebar.success("Firebase connection established. Results will be uploaded to Firestore.")
    else:
        st.sidebar.warning("Firebase connection not established. Results will only be saved locally.")
    
    # Load previous results if they exist
    previous_results = None
    if os.path.exists(RESULT_FILE):
        previous_results = pd.read_csv(RESULT_FILE)
        st.subheader("Previous Results")
        st.dataframe(previous_results, hide_index=True)

    with st.spinner("Running...", show_time=True):
        for i in range(1,run_count+1):
            for model_choice in model_list.keys():
                for _,row in df.iterrows():
                    user_input=row['Prompt']
                    update_ui.write(f"Completed {current_count}/{total_count} steps. {i=}, {model_choice=}, {user_input=}")
                    rsp,elapsed_time = apply_model(models[model_choice],user_input)
                    results.append({'model':model_choice,'prompt':user_input,'response':rsp,'time_seconds':elapsed_time,'current_date':current_date})
                    
                    # Upload to Firestore
                    if firebase_enabled:
                        upload_success = upload_result_to_firestore(model_choice, user_input, rsp, elapsed_time)
                        if upload_success:
                            update_ui.write(f"Uploaded result to Firestore: {model_choice} - {user_input[:30]}...")
                    
                    current_count+=1
                    progress_bar.progress( (1.0*current_count) / total_count)

    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time
    
    update_ui.write(f"All done!! Total time taken: {total_elapsed_time:.2f} seconds")
    result_df=pd.DataFrame(results)
    st.subheader("Current Run Results")
    st.dataframe(result_df,hide_index=True)
    save_results(current_count,result_df)

#
# Main
#

st.title("Sentio")
update_ui=st.empty()
df = read_file_from_ui_or_fs()
models=initialize_models()

# Add Firebase configuration to secrets.toml if not already present
if 'FIREBASE_CONFIG_ADDED' not in st.session_state:
    with st.sidebar.expander("Firebase Configuration", expanded=False):
        st.write("To enable Firestore uploads, add the following fields to your .streamlit/secrets.toml file:")
        st.code("""
        # Firebase Configuration
        FIREBASE_PROJECT_ID = "your-project-id"
        FIREBASE_PRIVATE_KEY_ID = "your-private-key-id"
        FIREBASE_PRIVATE_KEY = "your-private-key"
        FIREBASE_CLIENT_EMAIL = "your-client-email"
        FIREBASE_CLIENT_ID = "your-client-id"
        FIREBASE_CLIENT_X509_CERT_URL = "your-cert-url"
        """)
    st.session_state['FIREBASE_CONFIG_ADDED'] = True

    
if df is not None:
    with st.sidebar.expander("Prompts"):
        st.dataframe(df, hide_index=True)
    options = st.sidebar.multiselect('Models',options=list(models.keys()),default=list(models.keys()))
    model_list={key:models[key] for key in options}
    run_count=st.sidebar.number_input("Runs",min_value=1,max_value=100, value=1)
    if st.sidebar.button("Run"):
        run_all_models(df,model_list,run_count)
show_download_sidebar()


  

