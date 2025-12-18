"""
API 요청/응답 스키마 정의
Pydantic을 사용한 데이터 검증
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class TendencySurvey(BaseModel):
    """성향 조사 입력 데이터"""
    user_id: str = Field(..., description="사용자 고유 ID")
    time_preference: str = Field(..., description="morning 또는 evening")
    concentration_level: int = Field(..., ge=1, le=10, description="집중력 수준 (1-10)")
    max_focus_duration: int = Field(..., gt=0, description="최대 집중 시간 (분)")
    sleep_time: str = Field(..., description="취침 시간 (HH:MM)")
    wake_time: str = Field(..., description="기상 시간 (HH:MM)")
    
    @validator('time_preference')
    def validate_time_preference(cls, v):
        if v not in ['morning', 'evening']:
            raise ValueError('time_preference는 "morning" 또는 "evening"이어야 합니다')
        return v
    
    @validator('sleep_time', 'wake_time')
    def validate_time_format(cls, v):
        try:
            hours, minutes = map(int, v.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError
        except:
            raise ValueError('시간 형식은 HH:MM이어야 합니다 (예: 23:00)')
        return v

class TendencyResponse(TendencySurvey):
    """성향 조사 응답 데이터"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FixedTime(BaseModel):
    """고정 시간대 (수업, 약속 등)"""
    start_time: str = Field(..., description="시작 시간 (HH:MM)")
    end_time: str = Field(..., description="종료 시간 (HH:MM)")
    description: str = Field(..., description="일정 설명")
    
    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            hours, minutes = map(int, v.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError
        except:
            raise ValueError('시간 형식은 HH:MM이어야 합니다')
        return v

class Task(BaseModel):
    """처리할 작업"""
    name: str = Field(..., description="작업 이름")
    estimated_duration: int = Field(..., gt=0, description="예상 소요 시간 (분)")
    priority: int = Field(default=3, ge=1, le=5, description="우선순위 (1-5, 5가 가장 높음)")
    requires_high_focus: bool = Field(default=False, description="높은 집중력 필요 여부")

class ScheduleRequest(BaseModel):
    """일정 생성 요청"""
    user_id: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    tasks: List[Task] = Field(..., min_items=1, description="작업 목록")
    fixed_times: List[FixedTime] = Field(default_factory=list, description="고정 시간대 목록")
    
    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except:
            raise ValueError('날짜 형식은 YYYY-MM-DD이어야 합니다 (예: 2025-01-15)')
        return v

class ScheduleItem(BaseModel):
    """생성된 일정 항목"""
    start_time: str = Field(..., description="시작 시간")
    end_time: str = Field(..., description="종료 시간")
    task_name: str = Field(..., description="작업 이름")
    description: str = Field(..., description="상세 설명")
    reason: str = Field(..., description="이 시간대에 배치한 이유")

class ScheduleResponse(BaseModel):
    """일정 생성 응답"""
    schedule_id: int = Field(..., description="일정 ID")
    date: str = Field(..., description="날짜")
    schedule_items: List[ScheduleItem] = Field(..., description="일정 목록")
    recommendation: str = Field(..., description="전체 일정에 대한 조언")

class ScheduleFeedback(BaseModel):
    """일정 피드백"""
    schedule_id: int = Field(..., description="일정 ID")
    rating: int = Field(..., ge=1, le=5, description="만족도 (1-5)")
    feedback: Optional[str] = Field(None, description="상세 피드백")

class UserInsights(BaseModel):
    """사용자 인사이트"""
    user_id: str
    total_schedules: int
    average_rating: float
    most_common_tasks: dict
    learning_summary: str