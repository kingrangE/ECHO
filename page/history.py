import json
import streamlit as st
from utils.functions import navigate_to
from utils.supabase_function import load_json_logs
from functions import display_log_content
from datetime import datetime
import re

def extract_datetime_from_filename(filename):
    # 파일명에서 날짜 패턴 추출 (예: practice_conversation_20250702_123456.json)
    pattern = r'(\d{8}_\d{6})'
    match = re.search(pattern, filename)
    
    if match:
        date_str = match.group(1)
        try:
            # 날짜 문자열을 datetime 객체로 변환
            return datetime.strptime(date_str, '%Y%m%d_%H%M%S')
        except ValueError:
            # 날짜 형식이 맞지 않으면 최소값 반환
            return datetime.min
    return datetime.min  # 날짜 형식이 없으면 최소값 반환

def show_users_history():
    st.header("Talky와의 추억")
    st.subheader("처음 만났을 땐 영어 못하던 내가 어느새...", divider="orange")
    
    responses = load_json_logs(st.session_state.user_id)
    
    back = st.button("메인 화면으로 이동", use_container_width=True)
    if back:
        navigate_to("main")
    
    try:
        if responses and hasattr(responses, 'data') and responses.data:
            # 날짜 기준으로 정렬 (최신순)
            sorted_response = sorted(
                responses.data, 
                key=lambda x: extract_datetime_from_filename(x.get("filename", "")), 
                reverse=True  # True면 최신순, False면 오래된순
            )
            
            for resp in sorted_response:
                name = resp["filename"]
                json_data = resp["payload"]
                
                # JSON 문자열을 파싱
                if isinstance(json_data, str):
                    json_data = json.loads(json_data)
                
                # 파일명에서 날짜 추출하여 표시
                date_match = re.search(r'(\d{8}_\d{6})', name)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        date_obj = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        formatted_date = date_obj.strftime('%Y년 %m월 %d일 %H:%M:%S')
                        display_name = f"{formatted_date} - {name.split('_')[0]}"  # 날짜와 대화 유형 표시
                    except ValueError:
                        display_name = name
                else:
                    display_name = name
                
                with st.expander(display_name):
                    display_log_content(json_data)
        else:
            st.info("아직 대화 기록이 없습니다. Talky와 대화를 시작해보세요!")
    except Exception as e:
        st.error(f"대화 기록을 불러오는 중 오류가 발생했습니다: {e}")
        print(e)