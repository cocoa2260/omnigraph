# 일반 기업 보고서 전처리 및 OCR 엔진 선택 로직 (FastAPI)
def get_optimal_ocr_engine(file_path: str):
    # PDF Daol 방식: 텍스트 유무에 따른 고속 처리 분기
    if is_digital_pdf(file_path):
        return "PyPDF2" # 100% 정확도 보장
    
    # 기업 보고서(표/복합 구조) 특화: PaddleOCR 추천
    return "PaddleOCR"