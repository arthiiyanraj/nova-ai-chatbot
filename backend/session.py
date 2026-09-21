import streamlit as st


def initialize_session():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []


def login(user):

    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.current_session_id = None
    st.session_state.messages = []


def logout():

    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_session_id = None
    st.session_state.messages = []


def new_chat():

    st.session_state.current_session_id = None
    st.session_state.messages = []