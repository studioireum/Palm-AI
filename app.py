import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

st.set_page_config(page_title="Palm AI Pro", layout="centered")

# API 키 불러오기 (환경 변수 우선, 없으면 입력창)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 가장 안정적인 기본 모델명 사용
        model = genai.GenerativeModel('gemini-1.5-flash')

        st.title("✋ AI 수상 분석 마스터 Pro")
        st.markdown("---")

        uploaded_files = st.file_uploader("손바닥 사진을 업로드하세요", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = []
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                img = ImageOps.exif_transpose(img)
                images.append(img)
                st.image(img, use_column_width=True)
            
            if st.button("전문 분석 시작 (Start Analysis)"):
                with st.spinner('분석 중...'):
                    try:
                        response = model.generate_content(["이 손금 사진을 상세히 분석해서 한국어로 리포트해줘."] + images)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"모델 호출 오류: {e}")
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("사이드바에 API 키를 입력하거나 Secrets에 등록해주세요.")
