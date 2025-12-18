# """
# 학습 및 메모리 관리 서비스 (백엔드 분리 버전)
# 최신 LangChain 1.x 방식으로 사용자 패턴 학습 및 히스토리 관리
# DB 대신 메모리 내에서만 동작 (임시)
# """
# from langchain_groq import ChatGroq
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from typing import Dict
# import json
# from collections import defaultdict, Counter
# from datetime import datetime


# class MemoryManager:
#     """사용자별 학습 및 메모리 관리 클래스 (LangChain 1.x 호환)"""
    
#     def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
#         self.llm = ChatGroq(groq_api_key=api_key, model_name=model_name)
        
#         # 사용자별 히스토리 저장소 (메모리 내)
#         self.store: Dict[str, InMemoryChatMessageHistory] = {}
        
#         # 사용자별 피드백/일정 기록 (DB 대신 메모리에 임시 저장)
#         self.user_data: Dict[str, list] = defaultdict(list)  # user_id -> list of dicts
        
#         # 요약용 체인
#         summary_prompt = ChatPromptTemplate.from_messages([
#             SystemMessage(content="다음 대화를 3~5문장으로 간결하게 요약해 주세요. 중요한 사용자 선호도, 일정 패턴, 피드백 위주로."),
#             MessagesPlaceholder(variable_name="history")
#         ])
#         self.summary_chain = summary_prompt | self.llm
        
#     def get_session_history(self, user_id: str) -> InMemoryChatMessageHistory:
#         if user_id not in self.store:
#             self.store[user_id] = InMemoryChatMessageHistory()
#         return self.store[user_id]
    
#     def add_schedule_interaction(
#         self,
#         user_id: str,
#         schedule_request: dict,
#         generated_schedule: dict,
#         feedback: dict = None
#     ):
#         history = self.get_session_history(user_id)
        
#         # 사용자 요청 저장
#         task_names = [task.get('name', '') for task in schedule_request.get('tasks', [])]
#         request_text = f"""{schedule_request['date']}에 다음 작업들을 요청했습니다:
# 작업: {', '.join(task_names) if task_names else '없음'}
# 고정 약속: {len(schedule_request.get('fixed_times', []))}개"""
#         history.add_message(HumanMessage(content=request_text))
        
#         # AI 응답 저장
#         item_count = len(generated_schedule.get('schedule_items', []))
#         response_text = f"총 {item_count}개의 일정 항목을 생성했습니다. 추천: {generated_schedule.get('recommendation', '')[:100]}..."
#         history.add_message(AIMessage(content=response_text))
        
#         # 메모리에 일정 기록 저장 (DB 대신)
#         record = {
#             "date": schedule_request['date'],
#             "tasks": schedule_request.get('tasks', []),
#             "schedule_items": generated_schedule.get('schedule_items', []),
#             "recommendation": generated_schedule.get('recommendation', ''),
#             "created_at": datetime.utcnow().isoformat()
#         }
#         if feedback:
#             record["rating"] = feedback.get('rating')
#             record["feedback"] = feedback.get('feedback')
#             fb_text = f"피드백: {feedback.get('rating', '?')}/5 - {feedback.get('feedback', '')}"
#             history.add_message(HumanMessage(content="피드백 제출"))
#             history.add_message(AIMessage(content=fb_text))
        
#         self.user_data[user_id].append(record)
        
#         # 히스토리 너무 길면 요약
#         if len(history.messages) > 20:
#             self._summarize_and_reset(user_id)

#     def _summarize_and_reset(self, user_id: str):
#         history = self.get_session_history(user_id)
#         summary_response = self.summary_chain.invoke({"history": history.messages})
#         summary_text = summary_response.content
        
#         self.store[user_id] = InMemoryChatMessageHistory()
#         self.store[user_id].add_message(SystemMessage(content=f"이전 대화 요약: {summary_text}"))

#     def get_memory_context(self, user_id: str) -> str:
#         history = self.get_session_history(user_id)
#         if not history.messages:
#             return ""
        
