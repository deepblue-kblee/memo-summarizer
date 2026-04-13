"""
에이전트 팀 상태 관리 시스템

도메인 중립적인 상태 정의 및 SQLite 기반 영속성 제공
"""

from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import json
import os
from pathlib import Path


class AgentState(TypedDict):
    """
    범용 에이전트 상태 정의

    도메인에 관계없이 모든 요청에 대해 공통으로 사용되는 상태 구조
    """
    # 사용자 요청 관련
    user_request: str                    # 원본 사용자 요청
    request_id: str                     # 고유 요청 식별자

    # 계획 단계
    todo_list: List[Dict[str, Any]]     # Planner가 생성한 할 일 목록
    current_task_index: int             # 현재 진행 중인 작업 인덱스

    # 구현 단계
    generated_files: List[Dict[str, Any]]  # Engineer가 생성/수정한 파일 목록
    code_changes: List[Dict[str, Any]]     # 코드 변경 히스토리

    # 검증 단계
    validation_results: Dict[str, Any]   # Validator 검증 결과
    test_results: Dict[str, Any]        # 테스트 실행 결과
    quality_score: float                # 전체 품질 점수

    # 워크플로우 제어
    current_node: str                   # 현재 실행 중인 노드
    retry_count: int                    # 현재 작업 재시도 횟수
    max_retries: int                    # 최대 재시도 횟수

    # 에러 및 학습
    error_history: List[Dict[str, Any]] # 발생한 에러들의 히스토리
    lessons_learned: List[str]          # 에러로부터 학습한 내용들

    # 메타데이터
    created_at: str                     # 요청 생성 시간
    updated_at: str                     # 마지막 업데이트 시간
    status: str                         # 전체 상태 (planning, implementing, validating, completed, failed)


@dataclass
class SessionInfo:
    """세션 정보"""
    session_id: str
    user_request: str
    status: str
    created_at: datetime
    updated_at: datetime


class StateManager:
    """
    SQLite 기반 상태 관리자

    AgentState의 영속성을 제공하고 히스토리를 관리합니다.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        상태 관리자 초기화

        Args:
            db_path: SQLite 데이터베이스 파일 경로. None이면 기본 경로 사용.
        """
        if db_path is None:
            # agent_team/tracking 디렉토리에 저장
            db_dir = Path(__file__).parent.parent / "tracking"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "agent_states.db")

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """데이터베이스 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    request_id TEXT PRIMARY KEY,
                    state_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_history (
                    session_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    user_request TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES agent_states (request_id)
                )
            """)

            # 인덱스 생성
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_created ON session_history(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_state_updated ON agent_states(updated_at)")

    def save_state(self, state: AgentState) -> bool:
        """
        상태를 데이터베이스에 저장

        Args:
            state: 저장할 AgentState

        Returns:
            bool: 저장 성공 여부
        """
        try:
            state_json = json.dumps(state, ensure_ascii=False, indent=2)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO agent_states
                    (request_id, state_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    state['request_id'],
                    state_json,
                    state['created_at'],
                    state['updated_at']
                ))

                # 세션 히스토리도 업데이트
                conn.execute("""
                    INSERT OR REPLACE INTO session_history
                    (session_id, request_id, user_request, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    state['request_id'],  # session_id로 request_id 사용
                    state['request_id'],
                    state['user_request'],
                    state['status'],
                    state['created_at'],
                    state['updated_at']
                ))

            return True

        except Exception as e:
            print(f"상태 저장 실패: {e}")
            return False

    def load_state(self, request_id: str) -> Optional[AgentState]:
        """
        데이터베이스에서 상태 로드

        Args:
            request_id: 로드할 요청 ID

        Returns:
            AgentState 또는 None (찾을 수 없는 경우)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT state_data FROM agent_states WHERE request_id = ?",
                    (request_id,)
                )
                row = cursor.fetchone()

                if row:
                    return json.loads(row[0])
                return None

        except Exception as e:
            print(f"상태 로드 실패: {e}")
            return None

    def get_recent_sessions(self, limit: int = 10) -> List[SessionInfo]:
        """
        최근 세션 목록 조회

        Args:
            limit: 조회할 세션 수

        Returns:
            SessionInfo 리스트
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, user_request, status, created_at, updated_at
                    FROM session_history
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))

                sessions = []
                for row in cursor.fetchall():
                    sessions.append(SessionInfo(
                        session_id=row[0],
                        user_request=row[1],
                        status=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        updated_at=datetime.fromisoformat(row[4])
                    ))

                return sessions

        except Exception as e:
            print(f"세션 히스토리 조회 실패: {e}")
            return []

    def delete_state(self, request_id: str) -> bool:
        """
        상태 삭제

        Args:
            request_id: 삭제할 요청 ID

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM agent_states WHERE request_id = ?", (request_id,))
                conn.execute("DELETE FROM session_history WHERE request_id = ?", (request_id,))
            return True

        except Exception as e:
            print(f"상태 삭제 실패: {e}")
            return False


def create_initial_state(user_request: str, request_id: Optional[str] = None) -> AgentState:
    """
    초기 AgentState 생성

    Args:
        user_request: 사용자 요청
        request_id: 요청 ID (None이면 자동 생성)

    Returns:
        초기화된 AgentState
    """
    if request_id is None:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    now = datetime.now().isoformat()

    return AgentState(
        user_request=user_request,
        request_id=request_id,
        todo_list=[],
        current_task_index=0,
        generated_files=[],
        code_changes=[],
        validation_results={},
        test_results={},
        quality_score=0.0,
        current_node="planner",
        retry_count=0,
        max_retries=3,
        error_history=[],
        lessons_learned=[],
        created_at=now,
        updated_at=now,
        status="planning"
    )