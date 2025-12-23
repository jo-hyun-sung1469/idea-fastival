"""
API 요청/응답 스키마 정의
Spring Boot와 통신하기 위한 스키마만 포함
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional

# ===== Spring Boot에서 받을 요청 데이터 =====

class UserTendency(BaseModel):
    """사용자 성향 (Spring Boot에서 전달)"""
    timePreference: str = Field(..., description="morning 또는 evening")
    concentrationLevel: int = Field(..., ge=1, le=10, description="집중력 수준")
    maxFocusDuration: int = Field(..., gt=0, description="최대 집중 시간 (분)")
    sleepTime: str = Field(..., description="취침 시간 (HH:MM)")
    wakeTime: str = Field(..., description="기상 시간 (HH:MM)")


class Task(BaseModel):
    """작업"""
    name: str = Field(..., description="작업 이름")
    estimatedDuration: int = Field(..., gt=0, description="예상 소요 시간 (분)")
    priority: int = Field(default=3, ge=1, le=5, description="우선순위 (1-5)")
    requiresHighFocus: bool = Field(default=False, description="높은 집중력 필요 여부")


class FixedTime(BaseModel):
    """고정 시간대"""
    startTime: str = Field(..., description="시작 시간 (HH:MM)")
    endTime: str = Field(..., description="종료 시간 (HH:MM)")
    description: str = Field(..., description="일정 설명")


class AIScheduleRequest(BaseModel):
    """AI 일정 생성 요청 (Spring Boot → FastAPI)"""
    userId: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    userTendency: UserTendency = Field(..., description="사용자 성향")
    tasks: List[Task] = Field(..., min_items=1, description="작업 목록")
    fixedTimes: List[FixedTime] = Field(default_factory=list, description="고정 시간대")
    userHistory: Optional[str] = Field(None, description="과거 피드백 요약")


# ===== Spring Boot로 보낼 응답 데이터 =====

class ScheduleItem(BaseModel):
    """생성된 일정 항목"""
    startTime: str = Field(..., description="시작 시간 (HH:MM)")
    endTime: str = Field(..., description="종료 시간 (HH:MM)")
    taskName: str = Field(..., description="작업 이름")
    description: str = Field(..., description="상세 설명")
    reason: str = Field(..., description="이 시간대에 배치한 이유")


class AIScheduleResponse(BaseModel):
    """AI 일정 생성 응답 (FastAPI → Spring Boot)"""
    scheduleItems: List[ScheduleItem] = Field(..., description="일정 목록")
    recommendation: str = Field(..., description="전체 일정에 대한 조언")


# ===== 성향 분석 관련 =====

class TendencyAnalysisRequest(BaseModel):
    """성향 분석 요청"""
    userTendency: UserTendency


class TendencyAnalysisResponse(BaseModel):
    """성향 분석 응답"""
    analysis: str = Field(..., description="AI 분석 결과")

#schemas.py