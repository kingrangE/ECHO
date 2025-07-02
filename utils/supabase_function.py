from supabase import create_client, Client
import streamlit as st
from json import dumps
import os
import tempfile
from io import BytesIO
from datetime import datetime
from pytz import timezone
def get_supabase_client():
    """Supabase 클라이언트를 생성하고 반환합니다."""
    url: str = st.secrets["SUPABASE"]["URL"]
    key: str = st.secrets["SUPABASE"]["KEY"]
    supabase: Client = create_client(url, key)
    return supabase
# def upload_logs(user_id, file_path):
#     resp = supabase.storage.from_("conversation-logs").upload(f"{user_id}/{file_path}",file_path)
#     return resp

# JSON 문자열을 직접 업로드하는 함수
def upload_json_string(json_string, path):
    try:
        supabase = get_supabase_client()
        #임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file.write(json_string.encode('utf-8'))
            temp_file_path = temp_file.name
        
        response = (
            supabase.storage
            .from_("conversation-logs")
            .upload(
                path=path,
                file=temp_file_path,
            )
        )
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        return response
    except Exception as e:
        return {"error": str(e)}

def upload_json_logs(user_id,filename,json_data):
    try : 
        supabase = get_supabase_client()
        response = supabase.table("user_history").insert({
                                "user_id": user_id,
                                "filename": filename,
                                "payload": json_data
                            }).execute()
    except Exception as e:
        st.error(f"Error {e}")

def upload_review(user_id,content):
    try : 
        supabase = get_supabase_client()
        seoul_timezone = timezone('Asia/Seoul')
        current_time = datetime.now(seoul_timezone)
        formatted_time = current_time.isoformat()
        
        response = supabase.table("review").insert({
                                "user_id": user_id,
                                "content" : content,
                                "created_at": formatted_time  # 현재 시간 추가
                        }).execute()
    except Exception as e:
        st.error(f"Error {e}")

def load_json_logs(user_id):
    try : 
        supabase = get_supabase_client()
        response = supabase.table("user_history").select("*").eq("user_id", user_id).execute()
        return response
    except Exception as e:
        print(e)

def load_review():
    try : 
        supabase = get_supabase_client()
        response = supabase.table("review").select("*").execute()
        print(response)
        return response
    except Exception as e:
        print(e)

if __name__=="__main__":
    # test_json = '{"name": "test", "value": 123}'
    # print(upload_json_string(test_json, "direct_upload/test.json"))

    print(load_json_logs("f64fb355-9590-417c-9af7-8abf12d189f7"))
    