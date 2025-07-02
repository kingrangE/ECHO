from supabase import create_client, Client
import streamlit as st
from json import dumps
import os

url:str = st.secrets["SUPABASE"]["URL"]
key:str = st.secrets["SUPABASE"]["KEY"]
supabase: Client = create_client(url, key)

resp = supabase.storage.from_("test").upload("user1/test.json","conversation_logs/test.json")
print(resp)