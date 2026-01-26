import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(page_title="오늘의 여론 매치", layout="centered")

# 2. 스타일 설정
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight:bold; text-align:center; }
    .vs-text { font-size:50px; color:yellow; text-align:center; font-weight:bold; }
    .red-box { background-color: #ffcccc; padding: 10px; border-radius: 10px; color: black; }
    .blue-box { background-color: #ccccff; padding: 10px; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 불러오기 (여기가 핵심!)
# issue.json 파일이 있으면 읽고, 없으면 기본값 표시
file_path = 'issue.json'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    st.error("뉴스 데이터 파일이 없습니다!")
    st.stop()

# 4. 화면 구성 (데이터 연동)
st.markdown(f'<p class="big-font">{data["title"]}</p>', unsafe_allow_html=True)
st.write(f"<h3 style='text-align: center;'>{data['subtitle']}</h3>", unsafe_allow_html=True)

st.markdown("---")

# 5. 좌우 대립 의견 (JSON 데이터 활용)
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

# 6. 투표 시스템 (DB 연결 전이라 임시)
st.header("🔥 당신의 생각은?")
v_col1, v_col2 = st.columns(2)
with v_col1:
    st.button("🔵 왼쪽 편들기", use_container_width=True)
with v_col2:
    st.button("🔴 오른쪽 편들기", use_container_width=True)
