import streamlit as st



def home():
    name = st.session_state.username
    st.title(f"Welcome to LinkedOut, {name}")

    st.subheader("Recommended for you: ")
    