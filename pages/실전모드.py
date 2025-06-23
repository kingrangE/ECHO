import streamlit as st
import functions as f
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
import json
import os
from datetime import datetime
from time import sleep

st.set_page_config(
    page_title="실전모드",
    page_icon="🔥",
)

# 세션 상태 초기화
if 'chat_history_real' not in st.session_state:
    st.session_state.chat_history_real = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = None
if 'audio_to_play_b64' not in st.session_state:
    st.session_state.audio_to_play_b64 = None

# --- API 키 유효성 검사 및 리디렉션 ---
if not st.session_state.get("api_key"):
    st.warning("API 키가 설정되지 않았습니다. 메인 페이지로 이동합니다.")
    st.switch_page("app.py")
# 대화 기록 저장 디렉토리 설정
CONVERSATION_LOG_DIR = "conversation_logs"
os.makedirs(CONVERSATION_LOG_DIR, exist_ok=True) # 디렉토리가 없으면 생성

# --- 오디오 자동 재생 ---
if st.session_state.get("audio_to_play_b64"):
    st.html(f'<audio src="data:audio/mp3;base64,{st.session_state.audio_to_play_b64}" autoplay="true"></audio>')
    # 재생 후에는 다시 None으로 설정하여 반복 재생 방지
    st.session_state.audio_to_play_b64 = None


llm = ChatOpenAI(model='gpt-4.1-nano', api_key=st.session_state.api_key)
# 고정 크기 컨테이너를 위한 CSS 추가
st.markdown("""
<style>
.fixed-height-container {
    height: 800px;
    overflow-y: auto;
    border: 1px solid #e6e6e6;
    border-radius: 0.5rem;
    padding: 15px;
    margin-bottom: 20px;
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

def record_button_set(key_prefix):
    col1, col2 = st.columns(2)
    with col1:
        record_button = st.button('녹음 결과 전송', key=f"{key_prefix}_record", use_container_width=True, disabled=st.session_state.processing)
    with col2:
        quit_button = st.button('작업끝내기', key=f"{key_prefix}_quit", use_container_width=True, disabled=st.session_state.processing)

    return record_button, quit_button

st.title("NOVA - 실전 모드")
st.info("실전모드에서는 NOVA가 피드백을 주지 않아요. 영어로 대화해보세요!")

# 채팅 기록 표시
if len(st.session_state.chat_history_real) == 0:
    st.session_state.chat_history_real = f.real_chat_init(st.session_state.level)
    st.session_state.chat_history_real.append(AIMessage(f.start_question(llm, st.session_state.topic)))


f.display_chat_history(st.session_state.chat_history_real)


# 녹음 버튼이 클릭되면 채팅 기록에 메시지 추가 (예시)
audio_value = st.audio_input(
    "Talky의 질문에 영어로만 대답해주세요!",
    disabled=st.session_state.processing
)
if audio_value:
    st.session_state.audio_buffer = audio_value.getbuffer()

# 버튼 배치
record, quit = record_button_set("real")
if record:
    if st.session_state.audio_buffer and audio_value.size/100000 > 2:
        st.session_state.processing = True
        st.rerun()
    else : 
        # 음성파일이 없거나 너무 짧으면
        st.warning("잘못 녹음된 것 같아요! 녹음을 들어보고 다시 녹음해주세요!")


if quit:
    with st.spinner("최종 피드백을 생성 중입니다..."):
        feedback = f.final_feedback(llm, st.session_state.chat_history_real)
        
    st.subheader("📝 최종 대화 피드백")
    st.write(feedback)
        
    filename = f.save_final_feedback(feedback, st.session_state.chat_history_real, "real")
    st.success(f"대화 기록과 피드백이 저장되었습니다: {filename}")
    # 대화 기록 초기화 후 새로고침
    st.session_state.chat_history_real = []

if st.session_state.processing:
    with st.spinner("답변을 전송하는 중입니다..."):
        filepath = "audio.wav"
        try:
            with open(filepath, "wb") as file:
                file.write(st.session_state.audio_buffer)
            user_message = f.speech_to_text(api_key=st.session_state.api_key, audio_file_path=filepath)
            st.session_state.chat_history_real.append(HumanMessage(content=user_message))
            ai_response = f.continuation_question(llm, st.session_state.chat_history_real)
            st.session_state.chat_history_real.append(AIMessage(content=ai_response))
        except Exception as e:
            st.error(f"오디오 처리 중 오류가 발생했습니다: {e}")
        finally:
            st.session_state.processing = False
            st.session_state.audio_buffer = None
            audio_b64 = f.text_to_speech(api_key=st.session_state.api_key, text=ai_response)
            if audio_b64:
                st.session_state.audio_to_play_b64 = audio_b64
            st.rerun()