import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
from datetime import date

# 1. UI 설정 및 제목
st.set_page_config(page_title="AI 사주+수상(손금) 풀이", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)

        st.title("AI 사주+수상(손금) 풀이")
        
        st.subheader("👤 기본 정보 입력 (Personal Info)")
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.radio("성별 (Gender)", ["남성 (Male)", "여성 (Female)"])
            
            # [수정] 직접 입력을 위해 연/월/일 개별 입력창으로 변경
            st.write("**생년월일 (Birth Date)**")
            c1, c2, c3 = st.columns(3)
            with c1: b_year = st.number_input("연(Year)", 1900, 2100, 1980)
            with c2: b_month = st.number_input("월(Month)", 1, 12, 1)
            with c3: b_day = st.number_input("일(Day)", 1, 31, 1)
            
            # [반영 확인] 월 표기: MAY(5월) 형태로 표시
            # 임시 날짜 객체 생성하여 월 이름 추출
            temp_date = date(b_year, b_month, b_day)
            m_str = temp_date.strftime('%B').upper()
            st.success(f"선택: **{m_str}({b_month}월)**")

        with col2:
            # 나이 자동 계산 (한국 나이: 현재 연도 - 태어난 연도 + 1)
            current_year = date.today().year
            age = st.number_input("현재 나이 (Age)", value=(current_year - b_year + 1))
            
            # [수정] 태어난 시간 예시 변경 (24시간 기준 + 시(時) 표기)
            birth_time = st.text_input(
                "태어난 시간 (모를 경우 비워두세요)", 
                placeholder="예: 10:30 사시(巳時)"
            )

        st.divider()

        # 2. 사진 업로드 가이드 (설명 보강)
        st.subheader("📸 사진 업로드 (Upload Photos)")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
        1) <b>손톱/손등 사진:</b> 타고난 기질과 건강 상태, 에너지의 강약을 분석합니다.<br>
        2) <b>손바닥(손금) 사진:</b> 생명선, 지능선, 감정선을 통해 성격과 운명의 흐름을 분석합니다.
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader("사진을 업로드하세요", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            cols = st.columns(len(images))
            for i, img in enumerate(images):
                cols[i].image(img, use_column_width=True)
            
            if st.button("통합 운명 리포트 생성"):
                with st.spinner('사주와 수상을 통합 분석 중...'):
                    t_info = birth_time if birth_time else "모름"
                    try:
                        prompt = f"""
                        수상 및 명리학 전문가로서 다음을 분석하세요.
                        성별: {gender}, 나이: {age}세, 생년월일: {b_year}년 {b_month}월({m_str}) {b_day}일
                        태어난 시간: {t_info}
                        제공된 사진에서 손톱/손등의 기질과 손바닥의 손금을 결합하여 
                        현재 {age}세에 가장 필요한 삶의 전략을 한국어로 상세히 리포트해 주세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader(f"🔍 {gender} {age}세 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        if "429" in str(e):
                            st.warning("⚠️ 요청량이 많습니다. 1분 뒤 다시 시도해 주세요.")
                        else:
                            st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("Secrets에 API_KEY를 등록해주세요.")
