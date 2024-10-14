import streamlit as st
from insight_tracker.auth import login, signup

def auth_section():
    st.title("Welcome to Insight Tracker")
    st.write("Please log in or sign up to continue.")
    
    login()
