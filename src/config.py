"""
루미 AI 설정 파일
FastAPI는 Spring Boot의 요청만 처리합니다
"""
import os
from dotenv import load_dotenv
from functools import lru_cache

# .env 파일 로드
load_dotenv()

class Settings:
    """애플리케이션 설정"""
    
    def __init__(self):
        # Groq API 설정 (필수)
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        # LLM 설정
        self.model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # API 키 검증용 (선택사항 - 보안 강화)
        self.api_key = os.getenv("API_KEY", None)

@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스를 캐싱하여 반환 (싱글톤 패턴)"""
    return Settings()