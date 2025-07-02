import streamlit as st
import os
from supabase import create_client, Client

def get_user_info(supabase,user_id):
    return supabase.table("user_info").select("*").eq("user_id", user_id).execute()

def show_auth_page():
    
    url:str = st.secrets["SUPABASE"]["URL"]
    key:str = st.secrets["SUPABASE"]["KEY"]
    supabase: Client = create_client(url, key)

    st.header("Talky-English Conversation AI Agent")

    tab1, tab2 = st.tabs(["SignIn", "SignUp"])
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            email = st.text_input("Email",placeholder="사용하시는 이메일을 적어주세요.")
            password = st.text_input("Password",placeholder="8자 이상 15자 미만의 비밀번호를 작성해주세요.",type="password")
            submit = st.form_submit_button("Submit",use_container_width=True)
            if submit:
                try :
                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password,
                        }
                    )
                    user_id = response.user.id
                    existing_user = get_user_info(supabase,user_id)
                    # 첫 로그인이라면 users 테이블에 데이터 삽입
                    if len(existing_user.data) == 0:
                        supabase.table("user_info").insert({
                            "user_id": user_id,
                            "api_key": "",
                            "purchase": False
                        }).execute()
                        existing_user = get_user_info(supabase,user_id)
                    st.success("로그인 성공")
                    st.session_state.logged_in =True
                    st.session_state.api_key = existing_user.data[0]["api_key"]
                    st.session_state.user_id = user_id
                    st.rerun()                    
                except Exception as e:
                    st.error(f"Error {e}")
                

    with tab2:
        st.subheader("회원가입")
        with st.form("register_form"):
            email = st.text_input("Email",placeholder="사용하시는 이메일을 적어주세요.")
            password = st.text_input("Password",placeholder="8자 이상 15자 미만의 비밀번호를 작성해주세요.",type="password")
            submit = st.form_submit_button("Submit",use_container_width=True)
            if submit:
                try :
                    response = supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password,
                        }
                    )
                    st.success("회원가입 성공")
                except Exception as e:
                    st.error(f"다음의 이유로 회원 가입에 실패하였습니다. {e}")