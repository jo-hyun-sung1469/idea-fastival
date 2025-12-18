# # services/backend_client.py
# import httpx
# from typing import List, Dict, Any, Optional
# from models.schemas import (
#     TendencySurvey, TendencyResponse, ScheduleRequest, ScheduleResponse,
#     ScheduleFeedback, ScheduleItem
# )
# from config import get_settings

# settings = get_settings()

# class BackendClient:
#     def __init__(self):
#         self.base_url = settings.backend_api_url.rstrip("/")
#         self.client = httpx.Client(timeout=30.0)  # sync로 충분함
#         # 필요시 AsyncClient로 변경 가능

#     def _full_url(self, path: str) -> str:
#         return f"{self.base_url}{path}"

#     # === 성향 관련 ===
#     def get_tendency(self, user_id: str) -> TendencyResponse:
#         r = self.client.get(self._full_url(f"/api/users/{user_id}/tendency"))
#         r.raise_for_status()
#         return TendencyResponse(**r.json())

#     def save_or_update_tendency(self, survey: TendencySurvey) -> TendencyResponse:
#         r = self.client.post(
#             self._full_url(f"/api/users/{survey.user_id}/tendency"),
#             json=survey.dict()
#         )
#         r.raise_for_status()
#         return TendencyResponse(**r.json())

#     # === 일정 생성 관련 ===
#     def create_schedule_request(self, request: ScheduleRequest) -> int:
#         r = self.client.post(
#             self._full_url("/api/schedules"),
#             json=request.dict()
#         )
#         r.raise_for_status()
#         return r.json()["schedule_id"]

#     def save_generated_schedule(
#         self,
#         schedule_id: int,
#         schedule_items: List[ScheduleItem],
#         recommendation: str
#     ):
#         r = self.client.put(
#             self._full_url(f"/api/schedules/{schedule_id}/generated"),
#             json={
#                 "generated_schedule": [item.dict() for item in schedule_items],
#                 "recommendation": recommendation
#             }
#         )
#         r.raise_for_status()

#     # === 피드백 ===
#     def submit_feedback(self, feedback: ScheduleFeedback):
#         r = self.client.post(
#             self._full_url(f"/api/schedules/{feedback.schedule_id}/feedback"),
#             json=feedback.dict()
#         )
#         r.raise_for_status()

#     # === 인사이트 & 히스토리 ===
#     def get_user_insights(self, user_id: str) -> Dict[str, Any]:
#         r = self.client.get(self._full_url(f"/api/users/{user_id}/insights"))
#         r.raise_for_status()
#         return r.json()

#     def get_user_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
#         r = self.client.get(
#             self._full_url(f"/api/users/{user_id}/history"),
#             params={"limit": limit}
#         )
#         r.raise_for_status()
#         return r.json()

#     # === 개발용 ===
#     def reset_user_data(self, user_id: str):
#         r = self.client.delete(self._full_url(f"/api/dev/reset/{user_id}"))
#         r.raise_for_status()
#         return r.json()


# services/backend_client.py
from datetime import datetime
from typing import List, Dict, Any
from models.schemas import (
    TendencySurvey, TendencyResponse, ScheduleRequest,
    ScheduleFeedback, ScheduleItem
)
from config import get_settings

settings = get_settings()

class BackendClient:
    def __init__(self):
        print("⚠️  [임시 모드] 백엔드 없이 로컬에서만 동작 중입니다!")
        print(f"   백엔드 URL 설정: {settings.backend_api_url} (연결 안 함)")

    # === 성향 관련 (임시) ===
    def get_tendency(self, user_id: str) -> TendencyResponse:
        print(f"✅ [임시] 성향 조회: {user_id}")
        # 테스트용 고정값 반환 (실제 저장된 건 없지만 동작하게)
        return TendencyResponse(
            id=1,
            user_id=user_id,
            time_preference="morning",
            concentration_level=8,
            max_focus_duration=120,
            sleep_time="23:30",
            wake_time="07:00",
            created_at=datetime.utcnow()
        )

    def save_or_update_tendency(self, survey: TendencySurvey) -> TendencyResponse:
        print(f"✅ [임시] 성향 저장 성공! user_id: {survey.user_id}")
        print(f"   → {survey.time_preference}형, 집중력 {survey.concentration_level}/10")
        return TendencyResponse(
            id=1,
            user_id=survey.user_id,
            time_preference=survey.time_preference,
            concentration_level=survey.concentration_level,
            max_focus_duration=survey.max_focus_duration,
            sleep_time=survey.sleep_time,
            wake_time=survey.wake_time,
            created_at=datetime.utcnow()
        )

    # === 일정 생성 관련 (임시) ===
    def create_schedule_request(self, request: ScheduleRequest) -> int:
        print(f"✅ [임시] 일정 요청 저장 (user_id: {request.user_id}, 날짜: {request.date})")
        print(f"   → 작업 {len(request.tasks)}개, 고정 시간 {len(request.fixed_times)}개")
        return 999  # 가짜 schedule_id

    def save_generated_schedule(
        self,
        schedule_id: int,
        schedule_items: List[ScheduleItem],
        recommendation: str
    ):
        print(f"✅ [임시] 생성된 일정 저장 완료! (ID: {schedule_id})")
        print(f"   → 일정 항목 {len(schedule_items)}개")
        print(f"   → 추천 조언: {recommendation[:100]}...")

    # === 피드백 (임시) ===
    def submit_feedback(self, feedback: ScheduleFeedback):
        print(f"✅ [임시 모드] 피드백 저장 성공!")
        print(f"   → ID: {feedback.schedule_id}")
        print(f"   → 별점: {feedback.rating}/5")
        if feedback.feedback:
            print(f"   → 피드백: {feedback.feedback}")
        
        # 아무것도 안 하고 성공이라고만 함
        return {"message": "피드백 저장 완료!"}

    # === 인사이트 & 히스토리 (임시) ===
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        print(f"✅ [임시] 사용자 인사이트 제공: {user_id}")
        return {
            "total_schedules": 3,
            "average_rating": 4.7,
            "most_common_tasks": {"공부": 5, "운동": 3},
            "insights": "루미가 잘 맞춰드리고 있어요! 계속 피드백 주세요 🎉"
        }

    def get_user_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        print(f"✅ [임시] 히스토리 조회: {user_id} (최근 {limit}개)")
        return {
            "schedules": [
                {"date": "2025-12-18", "rating": 5, "tasks_count": 3},
                {"date": "2025-12-17", "rating": 4, "tasks_count": 2},
            ]
        }

    # === 개발용 (임시) ===
    def reset_user_data(self, user_id: str):
        print(f"✅ [임시] 사용자 데이터 초기화: {user_id}")
        return {"message": "임시 모드: 모든 데이터 초기화 완료!"}
    

