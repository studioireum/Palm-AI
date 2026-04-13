import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps

# UI 설정
st.set_page_config(page_title="Palm AI Pro", layout="centered")

# CSS로 손 위치 가이드 디자인 추가
st.markdown("""
    <style>
    .guide-box {
        border: 2px dashed #FF4B4B;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✋ AI 수상 분석 마스터 Pro")
st.write("전문가급 AI가 당신의 손금을 정밀 분석합니다.")

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("Settings (설정)")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("API 키는 서버에 저장되지 않습니다.")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 에러 방지를 위해 최신 모델 호출 방식 적용
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        # 가이드라인 안내
        st.markdown('<div class="guide-box">📸 <b>[가이드]</b> 손바닥이 화면에 꽉 차도록, 손가락을 펴고 정면에서 찍어주세요.</div>', unsafe_allow_html=True)

        # 파일 업로드 (여러 장 가능하도록 수정)
        uploaded_files = st.file_uploader("손바닥 사진을 업로드하세요 (최대 3장)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            images = []
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                # 이미지 회전 문제 해결 (Exif 정보 바탕으로 자동 보정)
                img = ImageOps.exif_transpose(img)
                images.append(img)
                st.image(img, caption=f'업로드된 이미지: {uploaded_file.name}', use_column_width=True)
            
            if st.button("전문 분석 시작 (Start Professional Analysis)"):
                with st.spinner('AI 전문가가 수상을 정밀 분석 중입니다...'):
                    try:
                        prompt = """
                        당신은 30년 경력의 수상학 전문가입니다. 업로드된 손바닥 사진을 보고 다음 항목을 심층 분석하세요:
                        1. [손의 형상] 전체적인 형태와 피부결이 주는 기질 분석
                        2. [3대 주선] 생명선, 지능선, 감정선의 굵기와 흐름 분석
                        3. [재물과 성공] 운명선과 태양구를 통한 경제적 미래 예측
                        4. [종합 조언] 현재 시점에서 가장 필요한 삶의 태도와 건강 주의점
                        분석 결과는 신뢰감 있는 전문가의 문체로 작성하고, 핵심 문구는 굵게(Bold) 표시하세요.
                        """
                        # 이미지 리스트와 프롬프트 전달
                        response = model.generate_content([prompt] + images)
                        st.divider()
                        st.subheader("🔍 정밀 분석 리포트")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요.")
