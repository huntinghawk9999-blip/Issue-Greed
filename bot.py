import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론 매치", layout="centered")

# 2. 스타일 설정 (디자인)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:50px; color:yellow; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 10px; border-radius: 10px; color: black; }
    .blue-box { background-color: #ccccff; padding: 10px; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 3. 구글 시트 연결 함수 (비밀 금고 사용)
def get_google_sheet():
    # Streamlit Secrets에서 아까 저장한 키를 가져옵니다.
    # [샌드위치 방식]으로 저장했으므로 변수명 gcp_service_account를 씁니다.
    key_dict = json.loads(st.secrets["gcp_service_account"], strict=False)
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    
    # 시트 열기 (이름이 틀리면 에러납니다!)
    sheet = client.open("fight_club_db").sheet1
    return sheet

# 4. 데이터(JSON) 불러오기
file_path = 'issue.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    st.error("뉴스 데이터 파일이 없습니다!")
    st.stop()

# 5. 화면 구성 (뉴스 내용 표시)
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

# 6. 실시간 투표 시스템 (DB 연동)
try:
    sheet = get_google_sheet()
    
    # 현재 투표값 읽어오기
    # A2: 이슈제목, B2: 파랑득표, C2: 빨강득표
    current_issue = data['title']
    saved_issue = sheet.acell('A2').value
    
    # 이슈가 바뀌었으면 투표 초기화 (새로운 주제가 올라왔을 때)
    if saved_issue != current_issue:
        sheet.update_acell('A2', current_issue)
        sheet.update_acell('B2', 0)
        sheet.update_acell('C2', 0)
        vote_blue = 0
        vote_red = 0
    else:
        # 값이 없으면 0으로 처리
        vote_blue = int(sheet.acell('B2').value or 0)
        vote_red = int(sheet.acell('C2').value or 0)

    st.header(f"🔥 실시간 여론 (총 {vote_blue + vote_red}명 참여)")

    # 투표 버튼 및 로직
    v_col1, v_col2 = st.columns(2)
    
    # [중복 클릭 방지] 한 번 누르면 버튼 비활성화
    if 'voted' not in st.session_state:
        st.session_state.voted = False

    with v_col1:
        if st.button("🔵 왼쪽 지지", use_container_width=True, disabled=st.session_state.voted):
            new_vote = vote_blue + 1
            sheet.update_acell('B2', new_vote) # 구글 시트에 저장
            st.session_state.voted = True
            st.rerun()

    with v_col2:
        if st.button("🔴 오른쪽 지지", use_container_width=True, disabled=st.session_state.voted):
            new_vote = vote_red + 1
            sheet.update_acell('C2', new_vote) # 구글 시트에 저장
            st.session_state.voted = True
            st.rerun()

    # 결과 그래프 보여주기
    total = vote_blue + vote_red
    if total > 0:
        blue_per = int((vote_blue / total) * 100)
        red_per = 100 - blue_per
        st.progress(blue_per)
        st.caption(f"🔵 {data['blue_side']['title']}: {blue_per}%  vs  🔴 {data['red_side']['title']}: {red_per}%")
    else:
        st.info("아직 투표한 사람이 없습니다. 첫 번째 투표자가 되어주세요!")

except Exception as e:
    st.error(f"DB 연결 오류: {e}")
    st.info("💡 힌트: Streamlit Secrets 설정을 확인하거나, 구글 시트 공유가 '편집자'로 되어있는지 보세요.")