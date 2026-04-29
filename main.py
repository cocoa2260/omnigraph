from fastapi import FastAPI, UploadFile, File, Body
from app.engine import RagEngine
import shutil
import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

app = FastAPI(title="OmniGraph API")
engine = RagEngine()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # 1. 임시 저장
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. PDF 처리 및 임베딩 (비동기)
    docs = await engine.process_pdf(temp_path)
    await engine.save_to_vector_db(docs, collection_name="company_docs")
    
    os.remove(temp_path) # 임시파일 삭제
    return {"status": "success", "message": f"{len(docs)} chunks indexed."}

@app.post("/chat")
async def chat_endpoint(payload: dict = Body(...)):
    query = payload.get("query")
    mode = payload.get("mode")
    
    # 1. 모델 선택 (Interface/Factory Pattern 개념 적용)
    if "LOCAL" in mode:
        llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3:8b"), base_url=os.getenv("OLLAMA_BASE_URL"))
    else:
        llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")) # 또는 Groq/Gemini

    # 2. RAG 체인 구성 (LCEL)
    vectorstore = engine.get_db(collection_name="company_docs") # engine.py에 get_db 메서드 추가 필요
    retriever = vectorstore.as_retriever()
    
    template = """당신은 기업의 문서 분석 비서입니다. 제공된 문맥(Context)을 바탕으로 질문에 답하세요.
    문맥에 없는 내용은 모른다고 답하세요. 답변은 한국어로 정중하게 하세요.
    
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