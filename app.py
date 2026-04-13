import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
from datetime import date

# 1. UI 설정
st.set_page_config(page_title="AI 사주+수상(손금) 풀이", layout="centered")

# --- 시간 -> 십이지시 변환 함수 ---
def get_oriental_hour(time_str):
    try:
        if not time_str or ':' not in time_str: return ""
        h, m = map(int, time_str.split(':'))
        total_minutes = h * 60 + m
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
    except: return ""

# API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("Secrets에 API_KEY를 등록해주세요.")
else:
    try:
        genai.configure(api_key=api_key)
        # 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')

        st.title("AI 사주+수상(손금) 풀이")
        
        st.subheader("👤 기본 정보 입력 (Personal Info)")
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.radio("성별 (Gender)", ["남성 (Male)", "여성 (Female)"])
            calendar_type = st.radio("달력 선택", ["양력", "음력(평달)", "음력(윤달)"], horizontal=True)
            
            st.write("**생년월일 (Birth Date)**")
            c1, c2, c3 = st.columns(3)
            with c1: b_year = st.number_input("연(Year)", 1900, 2100, 1980)
            with c2: b_month = st.number_input("월(Month)", 1, 12, 1)
            with c3: b_day = st.number_input("일(Day)", 1, 31, 1)
            
            try:
                t_date = date(b_year, b_month, b_day)
                m_str = t_date.strftime('%B').upper()
                st.success(f"선택: {m_str}({b_month}월) / {calendar_type}")
            except:
                st.error("날짜를 확인하세요.")

        with col2:
            current_year = date.today().year
            age = st.number_input("현재 나이 (Age)", value=(current_year - b_year + 1))
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1:
                birth_time = st.text_input("시간 (24시 기준)", placeholder="예: 10:30")
            calculated_hour = get_oriental_hour(birth_time)
            with t_col2:
                st.text_input("해당 시", value=calculated_hour, disabled=True)

        st.divider()

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
                with st.spinner('분석 중...'):
                    final_time = f"{birth_time} {calculated_hour}" if birth_time else "모름"
                    try:
                        prompt = f"""당신은 수상/명리 전문가입니다. {gender}, {age}세, {b_year}년 {b_month}월 {b_day}일({calendar_type}), 시간 {final_time} 정보를 바탕으로 사진 속 손톱/손금을 통합 분석하여 한국어로 상세 리포트를 작성하세요."""
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        if "429" in str(e): st.warning("잠시 후 다시 시도하세요.")
                        else: st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
