"""
Validator Node - 코드 품질 검증 및 테스트

생성된 코드의 품질을 검증하고 테스트를 실행하여 품질 점수를 산출합니다.
기존 harness_linter.py를 통합하여 포괄적인 검증을 수행합니다.
"""

from typing import Dict, List, Any, Optional
import os
import sys
import subprocess
import importlib.util
from datetime import datetime

from ..state import AgentState
from .base import BaseNode


class ValidatorNode(BaseNode):
    """
    범용 코드 검증기

    생성된 코드에 대해 다양한 품질 검증을 수행합니다:
    - 구문 검증 (문법 오류)
    - 정적 분석 (코딩 스타일, 복잡도)
    - 기존 harness_linter 통합
    - 테스트 실행
    - 보안 검사
    """

    def __init__(self, config: Dict[str, Any]):
        """Validator 초기화"""
        super().__init__(config)
        self.harness_linter = self._load_harness_linter()

    def execute(self, state: AgentState) -> AgentState:
        """
        검증 작업 실행

        Args:
            state: 현재 상태

        Returns:
            검증 결과가 포함된 업데이트된 상태
        """
        # 상태 업데이트
        state = self._update_state_metadata(state, "validator")
        state["status"] = "validating"

        try:
            # 검증할 파일들 수집
            files_to_validate = self._collect_files_to_validate(state)

            if not files_to_validate:
                # 검증할 파일이 없으면 성공으로 처리
                state["validation_results"] = {"status": "no_files", "score": 10.0}
                state["quality_score"] = 10.0
                return state

            # 종합 검증 실행
            validation_results = self._perform_comprehensive_validation(files_to_validate, state)

            # 결과 저장
            state["validation_results"] = validation_results
            state["quality_score"] = validation_results.get("overall_score", 0.0)

            # 검증 완료 로그
            self._add_lesson_learned(
                state,
                f"코드 검증 완료: 품질 점수 {state['quality_score']:.1f}/10.0"
            )

        except Exception as e:
            # 검증 실패
            state = self._add_error_to_history(state, e, "코드 검증 중 오류 발생")
            state["validation_results"] = {
                "status": "validation_error",
                "error": str(e),
                "overall_score": 0.0
            }
            state["quality_score"] = 0.0

        return state

    def _load_harness_linter(self):
        """기존 harness_linter.py 로드"""
        try:
            # harness_linter.py 경로
            linter_path = os.path.join(
                os.getcwd(), "app", "src", "memo_summarizer", "cli", "harness_linter.py"
            )

            if not os.path.exists(linter_path):
                print(f"⚠️ harness_linter.py를 찾을 수 없습니다: {linter_path}")
                return None

            # 모듈 동적 로드
            spec = importlib.util.spec_from_file_location("harness_linter", linter_path)
            harness_linter_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(harness_linter_module)

            return harness_linter_module.HarnessLinter

        except Exception as e:
            print(f"⚠️ harness_linter 로드 실패: {e}")
            return None

    def _collect_files_to_validate(self, state: AgentState) -> List[str]:
        """검증할 파일들 수집"""
        files_to_validate = []

        # 생성된 파일들
        for file_info in state.get("generated_files", []):
            file_path = file_info.get("path")
            if file_path and os.path.exists(file_path):
                files_to_validate.append(file_path)

        # 추가로 최근 수정된 파일들도 포함
        recent_files = self._find_recently_modified_files()
        files_to_validate.extend(recent_files)

        # 중복 제거
        return list(set(files_to_validate))

    def _find_recently_modified_files(self, hours: int = 1) -> List[str]:
        """최근 수정된 파일들 찾기"""
        try:
            import time
            cutoff_time = time.time() - (hours * 3600)

            recent_files = []
            for root, dirs, files in os.walk("."):
                # 제외할 디렉토리 건너뛰기
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'node_modules', '__pycache__']]

                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) > cutoff_time:
                        # 검증 가능한 파일만 포함
                        if self._is_validatable_file(file_path):
                            recent_files.append(file_path)

            return recent_files[:10]  # 최대 10개까지

        except Exception as e:
            print(f"최근 파일 찾기 실패: {e}")
            return []

    def _is_validatable_file(self, file_path: str) -> bool:
        """검증 가능한 파일인지 확인"""
        validatable_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.md']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in validatable_extensions

    def _perform_comprehensive_validation(self, files: List[str], state: AgentState) -> Dict[str, Any]:
        """종합적인 검증 수행"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "files_checked": len(files),
            "checks_performed": [],
            "scores": {},
            "issues_found": [],
            "overall_score": 0.0
        }

        total_score = 0.0
        check_count = 0

        # 1. 구문 검증
        syntax_score = self._validate_syntax(files, results)
        total_score += syntax_score
        check_count += 1

        # 2. Harness Linter 검증
        if self.harness_linter:
            linter_score = self._run_harness_linter(results)
            total_score += linter_score
            check_count += 1

        # 3. 코드 스타일 검증
        style_score = self._validate_code_style(files, results)
        total_score += style_score
        check_count += 1

        # 4. 테스트 실행
        test_score = self._run_tests(results)
        total_score += test_score
        check_count += 1

        # 5. 보안 검사
        security_score = self._security_check(files, results)
        total_score += security_score
        check_count += 1

        # 전체 점수 계산
        if check_count > 0:
            results["overall_score"] = total_score / check_count
        else:
            results["overall_score"] = 0.0

        return results

    def _validate_syntax(self, files: List[str], results: Dict[str, Any]) -> float:
        """구문 검증"""
        results["checks_performed"].append("syntax_validation")

        syntax_errors = []
        total_files = 0
        valid_files = 0

        for file_path in files:
            if not file_path.endswith(('.py', '.js', '.java')):
                continue

            total_files += 1

            try:
                if file_path.endswith('.py'):
                    # Python 구문 검사
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", file_path],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        valid_files += 1
                    else:
                        syntax_errors.append(f"{file_path}: {result.stderr.strip()}")

                elif file_path.endswith('.js'):
                    # JavaScript 구문 검사 (node 사용)
                    result = subprocess.run(
                        ["node", "--check", file_path],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        valid_files += 1
                    else:
                        syntax_errors.append(f"{file_path}: {result.stderr.strip()}")

            except Exception as e:
                syntax_errors.append(f"{file_path}: 검사 실패 - {e}")

        # 점수 계산
        if total_files == 0:
            score = 10.0
        else:
            score = (valid_files / total_files) * 10.0

        results["scores"]["syntax"] = score
        if syntax_errors:
            results["issues_found"].extend(syntax_errors)

        return score

    def _run_harness_linter(self, results: Dict[str, Any]) -> float:
        """Harness Linter 실행"""
        results["checks_performed"].append("harness_linter")

        try:
            if not self.harness_linter:
                results["scores"]["harness_linter"] = 8.0  # 기본 점수
                return 8.0

            linter = self.harness_linter()
            success = linter.run_all_checks()

            # 점수 계산 (위반사항과 경고사항 기반)
            violations = len(linter.violations)
            warnings = len(linter.warnings)

            if violations == 0 and warnings == 0:
                score = 10.0
            elif violations == 0:
                score = max(7.0, 10.0 - warnings * 0.5)
            else:
                score = max(0.0, 10.0 - violations * 2.0 - warnings * 0.5)

            results["scores"]["harness_linter"] = score

            # 이슈 기록
            for violation in linter.violations:
                results["issues_found"].append(f"VIOLATION: {violation['message']} ({violation['file']})")

            for warning in linter.warnings[:5]:  # 최대 5개 경고만
                results["issues_found"].append(f"WARNING: {warning['message']} ({warning['file']})")

            return score

        except Exception as e:
            results["issues_found"].append(f"Harness Linter 실행 실패: {e}")
            results["scores"]["harness_linter"] = 5.0
            return 5.0

    def _validate_code_style(self, files: List[str], results: Dict[str, Any]) -> float:
        """코드 스타일 검증"""
        results["checks_performed"].append("code_style")

        style_issues = []
        total_checks = 0
        passed_checks = 0

        for file_path in files:
            if not file_path.endswith('.py'):
                continue

            try:
                content = self._read_file_safe(file_path)
                if not content:
                    continue

                # 기본적인 스타일 검사
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    total_checks += 1

                    # 라인 길이 검사 (120자 제한)
                    if len(line) > 120:
                        style_issues.append(f"{file_path}:{i} - 라인이 너무 깁니다 ({len(line)} > 120)")
                    else:
                        passed_checks += 1

            except Exception as e:
                style_issues.append(f"{file_path}: 스타일 검사 실패 - {e}")

        # 점수 계산
        if total_checks == 0:
            score = 8.0
        else:
            score = (passed_checks / total_checks) * 10.0

        results["scores"]["code_style"] = score
        if style_issues:
            results["issues_found"].extend(style_issues[:10])  # 최대 10개

        return score

    def _run_tests(self, results: Dict[str, Any]) -> float:
        """테스트 실행"""
        results["checks_performed"].append("test_execution")

        # pytest 실행 시도
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--tb=short", "-v"],
                capture_output=True,
                text=True,
                timeout=60  # 60초 제한
            )

            if result.returncode == 0:
                score = 10.0
                results["issues_found"].append("모든 테스트 통과")
            else:
                # 테스트 실패가 있지만 일부는 통과할 수 있음
                if "failed" in result.stdout.lower():
                    score = 5.0
                    results["issues_found"].append(f"테스트 실패: {result.stdout[:200]}...")
                else:
                    score = 8.0
                    results["issues_found"].append("테스트 실행됨 (일부 문제 있음)")

        except subprocess.TimeoutExpired:
            score = 3.0
            results["issues_found"].append("테스트 실행 시간 초과")

        except FileNotFoundError:
            # pytest가 없거나 테스트 파일이 없음
            score = 7.0
            results["issues_found"].append("테스트 환경 없음 (기본 점수)")

        except Exception as e:
            score = 4.0
            results["issues_found"].append(f"테스트 실행 실패: {e}")

        results["scores"]["tests"] = score
        return score

    def _security_check(self, files: List[str], results: Dict[str, Any]) -> float:
        """기본적인 보안 검사"""
        results["checks_performed"].append("security_check")

        security_issues = []
        total_files = len(files)
        secure_files = 0

        # 간단한 보안 패턴 검사
        dangerous_patterns = [
            (r'eval\s*\(', "eval() 사용 감지"),
            (r'exec\s*\(', "exec() 사용 감지"),
            (r'shell=True', "shell=True 사용 감지"),
            (r'pickle\.loads?', "pickle 역직렬화 감지"),
            (r'input\s*\([^)]*\)\s*', "input() 사용 감지 (가능한 보안 위험)"),
        ]

        for file_path in files:
            if not file_path.endswith(('.py', '.js')):
                secure_files += 1
                continue

            try:
                content = self._read_file_safe(file_path)
                if not content:
                    secure_files += 1
                    continue

                file_issues = []
                for pattern, description in dangerous_patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        file_issues.append(f"{file_path}: {description}")

                if not file_issues:
                    secure_files += 1
                else:
                    security_issues.extend(file_issues)

            except Exception as e:
                security_issues.append(f"{file_path}: 보안 검사 실패 - {e}")

        # 점수 계산
        if total_files == 0:
            score = 9.0
        else:
            score = (secure_files / total_files) * 10.0

        results["scores"]["security"] = score
        if security_issues:
            results["issues_found"].extend(security_issues)

        return score