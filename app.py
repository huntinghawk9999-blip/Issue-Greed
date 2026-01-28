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

# 3. 데이터 로딩 (여기가 실패하면 화면에 경고 띄움)
file_path = 'issue.json'
if not os.path.exists(file_path):
    st.error("🚨 'issue.json' 파일이 없습니다! bot.py를 먼저 실행해주세요.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
except Exception as e:
    st.error(f"🚨 JSON 파일이 깨졌습니다: {e}")
    st.stop()

# 버튼 이름 안전하게 가져오기
blue_btn_text = new_data['blue_side'].get('button', '파란팀')
red_btn_text = new_data['red_side'].get('button', '빨간팀')

# =========================================================
# [중요] DB 연결 시도 (실패해도 일단 화면은 그리기 위해 분리함)
# =========================================================
vote_sheet = None
try:
    if "gcp_service_account" in st.secrets:
        key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        vote_sheet = client.open("fight_club_db").worksheet("시트1")
    else:
        st.warning("⚠️ Secrets 설정이 없습니다. 투표가 작동하지 않습니다.")
except Exception as e:
    st.error(f"⚠️ DB 연결 실패: {e}")

# =========================================================
# 4. 화면 그리기 (여기는 에러가 나도 무조건 실행됨)
# =========================================================
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio("페이지 이동", ["실시간 투표", "지난 투표 보기"])

if menu == "실시간 투표":
    # 제목 및 내용 표시
    st.markdown(f'<p class="big-font">{new_data["title"]}</p>', unsafe_allow_html=True)
    st.write(f"<h3 style='text-align: center;'>{new_data['subtitle']}</h3>", unsafe_allow_html=True)
    st.markdown("---")

    c1, c2, c3 = st.columns([4,1,4])
    with c1:
        html = "".join([f"<p>- {op}</p>" for op in new_data['blue_side']['opinions']])
        st.markdown(f'<div class="blue-box"><h3>{new_data["blue_side"]["title"]}</h3>{html}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<p class="vs-text">VS</p>', unsafe_allow_html=True)
    with c3:
        html = "".join([f"<p>- {op}</p>" for op in new_data['red_side']['opinions']])
        st.markdown(f'<div class="red-box"><h3>{new_data["red_side"]["title"]}</h3>{html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 투표 시스템 (DB 연결되었을 때만 표시)
    if vote_sheet:
        try:
            # 자동 아카이빙 로직
            current_issue = vote_sheet.acell('A2').value
            if current_issue and current_issue != new_data['title']:
                # 업데이트 로직 (간소화)
                vote_sheet.update_acell('A2', new_data['title'])
                vote_sheet.update_acell('B2', 0)
                vote_sheet.update_acell('C2', 0)
                st.rerun()

            # 투표 버튼
            vb = int(vote_sheet.acell('B2').value or 0)
            vr = int(vote_sheet.acell('C2').value or 0)
            
            st.header(f"📊 투표 현황 ({vb+vr}명)")
            col1, col2 = st.columns(2)
            
            if 'voted' not in st.session_state: st.session_state.voted = False
            
            with col1:
                if st.button(f"🔵 {blue_btn_text}", use_container_width=True, disabled=st.session_state.voted):
                    vote_sheet.update_acell('B2', vb+1)
                    st.session_state.voted = True
                    st.rerun()
            with col2:
                if st.button(f"🔴 {red_btn_text}", use_container_width=True, disabled=st.session_state.voted):
                    vote_sheet.update_acell('C2', vr+1)
                    st.session_state.voted = True
                    st.rerun()
            
            if vb+vr > 0: