import streamlit as st
import functions as f
from utils.functions import navigate_to
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_openai import ChatOpenAI
from datetime import datetime
from time import sleep
import os

def show_practice_page():
    # 세션 상태 초기화
    if not st.session_state.get("api_key"):
        st.warning("API 키가 설정되지 않았습니다. 메인 페이지로 이동합니다.")
        st.switch_page("app.py")

    llm = ChatOpenAI(model='gpt-4.1-nano', api_key=st.session_state.api_key)


    # --- 오디오 자동 재생 ---
    if st.session_state.get("audio_to_play_b64"):
        st.html(f'<audio src="data:audio/mp3;base64,{st.session_state.audio_to_play_b64}" autoplay="true"></audio>')
        # 재생 후에는 다시 None으로 설정하여 반복 재생 방지
        st.session_state.audio_to_play_b64 = None

    st.markdown("""
    <style>
    .fixed-height-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
        padding: 15px;
        margin-bottom: 20px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    def submit_button_set(key_prefix):
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.button('답변 전송', key=f"{key_prefix}_submit", use_container_width=True, disabled=st.session_state.processing)
        with col2:
            quit_button = st.button('작업 끝내기', key=f"{key_prefix}_quit", use_container_width=True, disabled=st.session_state.processing)


        return submit_button, quit_button

    def retry_button_set(key_prefix):
        col1, col2 = st.columns(2)
        with col1:
            retry_button = st.button('다시 답변 전송', key=f"{key_prefix}_retry", use_container_width=True, disabled=st.session_state.processing)
        with col2:
            continue_button = st.button('다음 질문받기', key=f"{key_prefix}_continue", use_container_width=True, disabled=st.session_state.processing)

        return retry_button, continue_button

    st.title("Talky - 연습 모드")
    st.info("연습모드에서는 Talky에게 한국어로 말하면 영어 표현을 안내해주고 " \
            "만약 잘못된 영어로 말해도 의도에 맞게 수정하여 답변해줘요.")

    # 채팅 기록 표시
    if len(st.session_state.chat_history_practice) == 0:
        st.session_state.processing = False
        st.session_state.chat_history_practice = f.practice_chat_init(st.session_state.level)
        st.session_state.chat_history_practice.append(AIMessage(f.start_question(llm, st.session_state.topic)))
        st.session_state.chat_history_practice.append(HumanMessage(f.answer_guide(llm, st.session_state.chat_history_practice[-1].content)))

    f.display_chat_history(st.session_state.chat_history_practice)

    audio_value = st.audio_input(
        "Talky의 질문에 한국어 또는 영어로 편하게 말해보세요!",
        disabled=st.session_state.processing
    )
    if audio_value:
        st.session_state.audio_buffer = audio_value.getbuffer()
    if st.session_state.phase :    
        submit, quit = submit_button_set("practice")
        if submit:
            st.session_state.chat_history_practice.pop() # 답변 가이드 제거
            try:
                if st.session_state.audio_buffer and audio_value.size/100000 > 2:
                    st.session_state.processing = True
                    st.rerun()
                else : 
                    st.warning("잘못 녹음된 것 같아요! 녹음을 들어보고 다시 녹음해주세요!")
            except Exception as e:
                st.error(f"잘못 녹음된 것 같아요! 녹음을 들어보고 다시 녹음해주세요!")
            
        if quit:
            st.session_state.processing = True
            with st.spinner("최종 피드백을 생성 중입니다..."):
                feedback = f.final_feedback(llm, st.session_state.chat_history_practice)
                st.session_state.final_feedback = feedback
                # filename = f.save_final_feedback(feedback, st.session_state.chat_history_practice, "practice")
                # st.success(f"대화 기록과 피드백이 저장되었습니다: {filename}")
                # 대화 기록 초기화 후 새로고침
                
                navigate_to("final_feedback")
    else : 
        retry,continue_button = retry_button_set("practice")
        if retry:
            st.session_state.chat_history_practice.pop() # 이전 답변
            st.session_state.chat_history_practice.pop() # 이전 피드백 제거

            if st.session_state.audio_buffer and audio_value.size/100000 > 2:
                st.session_state.processing = True
                st.rerun()
            else : 
                st.warning("잘못 녹음된 것 같아요! 녹음을 들어보고 다시 녹음해주세요!")

        if continue_button:
            st.session_state.phase = True
            ai_response = f.continuation_question(llm,st.session_state.chat_history_practice)
            audio_b64 = f.text_to_speech(api_key=st.session_state.api_key, text=ai_response)
            if audio_b64:
                st.session_state.audio_to_play_b64 = audio_b64
            st.session_state.chat_history_practice.append(AIMessage(ai_response))
            st.session_state.chat_history_practice.append(HumanMessage(f.answer_guide(llm, st.session_state.chat_history_practice[-1].content)))
            st.session_state.processing = False
            st.rerun()

    back = st.button("메인 화면으로 이동",use_container_width=True,disabled=st.session_state.processing)
    if back :
        navigate_to("main")


    if st.session_state.processing:
        with st.spinner("답변을 생성하는 중입니다..."):
            filepath = "audio.wav"
            try:
                with open(filepath, "wb") as file:
                    file.write(st.session_state.audio_buffer)
                user_message = f.speech_to_text(api_key=st.session_state.api_key, audio_file_path=filepath)
                st.session_state.chat_history_practice.append(HumanMessage(content=user_message))
                ai_response = f.correct(llm, st.session_state.chat_history_practice)
                st.session_state.chat_history_practice.append(SystemMessage(content=ai_response))
                st.session_state.phase = False
            except Exception as e:
                st.error(f"오디오 처리 중 오류가 발생했습니다: {e}")
            finally:
                st.session_state.processing = False
                st.session_state.audio_buffer = None
                os.remove(filepath)
                st.rerun()
