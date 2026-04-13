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

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("Secrets에 API_KEY를 등록해주세요.")
else:
    try:
        genai.configure(api_key=api_key)
        # 자동 모델 탐색
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        model = genai.GenerativeModel(target_model)

        st.title("AI 사주+수상(손금) 풀이")
        st.caption(f"시스템 연결 상태: {target_model} (Active)")

        st.subheader("👤 기본 정보 입력")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("성별", ["남성", "여성"], horizontal=True)
            calendar_type = st.radio("달력", ["양력", "음력(평달)", "음력(윤달)"], horizontal=True)
            st.write("**생년월일**")
            c1, c2, c3 = st.columns(3)
            with c1: b_year = st.number_input("연", 1900, 2100, 1971)
            with c2: b_month = st.number_input("월", 1, 12, 7)
            with c3: b_day = st.number_input("일", 1, 31, 2)
            
            try:
                t_date = date(b_year, b_month, b_day)
                m_str = t_date.strftime('%B').upper()
                st.success(f"선택: {m_str}({b_month}월) / {calendar_type}")
            except: st.error("날짜 오류")

        with col2:
            current_year = date.today().year
            age = current_year - b_year + 1
            st.info(f"현재 나이: {age}세")
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1: birth_time = st.text_input("시간 (24시)", value="10:30")
            calculated_hour = get_oriental_hour(birth_time)
            with t_col2: st.text_input("시", value=calculated_hour, disabled=True)

        st.divider()
        st.subheader("📸 사진 업로드")
        uploaded_files = st.file_uploader("사진을 올려주세요", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            cols = st.columns(len(images))
            for i, img in enumerate(images): cols[i].image(img, use_column_width=True)
            
            if st.button("운명 리포트 생성"):
                with st.spinner('사주와 수상을 정밀 분석 중...'):
                    final_time = f"{birth_time} {calculated_hour}" if birth_time else "모름"
                    try:
                        # [톤앤매너 고정 & 데이터 격리 프롬프트]
                        prompt = f"""
                        당신은 명리학과 수상학 전문가입니다. 
                        
                        [사용자 데이터 - 분석의 유일한 근거]
                        - 성별: {gender}
                        - 나이: {age}세
                        - 생년월일: {b_year}년 {b_month}월 {b_day}일 ({calendar_type})
                        - 시간: {final_time}
                        - 사진: 업로드된 실제 이미지들

                        [분석 지침]
                        1. **절대 금기**: 이전 대화에 등장했던 '김창기'라는 이름이나 그 사람의 특징을 언급하지 마십시오.
                        2. **톤앤매너(Style)**: 날카로운 통찰력을 가진 '야전 사령관' 스타일의 말투를 사용하세요. 뻔한 소리가 아닌 인생의 핵심을 찌르는 문체를 유지하세요.
                        3. **내용(Content)**: 오직 위에 제공된 {age}세 사용자의 사주 정보와 업로드된 사진 속 손금/손톱 특징만 대조하여 리포트를 작성하세요.
                        4. **구조**: 
                           - 1단계: 타고난 기질과 성향 (사진 근거)
                           - 2단계: 손금으로 보는 현재와 미래 (나이 근거)
                           - 3단계: {age}세에 필요한 맞춤 전략과 조언
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 정밀 분석 결과")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
