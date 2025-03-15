import os
import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

PROMPT_FILE = 'data/prompts.csv'
RESULT_FILE = 'data/results.csv'

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def initialize_models():
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.secrets["HF_TOKEN"]
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

    models = {
        "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini"),
        "claude-sonnet": ChatAnthropic(model="claude-3-5-sonnet-20240620"),
        "gemini-1.5-pro": ChatGoogleGenerativeAI(model="gemini-1.5-pro"),
        "grok-2-latest": ChatXAI(model="grok-2-latest"),
        "llama": ChatGroq(model="llama-3.3-70b-versatile"),
        "deepseek": ChatGroq(model="deepseek-r1-distill-llama-70b"),
    }
    return models

def apply_model(model, user_input):
    try:
        start_time = datetime.now().timestamp()
        user_message = HumanMessage(content=f"{user_input}")
        messages = [user_message]
        response = model.invoke(messages)
        end_time = datetime.now().timestamp()
        elapsed_time = end_time - start_time
        return response.content, elapsed_time
    except Exception as e:
        return f"Error: {e}", 0

def save_results(result_df):
    if result_df is not None and not result_df.empty:
        if os.path.exists(RESULT_FILE):
            result_df.to_csv(RESULT_FILE, mode='a', index=False, header=False)
        else:
            result_df.to_csv(RESULT_FILE, index=False)

def load_results():
    if os.path.exists(RESULT_FILE):
        return pd.read_csv(RESULT_FILE)
    return None

def clear_results():
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)

def ensure_data_directory():
    os.makedirs('data', exist_ok=True)
