import streamlit as st
import requests
import uuid
import json
import os
from streamlit_google_auth import Authenticate

st.set_page_config(
    page_title="Enterprise MCP AI Assistant",
    page_icon="🤖",
    layout="centered"
)

WEBHOOK_URL = "https://n8n.srv1542745.hstgr.cloud/webhook/8f34b1ef-3ceb-4045-8e5e-b4e2ea746914/chat"

FILE_UPLOAD_WEBHOOK = "https://n8n.srv1542745.hstgr.cloud/webhook/upload-file"

credentials_data = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "project_id": "enterprise-mcp-saas-devaprasad",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "redirect_uris": [
            st.secrets["REDIRECT_URI"]
        ]
    }
}

os.makedirs(".streamlit", exist_ok=True)

with open(".streamlit/google_credentials.json", "w") as f:
    json.dump(credentials_data, f)

authenticator = Authenticate(
    secret_credentials_path=".streamlit/google_credentials.json",
    cookie_name="mcp_ai_cookie",
    cookie_key="mcp_ai_key",
    redirect_uri=st.secrets["REDIRECT_URI"],
)

authenticator.check_authentification()

if not st.session_state.get("connected"):

    st.title("🤖 Enterprise MCP AI Assistant")

    st.info("Please sign in with Google to continue.")

    authenticator.login()

    st.stop()

user_info = st.session_state.get("user_info", {})

st.sidebar.success(
    f"Signed in as:\n{user_info.get('email', 'Unknown')}"
)

if st.sidebar.button("Logout"):

    authenticator.logout()

    st.rerun()

st.title("🤖 Enterprise MCP AI Assistant")

st.markdown("""
Ask questions using your MCP-powered n8n AI Agent.

Examples:

- When is Roland Garros 2026?
- Send an email to John
- Create a calendar event
- Read rows from Sales Tracker sheet
- Upload this file to Google Drive
- Read a Google Doc
- Search latest AI news
""")

question = st.text_area(
    "Ask your question",
    height=180
)

uploaded_file = st.file_uploader(
    "Upload a file (optional)"
)

if st.button("Submit"):

    if not question.strip() and uploaded_file is None:

        st.warning("Please enter a question or upload a file.")

        st.stop()

    try:

        if uploaded_file is not None:

            with st.spinner("Uploading file to Google Drive..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                data = {
                    "question": question,
                    "userEmail": user_info.get("email"),
                    "sessionId": str(uuid.uuid4())
                }

                response = requests.post(
                    FILE_UPLOAD_WEBHOOK,
                    files=files,
                    data=data,
                    timeout=120
                )

            if response.status_code == 200:

                st.success("File uploaded successfully")

                try:

                    result = response.json()

                    if isinstance(result, dict):

                        if "output" in result:

                            st.write(result["output"])

                        else:

                            st.json(result)

                    else:

                        st.write(result)

                except Exception:

                    st.write(response.text)

            else:

                st.error(f"HTTP Error {response.status_code}")

                st.code(response.text)

        else:

            payload = {
                "action": "sendMessage",
                "sessionId": str(uuid.uuid4()),
                "chatInput": question,
                "userEmail": user_info.get("email")
            }

            with st.spinner("Thinking..."):

                response = requests.post(
                    WEBHOOK_URL,
                    json=payload,
                    timeout=120
                )

            if response.status_code == 200:

                try:

                    data = response.json()

                    st.success("Response received")

                    if isinstance(data, dict):

                        if "output" in data:

                            st.write(data["output"])

                        else:

                            st.json(data)

                    else:

                        st.write(data)

                except Exception:

                    st.write(response.text)

            else:

                st.error(f"HTTP Error {response.status_code}")

                st.code(response.text)

    except Exception as e:

        st.error(str(e))