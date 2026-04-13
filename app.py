import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
from datetime import date, datetime

# 1. UI 설정 및 제목
st.set_page_config(page_title="AI 사주+수상(손금) 풀이", layout="centered")

# --- 시간 -> 십이지시 변환 함수 ---
def get_oriental_hour(time_str):
    try:
        # "10:30" 형태의 문자열을 시간 객체로 변환
        h, m = map(int, time_str.split(':'))
        total_minutes = h * 60 + m
        
        # 한국 표준시 기준 (동경 135도 기준 보정 전 일반 시간대)
        if 23 * 60 + 30 <= total_minutes or total_minutes < 1 * 60 + 30: return "자시(子時)"
        elif 1 * 60 + 30 <= total_minutes < 3 * 60 + 30: return "축시(丑時)"
        elif 3 * 60 + 30 <= total_minutes < 5 * 60 + 30: return "인시(寅時)"
        elif 5 * 60 + 30 <= total_minutes < 7 * 60 + 30: return "묘시(卯時)"
        elif 7 * 60 + 30 <= total_minutes < 9 * 60 + 30: return "진시(辰時)"
        elif 9 * 60 + 30 <= total_minutes < 11 * 60 + 30: return "사시(巳時)"
        elif 11 * 60 + 30 <= total_minutes < 13 * 60 + 30: return "오시(午時)"
        elif 13 * 60 + 30 <= total_minutes < 15 * 60 + 30: return "미시(未時)"
        elif 15 * 60 + 30 <= total_minutes < 17 * 60 + 30: return "신시(申時)"
        elif 17 * 60 + 30 <= total_minutes < 19 * 60 + 30: return "유시(酉時)"
        elif 19 * 60 + 30 <= total_minutes < 21 * 60 + 30: return "술시(戌時)"
        else: return "해시(亥時)"
    except:
        return ""

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
            st.write("**생년월일 (Birth Date)**")
            c1, c2, c3 = st.columns(3)
            with c1: b_year = st.number_input("연(Year)", 1900, 2100, 1980)
            with c2: b_month = st.number_input("월(Month)", 1, 12, 1)
            with c3: b_day = st.number_input("일(Day)", 1, 31, 1)
            
            t_date = date(b_year, b_month, b_day)
            m_str = t_date.strftime('%B').upper()
            st.success(f"선택: **{m_str}({b_month}월)**")

        with col2:
            current_year = date.today().year
            age = st.number_input("현재 나이 (Age)", value=(current_year - b_year + 1))
            
            # [수정] 시간 입력창과 자동 '시' 출력창 분리
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1:
                birth_time = st.text_input("태어난 시간 (24시 기준)", placeholder="예: 10:30")
            
            # 입력된 시간에 따라 '사시' 등 자동 계산
            calculated_hour = get_oriental_hour(birth_time)
            with t_col2:
                st.text_input("해당 시", value=calculated_hour, disabled=True)

        st.divider()

        # 2. 사진 업로드 가이드
        st.subheader("📸 사진 업로드 (Upload Photos)")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
        1) <b>손톱/손등 사진:</b> 타고난 기질과 건강 상태 분석<br>
        2) <b>손바닥(손금) 사진:</b> 성격과 운명의 흐름 분석
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
                    # 최종 시간 정보 (10:30 + 사시)
                    final_time = f"{birth_time} {calculated_hour}" if birth_time else "모름"
                    try:
                        prompt = f"""
                        수상 및 명리학 전문가로서 다음을 분석하세요.
                        정보: {gender}, {age}세, {b_year}년 {b_month}월({m_str}) {b_day}일
                        시간: {final_time}
                        사진의 손톱 기질과 손바닥 손금을 결합하여 전문적인 분석 리포트를 작성하세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader(f"🔍 {gender} {age}세 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        if "429" in str(e):
                            st.warning("⚠️ 요청량이 많습니다. 5분 뒤 다시 시도해 주세요.")
                        else:
                            st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("Secrets에 API_KEY를 등록해주세요.")
