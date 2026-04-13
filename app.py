import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
from datetime import date

# 1. UI 설정 및 제목 (이모티콘 제거)
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
            # 생년월일 선택 (1900년~2100년 직접 입력 가능)
            birth_date = st.date_input(
                "생년월일 (Birth Date)", 
                value=date(1980, 1, 1),
                min_value=date(1900, 1, 1), 
                max_value=date(2100, 12, 31)
            )
            # [반영 확인] 월 표기: MAY(5월) 형태로 숫자와 영문 병기
            m_str = birth_date.strftime('%B').upper() # 영문 월 (예: MAY)
            m_num = birth_date.month # 숫자 월 (예: 5)
            st.success(f"선택하신 달: **{m_str}({m_num}월)**")

        with col2:
            # 나이 자동 계산 (한국식: 현재 연도 - 태생 연도 + 1)
            c_year = date.today().year
            calc_age = c_year - birth_date.year + 1
            age = st.number_input("현재 나이 (Age)", value=calc_age)
            birth_time = st.text_input("태어난 시간 (모를 경우 비워두세요)", placeholder="예: 오전 10시 또는 진시")

        st.divider()

        # 2. 사진 업로드 가이드 (지침 준수)
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
                with st.spinner('사주와 수상을 대조하여 분석 중입니다...'):
                    t_info = birth_time if birth_time else "모름(생략)"
                    try:
                        prompt = f"""
                        당신은 명리학과 수상학 전문가입니다.
                        성별: {gender}, 나이: {age}세, 생년월일: {birth_date} (달: {m_str})
                        태어난 시간: {t_info}
                        제공된 사진에서 손톱/손등의 기질과 손바닥의 손금(생명/지능/감정선)을 결합하여 
                        현재 {age}세에 가장 중요한 사업/재물 전략을 한국어로 상세히 리포트해 주세요.
                        핵심은 굵게 표시하고 신뢰감 있는 전문가의 문체로 작성하세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader(f"🔍 {gender} {age}세 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        # 429 에러 대응 안내 강화
                        if "429" in str(e):
                            st.warning("⚠️ 현재 요청량이 많습니다. 1분만 기다렸다가 다시 버튼을 눌러주세요. (구글 무료 할당량 제한)")
                        else:
                            st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.warning("Streamlit Settings > Secrets에 'GEMINI_API_KEY'를 등록해주세요.")
