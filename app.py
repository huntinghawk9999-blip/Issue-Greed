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
    .news-card { 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0;
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .news-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .news-title { font-weight: bold; color: #1f77b4; text-decoration: none; font-size: 16px; }
    .news-source { color: #666; font-size: 12px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로딩
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

blue_btn_text = new_data['blue_side'].get('button', '파란팀')
red_btn_text = new_data['red_side'].get('button', '빨간팀')
# [NEW] 파이썬이 찾아온 진짜 링크 목록
real_news_list = new_data.get('real_news', [])

# =========================================================
# DB 연결
# =========================================================
@st.cache_resource
def get_google_client():
    if "gcp_service_account" not in st.secrets:
        return None
    key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_google_client()
    if not client: return None
    try:
        return client.open("fight_club_db").worksheet(sheet_name)
    except: return None

# =========================================================
# 4. 화면 그리기
# =========================================================
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio("페이지 이동", ["실시간 투표", "지난 투표 보기"])

if menu == "실시간 투표":
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

    # 투표 시스템
    vote_sheet = get_sheet("시트1")
    
    if vote_sheet:
        try:
            current_issue = vote_sheet.acell('A2').value
            if current_issue and current_issue != new_data['title']:
                history_sheet = get_sheet("History")
                if history_sheet:
                    try:
                        blue_v = vote_sheet.acell('B2').value or 0
                        red_v = vote_sheet.acell('C2').value or 0
                        now_str = datetime.now().strftime("%Y-%m-%d")
                        history_sheet.append_row([now_str, current_issue, "지난 이슈", blue_v, red_v])
                    except: pass
                vote_sheet.update_acell('A2', new_data['title'])
                vote_sheet.update_acell('B2', 0)
                vote_sheet.update_acell('C2', 0)
                st.rerun()

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
                bp = int(vb/(vb+vr)*100)
                st.progress(bp)
                st.caption(f"{blue_btn_text} {bp}% vs {red_btn_text} {100-bp}%")
                
        except Exception as e:
            st.error(f"투표 시스템 오류: {e}")
    else:
        st.warning("DB 연결 대기 중...")

    # [NEW] 진짜 뉴스 링크 섹션
    if real_news_list:
        st.markdown("---")
        st.subheader("📰 관련 기사 (자동 수집)")
        
        n_cols = st.columns(3) # 3열 배치
        
        for idx, news in enumerate(real_news_list):
            target_col = n_cols[idx % 3]
            with target_col:
                # 카드 형태의 디자인 적용
                st.markdown(f"""
                    <div class="news-card">
                        <a href="{news['url']}" target="_blank" class="news-title">{news['title']}</a>
                        <div class="news-source">🔍 키워드: {news['keyword']}</div>
                    </div>
                """, unsafe_allow_html=True)

    # 댓글 시스템
    st.markdown("---")
    st.subheader("💬 의견 나누기")
    
    with st.form("c_form", clear_on_submit=True):
        team = st.radio("입장 선택", [f"🔵 {blue_btn_text}", f"🔴 {red_btn_text}"], horizontal=True)
        msg = st.text_input("메시지 입력")
        if st.form_submit_button("등록") and msg:
            cs = get_sheet("시트2")
            if cs:
                try:
                    cs.append_row([datetime.now().strftime("%m-%d %H:%M"), team, msg, new_data['title']])
                    st.success("등록되었습니다.")
                    st.rerun()
                except: st.error("등록 실패")

    cs = get_sheet("시트2")
    if cs:
        try:
            rows = cs.get_all_records()
            my_comments = [r for r in rows if str(r.get('topic')) == new_data['title']]
            for r in reversed(my_comments):
                bg = "#ccccff" if "🔵" in r['team'] else "#ffcccc"
                st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
        except: pass

elif menu == "지난 투표 보기":
    st.header("📂 지난 투표 기록")
    hs = get_sheet("History")
    if hs:
        try:
            records = hs.get_all_records()
            if not records:
                st.info("저장된 기록이 없습니다.")
            else:
                titles = [f"[{r['date']}] {r['title']}" for r in records]
                choice = st.selectbox("조회할 주제 선택", titles)
                selected = next(r for r in records if f"[{r['date']}] {r['title']}" == choice)
                
                st.markdown("---")
                st.subheader(selected['title'])
                st.metric("최종 결과", f"🔵 {selected['blue_vote']} vs 🔴 {selected['red_vote']}")
                
                # 지난 기록에서도 댓글 보기
                st.subheader("당시 의견들")
                cs = get_sheet("시트2")
                if cs:
                    past_comments = [r for r in cs.get_all_records() if str(r.get('topic')) == selected['title']]
                    if not past_comments: st.write("등록된 의견이 없습니다.")
                    for r in reversed(past_comments):
                        bg = "#ccccff" if "🔵" in r['team'] else "#ffcccc"
                        st.markdown(f"<div style='background:{bg};padding:10px;margin:5px;border-radius:5px;'><b>{r['team']}</b>: {r['comment']}<br><small>{r['time']}</small></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"기록 조회 오류: {e}")
    else:
        st.error("History 시트 없음")