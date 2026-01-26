import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 (모바일 친화적)
st.set_page_config(page_title="오늘의 여론 매치", layout="centered")

# 2. 스타일 설정 (다크모드 & 폰트)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:50px; color:yellow; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 10px; border-radius: 10px; color: black; }
    .blue-box { background-color: #ccccff; padding: 10px; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 3. 오늘의 주제 (나중에 윤준님이 여기만 바꾸면 됨)
match_title = "📢 금투세(금융투자소득세) 폐지"
match_subtitle = "개미를 위한 감세인가 vs 부자 감세인가?"

# 4. 화면 구성
st.markdown(f'<p class="big-font">{match_title}</p>', unsafe_allow_html=True)
st.write(f"<h3 style='text-align: center;'>{match_subtitle}</h3>", unsafe_allow_html=True)

st.markdown("---")

# 5. 좌우 대립 의견 보여주기
col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    st.markdown('<div class="blue-box"><h3>🔵 반대 / 민주당측</h3><p>- "초부자 감세일 뿐이다"<br>- "세수 부족 심각해진다"<br>- "소득 있는 곳에 세금 있다"</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="vs-text">VS</p>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="red-box"><h3>🔴 찬성 / 국힘측</h3><p>- "국내 증시 다 죽는다"<br>- "큰손 떠나면 개미도 손해"<br>- "코리아 디스카운트 해소"</p></div>', unsafe_allow_html=True)

st.markdown("---")

# 6. 투표 시스템 (임시 데이터)
if 'vote_blue' not in st.session_state:
    st.session_state.vote_blue = 1420
if 'vote_red' not in st.session_state:
    st.session_state.vote_red = 1680

st.header("🔥 당신의 생각은? (클릭하여 투표)")

# 투표 버튼
vote_col1, vote_col2 = st.columns(2)

with vote_col1:
    if st.button("🔵 반대 (세금 내야한다)", use_container_width=True):
        st.session_state.vote_blue += 1
        st.success("반대측에 한 표 행사하셨습니다!")

with vote_col2:
    if st.button("🔴 찬성 (폐지 해야한다)", use_container_width=True):
        st.session_state.vote_red += 1
        st.success("찬성측에 한 표 행사하셨습니다!")

# 7. 실시간 결과 그래프
total = st.session_state.vote_blue + st.session_state.vote_red
blue_per = int((st.session_state.vote_blue / total) * 100)
red_per = int((st.session_state.vote_red / total) * 100)

st.write(f"### 📊 실시간 스코어 (총 {total}명 참여)")
st.progress(blue_per)
st.caption(f"🔵 반대 {blue_per}% vs 🔴 찬성 {red_per}%")

# 댓글 유도 문구
st.info("💡 투표 후 아래 댓글로 싸워주세요! (욕설 시 AI가 자동 삭제)")