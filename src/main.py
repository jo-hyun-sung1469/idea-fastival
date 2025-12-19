"""
루미 AI 엔진 - FastAPI 서버
Spring Boot의 요청만 처리하는 AI 전용 엔진입니다.
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from config import get_settings
from services.schedule_generator import ScheduleGenerator
from models.schemas import (
    AIScheduleRequest, AIScheduleResponse,
    TendencyAnalysisRequest, TendencyAnalysisResponse
)

# 설정 로드
settings = get_settings()

# FastAPI 앱 생성
app = FastAPI(
    title="루미 AI 엔진",
    description="Spring Boot 백엔드를 위한 AI 일정 생성 엔진",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 - Spring Boot에서 접근 가능하도록
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 Spring Boot URL만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI 서비스 초기화
schedule_generator = ScheduleGenerator(
    api_key=settings.groq_api_key,
    model_name=settings.model_name
)

print("=" * 60)
print("🚀 루미 AI 엔진 시작!")
print("=" * 60)
print(f"📊 모델: {settings.model_name}")
print(f"🌡️  Temperature: {settings.temperature}")
print(f"🔑 API Key: {settings.groq_api_key[:20]}...")
print("=" * 60)


# ===== API 엔드포인트 =====

@app.get("/")
def root():
    """서비스 상태 확인"""
    return {
        "service": "루미 AI 엔진",
        "status": "running",
        "version": "1.0.0",
        "description": "Spring Boot 백엔드를 위한 AI 일정 생성 서비스",
        "endpoints": {
            "generate_schedule": "POST /api/ai/generate-schedule",
            "analyze_tendency": "POST /api/ai/analyze-tendency",
            "health": "GET /health"
        }
    }


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {
        "status": "ok",
        "service": "lumi-ai-engine",
        "model": settings.model_name
    }


@app.post("/api/ai/generate-schedule", response_model=AIScheduleResponse)
async def generate_schedule(
    request: AIScheduleRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    AI로 일정 생성
    
    Spring Boot에서 이 엔드포인트를 호출합니다.
    
    Args:
        request: 일정 생성 요청 데이터
        api_key: API 키 (선택사항, 보안 강화용)
    
    Returns:
        생성된 일정과 추천사항
    """
    # API 키 검증 (설정된 경우만)
    if settings.api_key and api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    print("\n" + "=" * 60)
    print(f"📅 AI 일정 생성 요청")
    print(f"   사용자: {request.userId}")
    print(f"   날짜: {request.date}")
    print(f"   작업 수: {len(request.tasks)}개")
    print(f"   고정 시간: {len(request.fixedTimes)}개")
    print("=" * 60)
    
    try:
        # 성향을 dict로 변환
        tendency_dict = request.userTendency.dict()
        
        # AI 일정 생성
        result = schedule_generator.generate_schedule(
            user_tendency=tendency_dict,
            tasks=[task.dict() for task in request.tasks],
            fixed_times=[ft.dict() for ft in request.fixedTimes],
            date=request.date,
            user_history=request.userHistory or ""
        )
        
        print(f"✅ 일정 생성 완료!")
        print(f"   생성된 일정: {len(result['scheduleItems'])}개")
        print("=" * 60 + "\n")
        
        return AIScheduleResponse(**result)
        
    except Exception as e:
        print(f"❌ 일정 생성 오류: {e}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=500, detail=f"일정 생성 실패: {str(e)}")


@app.post("/api/ai/analyze-tendency", response_model=TendencyAnalysisResponse)
async def analyze_tendency(
    request: TendencyAnalysisRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    사용자 성향 분석
    
    Args:
        request: 성향 분석 요청
        api_key: API 키 (선택사항)
    
    Returns:
        AI 분석 결과
    """
    # API 키 검증 (설정된 경우만)
    if settings.api_key and api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    print("\n" + "=" * 60)
    print(f"🧠 성향 분석 요청")
    print(f"   시간대 선호: {request.userTendency.timePreference}")
    print(f"   집중력: {request.userTendency.concentrationLevel}/10")
    print("=" * 60)
    
    try:
        analysis = schedule_generator.generate_tendency_analysis(
            request.userTendency.dict()
        )
        
        print(f"✅ 성향 분석 완료!")
        print("=" * 60 + "\n")
        
        return TendencyAnalysisResponse(analysis=analysis)
        
    except Exception as e:
        print(f"❌ 분석 오류: {e}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")


# 실행
if __name__ == "__main__":
    import uvicorn
    print("\n🌐 서버 시작 중...")
    print(f"📡 주소: http://0.0.0.0:8000")
    print(f"📝 API 문서: http://localhost:8000/docs\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )