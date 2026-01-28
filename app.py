import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론", layout="wide")

# 2. 스타일 설정 (박스 색상은 유지하되 톤앤매너만 깔끔하게)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:40px; color:gray; text-align:center; font-weight:bold; } 
    .red-box { background-color: #ffcccc; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .blue-box { background-color: #ccccff; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 구글 시트 연결
@st.cache_resource
def get_google_client():
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets 설정이 필요합니다.")
        st.stop() 
    key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_google_client()
    try:
        return client.open("fight_club_db").worksheet(sheet_name)
    except: return None

# 4. 데이터 로딩
file_path = 'issue.json'
if not os.path.exists(file_path):
    st.warning("⚠️ 현재 진행 중인 투표가 없습니다.")
    st.stop()

with open(file_path, 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 버튼 이름 가져오기
blue_btn_text = new_data['blue_side'].get('button', '파란팀')
red_btn_text = new_data['red_side'].get('button', '빨간팀')

# 5. 자동 아카이빙 (지난 기록 저장)
try:
    vote_sheet = get_sheet("시트1")
    current_db_issue = vote_sheet.acell('A2').value
    
    # 주제가 바뀌었으면 지난 기록으로 이동
    if current_db_issue and (current_db_issue != new_data['title']):
        st.toast("🔄 새로운 투표 주제를 불러오는 중...")
        history_sheet = get_sheet("History")
        blue_v = vote_sheet.acell('B2').value or 0
        red_v = vote_sheet.acell('C2').value or 0
        now_str = datetime.now().strftime("%Y-%m-%d")
        history_sheet.append_row([now_str, current_db_issue, "지난 이슈", blue_v, red_v])
        
        # 투표판 초기화
        vote_sheet.update_acell('A2', new_data['title'])
        vote_sheet.update_acell('B2', 0)
        vote_sheet.update_acell('C2', 0)
        time.sleep(1)
        st.rerun()
except: pass

# ==========================================
# 6. 사이드바 (메뉴 구성 - 순화된 버전)
# ==========================================
st.sidebar.title("📌 메뉴") # '싸움 구경' -> '메뉴'로 변경
#