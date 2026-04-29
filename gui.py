import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="OmniGraph - AI Document Assistant", layout="wide")

# 사이드바: 설정 및 모델 선택
with st.sidebar:
    st.title("⚙️ OmniGraph 설정")
    llm_mode = st.radio("LLM 엔진 선택", ["LOCAL (Ollama)", "CLOUD (Groq/Gemini)"])
    
    uploaded_file = st.file_uploader("회의록/문서 업로드 (PDF)", type="pdf")
    if uploaded_file and st.button("문서 분석 시작"):
        with st.spinner("문서를 분석하고 벡터 DB에 저장 중..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post("http://localhost:8000/upload", files=files)
            if response.status_code == 200:
                st.success("분석 완료!")
            else:
                st.error("분석 실패")

st.title("🤖 OmniGraph 지식 어시스턴트")
st.info("업로드된 문서를 바탕으로 질문에 답변합니다.")

# 채팅 메시지 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력 및 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Backend(FastAPI)와 통신하여 답변 생성 (다음 Step에서 구현될 /chat 엔드포인트 호출)
    with st.chat_message("assistant"):
        # 실제 운영시에는 비동기 스트리밍(SSE) 처리가 권장됨
        payload = {"query": prompt, "mode": llm_mode}
        # response = requests.post("http://localhost:8000/chat", json=payload) # 아직 미구현
        st.write(f"[{llm_mode} 모드] 분석된 내용을 바탕으로 답변을 준비 중입니다... (Backend 연동 필요)")