# """
# 루미 AI 일정 관리 시스템 - 메인 API 서버 (DB 없이 백엔드 연동 버전)
# """
# from fastapi import FastAPI, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List

# import httpx

# # 로컬 모듈 임포트
# from config import get_settings
# from models.schemas import (
#     TendencySurvey, TendencyResponse,
#     ScheduleRequest, ScheduleResponse, ScheduleFeedback
# )
# from services.schedule_generator import ScheduleGenerator
# from services.memory_manager import MemoryManager
# from services.backend_client import BackendClient  # 새로 추가

# # 설정 로드
# settings = get_settings()

# # FastAPI 앱 생성
# app = FastAPI(
#     title="루미 (Lumi) AI",
#     description="개인 맞춤형 일정 관리 AI 시스템 (백엔드 연동 버전)",
#     version="1.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 서비스 초기화
# print("🚀 루미 AI 초기화 중...")
# schedule_generator = ScheduleGenerator(
#     api_key=settings.groq_api_key,
#     model_name=settings.model_name
# )
# memory_manager = MemoryManager(
#     api_key=settings.groq_api_key,
#     model_name=settings.model_name
# )
# backend = BackendClient()  # 백엔드 클라이언트
# print("✅ 루미 AI 초기화 완료!")

# @app.get("/")
# def root():
#     return {
#         "message": "루미 AI 서비스가 정상 작동 중입니다! 🤖",
#         "version": "1.0.0",
#         "status": "healthy",
#         "docs": "/docs"
#     }

# @app.get("/health")
# def health_check():
#     return {"status": "ok"}

# # ===== 성향 조사 API =====
# @app.post("/api/tendency/survey", response_model=TendencyResponse)
# def create_tendency_survey(survey: TendencySurvey):
#     print(f"📝 성향 조사 등록: {survey.user_id}")
    
#     # 백엔드에 저장 + 분석 생성은 백엔드에서 해도 되고, 여기서 해도 됨
#     saved_tendency = backend.save_or_update_tendency(survey)
    
#     # 필요시 여기서 추가 분석 생성 후 메모리 저장
#     analysis = schedule_generator.generate_tendency_analysis(survey.dict())
#     # memory_manager에 저장하거나 백엔드에 별도 API로 보낼 수 있음
    
#     return saved_tendency

# @app.get("/api/tendency/{user_id}", response_model=TendencyResponse)
# def get_tendency(user_id: str):
#     try:
#         return backend.get_tendency(user_id)
#     except httpx.HTTPStatusError as e:
#         if e.response.status_code == 404:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"사용자 '{user_id}'의 성향 조사를 찾을 수 없습니다."
#             )
#         raise

# # ===== 일정 생성 API =====
# @app.post("/api/schedule/generate", response_model=ScheduleResponse)
# def generate_schedule(request: ScheduleRequest):
#     print(f"📅 일정 생성 요청: {request.user_id} - {request.date}")
    
#     # 1. 사용자 성향 조회
#     tendency = backend.get_tendency(request.user_id)
    
#     # 2. 학습 히스토리 조회 (MemoryManager가 필요로 함)
#     user_history = memory_manager.get_user_learning_summary(request.user_id)  # 백엔드 API로 변경 가능
    
#     # 3. AI 일정 생성
#     tendency_dict = tendency.dict(exclude={"id", "created_at"})
#     tasks_dict = [task.dict() for task in request.tasks]
#     fixed_times_dict = [ft.dict() for ft in request.fixed_times]
    
#     result = schedule_generator.generate_schedule(
#         user_tendency=tendency_dict,
#         tasks=tasks_dict,
#         fixed_times=fixed_times_dict,
#         date=request.date,
#         user_history=user_history
#     )
    
#     # 4. 백엔드에 일정 요청 저장 → schedule_id 발급
#     schedule_id = backend.create_schedule_request(request)
    
