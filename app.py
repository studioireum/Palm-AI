import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

st.set_page_config(page_title="Palm AI Pro", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 모델 자동 선택 로직 (최신 flash 모델 우선)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)

        st.title("✋ AI 통합 수상 분석 (Pro)")
        st.markdown("""
        **[정밀 분석을 위한 사진 가이드]**
        1. **첫 번째 사진:** 손등이나 손가락을 접어 **손톱 모양**이 잘 보이게 찍어주세요.
        2. **두 번째 사진:** 손바닥을 쫙 펴서 **손금**이 잘 보이게 찍어주세요.
        """)

        uploaded_files = st.file_uploader("사진을 2장 이상 업로드하세요", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            cols = st.columns(len(images))
            for i, img in enumerate(images):
                cols[i].image(img, caption=f"사진 {i+1}", use_column_width=True)
            
            if st.button("통합 정밀 분석 시작"):
                with st.spinner('손톱의 기질과 손바닥의 운세를 통합 분석 중...'):
                    try:
                        # 두 장의 사진을 분석하는 정교한 프롬프트
                        prompt = """
                        당신은 수상학 및 관상학 전문가입니다. 제공된 사진들을 통합 분석하세요.
                        1. 손톱 사진이 있다면: 손톱의 모양, 색택을 통해 타고난 기질과 건강, 에너지를 분석하세요.
                        2. 손바닥 사진이 있다면: 생명선, 지능선, 감정선 및 구(Hill)의 발달 정도를 분석하세요.
                        3. 결론: 위 두 요소를 결합하여 이 사람의 현재 상태와 미래 성공 전략을 한국어로 상세히 리포트하세요.
                        핵심 내용은 굵게(Bold) 표시하고 전문 용어는 괄호 안에 쉬운 설명을 덧붙이세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 전문가 통합 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("Secrets에 GEMINI_API_KEY를 등록해주세요.")
