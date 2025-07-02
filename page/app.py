import streamlit as st
import os
import glob
import functions as f
import re
def show_main_page():
    """메인 페이지"""
    # 세션 상태 초기화
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'selected_log' not in st.session_state:
        st.session_state.selected_log = None
    if 'topic' not in st.session_state:
        st.session_state.topic = "자기소개"
    if 'level' not in st.session_state:
        st.session_state.level = "중"
    st.title("Talky")
    st.markdown("### 영어 대화 연습을 위한 AI 어시스턴트")
    st.markdown("""
    Talky는 영어 학습자를 위한 AI Agent입니다.
    두 가지 모드를 제공합니다:

    1. **연습 모드**: 한국어로 말하면 영어 표현을 안내해주고, 잘못된 영어는 수정해줍니다.
    2. **실전 모드**: 영어로만 대화하며 실전 감각을 키울 수 있습니다.

    시작하려면 API 키를 입력하고 사이드바에서 모드를 선택하세요.
    """)

    st.warning("올바르지 않은 API 키를 입력하거나 입력을 하지 않으시면 해당 페이지로 돌아옵니다.")
    # API 키 입력
    api_key = st.text_input(
        label="GPT API KEY",
        placeholder="sk-...",
        value=st.session_state.api_key,
        type="password"
    )

    # API 키 저장
    if api_key:
        st.session_state.api_key = api_key
        st.success("API 키가 저장되었습니다. 이제 사이드바에서 모드를 선택하세요.")

    # --- 선택된 로그 내용 표시 ---
    if st.session_state.selected_log:
        f.display_log_content(st.session_state.selected_log)
        # 다른 페이지로 이동했다가 돌아왔을 때도 로그가 계속 보이지 않도록 초기화
        st.session_state.selected_log = None
    st.sidebar.title("대화 설정")

    topic_options = ["자기소개", "여행", "식당", "비즈니스", "쇼핑", "일상"]
    level_options = ["상", "중", "하"]

    st.session_state.topic = st.sidebar.selectbox(
        "대화 주제를 선택하세요",
        topic_options,
        index=topic_options.index(st.session_state.topic)
    )

    st.session_state.level = st.sidebar.selectbox(
        "본인의 영어 실력을 선택하세요",
        level_options,
        index=level_options.index(st.session_state.level)
    )

    # --- 사이드바에 대화 기록 표시 ---
    st.sidebar.divider()
    st.sidebar.title("대화 기록")

    CONVERSATION_LOG_DIR = "conversation_logs"
    if os.path.exists(CONVERSATION_LOG_DIR):
        log_files = sorted(glob.glob(os.path.join(CONVERSATION_LOG_DIR, "*.json")), reverse=True)
        
        if not log_files:
            st.sidebar.write("저장된 기록이 없습니다.")
        else:
            for log_file in log_files:
                # 파일명에서 날짜 부분만 추출하여 버튼 레이블로 사용
                filename = os.path.basename(log_file)
                # "practice_conversation_..." 또는 "real_conversation_..." 접두사 제거
                label = re.sub(r'^(practice|real)_conversation_', '', filename)
                label = label.replace('.json', '')
                if st.sidebar.button(label, key=log_file, use_container_width=True):
                    st.session_state.selected_log = log_file
                    st.rerun()