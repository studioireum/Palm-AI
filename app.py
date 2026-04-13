import streamlit as st
import google.generativeai as genai
from PIL import Image

# UI 설정
st.set_page_config(page_title="Palm AI Master", layout="centered")
st.title("✋ AI 수상 분석 마스터 (MVP)")
st.write("사진을 업로드하면 AI가 당신의 수상을 분석합니다.")

# API 키 설정 (사이드바)
with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("API 키는 서버에 저장되지 않습니다.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 파일 업로드
    uploaded_file = st.file_uploader("손바닥 사진을 업로드하세요 (Upload Palm Photo)", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='업로드된 이미지', use_column_width=True)
        
        if st.button("분석 시작 (Start Analysis)"):
            with st.spinner('AI가 수상을 분석 중입니다...'):
                try:
                    prompt = """
                    이 손바닥 사진을 수상학 전문가의 관점에서 분석해줘.
                    1. 전체적인 성향 (방형, 철학수형 등)
                    2. 주요 손금 (생명선, 지능선, 감정선)의 특징
                    3. 재물운과 미래의 성공 전략
                    4. 건강 및 조언
                    답변은 친절하고 전문적인 톤으로 한국어로 작성해줘.
                    """
                    response = model.generate_content([prompt, image])
                    st.subheader("🔍 분석 결과 (Analysis Result)")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요.")
