import streamlit as st
from utils.functions import navigate_to
def show_survey_page():
    st.title("설문조사 페이지")
    col1,col2=st.columns(2)
    with col1 :
        back = st.button("뒤로가기",use_container_width=True)
        if back : 
            navigate_to("main")
    with col2 :
        start = st.button("시작하기",use_container_width=True)
        if back : 
            navigate_to("survey_1")