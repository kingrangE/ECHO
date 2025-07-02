import streamlit as st
from utils.functions import navigate_to
from supabase import create_client, Client

def update_api_key(api_key):
    url:str = st.secrets["SUPABASE"]["URL"]
    key:str = st.secrets["SUPABASE"]["KEY"]
    supabase: Client = create_client(url, key)
    user_id = st.session_state.user_id
    supabase.table("user_info").update({"api_key": api_key}).eq("user_id", user_id).execute()

def show_set_api_key_page():
    st.markdown("### Talky 이용을 위해선 API KEY 입력이 필요해요.")
    st.warning("올바르지 않은 API KEY를 입력하시거나 입력을 하지 않으시면 이용을 할 수 없어요.")
    
    if st.session_state.api_key == "":
        st.session_state.is_api_key_editable = True
    st.markdown("#")
    api_key = st.text_input(
        label="GPT API KEY",
        value=st.session_state.api_key,
        type="password",
        disabled = not st.session_state.is_api_key_editable
    )
    
    if st.session_state.api_key and not st.session_state.is_api_key_editable:
        # API 키가 이미 존재하고 편집 불가능한 상태일 때 "변경" 버튼 표시
        if st.button("변경",use_container_width=True):
            st.session_state.is_api_key_editable = True
    else:
        # API 키가 없거나 편집 가능한 상태일 때 "저장" 버튼 표시
        if st.button("저장",use_container_width=True):
            if api_key:
                st.session_state.api_key = api_key
                st.session_state.is_api_key_editable = False
                update_api_key(api_key)
                st.success("API 키가 저장되었습니다.")
            else:
                st.error("API 키를 입력해주세요.")
    next = st.button("Talky와 대화하러 가기",use_container_width=True)
    if next :
        navigate_to("main")
    