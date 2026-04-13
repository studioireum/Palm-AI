import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

# UI 설정
st.set_page_config(page_title="Palm AI Pro", layout="centered")

# CSS 가이드 디자인 (성공 꿀팁 반영)
st.markdown("""
    <style>
    .guide-box {
        border: 2px dashed #FF4B4B;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        background-color: #ffffff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✋ AI 수상 분석 마스터 Pro")

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("Settings (설정)")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("API 키는 서버에 저장되지 않습니다.")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 검증된 최신 모델명 사용
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        st.markdown('<div class="guide-box">📸 <b>[촬영 가이드]</b><br>손바닥이 화면 중앙에 꽉 차도록 촬영해 주세요.<br>(그림자가 생기지 않게 밝은 곳에서 찍으면 더 정확합니다)</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader("손바닥 사진을 업로드하세요 (최대 3장)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = []
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                img = ImageOps.exif_transpose(img) # 사진 회전 문제 해결
                images.append(img)
                st.image(img, caption=f'업로드 완료: {uploaded_file.name}', use_column_width=True)
            
            if st.button("전문 분석 시작 (Start Professional Analysis)"):
                with st.spinner('AI 전문가가 데이터를 분석 중입니다...'):
                    try:
                        prompt = "당신은 전문 수상학자입니다. 사진을 보고 성격, 재물운, 미래 전략을 굵은 글씨를 섞어 한국어로 상세히 리포트해주세요."
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 정밀 분석 리포트")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요.")
