from fastapi import FastAPI, UploadFile, File, Body, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import socketio # 추가 필요
import shutil
import os

# 기존 PDF Daol의 엔진 및 설정 참조
from app.engine import RagEngine
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

app = FastAPI(title="OmniGraph API")

# Socket.IO 서버 설정 (실시간 협업 지원용)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# CORS 설정 (React 연동 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RagEngine()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # PDF Daol 방식: 비동기 처리 및 실시간 상태 전송
        docs = await engine.process_pdf(temp_path)
        await engine.save_to_vector_db(docs, collection_name="company_docs")
        
        # 실시간 상태 알림 (WebSocket)
        await sio.emit("document_status", {"filename": file.filename, "status": "completed"})
        
        return {"status": "success", "message": f"{len(docs)} chunks indexed."}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/chat")
async def chat_endpoint(payload: dict = Body(...)):
    query = payload.get("query")
    mode = payload.get("mode", "LOCAL")
    
    # PDF Daol의 모델 선택 로직 (Interface/Factory Pattern)
    if "LOCAL" in mode:
        llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "exaone3.5:2.4b"), base_url=os.getenv("OLLAMA_BASE_URL"))
    else:
        llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    # RAG 체인 구성 (LCEL)
    vectorstore = engine.get_db(collection_name="company_docs")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # 상위 5개 문서 참조
    
    template = """당신은 기업의 문서 분석 비서입니다. 제공된 문맥(Context)을 바탕으로 질문에 답하세요.
    반드시 문맥에 근거하여 답변하고, 근거가 없으면 "관련 내용을 찾을 수 없습니다"라고 답하세요.
    
    Context: {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    response = await chain.ainvoke(query)
    return {"answer": response}

# 주의: 서버 실행 시 socket_app을 사용해야 함 (uvicorn main:socket_app)