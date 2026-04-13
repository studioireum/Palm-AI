import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

st.set_page_config(page_title="Palm AI Master Pro", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)

        st.title("✋ AI 사주-수상 통합 분석")
        
        st.subheader("👤 기본 정보 입력 (Personal Info)")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("성별 (Gender)", ["남성 (Male)", "여성 (Female)"])
            birth_date = st.date_input("생년월일 (Birth Date)")
        with col2:
            age = st.number_input("현재 나이 (Age)", min_value=1, max_value=120, value=40)
            # [수정] 태어난 시간을 모를 경우를 대비한 안내 문구 추가 및 기본값 설정
            birth_time = st.text_input("태어난 시간 (모를 경우 비워두세요)", placeholder="예: 오전 10시 또는 모름")

        st.divider()

        st.subheader("📸 사진 업로드 (Upload Photos)")
        st.info("1) 손톱/손등 사진과 2) 손바닥 사진을 함께 올리면 정확도가 올라갑니다.")
        uploaded_files = st.file_uploader("사진 업로드", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            cols = st.columns(len(images))
            for i, img in enumerate(images):
                cols[i].image(img, use_column_width=True)
            
            if st.button("통합 운명 리포트 생성"):
                with st.spinner('사주와 수상을 대조하여 분석 중...'):
                    # 시간을 모를 경우에 대한 처리 로직
                    time_info = birth_time if birth_time else "모름(생략)"
                    
                    try:
                        prompt = f"""
                        당신은 명리학과 수상학 전문가입니다. 다음 정보를 통합 분석하세요.
                        
                        [사용자 데이터]
                        - 성별: {gender} / 나이: {age}세
                        - 생년월일: {birth_date} / 태어난 시간: {time_info}

                        [중요 지침]
                        1. **태어난 시간이 '{time_info}'인 경우**, 사주 원국에서 시주(時柱)를 제외한 삼주(三柱)와 수상 정보를 결합하여 분석하세요. 
                        2. 시간이 누락되었다고 분석을 멈추지 말고, 손금의 특징을 더 비중 있게 다루어 부족한 정보를 보완하세요.
                        3. 결과는 신뢰감 있는 전문가의 문체로, 핵심은 굵게 표시하여 리포트하세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader(f"🔍 {gender} {age}세 맞춤형 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"분석 중 오류: {e}")
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.warning("Secrets에 GEMINI_API_KEY를 등록해주세요.")
