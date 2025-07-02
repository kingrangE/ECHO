import streamlit as st
from utils.functions import navigate_to

def show_setting_page():
    st.title("Talky와 대화하기 위한 레벨 및 주제 설정")

    level = st.radio("본인의 영어 회화 수준은?",["1","2","3"],index=int(st.session_state.level) - 1,horizontal=True)
    st.markdown("""
                영어 수준이 아닌 회화 수준을 묻는 것입니다.
                - 1 : 초등학교 수준의 영어 회화 가능 (OPIc IM1-2)
                - 2 : 중,고등학교 수준의 영어 회화 가능 (OPIc IM3)
                - 3 : 대학교 수준 이상의 영어 회화 가능 (OPIc IH,AL)
                """)
    st.divider()
    topic = st.text_input("원하는 주제를 입력해주세요.",value=st.session_state.topic,label_visibility="visible")
    st.divider()
    save = st.button("저장",use_container_width=True)
    if save :
        print(topic)
        st.session_state.level = level
        st.session_state.topic = topic
        navigate_to("main")