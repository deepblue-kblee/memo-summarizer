"""
워크플로우 시뮬레이션 도구

에이전트 팀의 동작을 다양한 시나리오로 테스트하여 검증합니다.
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import tempfile
import shutil
from datetime import datetime
from dataclasses import dataclass

from .agent_team import AgentTeam
from .state import AgentState


@dataclass
class SimulationScenario:
    """시뮬레이션 시나리오"""
    name: str
    description: str
    user_request: str
    expected_outcome: str
    success_criteria: Dict[str, Any]
    setup_files: Optional[Dict[str, str]] = None  # 파일명: 내용
    cleanup_files: Optional[List[str]] = None


class WorkflowSimulator:
    """
    워크플로우 시뮬레이터

    다양한 시나리오를 통해 에이전트 팀의 동작을 검증합니다.
    """

    def __init__(self, agent_team: Optional[AgentTeam] = None):
        """
        시뮬레이터 초기화

        Args:
            agent_team: 테스트할 에이전트 팀 (None이면 새로 생성)
        """
        self.agent_team = agent_team or AgentTeam()
        self.scenarios = self._create_default_scenarios()
        self.simulation_results: List[Dict[str, Any]] = []

    def run_all_simulations(self) -> Dict[str, Any]:
        """
        모든 시뮬레이션 실행

        Returns:
            전체 시뮬레이션 결과
        """
        print("🚀 워크플로우 시뮬레이션 시작...")
        print(f"📋 총 {len(self.scenarios)}개 시나리오 실행")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(self.scenarios),
            "passed": 0,
            "failed": 0,
            "details": []
        }

        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\n[{i}/{len(self.scenarios)}] {scenario.name}")
            print(f"📝 {scenario.description}")

            result = self._run_single_scenario(scenario)
            results["details"].append(result)

            if result["success"]:
                results["passed"] += 1
                print(f"✅ 성공: {result['message']}")
            else:
                results["failed"] += 1
                print(f"❌ 실패: {result['message']}")

        # 최종 결과
        success_rate = (results["passed"] / results["total_scenarios"]) * 100
        print(f"\n{'='*50}")
        print(f"🏁 시뮬레이션 완료")
        print(f"📊 성공률: {success_rate:.1f}% ({results['passed']}/{results['total_scenarios']})")
        print(f"{'='*50}")

        return results

    def run_single_simulation(self, scenario_name: str) -> Dict[str, Any]:
        """
        단일 시뮬레이션 실행

        Args:
            scenario_name: 실행할 시나리오 이름

        Returns:
            시뮬레이션 결과
        """
        scenario = self._find_scenario(scenario_name)
        if not scenario:
            return {
                "scenario": scenario_name,
                "success": False,
                "message": f"시나리오 '{scenario_name}'를 찾을 수 없습니다",
                "details": {}
            }

        return self._run_single_scenario(scenario)

    def _run_single_scenario(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """
        단일 시나리오 실행

        Args:
            scenario: 실행할 시나리오

        Returns:
            실행 결과
        """
        # 임시 디렉토리에서 실행
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()

            try:
                # 임시 디렉토리로 이동
                os.chdir(temp_dir)

                # 시나리오 설정
                self._setup_scenario(scenario)

                # 에이전트 팀 실행
                result_state = self.agent_team.process_request(scenario.user_request)

                # 결과 검증
                success, message, details = self._verify_result(scenario, result_state)

                return {
                    "scenario": scenario.name,
                    "success": success,
                    "message": message,
                    "details": details,
                    "final_state": self._extract_state_summary(result_state)
                }

            except Exception as e:
                return {
                    "scenario": scenario.name,
                    "success": False,
                    "message": f"시뮬레이션 실행 중 오류: {e}",
                    "details": {"error": str(e)},
                    "final_state": None
                }

            finally:
                # 원래 디렉토리로 복귀
                os.chdir(original_cwd)

    def _setup_scenario(self, scenario: SimulationScenario):
        """시나리오 환경 설정"""
        if scenario.setup_files:
            for filename, content in scenario.setup_files.items():
                # 디렉토리 생성
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # 파일 생성
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)

    def _verify_result(self, scenario: SimulationScenario, result_state: AgentState) -> Tuple[bool, str, Dict[str, Any]]:
        """
        결과 검증

        Args:
            scenario: 시나리오
            result_state: 최종 상태

        Returns:
            (성공 여부, 메시지, 상세 정보)
        """
        details = {
            "quality_score": result_state.get("quality_score", 0.0),
            "status": result_state.get("status", "unknown"),
            "files_generated": len(result_state.get("generated_files", [])),
            "errors": len(result_state.get("error_history", [])),
            "lessons_learned": len(result_state.get("lessons_learned", []))
        }

        success_criteria = scenario.success_criteria
        failures = []

        # 상태 검증
        expected_status = success_criteria.get("status")
        if expected_status and result_state.get("status") != expected_status:
            failures.append(f"상태 불일치: 예상 {expected_status}, 실제 {result_state.get('status')}")

        # 품질 점수 검증
        min_quality = success_criteria.get("min_quality_score", 0.0)
        actual_quality = result_state.get("quality_score", 0.0)
        if actual_quality < min_quality:
            failures.append(f"품질 점수 부족: 예상 >= {min_quality}, 실제 {actual_quality}")

        # 파일 생성 검증
        min_files = success_criteria.get("min_files_generated", 0)
        actual_files = len(result_state.get("generated_files", []))
        if actual_files < min_files:
            failures.append(f"생성 파일 부족: 예상 >= {min_files}, 실제 {actual_files}")

        # 에러 한계 검증
        max_errors = success_criteria.get("max_errors", float('inf'))
        actual_errors = len(result_state.get("error_history", []))
        if actual_errors > max_errors:
            failures.append(f"에러 과다: 예상 <= {max_errors}, 실제 {actual_errors}")

        # 파일 존재 검증
        required_files = success_criteria.get("required_files", [])
        for filename in required_files:
            if not os.path.exists(filename):
                failures.append(f"필수 파일 누락: {filename}")

        # 결과 반환
        if failures:
            return False, "; ".join(failures), details
        else:
            return True, "모든 검증 통과", details

    def _extract_state_summary(self, state: AgentState) -> Dict[str, Any]:
        """상태 요약 추출"""
        return {
            "request_id": state.get("request_id"),
            "status": state.get("status"),
            "quality_score": state.get("quality_score"),
            "current_node": state.get("current_node"),
            "retry_count": state.get("retry_count"),
            "files_generated": len(state.get("generated_files", [])),
            "todo_completed": f"{state.get('current_task_index', 0)}/{len(state.get('todo_list', []))}"
        }

    def _find_scenario(self, scenario_name: str) -> Optional[SimulationScenario]:
        """시나리오 이름으로 찾기"""
        for scenario in self.scenarios:
            if scenario.name == scenario_name:
                return scenario
        return None

    def _create_default_scenarios(self) -> List[SimulationScenario]:
        """기본 시뮬레이션 시나리오들 생성"""
        return [
            # 1. 간단한 파일 생성
            SimulationScenario(
                name="simple_file_creation",
                description="간단한 Python 파일 생성 테스트",
                user_request="hello.py 파일을 만들어줘",
                expected_outcome="hello.py 파일이 생성됨",
                success_criteria={
                    "status": "completed",
                    "min_quality_score": 6.0,
                    "min_files_generated": 1,
                    "max_errors": 2,
                    "required_files": ["hello.py"]
                }
            ),

            # 2. 기능 구현 요청
            SimulationScenario(
                name="feature_implementation",
                description="간단한 기능 구현 요청 테스트",
                user_request="계산기 함수를 구현해줘",
                expected_outcome="계산기 관련 코드가 구현됨",
                success_criteria={
                    "status": "completed",
                    "min_quality_score": 5.0,
                    "min_files_generated": 1,
                    "max_errors": 3
                }
            ),

            # 3. 복잡한 프로젝트 요청
            SimulationScenario(
                name="complex_project",
                description="여러 파일이 필요한 복잡한 프로젝트 테스트",
                user_request="간단한 웹 API를 만들어줘. 사용자 관리 기능이 필요해",
                expected_outcome="여러 파일로 구성된 웹 API 프로젝트",
                success_criteria={
                    "min_quality_score": 4.0,
                    "min_files_generated": 2,
                    "max_errors": 5
                }
            ),

            # 4. 의도적 실패 시나리오
            SimulationScenario(
                name="intentional_failure",
                description="재시도 메커니즘 테스트를 위한 의도적 어려운 요청",
                user_request="불가능한 요청: 우주선을 만들어줘",
                expected_outcome="적절한 재시도 후 에스컬레이션",
                success_criteria={
                    "max_errors": 10  # 더 관대한 기준
                }
            ),

            # 5. 버그 수정 시뮬레이션
            SimulationScenario(
                name="bug_fix_simulation",
                description="기존 코드의 버그 수정 테스트",
                user_request="broken.py 파일의 오류를 수정해줘",
                expected_outcome="버그가 수정된 코드",
                success_criteria={
                    "min_quality_score": 5.0,
                    "max_errors": 3
                },
                setup_files={
                    "broken.py": '''def add(a, b):
    return a +  # 의도적 구문 오류

def multiply(a, b):
    return a * b

print("Hello, World!")'''
                }
            ),

            # 6. 테스트 작성 요청
            SimulationScenario(
                name="test_creation",
                description="테스트 코드 작성 요청 테스트",
                user_request="math_utils.py에 대한 테스트를 작성해줘",
                expected_outcome="테스트 파일이 생성됨",
                success_criteria={
                    "min_quality_score": 6.0,
                    "min_files_generated": 1
                },
                setup_files={
                    "math_utils.py": '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b'''
                }
            ),

            # 7. 리팩토링 요청
            SimulationScenario(
                name="refactoring_request",
                description="코드 리팩토링 요청 테스트",
                user_request="legacy_code.py를 더 깔끔하게 리팩토링해줘",
                expected_outcome="리팩토링된 코드",
                success_criteria={
                    "min_quality_score": 5.0,
                    "max_errors": 3
                },
                setup_files={
                    "legacy_code.py": '''# 레거시 코드
def processData(data):
    result = []
    for i in range(len(data)):
        if data[i] is not None:
            if isinstance(data[i], str):
                result.append(data[i].upper())
            elif isinstance(data[i], (int, float)):
                result.append(data[i] * 2)
    return result

def calculateTotal(numbers):
    total = 0
    for num in numbers:
        total += num
    return total'''
                }
            )
        ]

    def list_scenarios(self) -> List[str]:
        """사용 가능한 시나리오 목록 반환"""
        return [scenario.name for scenario in self.scenarios]

    def get_scenario_info(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """시나리오 정보 조회"""
        scenario = self._find_scenario(scenario_name)
        if not scenario:
            return None

        return {
            "name": scenario.name,
            "description": scenario.description,
            "user_request": scenario.user_request,
            "expected_outcome": scenario.expected_outcome,
            "success_criteria": scenario.success_criteria
        }