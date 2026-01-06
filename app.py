import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

API_URL = os.getenv("LANGFLOW_API_URL")
API_TOKEN = os.getenv("LANGFLOW_API_TOKEN")

# --- Page Configuration ---
st.set_page_config(
    page_title="Chatbot Informasi Universitas Widyatama",
    page_icon="🤖",
    layout="centered"
)

# --- Helper Functions ---
def run_flow(message):
    """
    Sends the user message to the LangFlow API and returns the JSON response.
    """
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": message,
    }
    
    # Headers configured from .env as requested
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_TOKEN
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}
    except ValueError as e:
        return {"error": f"Parsing Error: {str(e)}"}

def extract_message(response_json):
    """
    Parses the LangFlow JSON response to find the actual text output.
    """
    try:
        if "error" in response_json:
            return response_json["error"]
            
        # Standard LangFlow response traversal
        if "outputs" in response_json:
            flow_outputs = response_json["outputs"][0]
            first_component_output = flow_outputs["outputs"][0]
            result_data = first_component_output["results"]
            
            if "message" in result_data:
                return result_data["message"].get("text", "")
            if "text" in result_data:
                return result_data["text"]

        return f"Could not parse response. Raw: {json.dumps(response_json)}"
        
    except Exception as e:
        return f"Error processing response: {str(e)}"

# --- UI Layout ---
st.title("☺ Chatbot Informasi Universitas Widyatama")
st.caption("Tanyakan kepada saya terkait akademik dan kemahasiswaan")

# --- Chat Input Handler (Stateless / No History) ---
if prompt := st.chat_input("Type a message..."):
    
    # Display the user's current question
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and display the bot's response immediately
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            api_response = run_flow(prompt)
            bot_text = extract_message(api_response)
            st.markdown(bot_text)