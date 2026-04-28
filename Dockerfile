FROM python:3.11-slim

# 시스템 의존성 설치 (OCR 및 PDF 처리용)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치(numpy<2.0.0 준수)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# FastAPI와 Streamlit을 동시에 관리하거나 각각 분리 가능
# 여기서는 백엔드 실행을 기본으로 설정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]