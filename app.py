import streamlit as st
import hashlib
from page.sign import show_auth_page
from page.set_api_key import show_set_api_key_page
from page.main import show_main_page
from page.survey.set_survey import show_survey_page
from page.practice import show_practice_page
from page.final_feedback import show_final_feedback
from page.history import show_users_history
from page.review_page import show_review
from page.setting import show_setting_page
from utils.initialize import initialize
from PIL import Image
# 페이지 설정
talky_logo = Image.open('image.ico')
st.set_page_config(
    page_title="Talky - English Conversation AI Agent",
    page_icon= talky_logo,
    layout="centered"
)

# session initialize
initialize()

def main():
    """메인 애플리케이션"""
    page_map={
        "set_api_key" : show_set_api_key_page,
        "main" : show_main_page,
        "survey" : show_survey_page,
        "practice" : show_practice_page,
        "final_feedback" : show_final_feedback,
        "history": show_users_history,
        "review" : show_review,
        "setting" : show_setting_page
    }
    # 로그인 상태에 따른 페이지 분기
    if not st.session_state.logged_in:
        # 로그인되지 않은 경우: 인증 페이지만 표시 
        show_auth_page()
    else:
        # 로그인된 경우: 메인 페이지 표시 
        page_map[st.session_state.page]()

if __name__ == "__main__":
    main()