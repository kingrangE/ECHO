import streamlit as st
from utils.functions import navigate_to
def show_main_page():
    st.title("Talky")
    st.subheader("""나에게 딱 맞춘 회화 선생님 Talky""",divider="orange")
    st.markdown("""### MENU""")
    
    practice = st.button("회화 연습 모드",use_container_width=True)
    if practice :
        navigate_to("practice")
    history = st.button("과거 기록 확인하기",use_container_width=True)
    if history :
        navigate_to("history")
    setting = st.button("주제 및 레벨 설정하기",use_container_width=True)
    if setting :
        navigate_to("setting")
    survey = st.button("API KEY 설정하기",use_container_width=True)
    if survey :
        navigate_to("set_api_key")
    comment = st.button("후기 및 건의사항 남기기",use_container_width=True)
    if comment : 
        navigate_to("review")
    OPIc = st.button("OPIc 시험 모드",use_container_width=True)
    if OPIc :
        st.info("오픈 준비중입니다!")
    now_me = st.button("지금 나는?",use_container_width=True)
    if now_me :
        st.info("오픈 준비중입니다!")