#         context_parts = []
#         for msg in history.messages:
#             role = "사용자" if isinstance(msg, HumanMessage) else "루미" if isinstance(msg, AIMessage) else "시스템"
#             context_parts.append(f"{role}: {msg.content}")
#         return "\n".join(context_parts)

#     def get_user_learning_summary(self, user_id: str) -> str:
#         """DB 없이 메모리에서 학습 요약 생성 (임시)"""
#         records = self.user_data.get(user_id, [])
#         if not records:
#             return "아직 학습된 데이터가 없습니다. 일정을 더 생성하고 피드백을 남겨주세요!"
        
#         # 피드백 있는 기록만
#         feedback_records = [r for r in records if r.get('rating')]
#         if feedback_records:
#             positive = [r for r in feedback_records if r['rating'] >= 4]
#             negative = [r for r in feedback_records if r['rating'] <= 2]
            
#             parts = []
#             if positive:
#                 parts.append("✅ 좋아했던 일정 패턴:")
#                 for r in positive[:3]:
#                     parts.append(f"  - {r['date']}: {r.get('feedback', '좋아요!')}")
#             if negative:
#                 parts.append("\n⚠️ 개선이 필요한 부분:")
#                 for r in negative[:3]:
#                     parts.append(f"  - {r['date']}: {r.get('feedback', '개선 필요')}")
#             return "\n".join(parts)
        
#         return "일정을 생성했지만 아직 피드백이 없어요. 별점과 코멘트를 남겨주시면 더 똑똑해질게요!"

#     def analyze_user_patterns(self, user_id: str) -> dict:
#         """DB 없이 메모리에서 패턴 분석 (임시)"""
#         records = self.user_data.get(user_id, [])
#         total = len(records)
#         if total == 0:
#             return {
#                 "total_schedules": 0,
#                 "average_rating": 0,
#                 "most_common_tasks": {},
#                 "insights": "아직 데이터가 없어요. 첫 일정을 만들어 보세요!"
#             }
        
#         ratings = [r['rating'] for r in records if r.get('rating')]
#         avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
#         task_counter = Counter()
#         for r in records:
#             for task in r.get('tasks', []):
#                 name = task.get('name', 'unknown')
#                 task_counter[name] += 1
        
#         most_common = dict(task_counter.most_common(5))
        
#         insights = f"총 {total}번 일정을 만들었어요! 평균 만족도 {avg_rating:.1f}/5"
#         if avg_rating >= 4:
#             insights += " 🎉 정말 잘 맞춰드리고 있네요!"
#         elif avg_rating >= 3:
#             insights += " 😊 조금 더 피드백 주시면 완벽해질 거예요!"
#         else:
#             insights += " 💪 더 열심히 공부할게요!"
        
#         return {
#             "total_schedules": total,
#             "average_rating": round(avg_rating, 2),
#             "most_common_tasks": most_common,
#             "insights": insights
#         }


## memory_manager.py

from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, Optional
import json
from collections import defaultdict, Counter
from datetime import datetime