#     # 5. 생성된 일정 백엔드에 저장
#     backend.save_generated_schedule(
#         schedule_id=schedule_id,
#         schedule_items=result["schedule_items"],
#         recommendation=result["recommendation"]
#     )
    
#     # 6. 메모리 업데이트 (학습용)
#     memory_manager.add_schedule_interaction(
#         user_id=request.user_id,
#         schedule_request=request.dict(),
#         generated_schedule=result
#     )
    
#     print(f"✅ 일정 생성 완료: Schedule ID {schedule_id}")
    
#     return ScheduleResponse(
#         schedule_id=schedule_id,
#         date=request.date,
#         schedule_items=result["schedule_items"],
#         recommendation=result["recommendation"]
#     )

# # ===== 기타 API =====
# @app.get("/api/schedule/{schedule_id}")
# def get_schedule(schedule_id: int):
#     # 백엔드에 별도 조회 API가 있다면 호출
#     # 없으면 프론트에서 schedule_id만으로 충분히 재사용 가능
#     raise HTTPException(status_code=501, detail="백엔드에서 직접 조회하세요")

# @app.post("/api/schedule/feedback")
# def submit_feedback(feedback: ScheduleFeedback):
#     backend.submit_feedback(feedback)
    
#     # 메모리 업데이트
#     memory_manager.add_schedule_interaction(
#         user_id=None,  # 필요시 백엔드에서 user_id 조회하거나 별도 전달
#         schedule_request=None,
#         generated_schedule=None,
#         feedback=feedback.dict()
#     )
    
#     return {"message": "피드백이 성공적으로 저장되었습니다. 감사합니다! 🙏"}

# @app.get("/api/user/{user_id}/insights")
# def get_user_insights(user_id: str):
#     return backend.get_user_insights(user_id)

# @app.get("/api/user/{user_id}/history")
# def get_user_history(user_id: str, limit: int = 10):
#     return backend.get_user_history(user_id, limit)

# @app.delete("/api/dev/reset/{user_id}")
# def reset_user_data(user_id: str):
#     return backend.reset_user_data(user_id)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
루미 AI 일정 관리 시스템 - 메인 API 서버 (DB 없이 백엔드 연동 버전)
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

import httpx

# 로컬 모듈 임포트
from config import get_settings
from models.schemas import (
    TendencySurvey, TendencyResponse,
    ScheduleRequest, ScheduleResponse, ScheduleFeedback
)
from services.schedule_generator import ScheduleGenerator
from services.memory_manager import MemoryManager
from services.backend_client import BackendClient  # 새로 추가

# 설정 로드
settings = get_settings()

