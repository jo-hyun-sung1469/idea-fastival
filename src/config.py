"""
루미 AI 설정 파일 (백엔드 연동 버전)
환경 변수를 관리합니다.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Groq API 설정 (필수)
    groq_api_key: str
    
    # LLM 설정
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    
    # 백엔드 API 설정 (새로 추가 - 필수!)
    backend_api_url: str = "http://localhost:8080"  # 기본값 제공

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 대소문자 구분 없이 환경변수 매핑 (편의성 향상)
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스를 캐싱하여 반환 (싱글톤 패턴)"""
    return Settings()