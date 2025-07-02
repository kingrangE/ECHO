import streamlit as st
def initialize():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'is_api_key_editable' not in st.session_state:
        st.session_state.is_api_key_editable = st.session_state.api_key == ""
    if 'page' not in st.session_state:
        st.session_state.page = "set_api_key"
    if 'level' not in st.session_state:
        st.session_state.level = "1"
    if 'topic' not in st.session_state:
        st.session_state.topic = "일상 대화"
    if 'final_feedback' not in st.session_state:
        st.session_state.final_feedback = ""
    if 'access_token' not in st.session_state:
        st.session_state.access_token = ""
    if 'chat_history_practice' not in st.session_state:
        st.session_state.chat_history_practice = []
    if 'phase' not in st.session_state:
        st.session_state.phase = True 
    