"""
Gatekeeper Edge - 워크플로우 제어 로직

검증 결과를 바탕으로 Pass/Retry/Escalate를 결정하는 조건부 엣지입니다.
"""

from typing import Dict, Any, Literal
from datetime import datetime

from ..state import AgentState


class GatekeeperEdge:
    """
    워크플로우 게이트키퍼

    검증 결과를 분석하여 다음 단계를 결정합니다:
    - Pass: 품질 기준을 만족하여 완료
    - Retry: 품질 개선이 필요하여 재시도
    - Escalate: 재시도 한계에 도달하여 에스컬레이션
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Gatekeeper 초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.quality_threshold = config.get("quality_threshold", 7.0)  # 기본 품질 임계값
        self.max_retries = config.get("max_retries", 3)               # 최대 재시도 횟수

    def decide(self, state: AgentState) -> Literal["pass", "retry", "escalate"]:
        """
        워크플로우 결정

        Args:
            state: 현재 상태

        Returns:
            다음 단계 결정 ("pass", "retry", "escalate")
        """
        try:
            # 현재 품질 점수 확인
            quality_score = state.get("quality_score", 0.0)
            retry_count = state.get("retry_count", 0)
            max_retries = state.get("max_retries", self.max_retries)

            # 재시도 한계 확인
            if retry_count >= max_retries:
                return self._handle_escalate(state, "재시도 한계 도달")

            # 품질 점수 기반 판단
            if quality_score >= self.quality_threshold:
                return self._handle_pass(state)

            # 심각한 오류 확인
            validation_results = state.get("validation_results", {})
            if self._has_critical_issues(validation_results):
                return self._handle_escalate(state, "심각한 품질 문제 감지")

            # 개선 가능성 확인
            if self._can_improve(state):
                return self._handle_retry(state)
            else:
                return self._handle_escalate(state, "개선 불가능한 상태")

        except Exception as e:
            # 결정 로직 실패 시 안전하게 에스컬레이션
            self._add_error_to_history(state, e, "Gatekeeper 결정 실패")
            return self._handle_escalate(state, f"결정 로직 오류: {e}")

    def _handle_pass(self, state: AgentState) -> Literal["pass"]:
        """
        통과 처리

        Args:
            state: 현재 상태

        Returns:
            "pass"
        """
        # 성공 기록
        self._add_lesson_learned(
            state,
            f"품질 기준 통과: 점수 {state.get('quality_score', 0):.1f}/{self.quality_threshold}"
        )

        # 상태 업데이트
        state["status"] = "passed_validation"

        print(f"✅ 품질 검증 통과! (점수: {state.get('quality_score', 0):.1f})")
        return "pass"

    def _handle_retry(self, state: AgentState) -> Literal["retry"]:
        """
        재시도 처리

        Args:
            state: 현재 상태

        Returns:
            "retry"
        """
        retry_count = state.get("retry_count", 0)
        quality_score = state.get("quality_score", 0.0)

        # 재시도 이유 분석
        retry_reason = self._analyze_retry_reason(state)

        # 학습 내용 추가
        self._add_lesson_learned(
            state,
            f"재시도 {retry_count + 1}: {retry_reason} (현재 점수: {quality_score:.1f})"
        )

        # 개선 힌트 제공
        improvement_hints = self._generate_improvement_hints(state)
        if improvement_hints:
            self._add_lesson_learned(state, f"개선 힌트: {improvement_hints}")

        print(f"🔄 재시도 필요: {retry_reason} (점수: {quality_score:.1f})")
        return "retry"

    def _handle_escalate(self, state: AgentState, reason: str) -> Literal["escalate"]:
        """
        에스컬레이션 처리

        Args:
            state: 현재 상태
            reason: 에스컬레이션 이유

        Returns:
            "escalate"
        """
        # 에스컬레이션 기록
        escalation_info = {
            "reason": reason,
            "final_score": state.get("quality_score", 0.0),
            "retry_count": state.get("retry_count", 0),
            "timestamp": datetime.now().isoformat(),
            "validation_results": state.get("validation_results", {}),
            "error_history": state.get("error_history", [])
        }

        # 상태 업데이트
        state["status"] = "escalated"
        state["escalation_info"] = escalation_info

        # 학습 내용 추가
        self._add_lesson_learned(
            state,
            f"에스컬레이션: {reason} (최종 점수: {state.get('quality_score', 0.0):.1f})"
        )

        print(f"⚠️ 에스컬레이션: {reason}")
        return "escalate"

    def _has_critical_issues(self, validation_results: Dict[str, Any]) -> bool:
        """
        심각한 품질 문제 확인

        Args:
            validation_results: 검증 결과

        Returns:
            심각한 문제 존재 여부
        """
        # 구문 오류 확인
        syntax_score = validation_results.get("scores", {}).get("syntax", 10.0)
        if syntax_score < 5.0:
            return True

        # 보안 문제 확인
        security_score = validation_results.get("scores", {}).get("security", 10.0)
        if security_score < 3.0:
            return True

        # 심각한 이슈 키워드 확인
        issues = validation_results.get("issues_found", [])
        critical_keywords = ["VIOLATION", "CRITICAL", "SECURITY", "SYNTAX ERROR"]

        for issue in issues:
            if any(keyword in issue.upper() for keyword in critical_keywords):
                return True

        return False

    def _can_improve(self, state: AgentState) -> bool:
        """
        개선 가능성 확인

        Args:
            state: 현재 상태

        Returns:
            개선 가능 여부
        """
        # 현재 점수가 너무 낮으면 개선 어려움
        quality_score = state.get("quality_score", 0.0)
        if quality_score < 2.0:
            return False

        # 과거 재시도에서 점수가 개선되었는지 확인
        lessons = state.get("lessons_learned", [])
        recent_scores = []

        for lesson in lessons[-5:]:  # 최근 5개 학습 내용 확인
            if "점수" in lesson or "score" in lesson.lower():
                import re
                score_match = re.search(r'(\d+\.?\d*)', lesson)
                if score_match:
                    recent_scores.append(float(score_match.group(1)))

        # 점수가 개선 추세인지 확인
        if len(recent_scores) >= 2:
            return recent_scores[-1] > recent_scores[-2]

        # 기본적으로는 개선 가능하다고 가정
        return True

    def _analyze_retry_reason(self, state: AgentState) -> str:
        """
        재시도 이유 분석

        Args:
            state: 현재 상태

        Returns:
            재시도 이유 문자열
        """
        validation_results = state.get("validation_results", {})
        scores = validation_results.get("scores", {})
        issues = validation_results.get("issues_found", [])

        reasons = []

        # 점수별 문제 분석
        for check_name, score in scores.items():
            if score < self.quality_threshold:
                if check_name == "syntax":
                    reasons.append("구문 오류")
                elif check_name == "code_style":
                    reasons.append("코딩 스타일")
                elif check_name == "tests":
                    reasons.append("테스트 실패")
                elif check_name == "security":
                    reasons.append("보안 문제")
                elif check_name == "harness_linter":
                    reasons.append("품질 규칙 위반")

        # 이슈 기반 분석
        if not reasons and issues:
            if any("WARNING" in issue for issue in issues):
                reasons.append("경고 사항 해결 필요")
            else:
                reasons.append("품질 개선 필요")

        if not reasons:
            reasons.append(f"품질 점수 부족 ({state.get('quality_score', 0):.1f} < {self.quality_threshold})")

        return ", ".join(reasons)

    def _generate_improvement_hints(self, state: AgentState) -> str:
        """
        개선 힌트 생성

        Args:
            state: 현재 상태

        Returns:
            개선 힌트 문자열
        """
        validation_results = state.get("validation_results", {})
        scores = validation_results.get("scores", {})
        issues = validation_results.get("issues_found", [])

        hints = []

        # 점수별 힌트
        if scores.get("syntax", 10) < 7:
            hints.append("구문 오류 수정")

        if scores.get("code_style", 10) < 7:
            hints.append("코딩 스타일 개선")

        if scores.get("tests", 10) < 7:
            hints.append("테스트 케이스 추가")

        if scores.get("security", 10) < 7:
            hints.append("보안 취약점 해결")

        # 이슈별 힌트
        if any("라인이 너무 깁니다" in issue for issue in issues):
            hints.append("코드 라인 길이 단축")

        if any("VIOLATION" in issue for issue in issues):
            hints.append("품질 규칙 준수")

        if not hints:
            hints.append("코드 품질 전반적 개선")

        return ", ".join(hints[:3])  # 최대 3개 힌트

    def _add_lesson_learned(self, state: AgentState, lesson: str):
        """학습 내용 추가"""
        if lesson not in state["lessons_learned"]:
            state["lessons_learned"].append(lesson)

        # 최대 20개까지만 유지
        if len(state["lessons_learned"]) > 20:
            state["lessons_learned"] = state["lessons_learned"][-20:]

    def _add_error_to_history(self, state: AgentState, error: Exception, context: str):
        """에러 히스토리 추가"""
        error_entry = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "node": "gatekeeper"
        }
        state["error_history"].append(error_entry)