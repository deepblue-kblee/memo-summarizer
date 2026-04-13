"""
범용 LangGraph 에이전트 개발팀 메인 클래스

사용자 요청을 받아 자동으로 계획 -> 구현 -> 검증 워크플로우를 수행합니다.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
try:
    from langgraph_checkpoint.sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        # 폴백: 임시 클래스
        class SqliteSaver:
            @classmethod
            def from_conn_string(cls, conn_string):
                return None

from .state import AgentState, StateManager, create_initial_state
from .nodes import PlannerNode, EngineerNode, ValidatorNode
from .edges import GatekeeperEdge


class AgentTeam:
    """
    범용 에이전트 개발팀

    LangGraph StateGraph를 기반으로 한 자율적 개발 워크플로우를 제공합니다.
    """

    def __init__(self, db_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        에이전트 팀 초기화

        Args:
            db_path: SQLite 데이터베이스 경로
            config: 에이전트 설정 (AI 클라이언트, 최대 재시도 등)
        """
        self.state_manager = StateManager(db_path)
        self.config = config or {}

        # 노드 초기화
        self.planner = PlannerNode(self.config)
        self.engineer = EngineerNode(self.config)
        self.validator = ValidatorNode(self.config)
        self.gatekeeper = GatekeeperEdge(self.config)

        # LangGraph StateGraph 구성
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        LangGraph StateGraph 구성

        Returns:
            설정된 StateGraph
        """
        # StateGraph 생성
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node("planner", self.planner.execute)
        workflow.add_node("engineer", self.engineer.execute)
        workflow.add_node("validator", self.validator.execute)
        workflow.add_node("user_interface", self._user_interface_node)

        # 시작점 설정
        workflow.set_entry_point("planner")

        # 엣지 추가
        workflow.add_edge("planner", "engineer")
        workflow.add_edge("engineer", "validator")

        # 조건부 엣지 (Gatekeeper)
        workflow.add_conditional_edges(
            "validator",
            self.gatekeeper.decide,
            {
                "pass": "user_interface",  # 완료 -> 사용자 인터페이스
                "retry": "engineer",       # 재시도 -> 엔지니어로 돌아가기
                "escalate": END           # 에스컬레이션 -> 종료
            }
        )

        workflow.add_edge("user_interface", END)

        return workflow

    def _user_interface_node(self, state: AgentState) -> AgentState:
        """
        사용자 인터페이스 노드

        작업 완료 후 사용자에게 결과를 제시하고 다음 요청을 안내합니다.

        Args:
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        # 상태 업데이트
        state["current_node"] = "user_interface"
        state["status"] = "completed"
        state["updated_at"] = datetime.now().isoformat()

        # 작업 완료 메시지 생성
        completion_message = self._generate_completion_message(state)
        print(completion_message)

        # 다음 요청 안내
        print("\n" + "="*50)
        print("🎯 작업이 완료되었습니다!")
        print("💡 다음에 무엇을 개발할까요?")
        print("   새로운 요청을 입력해주세요.")
        print("="*50)

        return state

    def _generate_completion_message(self, state: AgentState) -> str:
        """
        작업 완료 메시지 생성

        Args:
            state: 완료된 상태

        Returns:
            완료 메시지 문자열
        """
        messages = [
            f"✅ 요청 완료: {state['user_request']}",
            f"📋 처리된 작업: {len(state['todo_list'])}개",
            f"📝 생성된 파일: {len(state['generated_files'])}개",
            f"⭐ 품질 점수: {state['quality_score']:.2f}/10.0"
        ]

        if state['error_history']:
            messages.append(f"🔧 해결된 문제: {len(state['error_history'])}개")

        if state['lessons_learned']:
            messages.append("🧠 학습된 내용:")
            for lesson in state['lessons_learned'][-3:]:  # 최근 3개만
                messages.append(f"   • {lesson}")

        return "\n".join(messages)

    def process_request(self, user_request: str, request_id: Optional[str] = None) -> AgentState:
        """
        사용자 요청 처리

        Args:
            user_request: 사용자 요청
            request_id: 요청 ID (None이면 자동 생성)

        Returns:
            최종 처리된 상태
        """
        # 초기 상태 생성
        if request_id is None:
            request_id = f"req_{uuid.uuid4().hex[:8]}"

        initial_state = create_initial_state(user_request, request_id)

        # SQLite checkpointer 설정
        checkpointer = SqliteSaver.from_conn_string(self.state_manager.db_path)
        compiled_graph = self.graph.compile(checkpointer=checkpointer)

        try:
            # 그래프 실행
            config = {"configurable": {"thread_id": request_id}}
            result = None

            for chunk in compiled_graph.stream(initial_state, config):
                # 중간 상태를 데이터베이스에 저장
                for node_name, node_state in chunk.items():
                    self.state_manager.save_state(node_state)
                    result = node_state

            return result

        except Exception as e:
            # 에러 발생 시 상태 업데이트
            error_state = initial_state.copy()
            error_state["status"] = "failed"
            error_state["error_history"].append({
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "node": error_state.get("current_node", "unknown")
            })
            error_state["updated_at"] = datetime.now().isoformat()

            self.state_manager.save_state(error_state)
            raise

    def resume_request(self, request_id: str) -> Optional[AgentState]:
        """
        중단된 요청 재개

        Args:
            request_id: 재개할 요청 ID

        Returns:
            재개된 상태 또는 None (찾을 수 없는 경우)
        """
        saved_state = self.state_manager.load_state(request_id)
        if not saved_state:
            print(f"요청 ID '{request_id}'를 찾을 수 없습니다.")
            return None

        # 완료된 요청은 재개할 수 없음
        if saved_state["status"] in ["completed", "failed"]:
            print(f"요청이 이미 {saved_state['status']} 상태입니다.")
            return saved_state

        try:
            # SQLite checkpointer로 재개
            checkpointer = SqliteSaver.from_conn_string(self.state_manager.db_path)
            compiled_graph = self.graph.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": request_id}}
            result = None

            for chunk in compiled_graph.stream(None, config):  # None으로 시작하면 저장된 상태에서 재개
                for node_name, node_state in chunk.items():
                    self.state_manager.save_state(node_state)
                    result = node_state

            return result

        except Exception as e:
            print(f"요청 재개 실패: {e}")
            return None

    def get_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        요청 상태 조회

        Args:
            request_id: 조회할 요청 ID

        Returns:
            상태 정보 딕셔너리 또는 None
        """
        state = self.state_manager.load_state(request_id)
        if not state:
            return None

        return {
            "request_id": state["request_id"],
            "user_request": state["user_request"],
            "status": state["status"],
            "current_node": state["current_node"],
            "progress": f"{state['current_task_index']}/{len(state['todo_list'])}",
            "quality_score": state["quality_score"],
            "retry_count": state["retry_count"],
            "created_at": state["created_at"],
            "updated_at": state["updated_at"]
        }

    def list_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최근 요청 목록 조회

        Args:
            limit: 조회할 요청 수

        Returns:
            요청 정보 리스트
        """
        sessions = self.state_manager.get_recent_sessions(limit)
        return [
            {
                "session_id": session.session_id,
                "user_request": session.user_request[:100] + "..." if len(session.user_request) > 100 else session.user_request,
                "status": session.status,
                "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": session.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for session in sessions
        ]