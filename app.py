import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:40px; color:gray; text-align:center; font-weight:bold; } 
    .red-box { background-color: #ffcccc; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .blue-box { background-color: #ccccff; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 구글 시트 연결 (안전장치 추가)
@st.cache_resource
def get_google_client():
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets 설정이 필요합니다.")
        st.stop() 
    key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)