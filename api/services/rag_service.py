# ChromaDB 벡터 임베딩 및 검색 (ChromaDB VectorDB Status 연동)
from langchain_community.vectorstores import Chroma

async def search_enterprise_knowledge(query: str, user_role: str):
    # RBAC 적용: 사용자 권한에 맞는 컬렉션만 탐색
    db = Chroma(persist_directory="./chroma_data", embedding_function=embeddings)
    
    # PDF Daol의 3~5문장 단위 청크 분할 기법 적용
    docs = db.similarity_search(query, k=5, filter={"access_level": user_role})
    
    # Exaone 3.5:2.4b를 통한 출처 기반 답변 생성
    return generate_answer_with_source(docs, query)