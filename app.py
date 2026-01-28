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

# 3. 데이터 로딩 (파일 확인)
file_path = 'issue.json'
if not os.path.exists(file_path):
    st.error("🚨 'issue.json' 파일이 없습니다! bot.py를 먼저 실행해주세요.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        new_data =