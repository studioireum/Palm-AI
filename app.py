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
        # 자동 모델 탐색 로직 적용
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
            with c1: b_year = st.number_input("연", 1900, 2100, 1980)
            with c2: b_month = st.number_input("월", 1, 12, 1)
            with c3: b_day = st.number_input("일", 1, 31, 1)
        with col2:
            current_year = date.today().year
            age = current_year - b_year + 1
            st.info(f"현재 나이: {age}세")
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1: birth_time = st.text_input("시간 (24시)", placeholder="10:30")
            calculated_hour = get_oriental_hour(birth_time)
            with t_col2: st.text_input("시", value=calculated_hour, disabled=True)

        st.divider()
        st.subheader("📸 사진 업로드")
        uploaded_files = st.file_uploader("손톱/손등 사진 1장, 손바닥 사진 1장을 올려주세요.", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = [ImageOps.exif_transpose(Image.open(f)) for f in uploaded_files]
            cols = st.columns(len(images))
            for i, img in enumerate(images): cols[i].image(img, use_column_width=True)
            
            if st.button("전문 운명 리포트 생성"):
                with st.spinner('사주와 수상을 통합하여 깊이 있게 분석 중입니다...'):
                    final_time = f"{birth_time} {calculated_hour}" if birth_time else "모름"
                    try:
                        # [핵심] 김창기 님 풀이 스타일을 재현하는 프롬프트
                        prompt = f"""
                        당신은 명리학과 수상학을 결합하여 개인의 인생을 꿰뚫어 보는 최고의 운명 전략가입니다. 
                        보내드린 김창기 님의 사례처럼 매우 구체적이고 현장감 있는 분석을 제공하세요.

                        [분석 대상 데이터]
                        - 성별: {gender}
                        - 나이: {age}세 (만 나이와 생년 정보 활용)
                        - 생년월일: {b_year}년 {b_month}월 {b_day}일 ({calendar_type})
                        - 태어난 시간: {final_time}

                        [분석 지침 - 반드시 지킬 것]
                        1. **'여름에 물가에 가지 마라' 같은 뻔한 소리는 금지입니다.** 대신 사진 속 손바닥의 구체적 특징(예: 굳은살의 위치, 구의 발달, 손금의 모양)을 언급하며 사주적 기운과 연결하세요.
                        2. **성향 분석**: 손톱과 손등 사진을 보고 타고난 기질(자수성가형, 아티스트형 등)을 정의하세요.
                        3. **현재와 미래**: {age}세를 기점으로 인생의 전환점이 어디인지, 어떤 운의 변화가 오는지 손금 유년법과 사주 대운을 결합해 설명하세요.
                        4. **맞춤 조언**: 건강, 재물, 인간관계에 대해 '야전 사령관' 스타일로 명확한 솔루션을 제시하세요.
                        5. **문체**: 정중하면서도 카리스마 있는 전문가의 톤을 유지하세요.
                        """
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader(f"🔍 {gender} {age}세 정밀 분석 리포트")
                        st.markdown(response.text)
                    except Exception as e:
                        if "429" in str(e): st.warning("현재 요청이 많습니다. 사진 용량을 줄이거나 5분 뒤 다시 시도해 주세요.")
                        else: st.error(f"분석 오류: {e}")
    except Exception as e:
        st.error(f"시스템 오류: {e}")
