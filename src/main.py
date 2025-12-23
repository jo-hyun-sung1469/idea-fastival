"""
티모 AI 엔진 - FastAPI 서버
Spring Boot의 요청만 처리하는 AI 전용 엔진입니다.
"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import json

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
    title="티모 AI 엔진",
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
print("🚀 티모 AI 엔진 시작!")
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
        "service": "티모 AI 엔진",
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
        "service": "timo-ai-engine",
        "model": settings.model_name
    }


@app.post("/api/ai/generate-schedule")
async def generate_schedule(
    raw_request: Request,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    AI로 일정 생성
    
    Spring Boot에서 이 엔드포인트를 호출합니다.
    
    Args:
        raw_request: 원본 요청 (디버깅용)
        api_key: API 키 (선택사항, 보안 강화용)
    
    Returns:
        생성된 일정과 추천사항
    """
    # API 키 검증 (설정된 경우만)
    if settings.api_key and api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # 원본 요청 바디 출력 (디버깅)
    try:
        body = await raw_request.json()
        print("\n" + "=" * 60)
        print("📥 스프링부트에서 받은 요청 데이터:")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # Pydantic으로 파싱 시도
        request = AIScheduleRequest(**body)
        
    except Exception as e:
        print(f"❌ 요청 파싱 실패: {e}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=422, detail=f"요청 형식 오류: {str(e)}")
    
    print(f"📅 AI 일정 생성 요청")
    print(f"   사용자: {request.nickname}")
    print(f"   날짜: {request.date}")
    print(f"   작업 수: {len(request.task)}개")
    print(f"   고정 시간: {len(request.fixed)}개")
    print("=" * 60)
    
    try:
        # 성향을 dict로 변환
        tendency_dict = request.tendency.model_dump()
        
        # AI 일정 생성
        result = schedule_generator.generate_schedule(
            user_tendency=tendency_dict,
            tasks=[task.model_dump() for task in request.task],
            fixed_times=[ft.model_dump() for ft in request.fixed],
            date=request.date,
            user_history=request.feed or ""
        )
        
        print(f"✅ 일정 생성 완료! (항목: {len(result['schedules'])}개)")
        
        # 응답 데이터 생성
        response_data = AIScheduleResponse(**result)
        response_dict = response_data.model_dump()
        
        # 실제 보내는 응답 출력 (디버깅)
        print("\n" + "=" * 60)
        print("📤 스프링부트로 보내는 응답 데이터:")
        print(json.dumps(response_dict, ensure_ascii=False, indent=2))
        print("=" * 60 + "\n")
        
        # JSONResponse로 명시적으로 반환
        return JSONResponse(
            content=response_dict,
            status_code=200,
            media_type="application/json"
        )
        
    except Exception as e:
        print(f"❌ 일정 생성 오류: {e}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=500, detail=f"일정 생성 실패: {str(e)}")


@app.post("/api/ai/analyze-tendency")
async def analyze_tendency(
    raw_request: Request,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    사용자 성향 분석
    
    Args:
        raw_request: 원본 요청 (디버깅용)
        api_key: API 키 (선택사항)
    
    Returns:
        AI 분석 결과
    """
    # API 키 검증 (설정된 경우만)
    if settings.api_key and api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # 원본 요청 바디 출력 (디버깅)
    try:
        body = await raw_request.json()
        print("\n" + "=" * 60)
        print("📥 성향 분석 요청 데이터:")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # Pydantic으로 파싱 시도
        request = TendencyAnalysisRequest(**body)
        
    except Exception as e:
        print(f"❌ 요청 파싱 실패: {e}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=422, detail=f"요청 형식 오류: {str(e)}")
    
    print(f"🧠 성향 분석 요청")
    print(f"   시간대 선호: {request.morningNight}")
    print(f"   집중력: {request.focus}/10")
    print("=" * 60)
    
    try:
        analysis = schedule_generator.generate_tendency_analysis(
            request.model_dump()
        )
        
        print(f"✅ 성향 분석 완료!")
        
        response_data = TendencyAnalysisResponse(analysis=analysis)
        response_dict = response_data.model_dump()
        
        # 실제 보내는 응답 출력 (디버깅)
        print("\n" + "=" * 60)
        print("📤 성향 분석 응답 데이터:")
        print(json.dumps(response_dict, ensure_ascii=False, indent=2))
        print("=" * 60 + "\n")
        
        # JSONResponse로 명시적으로 반환
        return JSONResponse(
            content=response_dict,
            status_code=200,
            media_type="application/json"
        )
        
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

#endtime