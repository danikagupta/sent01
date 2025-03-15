import streamlit as st
from utils import ensure_data_directory

# Initialize the app
st.set_page_config(
    page_title="LLM Comparison",
    page_icon="🤖",
    layout="centered"
)

# Create data directory if it doesn't exist
ensure_data_directory()

# Main page content
st.title("LLM Comparison Tool")
st.write("Compare responses from different LLMs using a structured workflow")

# Navigation guide
st.header("📋 How to Use")

st.markdown("""
1. **Upload Prompts** (📤)
   - Go to the Upload page
   - Upload your CSV file containing prompts
   - Preview and verify your prompts

2. **Run Models** (🚀)
   - Select which models to run
   - Set the number of runs per prompt
   - Monitor progress in real-time

3. **Download Results** (📥)
   - Access both local and Firestore results
   - Filter and download results as needed
   - Clear old results when desired
""")

# Additional information
st.sidebar.success("Select a page from the sidebar to get started!")

st.markdown("---")
st.markdown("""
### 📝 Notes
- Make sure your CSV file has a 'Prompt' column
- Results are saved both locally and to Firestore (if configured)
- You can track progress in real-time during model runs
""")

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
