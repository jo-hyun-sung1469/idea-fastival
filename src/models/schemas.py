"""
API 요청/응답 스키마 정의
Spring Boot DTO와 매칭되는 스키마
"""
from pydantic import BaseModel, Field
from typing import List, Optional

# ===== Spring Boot에서 받을 요청 데이터 =====

class TendencyDTO(BaseModel):
    """사용자 성향 (Spring Boot의 TendencyDTO와 매칭)"""
    nickname: Optional[str] = Field(None, description="사용자 닉네임")
    morningNight: str = Field(..., description="morning 또는 evening")
    focus: int = Field(..., ge=0, le=10, description="집중력 수준 (0-10)")
    maxFocus: int = Field(..., gt=0, description="최대 집중 시간 (분)")
    sleep: str = Field(..., description="취침 시간 (HH:MM)")
    rising: str = Field(..., description="기상 시간 (HH:MM)")


class TaskDTO(BaseModel):
    """작업 (Spring Boot의 TaskDTO와 매칭)"""
    title: str = Field(..., description="작업 제목")
    timeTaken: str = Field(..., description="예상 소요 시간 (endtime을 duration으로 사용)")


class FixedTimeDTO(BaseModel):
    """고정 시간대 (Spring Boot의 FixedTimeDTO와 매칭)"""
    time: str = Field(..., description="시작 시간 (HH:MM)")
    timeTaken: str = Field(..., description="종료 시간 (HH:MM)")
    title: str = Field(..., description="일정 제목")


class AIScheduleRequest(BaseModel):
    """AI 일정 생성 요청 (Spring Boot → FastAPI)"""
    nickname: str = Field(..., description="사용자 닉네임")
    date: str = Field(..., description="날짜 (YYYY-MM-DD 또는 String)")
    tendency: TendencyDTO = Field(..., description="사용자 성향")
    task: List[TaskDTO] = Field(..., min_items=1, description="작업 목록")
    fixed: List[FixedTimeDTO] = Field(default_factory=list, description="고정 시간대")
    feed: Optional[str] = Field(None, description="과거 피드백 요약")


# ===== Spring Boot로 보낼 응답 데이터 =====

class ScheduleDTO(BaseModel):
    """생성된 일정 항목 (Spring Boot의 ScheduleDTO와 매칭)"""
    time: str = Field(..., description="시작 시간 (HH:MM)")
    timeTaken: str = Field(..., description="종료 시간 (HH:MM)")
    title: str = Field(..., description="작업 제목")


class AIScheduleResponse(BaseModel):
    """AI 일정 생성 응답 (FastAPI → Spring Boot)"""
    schedules: List[ScheduleDTO] = Field(..., description="일정 목록")
    recommend: str = Field(..., description="전체 일정에 대한 조언")


# ===== 성향 분석 관련 =====

class TendencyAnalysisRequest(BaseModel):
    """성향 분석 요청 - TendencyDTO를 직접 받음"""
    nickname: Optional[str] = Field(None, description="사용자 닉네임")
    morningNight: str = Field(..., description="morning 또는 evening")
    focus: int = Field(..., ge=0, le=10, description="집중력 수준")
    maxFocus: int = Field(..., gt=0, description="최대 집중 시간 (분)")
    sleep: str = Field(..., description="취침 시간 (HH:MM)")
    rising: str = Field(..., description="기상 시간 (HH:MM)")


class TendencyAnalysisResponse(BaseModel):
    """성향 분석 응답"""
    analysis: str = Field(..., description="AI 분석 결과")

#endtime