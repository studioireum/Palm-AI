import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

# UI 설정
st.set_page_config(page_title="Palm AI Pro", layout="centered")

# CSS 가이드 디자인
st.markdown("""
    <style>
    .guide-box {
        border: 2px dashed #FF4B4B;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
        background-color: #f9f9f9;
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
        # 호환성을 위해 모델명 경로를 단순화함
        model = genai.GenerativeModel('gemini-1.5-flash')

        st.markdown('<div class="guide-box">📸 <b>[가이드]</b> 손바닥이 화면 중앙에 오도록 촬영해주세요.</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader("손바닥 사진을 업로드하세요 (Multiple Upload)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = []
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                img = ImageOps.exif_transpose(img) # 자동 회전 방지
                images.append(img)
                st.image(img, caption=f'업로드 완료: {uploaded_file.name}', use_column_width=True)
            
            if st.button("전문 분석 시작 (Start Professional Analysis)"):
                with st.spinner('AI 전문가가 정밀 분석 중...'):
                    try:
                        prompt = "당신은 수상학 전문가입니다. 이 사진을 분석하여 성격, 재물운, 건강에 대해 상세히 한국어로 알려주세요."
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 분석 결과")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요.")
