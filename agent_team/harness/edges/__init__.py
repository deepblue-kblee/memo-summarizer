"""
에이전트 팀 엣지 로직

조건부 분기를 담당합니다:
- Gatekeeper: 검증 결과에 따른 Pass/Retry/Escalate 결정
"""

from .gatekeeper import GatekeeperEdge

__all__ = ["GatekeeperEdge"]