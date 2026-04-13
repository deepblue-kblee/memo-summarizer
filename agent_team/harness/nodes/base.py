"""
에이전트 노드 베이스 클래스

모든 노드가 상속받는 공통 기능을 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import subprocess
import json

from ..state import AgentState


class BaseNode(ABC):
    """
    모든 에이전트 노드의 베이스 클래스

    공통 기능:
    - AI 클라이언트 연동
    - 에러 처리 및 로깅
    - 상태 업데이트 유틸리티
    - 파일 시스템 작업
    """

    def __init__(self, config: Dict[str, Any]):
        """
        베이스 노드 초기화

        Args:
            config: 노드 설정 딕셔너리
        """
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        self.ai_client = self._init_ai_client()

    def _init_ai_client(self):
        """AI 클라이언트 초기화"""
        # TODO: 실제 AI 클라이언트 초기화
        # anthropic.Client() 또는 다른 AI 클라이언트
        return None

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """
        노드 실행 (추상 메서드)

        Args:
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        pass

    def _update_state_metadata(self, state: AgentState, node_name: str) -> AgentState:
        """
        상태 메타데이터 업데이트

        Args:
            state: 현재 상태
            node_name: 노드 이름

        Returns:
            메타데이터가 업데이트된 상태
        """
        state["current_node"] = node_name
        state["updated_at"] = datetime.now().isoformat()
        return state

    def _add_error_to_history(self, state: AgentState, error: Exception, context: str = "") -> AgentState:
        """
        에러를 히스토리에 추가

        Args:
            state: 현재 상태
            error: 발생한 에러
            context: 에러 컨텍스트

        Returns:
            에러가 추가된 상태
        """
        error_entry = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "node": state.get("current_node", "unknown")
        }

        state["error_history"].append(error_entry)
        return state

    def _add_lesson_learned(self, state: AgentState, lesson: str) -> AgentState:
        """
        학습 내용을 추가

        Args:
            state: 현재 상태
            lesson: 학습된 내용

        Returns:
            학습 내용이 추가된 상태
        """
        if lesson not in state["lessons_learned"]:
            state["lessons_learned"].append(lesson)

        # 최대 20개까지만 유지 (메모리 절약)
        if len(state["lessons_learned"]) > 20:
            state["lessons_learned"] = state["lessons_learned"][-20:]

        return state

    def _get_project_context(self) -> Dict[str, Any]:
        """
        현재 프로젝트의 컨텍스트 정보 수집

        Returns:
            프로젝트 컨텍스트 딕셔너리
        """
        context = {
            "working_directory": os.getcwd(),
            "files_structure": self._get_files_structure(),
            "git_info": self._get_git_info(),
            "language_info": self._detect_project_languages()
        }

        return context

    def _get_files_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        프로젝트 파일 구조 분석

        Args:
            max_depth: 최대 탐색 깊이

        Returns:
            파일 구조 정보
        """
        try:
            result = subprocess.run(
                ["find", ".", "-type", "f", "-not", "-path", "*/.*", "-not", "-path", "*/venv/*", "-not", "-path", "*/node_modules/*"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")[:100]  # 최대 100개 파일
                return {
                    "total_files": len(files),
                    "sample_files": files[:20],  # 샘플 20개
                    "extensions": self._analyze_file_extensions(files)
                }
        except Exception:
            pass

        return {"total_files": 0, "sample_files": [], "extensions": {}}

    def _analyze_file_extensions(self, files: List[str]) -> Dict[str, int]:
        """파일 확장자 분석"""
        extensions = {}
        for file in files:
            if "." in file:
                ext = file.split(".")[-1]
                extensions[ext] = extensions.get(ext, 0) + 1
        return extensions

    def _get_git_info(self) -> Dict[str, Any]:
        """Git 정보 수집"""
        git_info = {}

        try:
            # 현재 브랜치
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_info["current_branch"] = result.stdout.strip()

            # 최근 커밋
            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_info["last_commit"] = result.stdout.strip()

        except Exception:
            pass

        return git_info

    def _detect_project_languages(self) -> List[str]:
        """프로젝트에서 사용되는 프로그래밍 언어 감지"""
        languages = []

        # 파일 존재 확인으로 언어 감지
        language_files = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml"],
            "javascript": ["package.json", "yarn.lock"],
            "java": ["pom.xml", "build.gradle"],
            "go": ["go.mod", "go.sum"],
            "rust": ["Cargo.toml"],
            "ruby": ["Gemfile"],
            "php": ["composer.json"],
            "csharp": ["*.csproj", "*.sln"]
        }

        for lang, files in language_files.items():
            for file_pattern in files:
                if "*" in file_pattern:
                    # 와일드카드 패턴
                    try:
                        result = subprocess.run(
                            ["find", ".", "-name", file_pattern, "-type", "f"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            languages.append(lang)
                            break
                    except Exception:
                        pass
                else:
                    # 정확한 파일명
                    if os.path.exists(file_pattern):
                        languages.append(lang)
                        break

        return languages

    def _execute_shell_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        셸 명령어 실행

        Args:
            command: 실행할 명령어 리스트
            timeout: 타임아웃 (초)

        Returns:
            실행 결과 딕셔너리
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "success": False
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }

    def _read_file_safe(self, file_path: str, max_size: int = 1024 * 1024) -> Optional[str]:
        """
        안전한 파일 읽기

        Args:
            file_path: 읽을 파일 경로
            max_size: 최대 파일 크기 (바이트)

        Returns:
            파일 내용 또는 None (실패 시)
        """
        try:
            if not os.path.exists(file_path):
                return None

            if os.path.getsize(file_path) > max_size:
                return f"[파일이 너무 큽니다: {os.path.getsize(file_path)} bytes]"

            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            return f"[파일 읽기 실패: {e}]"

    def _write_file_safe(self, file_path: str, content: str, backup: bool = True) -> bool:
        """
        안전한 파일 쓰기

        Args:
            file_path: 쓸 파일 경로
            content: 파일 내용
            backup: 기존 파일 백업 여부

        Returns:
            쓰기 성공 여부
        """
        try:
            # 파일 경로 유효성 검사
            if not file_path or file_path.strip() == "":
                print(f"파일 쓰기 실패: 빈 파일 경로")
                return False

            # 백업 생성
            if backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(file_path, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())

            # 디렉토리 생성 (파일명만 있는 경우 현재 디렉토리)
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)

            # 파일 쓰기
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        except Exception as e:
            print(f"파일 쓰기 실패: {e}")
            return False

    def _call_ai(self, prompt: str, system_prompt: str = None, max_tokens: int = 4000) -> Optional[str]:
        """
        AI 클라이언트 호출

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            max_tokens: 최대 토큰 수

        Returns:
            AI 응답 또는 None (실패 시)
        """
        try:
            # TODO: 실제 AI 클라이언트 호출 구현
            # 현재는 모의 응답 반환
            return f"[AI 응답 모의] 프롬프트: {prompt[:100]}..."

        except Exception as e:
            print(f"AI 호출 실패: {e}")
            return None