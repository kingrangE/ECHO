import streamlit as st
from utils.functions import navigate_to
from utils.supabase_function import upload_json_logs
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
import json
from datetime import datetime
from time import sleep

def show_final_feedback():
    st.markdown(st.session_state.final_feedback)
    col1,col2 = st.columns(2)
    with col1:
        go_main = st.button("메인 화면으로 이동",use_container_width=True)
        if go_main :
            st.session_state.chat_history_practice = ""
            navigate_to("main")
    with col2 :
        save = st.button("최종 피드백 및 대화기록 저장",use_container_width=True)
        serializable_chat_history = []
        if save :
            for msg in st.session_state.chat_history_practice:
                if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                    serializable_chat_history.append({"type": msg.type, "content": msg.content})
                else: # 기타 메시지 (예: st.info로 표시되는 SystemMessage)
                    serializable_chat_history.append({"type": "info", "content": str(msg)})
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "chat_history": serializable_chat_history,
                "final_feedback": st.session_state.final_feedback
            }
            try :
                #bucket에 저장하는 코드 upload_json_string(json.dumps(conversation_data),f"{st.session_state.user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_practice_mode.json")    
                upload_json_logs(st.session_state.user_id,f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_practice_mode.json",json.dumps(conversation_data))
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
            with st.empty():
                for i in range(3,0):
                    st.success(f"최종 피드백 및 대화기록이 저장되었습니다. {i}초 뒤 메인으로 이동합니다.")
                    sleep(1)
                st.session_state.chat_history_practice = ""
                navigate_to("main")