import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

st.set_page_config(page_title="Palm AI Pro", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # [검증 로직] 사용 가능한 모델 중 flash 모델을 자동으로 찾음
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # flash가 포함된 모델 중 가장 최신 모델 선택, 없으면 첫 번째 모델 사용
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        
        model = genai.GenerativeModel(model_name=target_model)

        st.title("✋ AI 수상 분석 마스터 Pro")
        st.info(f"사용 중인 모델: {target_model}") # 어떤 모델로 연결되었는지 표시

        uploaded_files = st.file_uploader("손바닥 사진 업로드", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            for img in images:
                st.image(img, use_column_width=True)
            
            if st.button("전문 분석 시작 (Start Analysis)"):
                with st.spinner('분석 중...'):
                    try:
                        response = model.generate_content(["이 손바닥 사진을 보고 성격과 재물운을 한국어로 분석해줘."] + images)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"모델 목록 확인 실패: {e}. API 키를 확인해주세요.")
else:
    st.warning("Secrets에 GEMINI_API_KEY를 등록해주세요.")
