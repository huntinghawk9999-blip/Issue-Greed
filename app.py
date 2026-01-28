import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론 매치", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:40px; color:orange; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    .blue-box { background-color: #ccccff; padding: 15px; border-radius: 10px; color: black; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 구글 시트 연결
@st.cache_resource
def get_google_client():
    # Secrets에서 키 가져오기
    key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_google_client()
    return client.open("fight_club_db").worksheet(sheet_name)

# 4. 데이터 로딩 및 [자동 창고 정리] 로직
file_path = 'issue.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
else:
    st.error("데이터가 없습니다.")
    st.stop()

# [핵심] 주제가 바뀌었으면 과거 기록을 History 시트로 이사 보냄
try:
    vote_sheet = get_sheet("시트1")
    current_db_issue = vote_sheet.acell('A2').value
    
    # DB(시트)에 적힌 주제와, 방금 파일(issue.json)로 들어온 주제가 다르면? -> "새 이슈 발생!"
    if current_db_issue != new_data['title']:
        try:
            history_sheet = get_sheet("History")
            blue_v = vote_sheet.acell('B2').value or 0
            red_v = vote_sheet.acell('C2').value or 0
            now_str = datetime.now().strftime("%Y-%m-%d")
            
            # History 시트에 저장: [날짜, 제목, 부제, 파랑득표, 빨강득표]
            history_sheet.append_row([now_str, current_db_issue, "지난 이슈", blue_v, red_v])
        except Exception as e:
            pass # History 시트가 없거나 에러나면 일단 패스

        # 투표판 초기화 (새 주제로 교체)
        vote_sheet.update_acell('A2', new_data['title'])
        vote_sheet.update_acell('B2', 0)
        vote_sheet.update_acell('C2', 0)
        st.rerun() # 새로고침해서 반영

except Exception as e:
    pass # DB 연결 전이면 패스

# ==========================================
# 5. 사이드바 (메뉴 선택)
# ==========================================
st.sidebar.title("🔥 싸움 구경")
menu = st.sidebar.radio("이동", ["현재 진행 중인 매치", "명예의 전당 (과거 기록)"])

# ==========================================
# A. 현재 매치 페이지
# ==========================================
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
    
    # 투표 기능
    try:
        vote_sheet = get_sheet("시트1")
        vb = int(vote_sheet.acell('B2').value or 0)
        vr = int(vote_sheet.acell('C2').value or 0)
        
        st.header(f"📊 실시간 투표 현황 (총 {vb+vr}명)")
        col1, col2 = st.columns(2)
        
        if 'voted' not in st.session_state: st.session_state.voted = False
        
        with col1:
            if st.button("🔵 왼쪽 팀 투표", use_container_width=True, disabled=st.session_state.voted):
                vote_sheet.update_acell('B2', vb+1)
                st.session_state.voted = True
                st.rerun()
        with col2:
            if st.button("🔴 오른쪽 팀 투표", use_container_width=True, disabled=st.session_state.voted):
                vote_sheet.update_acell('C2', vr+1)
                st.session_state.voted = True
                st.rerun()
                
        if vb+vr > 0:
            bp = int(vb/(vb+vr)*100)
            st.progress(bp)
            st.caption(f"🔵 {bp}%  VS  🔴 {100-bp}%")
            
    except:
        st.error("DB 연결 대기중...")

    # 댓글 시스템
    st.markdown("---")
    st.subheader("🗣️ 댓글 토론")
    
    with st.form("c_form", clear_on_submit=True):
        team = st.radio("팀 선택", ["🔵파랑팀", "🔴빨강팀"], horizontal=True)
        msg = st.text_input("내용")
        if st.form_submit_button("등록") and msg:
            try:
                cs = get_sheet("시트2")
                # [시간, 팀, 내용, 주제] 순서로 저장
                cs.append_row([datetime.now().strftime("%m-%d %H:%M"), team, msg, new_data['title']])
                st.success("등록 완료")
                st.rerun()
            except: pass

    # 댓글 보여주기 (현재 주제만 필터링)
    try:
        cs = get_sheet("시트2")
        rows = cs.get_all_records()
        # 'topic' 헤더가 없으면 에러날 수 있으므로 안전장치
        my_comments = [r for r in rows if str(r.get('topic')) == new_data['title']]
        
        for r in reversed(my_comments):
            bg = "#ccccff" if "파랑" in r['team'] else "#ffcccc"
            st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
    except: pass

# ==========================================
# B. 명예의 전당 (과거 기록) 페이지
# ==========================================
elif menu == "명예의 전당 (과거 기록)":
    st.header("🏛️ 지난 이슈 기록관")
    
    try:
        hs = get_sheet("History")
        records = hs.get_all_records()
        
        if not records:
            st.info("아직 저장된 과거 기록이 없습니다.")
        else:
            # 선택 상자 만들기
            titles = [f"[{r['date']}] {r['title']}" for r in records]
            choice = st.selectbox("보고 싶은 과거 이슈를 선택하세요", titles)
            
            # 선택한 이슈 데이터 찾기
            selected = next(r for r in records if f"[{r['date']}] {r['title']}" == choice)
            
            st.markdown("---")
            st.subheader(selected['title'])
            st.metric("최종 결과", f"🔵 {selected['blue_vote']} vs 🔴 {selected['red_vote']}")
            
            # 승자 표시
            if selected['blue_vote'] > selected['red_vote']:
                st.success("🏆 파란팀 승리!")
            elif selected['blue_vote'] < selected['red_vote']:
                st.error("🏆 빨간팀 승리!")
            else:
                st.warning("🤝 무승부")
                
            st.markdown("---")
            st.subheader("그때 그 댓글들")
            
            cs = get_sheet("시트2")
            all_comments = cs.get_all_records()
            # 과거 주제와 일치하는 댓글만 가져오기
            past_comments = [r for r in all_comments if str(r.get('topic')) == selected['title']]
            
            if not past_comments:
                st.write("작성된 댓글이 없습니다.")
            
            for r in reversed(past_comments):
                bg = "#ccccff" if "파랑" in r['team'] else "#ffcccc"
                st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"기록을 불러오지 못했습니다. (History 시트가 있는지 확인해주세요) : {e}")