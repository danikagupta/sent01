import os
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq


from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage

import pandas as pd

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
os.environ["GOOGLE_API_KEY"]=st.secrets["GEMINI_API_KEY"]
os.environ["XAI_API_KEY"]=st.secrets["XAI_API_KEY"]
os.environ["HUGGINGFACEHUB_API_TOKEN"]=st.secrets["HF_TOKEN"]
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

models={

    #"gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini"),
    #"claude-sonnet": ChatAnthropic(model="claude-3-5-sonnet-20240620"),
    #"gemini-1.5-pro": ChatGoogleGenerativeAI(model="gemini-1.5-pro"),

    #"grok-2-latest": ChatXAI(model="grok-2-latest"),
    #"llama": HuggingFaceEndpoint(repo_id="meta-llama/Llama-2-70b-chat-hf",task="text-generation",max_new_tokens=512,temperature=0.7),
    #"llama":ChatGroq(model="llama-3.3-70b-versatile"),
    "deepseek":ChatGroq(model="deepseek-r1-distill-llama-70b"),
    
    #"gpt-4o": ChatOpenAI(model="gpt-4o"),
    #"claude-haiku": ChatAnthropic(model="claude-3-haiku-20240307"),

}

def apply_model(model,user_input):
    try:
        user_message=HumanMessage(content=f"{user_input}")
        #system_message=SystemMessage(content=f"{prompt} Relevant Content:\n\n {ai_text}\n")
        #ai_message=SystemMessage(content=f"Relevant Content:\n\n {ai_text}\n")
        messages = [user_message]
        response=model.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error: {e}"

st.title("Sentio")
df = None

uploaded_file = st.file_uploader("Upload prompt file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Check the file type and read it into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type")
        df = None

if df is not None:
    with st.expander("Input prompts"):
        st.dataframe(df, hide_index=True)
    if st.button("Run"):
        for model_choice in models.keys():
            model_selected=models[model_choice]
            st.write(f"Running model: {model_choice}")
            for index,row in df.iterrows():
                user_input=row['Prompt']
                rsp = apply_model(model_selected,user_input)
                st.write(f"Record: {index=},{user_input=},{rsp=}")
                break
  
        #st.write("Completed all models")
        #df.to_csv("Sentio_outputs.csv",index=False)
        #with st.expander("Output"):
        st.dataframe(df, hide_index=True)