# FastAPI 앱 생성
app = FastAPI(
    title="루미 (Lumi) AI",
    description="개인 맞춤형 일정 관리 AI 시스템 (백엔드 연동 버전)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
print("🚀 루미 AI 초기화 중...")
schedule_generator = ScheduleGenerator(
    api_key=settings.groq_api_key,
    model_name=settings.model_name
)
memory_manager = MemoryManager(
    api_key=settings.groq_api_key,
    model_name=settings.model_name
)
backend = BackendClient()  # 백엔드 클라이언트
print("✅ 루미 AI 초기화 완료!")

@app.get("/")
def root():
    return {
        "message": "루미 AI 서비스가 정상 작동 중입니다! 🤖",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ===== 성향 조사 API =====
@app.post("/api/tendency/survey", response_model=TendencyResponse)
def create_tendency_survey(survey: TendencySurvey):
    print(f"📝 성향 조사 등록: {survey.user_id}")
    
    # 백엔드에 저장 + 분석 생성은 백엔드에서 해도 되고, 여기서 해도 됨
    saved_tendency = backend.save_or_update_tendency(survey)
    
    # 필요시 여기서 추가 분석 생성 후 메모리 저장
    analysis = schedule_generator.generate_tendency_analysis(survey.dict())
    # memory_manager에 저장하거나 백엔드에 별도 API로 보낼 수 있음
    
    return saved_tendency

@app.get("/api/tendency/{user_id}", response_model=TendencyResponse)
def get_tendency(user_id: str):
    try:
        return backend.get_tendency(user_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"사용자 '{user_id}'의 성향 조사를 찾을 수 없습니다."
            )
        raise

# ===== 일정 생성 API =====
@app.post("/api/schedule/generate", response_model=ScheduleResponse)
def generate_schedule(request: ScheduleRequest):
    print(f"📅 일정 생성 요청: {request.user_id} - {request.date}")
    
    # 1. 사용자 성향 조회
    tendency = backend.get_tendency(request.user_id)
    
    # 2. 학습 히스토리 조회 (MemoryManager가 필요로 함)
    user_history = memory_manager.get_user_learning_summary(request.user_id)  # 백엔드 API로 변경 가능
    
    # 3. AI 일정 생성
    tendency_dict = tendency.dict(exclude={"id", "created_at"})
    tasks_dict = [task.dict() for task in request.tasks]
    fixed_times_dict = [ft.dict() for ft in request.fixed_times]
    
    result = schedule_generator.generate_schedule(
        user_tendency=tendency_dict,
        tasks=tasks_dict,
        fixed_times=fixed_times_dict,
        date=request.date,
        user_history=user_history
    )
    
    # 4. 백엔드에 일정 요청 저장 → schedule_id 발급
    schedule_id = backend.create_schedule_request(request)
    
    # 5. 생성된 일정 백엔드에 저장
    backend.save_generated_schedule(
        schedule_id=schedule_id,
        schedule_items=result["schedule_items"],
        recommendation=result["recommendation"]
    )
    
    # 6. 메모리 업데이트 (학습용)
    memory_manager.add_schedule_interaction(
        user_id=request.user_id,
        schedule_request=request.dict(),
        generated_schedule=result
    )
    
    print(f"✅ 일정 생성 완료: Schedule ID {schedule_id}")
    
    return ScheduleResponse(
        schedule_id=schedule_id,
        date=request.date,
        schedule_items=result["schedule_items"],
        recommendation=result["recommendation"]
    )

# ===== 기타 API =====
# ===== 기타 API =====
@app.get("/api/schedule/{schedule_id}")
def get_schedule(schedule_id: int):
    # 백엔드에 별도 조회 API가 있다면 호출
    # 없으면 프론트에서 schedule_id만으로 충분히 재사용 가능
    raise HTTPException(status_code=501, detail="백엔드에서 직접 조회하세요")

# 이 부분(라인 152 근처)을 아래 내용으로 교체하세요!
@app.post("/api/schedule/feedback")
def submit_feedback(feedback: ScheduleFeedback):
    try:
        # 1. 백엔드에 피드백 전송
        backend.submit_feedback(feedback) 
        
        # 2. 피드백 데이터를 딕셔너리로 변환
        fb_data = feedback.dict() if feedback else {}
        
        # 3. 메모리 업데이트
        # 만약 feedback에 user_id가 들어있다면 그것을 쓰고, 없으면 "my_first_user" 사용
        user_id = fb_data.get("user_id", "my_first_user")
        
        memory_manager.add_schedule_interaction(
            user_id=user_id,
            schedule_request={},      # 빈 값 방어
            generated_schedule={},    # 빈 값 방어
            feedback=fb_data
        )
        
        return {"message": "피드백이 성공적으로 저장되었습니다. 감사합니다! 🙏"}
        
    except Exception as e:
        print(f"❌ 피드백 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=400, detail="잘못된 요청 형식입니다.")

@app.get("/api/user/{user_id}/insights")
def get_user_insights(user_id: str):
    return backend.get_user_insights(user_id)

@app.get("/api/user/{user_id}/history")
def get_user_history(user_id: str, limit: int = 10):
    return backend.get_user_history(user_id, limit)

@app.delete("/api/dev/reset/{user_id}")
def reset_user_data(user_id: str):
    return backend.reset_user_data(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)