class MemoryManager:
    """사용자별 학습 및 메모리 관리 클래스 (LangChain 1.x 호환)"""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(groq_api_key=api_key, model_name=model_name)
        
        # 사용자별 히스토리 저장소
        self.store: Dict[str, InMemoryChatMessageHistory] = {}
        
        # 사용자별 데이터 기록 (DB 대신 메모리)
        self.user_data: Dict[str, list] = defaultdict(list)
        
        # 요약용 체인 설정
        summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="다음 대화를 3~5문장으로 간결하게 요약해 주세요. 중요한 사용자 선호도, 일정 패턴, 피드백 위주로."),
            MessagesPlaceholder(variable_name="history")
        ])
        self.summary_chain = summary_prompt | self.llm
        
    def get_session_history(self, user_id: str) -> InMemoryChatMessageHistory:
        if user_id not in self.store:
            self.store[user_id] = InMemoryChatMessageHistory()
        return self.store[user_id]

    # --- 수정된 add_schedule_interaction 메서드 시작 ---
    def add_schedule_interaction(
        self,
        user_id: str,
        schedule_request: dict = None,
        generated_schedule: dict = None,
        feedback: dict = None
    ):
        # 1. 안전한 None 처리
        if schedule_request is None:
            schedule_request = {}
        if generated_schedule is None:
            generated_schedule = {}

        history = self.get_session_history(user_id)
        
        # 2. 요청 텍스트 처리 (데이터가 없어도 오류 방지)
        task_names = [task.get('name', '') for task in schedule_request.get('tasks', [])]
        request_text = "이전 일정에 대한 피드백을 남겼습니다."
        
        if task_names:
            request_text = f"작업: {', '.join(task_names)}에 대한 피드백"
        
        history.add_message(HumanMessage(content=request_text))
        
        # 3. 피드백 처리 및 AI 응답 기록
        if feedback:
            rating = feedback.get('rating', 0)
            fb_text = f"평점: {rating}/5"
            if feedback.get('feedback'):
                fb_text += f" - {feedback['feedback']}"
            
            history.add_message(AIMessage(content=fb_text))
            print(f"📝 피드백 저장됨 (User: {user_id}): {rating}/5")
            
        # 4. 기록 저장 (임시 메모리 user_data)
        record = {
            "date": schedule_request.get('date', "unknown"),
            "tasks": schedule_request.get('tasks', []),
            "created_at": datetime.utcnow().isoformat(),
            "rating": feedback.get('rating') if feedback else None,
            "feedback": feedback.get('feedback') if feedback else None
        }
        self.user_data[user_id].append(record)
        
        # 5. 대화 요약 관리 (20개 초과 시)
        if len(history.messages) > 20:
            self._summarize_and_reset(user_id)
    # --- 수정된 메서드 끝 ---

    def _summarize_and_reset(self, user_id: str):
        history = self.get_session_history(user_id)
        summary_response = self.summary_chain.invoke({"history": history.messages})
        summary_text = summary_response.content
        
        self.store[user_id] = InMemoryChatMessageHistory()
        self.store[user_id].add_message(SystemMessage(content=f"이전 대화 요약: {summary_text}"))

    def get_memory_context(self, user_id: str) -> str:
        history = self.get_session_history(user_id)
        if not history.messages:
            return ""
        
        context_parts = []
        for msg in history.messages:
            role = "사용자" if isinstance(msg, HumanMessage) else "루미" if isinstance(msg, AIMessage) else "시스템"
            context_parts.append(f"{role}: {msg.content}")
        return "\n".join(context_parts)

    def get_user_learning_summary(self, user_id: str) -> str:
        records = self.user_data.get(user_id, [])
        if not records:
            return "아직 학습된 데이터가 없습니다."
        
        feedback_records = [r for r in records if r.get('rating') is not None]
        if feedback_records:
            positive = [r for r in feedback_records if r['rating'] >= 4]
            negative = [r for r in feedback_records if r['rating'] <= 2]
            
            parts = []
            if positive:
                parts.append("✅ 좋아했던 일정 패턴:")
                for r in positive[:3]:
                    parts.append(f"  - {r.get('date', 'Unknown')}: {r.get('feedback', '좋아요!')}")
            if negative:
                parts.append("\n⚠️ 개선이 필요한 부분:")
                for r in negative[:3]:
                    parts.append(f"  - {r.get('date', 'Unknown')}: {r.get('feedback', '개선 필요')}")
            return "\n".join(parts)
        
        return "일정을 생성했지만 아직 피드백이 없어요."

    def analyze_user_patterns(self, user_id: str) -> dict:
        records = self.user_data.get(user_id, [])
        total = len(records)
        if total == 0:
            return {"total_schedules": 0, "insights": "데이터가 없습니다."}
        
        ratings = [r['rating'] for r in records if r.get('rating') is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "total_schedules": total,
            "average_rating": round(avg_rating, 2),
            "insights": f"총 {total}번의 일정 중 평균 평점 {avg_rating:.1f}점을 기록 중입니다."
        }