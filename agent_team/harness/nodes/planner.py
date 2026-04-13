"""
Planner Node - 요구사항 분석 및 계획 수립

사용자 요청을 분석하여 구체적이고 실행 가능한 Todo List로 분해합니다.
"""

from typing import Dict, List, Any
import json
import re

from ..state import AgentState
from .base import BaseNode


class PlannerNode(BaseNode):
    """
    범용 요구사항 분석기

    사용자의 자연어 요청을 분석하여 구체적인 개발 작업 목록으로 변환합니다.
    도메인에 관계없이 모든 종류의 개발 요청을 처리할 수 있습니다.
    """

    def execute(self, state: AgentState) -> AgentState:
        """
        계획 수립 실행

        Args:
            state: 현재 상태

        Returns:
            Todo List가 포함된 업데이트된 상태
        """
        # 상태 업데이트
        state = self._update_state_metadata(state, "planner")
        state["status"] = "planning"

        try:
            # 프로젝트 컨텍스트 수집
            project_context = self._get_project_context()

            # 사용자 요청 분석 및 Todo List 생성
            todo_list = self._analyze_request_and_create_todos(
                state["user_request"],
                project_context,
                state["error_history"]
            )

            # 상태에 Todo List 저장
            state["todo_list"] = todo_list
            state["current_task_index"] = 0

            # 성공 로깅
            self._add_lesson_learned(
                state,
                f"요청 '{state['user_request'][:50]}...'을 {len(todo_list)}개의 작업으로 분해 완료"
            )

        except Exception as e:
            # 에러 처리
            state = self._add_error_to_history(state, e, "계획 수립 중 오류 발생")
            state["status"] = "planning_failed"

            # 간단한 폴백 계획 생성
            state["todo_list"] = self._create_fallback_plan(state["user_request"])

        return state

    def _analyze_request_and_create_todos(
        self,
        user_request: str,
        project_context: Dict[str, Any],
        error_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        사용자 요청을 분석하여 Todo List 생성

        Args:
            user_request: 사용자 요청
            project_context: 프로젝트 컨텍스트
            error_history: 이전 에러 히스토리

        Returns:
            Todo 아이템 리스트
        """
        # 요청 타입 분류
        request_type = self._classify_request_type(user_request)

        # 프로젝트 언어 및 프레임워크 감지
        tech_stack = self._analyze_tech_stack(project_context)

        # 복잡도 분석
        complexity = self._analyze_complexity(user_request)

        # Todo List 생성
        if request_type == "file_creation":
            todos = self._create_file_creation_todos(user_request, tech_stack, complexity)
        elif request_type == "feature_implementation":
            todos = self._create_feature_implementation_todos(user_request, tech_stack, complexity)
        elif request_type == "bug_fix":
            todos = self._create_bug_fix_todos(user_request, tech_stack, error_history)
        elif request_type == "refactoring":
            todos = self._create_refactoring_todos(user_request, tech_stack, complexity)
        elif request_type == "testing":
            todos = self._create_testing_todos(user_request, tech_stack)
        else:
            # 범용 작업 분해
            todos = self._create_generic_todos(user_request, tech_stack, complexity)

        # 각 Todo에 메타데이터 추가
        for i, todo in enumerate(todos):
            todo["index"] = i
            todo["estimated_complexity"] = self._estimate_todo_complexity(todo["description"])
            todo["dependencies"] = self._identify_dependencies(todo, todos[:i])

        return todos

    def _classify_request_type(self, user_request: str) -> str:
        """요청 타입 분류"""
        request_lower = user_request.lower()

        if any(keyword in request_lower for keyword in ["파일", "생성", "만들", "추가해", "create", "add"]):
            return "file_creation"

        if any(keyword in request_lower for keyword in ["기능", "구현", "개발", "feature", "implement"]):
            return "feature_implementation"

        if any(keyword in request_lower for keyword in ["버그", "오류", "수정", "고치", "bug", "fix", "error"]):
            return "bug_fix"

        if any(keyword in request_lower for keyword in ["리팩토링", "정리", "개선", "refactor", "clean", "improve"]):
            return "refactoring"

        if any(keyword in request_lower for keyword in ["테스트", "검증", "test", "verify"]):
            return "testing"

        return "generic"

    def _analyze_tech_stack(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """기술 스택 분석"""
        languages = project_context.get("language_info", [])
        files = project_context.get("files_structure", {}).get("sample_files", [])

        tech_stack = {
            "primary_language": None,
            "frameworks": [],
            "tools": [],
            "file_patterns": {}
        }

        # 주요 언어 결정
        if "python" in languages:
            tech_stack["primary_language"] = "python"
            tech_stack["frameworks"] = self._detect_python_frameworks(files)
        elif "javascript" in languages:
            tech_stack["primary_language"] = "javascript"
            tech_stack["frameworks"] = self._detect_js_frameworks(files)
        elif "java" in languages:
            tech_stack["primary_language"] = "java"
        elif "go" in languages:
            tech_stack["primary_language"] = "go"
        else:
            # 파일 확장자로 추정
            extensions = project_context.get("files_structure", {}).get("extensions", {})
            if extensions:
                most_common_ext = max(extensions.items(), key=lambda x: x[1])[0]
                tech_stack["primary_language"] = self._ext_to_language(most_common_ext)

        return tech_stack

    def _detect_python_frameworks(self, files: List[str]) -> List[str]:
        """Python 프레임워크 감지"""
        frameworks = []

        file_names = " ".join(files).lower()

        if "django" in file_names or "manage.py" in file_names:
            frameworks.append("django")
        if "flask" in file_names or "app.py" in file_names:
            frameworks.append("flask")
        if "fastapi" in file_names:
            frameworks.append("fastapi")
        if "streamlit" in file_names:
            frameworks.append("streamlit")

        return frameworks

    def _detect_js_frameworks(self, files: List[str]) -> List[str]:
        """JavaScript 프레임워크 감지"""
        frameworks = []

        file_names = " ".join(files).lower()

        if "react" in file_names or ".jsx" in file_names:
            frameworks.append("react")
        if "vue" in file_names or ".vue" in file_names:
            frameworks.append("vue")
        if "angular" in file_names:
            frameworks.append("angular")
        if "next" in file_names:
            frameworks.append("nextjs")

        return frameworks

    def _ext_to_language(self, extension: str) -> str:
        """파일 확장자로 언어 추정"""
        ext_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "java": "java",
            "go": "go",
            "rs": "rust",
            "cpp": "cpp",
            "c": "c",
            "cs": "csharp",
            "php": "php",
            "rb": "ruby"
        }
        return ext_map.get(extension, "unknown")

    def _analyze_complexity(self, user_request: str) -> str:
        """요청 복잡도 분석"""
        request_lower = user_request.lower()
        word_count = len(user_request.split())

        # 복잡도 지표
        complex_indicators = [
            "api", "데이터베이스", "database", "인증", "auth", "배포", "deploy",
            "테스트", "test", "보안", "security", "성능", "performance",
            "통합", "integration", "실시간", "real-time", "알고리즘", "algorithm"
        ]

        simple_indicators = [
            "파일", "file", "함수", "function", "변수", "variable",
            "출력", "print", "로그", "log", "간단", "simple"
        ]

        complex_count = sum(1 for indicator in complex_indicators if indicator in request_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in request_lower)

        if complex_count >= 2 or word_count > 50:
            return "high"
        elif complex_count >= 1 or word_count > 20:
            return "medium"
        elif simple_count >= 1 or word_count <= 10:
            return "low"
        else:
            return "medium"

    def _create_file_creation_todos(self, user_request: str, tech_stack: Dict[str, Any], complexity: str) -> List[Dict[str, Any]]:
        """파일 생성 작업 Todo 생성"""
        todos = []

        # 파일명 추출 시도 (더 넓은 패턴)
        file_patterns = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z]+)', user_request)

        if file_patterns:
            for file_path in file_patterns:
                todos.append({
                    "type": "file_creation",
                    "title": f"{file_path} 파일 생성",
                    "description": f"사용자 요청에 따라 {file_path} 파일을 생성합니다.",
                    "file_path": file_path,
                    "priority": "high"
                })
        else:
            # 언어별 기본 파일 구조 생성
            language = tech_stack.get("primary_language", "python")
            if language == "python":
                todos.extend(self._create_python_file_todos(user_request))
            elif language == "javascript":
                todos.extend(self._create_js_file_todos(user_request))
            else:
                todos.append({
                    "type": "file_creation",
                    "title": "새 파일 생성",
                    "description": user_request,
                    "file_path": f"new_file.{self._get_default_extension(language)}",
                    "priority": "medium"
                })

        # 검증 작업 추가
        todos.append({
            "type": "verification",
            "title": "생성된 파일 검증",
            "description": "파일이 올바르게 생성되고 기본 구조가 유효한지 확인합니다.",
            "priority": "medium"
        })

        return todos

    def _create_feature_implementation_todos(self, user_request: str, tech_stack: Dict[str, Any], complexity: str) -> List[Dict[str, Any]]:
        """기능 구현 작업 Todo 생성"""
        todos = []

        # 복잡도에 따른 작업 분해
        if complexity == "high":
            todos.extend([
                {
                    "type": "analysis",
                    "title": "요구사항 분석",
                    "description": "기능 요구사항을 상세히 분석하고 설계 방향을 결정합니다.",
                    "priority": "high"
                },
                {
                    "type": "design",
                    "title": "아키텍처 설계",
                    "description": "기능의 아키텍처와 인터페이스를 설계합니다.",
                    "priority": "high"
                },
                {
                    "type": "implementation",
                    "title": "핵심 로직 구현",
                    "description": "기능의 핵심 비즈니스 로직을 구현합니다.",
                    "priority": "high"
                },
                {
                    "type": "integration",
                    "title": "기존 시스템 통합",
                    "description": "구현된 기능을 기존 시스템과 통합합니다.",
                    "priority": "medium"
                },
                {
                    "type": "testing",
                    "title": "기능 테스트",
                    "description": "구현된 기능의 동작을 테스트합니다.",
                    "priority": "medium"
                }
            ])
        else:
            todos.extend([
                {
                    "type": "implementation",
                    "title": "기능 구현",
                    "description": user_request,
                    "priority": "high"
                },
                {
                    "type": "testing",
                    "title": "기능 테스트",
                    "description": "구현된 기능이 올바르게 동작하는지 테스트합니다.",
                    "priority": "medium"
                }
            ])

        return todos

    def _create_bug_fix_todos(self, user_request: str, tech_stack: Dict[str, Any], error_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """버그 수정 작업 Todo 생성"""
        todos = [
            {
                "type": "investigation",
                "title": "버그 원인 조사",
                "description": "버그의 근본 원인을 파악하고 영향 범위를 분석합니다.",
                "priority": "high"
            },
            {
                "type": "reproduction",
                "title": "버그 재현",
                "description": "버그를 일관되게 재현할 수 있는 방법을 찾습니다.",
                "priority": "high"
            },
            {
                "type": "fix_implementation",
                "title": "버그 수정 구현",
                "description": user_request,
                "priority": "high"
            },
            {
                "type": "regression_testing",
                "title": "회귀 테스트",
                "description": "수정사항이 다른 부분에 영향을 주지 않는지 확인합니다.",
                "priority": "medium"
            }
        ]

        # 이전 에러 히스토리 활용
        if error_history:
            todos.insert(0, {
                "type": "error_analysis",
                "title": "이전 에러 히스토리 분석",
                "description": "이전에 발생한 유사한 오류들을 분석하여 패턴을 파악합니다.",
                "priority": "medium"
            })

        return todos

    def _create_refactoring_todos(self, user_request: str, tech_stack: Dict[str, Any], complexity: str) -> List[Dict[str, Any]]:
        """리팩토링 작업 Todo 생성"""
        return [
            {
                "type": "code_analysis",
                "title": "코드 분석",
                "description": "리팩토링 대상 코드를 분석하고 개선점을 파악합니다.",
                "priority": "high"
            },
            {
                "type": "backup",
                "title": "백업 생성",
                "description": "기존 코드의 백업을 생성합니다.",
                "priority": "high"
            },
            {
                "type": "refactoring",
                "title": "코드 리팩토링",
                "description": user_request,
                "priority": "high"
            },
            {
                "type": "testing",
                "title": "리팩토링 검증",
                "description": "리팩토링된 코드가 기존과 동일하게 동작하는지 확인합니다.",
                "priority": "medium"
            }
        ]

    def _create_testing_todos(self, user_request: str, tech_stack: Dict[str, Any]) -> List[Dict[str, Any]]:
        """테스트 작업 Todo 생성"""
        language = tech_stack.get("primary_language", "python")

        todos = [
            {
                "type": "test_planning",
                "title": "테스트 계획 수립",
                "description": "테스트 범위와 방법을 계획합니다.",
                "priority": "high"
            }
        ]

        # 언어별 테스트 프레임워크
        if language == "python":
            todos.append({
                "type": "test_implementation",
                "title": "Python 테스트 구현",
                "description": "pytest를 사용하여 테스트를 구현합니다.",
                "priority": "high"
            })
        elif language == "javascript":
            todos.append({
                "type": "test_implementation",
                "title": "JavaScript 테스트 구현",
                "description": "Jest 또는 다른 테스트 프레임워크를 사용하여 테스트를 구현합니다.",
                "priority": "high"
            })
        else:
            todos.append({
                "type": "test_implementation",
                "title": "테스트 구현",
                "description": user_request,
                "priority": "high"
            })

        todos.append({
            "type": "test_execution",
            "title": "테스트 실행",
            "description": "작성된 테스트를 실행하고 결과를 확인합니다.",
            "priority": "medium"
        })

        return todos

    def _create_generic_todos(self, user_request: str, tech_stack: Dict[str, Any], complexity: str) -> List[Dict[str, Any]]:
        """범용 작업 Todo 생성"""
        # 요청을 단계별로 분해
        sentences = [s.strip() for s in user_request.split('.') if s.strip()]

        if len(sentences) <= 1:
            # 단일 작업
            return [{
                "type": "implementation",
                "title": "작업 수행",
                "description": user_request,
                "priority": "high"
            }]

        # 복수 작업으로 분해
        todos = []
        for i, sentence in enumerate(sentences):
            priority = "high" if i < 2 else "medium"
            todos.append({
                "type": "implementation",
                "title": f"작업 {i+1}: {sentence[:30]}...",
                "description": sentence,
                "priority": priority
            })

        return todos

    def _create_python_file_todos(self, user_request: str) -> List[Dict[str, Any]]:
        """Python 파일 생성 Todo"""
        return [{
            "type": "file_creation",
            "title": "Python 파일 생성",
            "description": f"Python 파일을 생성합니다: {user_request}",
            "file_path": "new_module.py",
            "priority": "high"
        }]

    def _create_js_file_todos(self, user_request: str) -> List[Dict[str, Any]]:
        """JavaScript 파일 생성 Todo"""
        return [{
            "type": "file_creation",
            "title": "JavaScript 파일 생성",
            "description": f"JavaScript 파일을 생성합니다: {user_request}",
            "file_path": "new_module.js",
            "priority": "high"
        }]

    def _get_default_extension(self, language: str) -> str:
        """언어별 기본 확장자"""
        ext_map = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "cpp": "cpp",
            "c": "c",
            "csharp": "cs"
        }
        return ext_map.get(language, "txt")

    def _estimate_todo_complexity(self, description: str) -> str:
        """개별 Todo 복잡도 추정"""
        if len(description) > 100:
            return "high"
        elif len(description) > 50:
            return "medium"
        else:
            return "low"

    def _identify_dependencies(self, current_todo: Dict[str, Any], previous_todos: List[Dict[str, Any]]) -> List[int]:
        """작업 간 의존성 식별"""
        dependencies = []

        # 타입 기반 의존성
        current_type = current_todo.get("type")

        for i, prev_todo in enumerate(previous_todos):
            prev_type = prev_todo.get("type")

            # 구현 -> 테스트 의존성
            if current_type == "testing" and prev_type in ["implementation", "feature_implementation"]:
                dependencies.append(i)

            # 분석 -> 구현 의존성
            if current_type == "implementation" and prev_type in ["analysis", "design"]:
                dependencies.append(i)

            # 통합 -> 구현 의존성
            if current_type == "integration" and prev_type == "implementation":
                dependencies.append(i)

        return dependencies

    def _create_fallback_plan(self, user_request: str) -> List[Dict[str, Any]]:
        """실패 시 폴백 계획 생성"""
        return [{
            "type": "manual_task",
            "title": "수동 작업 필요",
            "description": f"자동 분석에 실패했습니다. 수동으로 처리해주세요: {user_request}",
            "priority": "high"
        }]