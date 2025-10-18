# session_storage.py
import streamlit as st  
import time

def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def add_message(role, content):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.chat_history.append({"role": role, "content": content, "time": timestamp})

def get_chat_history():
    return st.session_state.get("chat_history", [])
