import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론 매치", layout="centered")

# 2. 스타일 설정
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:50px; color:yellow; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 10px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .blue-box { background-color: #ccccff; padding: 10px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .comment-box { border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 구글 시트 연결 함수
def get_google_sheet(sheet_name):
    try:
        key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        # sheet_name에 따라 1번 시트(투표) 또는 2번 시트(댓글)를 엽니다.
        return client.open("fight_club_db").worksheet(sheet_name)
    except Exception as e:
        return None

# 4. 데이터(JSON) 불러오기
file_path = 'issue.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    st.error("뉴스 데이터 파일이 없습니다!")
    st.stop()

# 5. 화면 구성 (뉴스)
st.markdown(f'<p class="big-font">{data["title"]}</p>', unsafe_allow_html=True)
st.write(f"<h3 style='text-align: center;'>{data['subtitle']}</h3>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([4, 1, 4])
with col1:
    opinions_html = "".join([f"<p>- {op}</p>" for op in data['blue_side']['opinions']])
    st.markdown(f'<div class="blue-box"><h3>{data["blue_side"]["title"]}</h3>{opinions_html}</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="vs-text">VS</p>', unsafe_allow_html=True)

with col3:
    opinions_html = "".join([f"<p>- {op}</p>" for op in data['red_side']['opinions']])
    st.markdown(f'<div class="red-box"><h3>{data["red_side"]["title"]}</h3>{opinions_html}</div>', unsafe_allow_html=True)

st.markdown("---")

# 6. 투표 시스템
try:
    vote_sheet = get_google_sheet("시트1") # 투표는 1번 시트
    
    current_issue = data['title']
    saved_issue = vote_sheet.acell('A2').value
    
    if saved_issue != current_issue:
        vote_sheet.update_acell('A2', current_issue)
        vote_sheet.update_acell('B2', 0)
        vote_sheet.update_acell('C2', 0)
        vote_blue = 0
        vote_red = 0
    else:
        vote_blue = int(vote_sheet.acell('B2').value or 0)
        vote_red = int(vote_sheet.acell('C2').value or 0)

    st.header(f"🔥 실시간 여론 (총 {vote_blue + vote_red}명 참여)")

    v_col1, v_col2 = st.columns(2)
    
    if 'voted' not in st.session_state:
        st.session_state.voted = False

    with v_col1:
        if st.button("🔵 왼쪽 지지", use_container_width=True, disabled=st.session_state.voted):
            vote_sheet.update_acell('B2', vote_blue + 1)
            st.session_state.voted = True
            st.rerun()

    with v_col2:
        if st.button("🔴 오른쪽 지지", use_container_width=True, disabled=st.session_state.voted):
            vote_sheet.update_acell('C2', vote_red + 1)
            st.session_state.voted = True
            st.rerun()

    # 결과 그래프
    total = vote_blue + vote_red
    if total > 0:
        blue_per = int((vote_blue / total) * 100)
        red_per = 100 - blue_per
        st.progress(blue_per)
        st.caption(f"🔵 {data['blue_side']['title']}: {blue_per}%  vs  🔴 {data['red_side']['title']}: {red_per}%")

except Exception as e:
    st.error("투표 서버 연결 중...")

st.markdown("---")

# 7. 댓글 시스템 (NEW!)
st.subheader("🗣️ 난장판 (댓글 토론)")

# 댓글 입력창
with st.form("comment_form", clear_on_submit=True):
    # 누구 편인지 선택
    team = st.radio("어느 편?", ["🔵 왼쪽 팀", "🔴 오른쪽 팀"], horizontal=True)
    user_input = st.text_input("한마디 (엔터 치면 등록됨)")
    submitted = st.form_submit_button("등록")

    if submitted and user_input:
        try:
            comment_sheet = get_google_sheet("시트2") # 댓글은 2번 시트
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            # 시트에 한 줄 추가 (시간, 팀, 내용)
            comment_sheet.append_row([now, team, user_input])
            st.success("등록되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"저장 실패: {e}")

# 댓글 보여주기 (최신순)
try:
    comment_sheet = get_google_sheet("시트2")
    # 모든 댓글 가져오기
    records = comment_sheet.get_all_records()
    
    # 최신순으로 뒤집기
    for row in reversed(records):
        color = "#ccccff" if "왼쪽" in row['team'] else "#ffcccc"
        st.markdown(f"""
        <div style="background-color:{color}; padding:10px; border-radius:5px; margin-bottom:5px;">
            <small>{row['time']}</small><br>
            <b>{row['comment']}</b>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.info("아직 댓글이 없습니다. 첫 댓글을 남겨주세요!")