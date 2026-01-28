import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

st.set_page_config(page_title="오늘의 여론 매치", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:40px; color:orange; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .blue-box { background-color: #ccccff; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

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

# 데이터 로딩
file_path = 'issue.json'
if not os.path.exists(file_path):
    st.warning("⚠️ 주제가 없습니다. bot.py를 실행해주세요.")
    st.stop()

with open(file_path, 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 버튼 이름 안전장치 (옛날 데이터 호환용)
blue_btn_text = new_data['blue_side'].get('button', '🔵 파란팀')
red_btn_text = new_data['red_side'].get('button', '🔴 빨간팀')

# 자동 아카이빙
try:
    vote_sheet = get_sheet("시트1")
    current_db_issue = vote_sheet.acell('A2').value
    
    if current_db_issue and (current_db_issue != new_data['title']):
        st.toast("🔄 새 주제 반영 중...")
        history_sheet = get_sheet("History")
        blue_v = vote_sheet.acell('B2').value or 0
        red_v = vote_sheet.acell('C2').value or 0
        now_str = datetime.now().strftime("%Y-%m-%d")
        history_sheet.append_row([now_str, current_db_issue, "지난 이슈", blue_v, red_v])
        
        vote_sheet.update_acell('A2', new_data['title'])
        vote_sheet.update_acell('B2', 0)
        vote_sheet.update_acell('C2', 0)
        time.sleep(1)
        st.rerun()
except: pass

# 화면 구성
st.sidebar.title("🔥 싸움 구경")
menu = st.sidebar.radio("이동", ["현재 진행 중인 매치", "명예의 전당"])

if menu == "현재 진행 중인 매치":
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
    
    # [수정된 부분] 동적 버튼 이름 적용
    try:
        vb = int(vote_sheet.acell('B2').value or 0)
        vr = int(vote_sheet.acell('C2').value or 0)
        
        st.header(f"📊 투표 현황 ({vb+vr}명)")
        col1, col2 = st.columns(2)
        
        if 'voted' not in st.session_state: st.session_state.voted = False
        
        with col1:
            # 버튼 이름에 blue_btn_text 변수 사용
            if st.button(f"🔵 {blue_btn_text}", use_container_width=True, disabled=st.session_state.voted):
                vote_sheet.update_acell('B2', vb+1)
                st.session_state.voted = True
                st.rerun()
        with col2:
            # 버튼 이름에 red_btn_text 변수 사용
            if st.button(f"🔴 {red_btn_text}", use_container_width=True, disabled=st.session_state.voted):
                vote_sheet.update_acell('C2', vr+1)
                st.session_state.voted = True
                st.rerun()
                
        if vb+vr > 0:
            bp = int(vb/(vb+vr)*100)
            st.progress(bp)
            st.caption(f"🔵 {blue_btn_text}: {bp}%  VS  🔴 {red_btn_text}: {100-bp}%")
            
    except: st.error("DB 연결 중...")

    # 댓글 (버튼 이름 반영)
    st.markdown("---")
    st.subheader("🗣️ 댓글 토론")
    
    with st.form("c_form", clear_on_submit=True):
        # 라디오 버튼 이름도 동적으로 변경
        team = st.radio("어느 편?", [f"🔵 {blue_btn_text}", f"🔴 {red_btn_text}"], horizontal=True)
        msg = st.text_input("내용")
        if st.form_submit_button("등록") and msg:
            try:
                cs = get_sheet("시트2")
                cs.append_row([datetime.now().strftime("%m-%d %H:%M"), team, msg, new_data['title']])
                st.success("등록 완료")
                st.rerun()
            except: pass

    try:
        cs = get_sheet("시트2")
        rows = cs.get_all_records()
        my_comments = [r for r in rows if str(r.get('topic')) == new_data['title']]
        for r in reversed(my_comments):
            bg = "#ccccff" if "🔵" in r['team'] else "#ffcccc"
            st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
    except: pass

elif menu == "명예의 전당":
    st.header("🏛️ 지난 이슈 기록관")
    try:
        hs = get_sheet("History")
        records = hs.get_all_records()
        if not records: st.info("기록 없음")
        else:
            titles = [f"[{r['date']}] {r['title']}" for r in records]
            choice = st.selectbox("선택", titles)
            selected = next(r for r in records if f"[{r['date']}] {r['title']}" == choice)
            
            st.markdown("---")
            st.subheader(selected['title'])
            st.metric("결과", f"🔵 {selected['blue_vote']} vs 🔴 {selected['red_vote']}")
            
            st.subheader("그때 그 댓글들")
            cs = get_sheet("시트2")
            past_comments = [r for r in cs.get_all_records() if str(r.get('topic')) == selected['title']]
            for r in reversed(past_comments):
                bg = "#ccccff" if "🔵" in r['team'] else "#ffcccc"
                st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
    except: pass