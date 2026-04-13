"""
사용자 인터페이스 모듈

에이전트 팀과 사용자 간의 상호작용을 처리합니다.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .state import AgentState


class UserInterface:
    """
    사용자 인터페이스 관리자

    작업 완료 후 사용자에게 결과를 제시하고 다음 요청을 안내합니다.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        사용자 인터페이스 초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}

    def present_completion_results(self, state: AgentState) -> str:
        """
        작업 완료 결과 제시

        Args:
            state: 완료된 상태

        Returns:
            완료 메시지
        """
        # 기본 완료 정보
        completion_info = {
            "request": state.get("user_request", ""),
            "status": state.get("status", ""),
            "quality_score": state.get("quality_score", 0.0),
            "files_generated": len(state.get("generated_files", [])),
            "tasks_completed": len(state.get("todo_list", [])),
            "errors_resolved": len(state.get("error_history", [])),
            "lessons_learned": len(state.get("lessons_learned", []))
        }

        # 완료 메시지 생성
        message_parts = [
            "🎯 작업 완료 결과",
            "=" * 50,
            f"📝 요청: {completion_info['request'][:100]}{'...' if len(completion_info['request']) > 100 else ''}",
            f"📊 상태: {completion_info['status']}",
            f"⭐ 품질 점수: {completion_info['quality_score']:.1f}/10.0",
            f"📁 생성된 파일: {completion_info['files_generated']}개",
            f"✅ 완료된 작업: {completion_info['tasks_completed']}개"
        ]

        if completion_info['errors_resolved'] > 0:
            message_parts.append(f"🔧 해결된 문제: {completion_info['errors_resolved']}개")

        if completion_info['lessons_learned'] > 0:
            message_parts.append(f"🧠 학습한 내용: {completion_info['lessons_learned']}개")

        # 생성된 파일 목록
        generated_files = state.get("generated_files", [])
        if generated_files:
            message_parts.extend([
                "",
                "📋 생성된 파일 목록:"
            ])
            for i, file_info in enumerate(generated_files[:10], 1):  # 최대 10개
                path = file_info.get("path", "unknown")
                file_type = file_info.get("type", "unknown")
                message_parts.append(f"  {i}. {path} ({file_type})")

            if len(generated_files) > 10:
                message_parts.append(f"  ... 외 {len(generated_files) - 10}개 파일")

        # 최근 학습 내용
        lessons = state.get("lessons_learned", [])
        if lessons:
            message_parts.extend([
                "",
                "💡 주요 학습 내용:"
            ])
            for lesson in lessons[-3:]:  # 최근 3개
                message_parts.append(f"  • {lesson}")

        # 품질 세부사항
        validation_results = state.get("validation_results", {})
        if validation_results and "scores" in validation_results:
            message_parts.extend([
                "",
                "🔍 품질 세부 점수:"
            ])
            scores = validation_results["scores"]
            for check_name, score in scores.items():
                message_parts.append(f"  • {check_name}: {score:.1f}/10.0")

        return "\n".join(message_parts)

    def generate_next_request_prompt(self, state: AgentState) -> str:
        """
        다음 요청 안내 메시지 생성

        Args:
            state: 현재 상태

        Returns:
            다음 요청 안내 메시지
        """
        prompt_parts = [
            "",
            "=" * 50,
            "🚀 다음 작업을 시작할 준비가 되었습니다!",
            "",
            "💬 무엇을 도와드릴까요?",
            "",
            "예시 요청:",
            "  • '새로운 기능을 구현해줘'",
            "  • '버그를 수정해줘'",
            "  • '테스트 코드를 작성해줘'",
            "  • '코드를 리팩토링해줘'",
            "  • '문서를 만들어줘'",
            "",
            "💡 팁: 구체적으로 설명할수록 더 좋은 결과를 얻을 수 있습니다.",
            "=" * 50
        ]

        return "\n".join(prompt_parts)

    def generate_error_message(self, state: AgentState, error: Exception) -> str:
        """
        에러 메시지 생성

        Args:
            state: 현재 상태
            error: 발생한 에러

        Returns:
            에러 메시지
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "current_node": state.get("current_node", "unknown"),
            "retry_count": state.get("retry_count", 0),
            "max_retries": state.get("max_retries", 3)
        }

        message_parts = [
            "❌ 작업 중 오류가 발생했습니다",
            "=" * 40,
            f"🔍 오류 유형: {error_info['error_type']}",
            f"📝 오류 메시지: {error_info['error_message']}",
            f"📍 발생 위치: {error_info['current_node']}",
            f"🔄 재시도 횟수: {error_info['retry_count']}/{error_info['max_retries']}"
        ]

        # 재시도 가능 여부에 따른 안내
        if error_info['retry_count'] < error_info['max_retries']:
            message_parts.extend([
                "",
                "🔄 자동으로 재시도됩니다...",
                "💡 문제를 학습하여 다음 시도에서 개선하겠습니다."
            ])
        else:
            message_parts.extend([
                "",
                "⚠️ 최대 재시도 횟수에 도달했습니다.",
                "🆘 수동 개입이 필요할 수 있습니다."
            ])

        # 이전 에러 패턴이 있으면 참고 정보 제공
        error_history = state.get("error_history", [])
        if len(error_history) > 1:
            message_parts.extend([
                "",
                f"📊 참고: 지금까지 {len(error_history)}개의 문제가 발생했습니다."
            ])

        return "\n".join(message_parts)

    def generate_progress_update(self, state: AgentState) -> str:
        """
        진행상황 업데이트 메시지 생성

        Args:
            state: 현재 상태

        Returns:
            진행상황 메시지
        """
        todo_list = state.get("todo_list", [])
        current_index = state.get("current_task_index", 0)
        current_node = state.get("current_node", "unknown")

        if not todo_list:
            return f"🔄 {current_node} 단계에서 작업 중..."

        progress_percent = (current_index / len(todo_list)) * 100 if todo_list else 0

        current_task = "진행 상황 파악 중..."
        if current_index < len(todo_list):
            current_task = todo_list[current_index].get("title", "작업 진행 중...")

        message_parts = [
            f"📊 진행률: {progress_percent:.0f}% ({current_index}/{len(todo_list)})",
            f"🎯 현재 작업: {current_task}",
            f"⚙️ 처리 단계: {current_node}"
        ]

        return "\n".join(message_parts)

    def format_session_summary(self, sessions: list) -> str:
        """
        세션 요약 포맷팅

        Args:
            sessions: 세션 목록

        Returns:
            포맷된 세션 요약
        """
        if not sessions:
            return "📭 최근 세션이 없습니다."

        message_parts = [
            "📚 최근 세션 히스토리",
            "=" * 40
        ]

        for i, session in enumerate(sessions[:10], 1):  # 최대 10개
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "planning": "📝",
                "implementing": "⚙️",
                "validating": "🔍"
            }.get(session["status"], "❓")

            message_parts.append(
                f"{i:2d}. {status_emoji} {session['user_request'][:60]}{'...' if len(session['user_request']) > 60 else ''}"
            )
            message_parts.append(
                f"     🕒 {session['created_at']} | ID: {session['session_id'][:8]}..."
            )
            message_parts.append("")

        return "\n".join(message_parts)

    def generate_help_message(self) -> str:
        """
        도움말 메시지 생성

        Returns:
            도움말 메시지
        """
        help_parts = [
            "🤖 Agent Team 사용법",
            "=" * 30,
            "",
            "기본 명령어:",
            "  agent-team run '요청 내용'           # 단일 요청 처리",
            "  agent-team run --interactive        # 대화형 모드",
            "  agent-team status [요청ID]          # 상태 조회",
            "  agent-team history                  # 히스토리 조회",
            "  agent-team resume 요청ID            # 중단된 요청 재개",
            "",
            "시뮬레이션:",
            "  agent-simulate                      # 모든 시나리오 실행",
            "  agent-simulate --list               # 시나리오 목록",
            "  agent-simulate --scenario 이름      # 특정 시나리오 실행",
            "",
            "예시 요청:",
            "  • 'Python 계산기 프로그램을 만들어줘'",
            "  • 'API 서버를 구현해줘'",
            "  • '버그를 수정해줘'",
            "  • '테스트 코드를 작성해줘'",
            "",
            "💡 자세한 내용은 문서를 참조하세요."
        ]

        return "\n".join(help_parts)