"""
일정 생성 서비스
Groq API와 LangChain을 사용하여 맞춤형 일정을 생성합니다.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json

from models.schemas import ScheduleItem


class ScheduleOutput(BaseModel):
    """LLM 출력 스키마"""
    scheduleItems: List[ScheduleItem] = Field(description="일정 항목 리스트")
    recommendation: str = Field(description="전체 일정에 대한 조언")


class ScheduleGenerator:
    """일정 생성 클래스"""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        """
        초기화
        
        Args:
            api_key: Groq API 키
            model_name: 사용할 모델 이름
        """
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
        self.parser = PydanticOutputParser(pydantic_object=ScheduleOutput)
        
    def generate_schedule(
        self,
        user_tendency: dict,
        tasks: List[dict],
        fixed_times: List[dict],
        date: str,
        user_history: str = ""
    ) -> dict:
        """
        사용자 성향을 바탕으로 일정을 생성합니다.
        
        Args:
            user_tendency: 사용자 성향 정보
            tasks: 처리할 작업 목록
            fixed_times: 고정 시간대 목록
            date: 일정 날짜
            user_history: 과거 피드백 요약
            
        Returns:
            생성된 일정과 추천사항
        """
        
        # 프롬프트 템플릿 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 '루미'라는 개인 맞춤형 일정 관리 AI입니다. 
사용자의 성향을 깊이 이해하고, 가장 효율적이고 실현 가능한 일정을 만들어주세요.

# 사용자 성향 정보
- 시간대 선호: {time_preference} (아침형/저녁형)
- 집중력 수준: {concentration_level}/10
- 최대 집중 지속 시간: {max_focus_duration}분
- 취침 시간: {sleep_time}
- 기상 시간: {wake_time}

# 일정 작성 원칙
1. **시간대 최적화**
   - 아침형: 중요하고 집중이 필요한 작업을 오전(7-12시)에 배치
   - 저녁형: 중요한 작업을 오후/저녁(14-22시)에 배치

2. **집중력 관리**
   - 최대 집중 시간을 초과하지 않도록 작업 분할
   - 집중 작업 후에는 반드시 10-15분 휴식 시간 배치
   - 집중력이 낮은 시간대에는 가벼운 작업 배치

3. **고정 시간대 준수**
   - 고정 시간대는 절대 침범하지 않음
   - 고정 시간대 전후에 이동/준비 시간 고려

4. **우선순위 반영**
   - 우선순위가 높은 작업(4-5)을 먼저 처리
   - 우선순위가 높고 집중이 필요한 작업은 최적 시간대에 배치

5. **현실성**
   - 하루에 너무 많은 작업을 배치하지 않음
   - 식사 시간, 휴식 시간을 반드시 포함
   - 이동 시간, 준비 시간도 고려

{user_history}

{format_instructions}
"""),
            ("human", """날짜: {date}

# 고정 시간대 (절대 침범 불가)
{fixed_times_str}

# 처리할 작업 목록
{tasks_str}

위 정보를 바탕으로 효율적인 일정을 만들어주세요. 

각 일정 항목은 다음 형식으로 작성:
- startTime: 시작 시간 (HH:MM 형식)
- endTime: 종료 시간 (HH:MM 형식)
- taskName: 작업 이름
- description: 구체적인 작업 설명
- reason: 이 시간대에 배치한 이유 (사용자 성향 기반으로 설명)

반드시 JSON 형식으로만 응답해주세요.""")
        ])
        
        # 포맷 지시사항
        format_instructions = self.parser.get_format_instructions()
        
        # 사용자 히스토리 텍스트 생성
        history_text = ""
        if user_history:
            history_text = f"""
# 과거 학습 데이터 (사용자 피드백)
{user_history}

위 피드백을 참고하여 사용자가 선호하는 패턴으로 일정을 만들어주세요.
"""
        
        # JSON 문자열 미리 준비
        tasks_str = json.dumps(tasks, ensure_ascii=False, indent=2)
        fixed_times_str = json.dumps(fixed_times, ensure_ascii=False, indent=2) if fixed_times else "고정 시간대 없음"
        
        # 체인 구성
        chain = prompt | self.llm | self.parser
        
        print(f"🤖 AI 일정 생성 중... (날짜: {date})")
        
        try:
            result: ScheduleOutput = chain.invoke({
                "time_preference": "아침형" if user_tendency.get("timePreference") == "morning" else "저녁형",
                "concentration_level": user_tendency.get("concentrationLevel", 7),
                "max_focus_duration": user_tendency.get("maxFocusDuration", 90),
                "sleep_time": user_tendency.get("sleepTime", "23:00"),
                "wake_time": user_tendency.get("wakeTime", "07:00"),
                "user_history": history_text,
                "date": date,
                "fixed_times_str": fixed_times_str,
                "tasks_str": tasks_str,
                "format_instructions": format_instructions
            })
            
            print(f"✅ 일정 생성 완료! (항목: {len(result.scheduleItems)}개)")
            
            # ScheduleItem 객체를 dict로 변환
            return {
                "scheduleItems": [item.dict() for item in result.scheduleItems],
                "recommendation": result.recommendation
            }
            
        except Exception as e:
            print(f"⚠️ 파싱 오류: {str(e)}")
            # Fallback: 기본 응답
            return {
                "scheduleItems": [],
                "recommendation": f"일정 생성 중 오류가 발생했습니다. 다시 시도해주세요. (오류: {str(e)})"
            }
    
    def generate_tendency_analysis(self, survey_data: dict) -> str:
        """
        사용자 성향을 분석하고 인사이트를 제공합니다.
        
        Args:
            survey_data: 성향 조사 데이터
            
        Returns:
            분석 결과 텍스트
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 사용자의 학습 및 업무 성향을 분석하는 전문가입니다. 친근하고 격려하는 톤으로 조언해주세요."),
            ("human", """다음 성향 조사 결과를 분석하고 맞춤형 조언을 제공해주세요:

시간대 선호: {time_preference}
집중력 수준: {concentration_level}/10
최대 집중 시간: {max_focus_duration}분
취침 시간: {sleep_time}
기상 시간: {wake_time}

이 사용자에게 가장 적합한 일정 관리 방식과 생산성 팁을 3~4문단으로 작성해주세요.
마크다운 형식으로 예쁘게 작성하고, 이모지도 적절히 사용해주세요.""")
        ])
        
        chain = prompt | self.llm
        
        print("🤖 성향 분석 중...")
        try:
            response = chain.invoke({
                "time_preference": "아침형" if survey_data.get("timePreference") == "morning" else "저녁형",
                "concentration_level": survey_data.get("concentrationLevel", 7),
                "max_focus_duration": survey_data.get("maxFocusDuration", 90),
                "sleep_time": survey_data.get("sleepTime", "23:00"),
                "wake_time": survey_data.get("wakeTime", "07:00")
            })
            print("✅ 성향 분석 완료!")
            return response.content
        except Exception as e:
            print(f"⚠️ 성향 분석 오류: {str(e)}")
            return "성향 분석 중 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."