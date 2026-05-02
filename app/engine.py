import os
from typing import List
import fitz # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

class RagEngine:
    def __init__(self):
        # 한국어 최적화 임베딩 모델 사용
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask"
        )
        self.db_path = os.getenv("CHROMA_DB_PATH", "./chroma_data")

    async def process_pdf(self, file_path: str) -> List[Document]:
        """PDF에서 텍스트를 추출하고 Chunk로 분할합니다."""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()

        # 문서의 문맥 유지를 위해 chunk_size 1000, overlap 100 설정
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return [Document(page_content=chunk, metadata={"source": file_path}) for chunk in chunks]
    
    async def save_to_vector_db(self, documents: List[Document], collection_name: str):
        """ChromaDB에 문서를 저장합니다."""
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.db_path,
            collection_name=collection_name
        )
        return vectorstore
    
    def get_db(self, collection_name: str):
        """저장된 ChromaDB 인스턴스를 로드합니다."""
        return Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )

    def get_retriever(self, collection_name: str):
        """
        'PDF Daol'의 높은 검색 정확도를 재현하기 위해 
        유사도 기반 검색에 상위 3개 청크를 가져오도록 설정합니다.
        """
        vectorstore = self.get_db(collection_name)
        return vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )