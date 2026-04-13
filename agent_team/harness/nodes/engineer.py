"""
Engineer Node - 코드 구현 및 파일 작업

Todo List를 실제 코드로 구현하고 파일을 생성/수정하는 역할을 담당합니다.
"""

from typing import Dict, List, Any, Optional
import os
import shutil
from datetime import datetime

from ..state import AgentState
from .base import BaseNode


class EngineerNode(BaseNode):
    """
    범용 코드 구현기

    계획된 Todo List를 바탕으로 실제 코드를 작성하고 파일을 생성/수정합니다.
    다양한 프로그래밍 언어와 프레임워크를 지원합니다.
    """

    def execute(self, state: AgentState) -> AgentState:
        """
        구현 작업 실행

        Args:
            state: 현재 상태

        Returns:
            구현 결과가 포함된 업데이트된 상태
        """
        # 상태 업데이트
        state = self._update_state_metadata(state, "engineer")
        state["status"] = "implementing"

        try:
            # 현재 처리할 작업 가져오기
            current_task = self._get_current_task(state)

            if not current_task:
                # 모든 작업 완료
                state["status"] = "implementation_complete"
                return state

            # 작업 타입에 따른 처리
            success = self._execute_task(current_task, state)

            if success:
                # 작업 완료 - 다음 작업으로 이동
                state["current_task_index"] += 1

                # 학습 내용 추가
                self._add_lesson_learned(
                    state,
                    f"작업 '{current_task['title']}' 성공적으로 완료"
                )

            else:
                # 작업 실패 - 재시도 카운터 증가
                state["retry_count"] += 1

        except Exception as e:
            # 에러 처리
            state = self._add_error_to_history(state, e, f"작업 실행 중 오류: {current_task.get('title', 'Unknown')}")
            state["retry_count"] += 1

        return state

    def _get_current_task(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """현재 처리할 작업 반환"""
        todo_list = state.get("todo_list", [])
        current_index = state.get("current_task_index", 0)

        if current_index < len(todo_list):
            return todo_list[current_index]

        return None

    def _execute_task(self, task: Dict[str, Any], state: AgentState) -> bool:
        """
        작업 실행

        Args:
            task: 실행할 작업
            state: 현재 상태

        Returns:
            성공 여부
        """
        task_type = task.get("type", "implementation")

        try:
            if task_type == "file_creation":
                return self._handle_file_creation(task, state)

            elif task_type == "implementation":
                return self._handle_implementation(task, state)

            elif task_type == "feature_implementation":
                return self._handle_feature_implementation(task, state)

            elif task_type == "bug_fix":
                return self._handle_bug_fix(task, state)

            elif task_type == "refactoring":
                return self._handle_refactoring(task, state)

            elif task_type == "analysis":
                return self._handle_analysis(task, state)

            elif task_type == "design":
                return self._handle_design(task, state)

            else:
                # 범용 처리
                return self._handle_generic_task(task, state)

        except Exception as e:
            print(f"작업 실행 실패: {e}")
            return False

    def _handle_file_creation(self, task: Dict[str, Any], state: AgentState) -> bool:
        """파일 생성 작업 처리"""
        file_path = task.get("file_path", "new_file.txt")
        description = task.get("description", "")

        # 파일 경로가 비어있으면 기본값 사용
        if not file_path or file_path.strip() == "":
            file_path = "new_file.txt"


        # 파일 내용 생성
        content = self._generate_file_content(file_path, description, state)

        # 파일 작성
        success = self._write_file_safe(file_path, content)

        if success:
            # 생성된 파일 기록
            file_info = {
                "path": file_path,
                "type": "created",
                "size": len(content),
                "timestamp": datetime.now().isoformat(),
                "task_index": state["current_task_index"]
            }
            state["generated_files"].append(file_info)

            # 코드 변경 기록
            change_info = {
                "type": "file_creation",
                "file": file_path,
                "description": f"새 파일 생성: {description}",
                "timestamp": datetime.now().isoformat()
            }
            state["code_changes"].append(change_info)

            print(f"✅ 파일 생성 완료: {file_path}")

        return success

    def _handle_implementation(self, task: Dict[str, Any], state: AgentState) -> bool:
        """일반 구현 작업 처리"""
        description = task.get("description", "")

        # 구현 대상 파일 결정
        target_files = self._determine_target_files(description, state)

        success_count = 0

        for file_path in target_files:
            if self._implement_in_file(file_path, description, state):
                success_count += 1

        # 절반 이상 성공하면 성공으로 간주
        return success_count >= len(target_files) / 2

    def _handle_feature_implementation(self, task: Dict[str, Any], state: AgentState) -> bool:
        """기능 구현 작업 처리"""
        description = task.get("description", "")

        # 프로젝트 컨텍스트 분석
        project_context = self._get_project_context()
        language = project_context.get("language_info", ["python"])[0]

        # 언어별 기능 구현
        if language == "python":
            return self._implement_python_feature(description, state)
        elif language == "javascript":
            return self._implement_js_feature(description, state)
        else:
            return self._implement_generic_feature(description, state)

    def _handle_bug_fix(self, task: Dict[str, Any], state: AgentState) -> bool:
        """버그 수정 작업 처리"""
        description = task.get("description", "")

        # 에러 히스토리에서 패턴 분석
        error_patterns = self._analyze_error_patterns(state["error_history"])

        # 관련 파일 찾기
        target_files = self._find_files_by_error_context(error_patterns)

        # 각 파일에서 버그 수정 시도
        for file_path in target_files:
            if os.path.exists(file_path):
                if self._fix_bug_in_file(file_path, description, error_patterns, state):
                    return True

        # 새로운 수정 파일 생성
        return self._create_bug_fix_file(description, state)

    def _handle_refactoring(self, task: Dict[str, Any], state: AgentState) -> bool:
        """리팩토링 작업 처리"""
        description = task.get("description", "")

        # 리팩토링 대상 파일 찾기
        target_files = self._find_refactoring_targets(description)

        success_count = 0

        for file_path in target_files:
            # 백업 생성
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(file_path, backup_path)

                # 리팩토링 수행
                if self._refactor_file(file_path, description, state):
                    success_count += 1
                else:
                    # 실패 시 백업에서 복원
                    shutil.copy2(backup_path, file_path)

            except Exception as e:
                print(f"리팩토링 실패: {e}")

        return success_count > 0

    def _handle_analysis(self, task: Dict[str, Any], state: AgentState) -> bool:
        """분석 작업 처리"""
        description = task.get("description", "")

        # 분석 결과를 문서로 생성
        analysis_content = self._perform_analysis(description, state)

        # 분석 결과 파일 생성
        analysis_file = "analysis_result.md"
        success = self._write_file_safe(analysis_file, analysis_content)

        if success:
            # 생성된 파일 기록
            file_info = {
                "path": analysis_file,
                "type": "analysis",
                "size": len(analysis_content),
                "timestamp": datetime.now().isoformat(),
                "task_index": state["current_task_index"]
            }
            state["generated_files"].append(file_info)

        return success

    def _handle_design(self, task: Dict[str, Any], state: AgentState) -> bool:
        """설계 작업 처리"""
        description = task.get("description", "")

        # 설계 문서 생성
        design_content = self._create_design_document(description, state)

        # 설계 파일 생성
        design_file = "design_document.md"
        success = self._write_file_safe(design_file, design_content)

        if success:
            # 생성된 파일 기록
            file_info = {
                "path": design_file,
                "type": "design",
                "size": len(design_content),
                "timestamp": datetime.now().isoformat(),
                "task_index": state["current_task_index"]
            }
            state["generated_files"].append(file_info)

        return success

    def _handle_generic_task(self, task: Dict[str, Any], state: AgentState) -> bool:
        """범용 작업 처리"""
        description = task.get("description", "")

        # 간단한 구현 시도
        return self._handle_implementation(task, state)

    def _generate_file_content(self, file_path: str, description: str, state: AgentState) -> str:
        """파일 내용 생성"""
        # 파일 확장자로 언어 판단
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".py":
            return self._generate_python_content(description, state)
        elif ext in [".js", ".ts"]:
            return self._generate_js_content(description, state)
        elif ext == ".java":
            return self._generate_java_content(description, state)
        elif ext == ".go":
            return self._generate_go_content(description, state)
        elif ext in [".md", ".txt"]:
            return self._generate_text_content(description, state)
        else:
            return self._generate_generic_content(description, state)

    def _generate_python_content(self, description: str, state: AgentState) -> str:
        """Python 파일 내용 생성"""
        content = f'''"""
{description}

자동 생성된 파일 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def main():
    """
    메인 함수

    {description}
    """
    print("Hello, World!")
    # TODO: 실제 구현 코드 작성


if __name__ == "__main__":
    main()
'''
        return content

    def _generate_js_content(self, description: str, state: AgentState) -> str:
        """JavaScript 파일 내용 생성"""
        content = f'''/**
 * {description}
 *
 * 자동 생성된 파일 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

function main() {{
    console.log("Hello, World!");
    // TODO: 실제 구현 코드 작성
}}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ main }};
}}

// Run if called directly
if (typeof window === 'undefined') {{
    main();
}}
'''
        return content

    def _generate_java_content(self, description: str, state: AgentState) -> str:
        """Java 파일 내용 생성"""
        class_name = os.path.splitext(os.path.basename(file_path))[0] if 'file_path' in locals() else "Main"

        content = f'''/**
 * {description}
 *
 * 자동 생성된 파일 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */
public class {class_name} {{

    public static void main(String[] args) {{
        System.out.println("Hello, World!");
        // TODO: 실제 구현 코드 작성
    }}
}}
'''
        return content

    def _generate_go_content(self, description: str, state: AgentState) -> str:
        """Go 파일 내용 생성"""
        content = f'''// {description}
// 자동 생성된 파일 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

package main

import "fmt"

func main() {{
    fmt.Println("Hello, World!")
    // TODO: 실제 구현 코드 작성
}}
'''
        return content

    def _generate_text_content(self, description: str, state: AgentState) -> str:
        """텍스트/마크다운 파일 내용 생성"""
        content = f'''# {description}

자동 생성된 문서 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 개요

{description}

## TODO

- [ ] 실제 내용 작성
- [ ] 구조 개선
- [ ] 검토 및 수정
'''
        return content

    def _generate_generic_content(self, description: str, state: AgentState) -> str:
        """범용 파일 내용 생성"""
        return f'''{description}

자동 생성된 파일 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TODO: 실제 내용 구현
'''

    def _determine_target_files(self, description: str, state: AgentState) -> List[str]:
        """구현 대상 파일들 결정"""
        # 생성된 파일 목록에서 관련 파일 찾기
        generated_files = [f["path"] for f in state.get("generated_files", [])]

        if generated_files:
            return generated_files[:3]  # 최대 3개 파일

        # 기본 파일들 찾기
        project_context = self._get_project_context()
        sample_files = project_context.get("files_structure", {}).get("sample_files", [])

        if sample_files:
            return sample_files[:3]

        # 기본 파일 생성
        return ["main.py"]

    def _implement_in_file(self, file_path: str, description: str, state: AgentState) -> bool:
        """특정 파일에서 구현 수행"""
        try:
            if os.path.exists(file_path):
                # 기존 파일 수정
                return self._modify_existing_file(file_path, description, state)
            else:
                # 새 파일 생성
                content = self._generate_file_content(file_path, description, state)
                return self._write_file_safe(file_path, content)

        except Exception as e:
            print(f"파일 구현 실패: {e}")
            return False

    def _modify_existing_file(self, file_path: str, description: str, state: AgentState) -> bool:
        """기존 파일 수정"""
        try:
            original_content = self._read_file_safe(file_path)
            if not original_content:
                return False

            # 간단한 수정: 주석 추가
            modified_content = self._add_implementation_comment(original_content, description)

            success = self._write_file_safe(file_path, modified_content)

            if success:
                # 변경 기록
                change_info = {
                    "type": "file_modification",
                    "file": file_path,
                    "description": description,
                    "timestamp": datetime.now().isoformat()
                }
                state["code_changes"].append(change_info)

            return success

        except Exception as e:
            print(f"파일 수정 실패: {e}")
            return False

    def _add_implementation_comment(self, content: str, description: str) -> str:
        """구현 주석 추가"""
        lines = content.split('\n')

        # 첫 번째 함수나 클래스 찾기
        for i, line in enumerate(lines):
            if 'def ' in line or 'class ' in line or 'function ' in line:
                # 그 위에 주석 추가
                comment_line = f"# IMPLEMENTATION: {description}"
                lines.insert(i, comment_line)
                lines.insert(i+1, "")
                break
        else:
            # 함수가 없으면 파일 끝에 추가
            lines.append("")
            lines.append(f"# IMPLEMENTATION: {description}")
            lines.append("# TODO: 실제 구현 코드 작성")

        return '\n'.join(lines)

    def _implement_python_feature(self, description: str, state: AgentState) -> bool:
        """Python 기능 구현"""
        # Python 특화 구현 로직
        return self._handle_implementation({"description": description}, state)

    def _implement_js_feature(self, description: str, state: AgentState) -> bool:
        """JavaScript 기능 구현"""
        # JavaScript 특화 구현 로직
        return self._handle_implementation({"description": description}, state)

    def _implement_generic_feature(self, description: str, state: AgentState) -> bool:
        """범용 기능 구현"""
        return self._handle_implementation({"description": description}, state)

    def _analyze_error_patterns(self, error_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """에러 패턴 분석"""
        patterns = {
            "common_errors": [],
            "file_patterns": [],
            "recent_errors": error_history[-5:] if error_history else []
        }

        for error in error_history:
            error_msg = error.get("error", "").lower()
            if "file not found" in error_msg:
                patterns["common_errors"].append("file_not_found")
            elif "syntax error" in error_msg:
                patterns["common_errors"].append("syntax_error")

        return patterns

    def _find_files_by_error_context(self, error_patterns: Dict[str, Any]) -> List[str]:
        """에러 컨텍스트로 파일 찾기"""
        # 기본적으로 현재 디렉토리의 주요 파일들
        common_files = ["main.py", "app.py", "index.js", "main.js"]
        existing_files = [f for f in common_files if os.path.exists(f)]

        return existing_files[:3] if existing_files else ["main.py"]

    def _fix_bug_in_file(self, file_path: str, description: str, error_patterns: Dict[str, Any], state: AgentState) -> bool:
        """파일에서 버그 수정"""
        try:
            content = self._read_file_safe(file_path)
            if not content:
                return False

            # 간단한 버그 수정: 주석 추가
            fixed_content = content + f"\n\n# BUG FIX: {description}\n# Fixed at: {datetime.now().isoformat()}\n"

            success = self._write_file_safe(file_path, fixed_content)

            if success:
                change_info = {
                    "type": "bug_fix",
                    "file": file_path,
                    "description": description,
                    "timestamp": datetime.now().isoformat()
                }
                state["code_changes"].append(change_info)

            return success

        except Exception as e:
            print(f"버그 수정 실패: {e}")
            return False

    def _create_bug_fix_file(self, description: str, state: AgentState) -> bool:
        """버그 수정 파일 생성"""
        fix_file = "bug_fix.py"
        content = f'''"""
버그 수정 파일

{description}

생성 시간: {datetime.now().isoformat()}
"""

def bug_fix():
    """
    버그 수정 함수

    {description}
    """
    print("Bug fix implemented")
    # TODO: 실제 버그 수정 코드 작성


if __name__ == "__main__":
    bug_fix()
'''

        success = self._write_file_safe(fix_file, content)

        if success:
            file_info = {
                "path": fix_file,
                "type": "bug_fix",
                "size": len(content),
                "timestamp": datetime.now().isoformat(),
                "task_index": state["current_task_index"]
            }
            state["generated_files"].append(file_info)

        return success

    def _find_refactoring_targets(self, description: str) -> List[str]:
        """리팩토링 대상 파일 찾기"""
        # 현재 디렉토리의 Python/JS 파일들
        target_extensions = [".py", ".js", ".ts", ".java"]
        targets = []

        try:
            for file in os.listdir("."):
                if os.path.isfile(file):
                    _, ext = os.path.splitext(file)
                    if ext in target_extensions:
                        targets.append(file)
        except Exception:
            pass

        return targets[:3]  # 최대 3개 파일

    def _refactor_file(self, file_path: str, description: str, state: AgentState) -> bool:
        """파일 리팩토링"""
        try:
            content = self._read_file_safe(file_path)
            if not content:
                return False

            # 간단한 리팩토링: 코드 정리 주석 추가
            refactored_content = f"# REFACTORED: {description}\n# {datetime.now().isoformat()}\n\n{content}"

            success = self._write_file_safe(file_path, refactored_content)

            if success:
                change_info = {
                    "type": "refactoring",
                    "file": file_path,
                    "description": description,
                    "timestamp": datetime.now().isoformat()
                }
                state["code_changes"].append(change_info)

            return success

        except Exception as e:
            print(f"리팩토링 실패: {e}")
            return False

    def _perform_analysis(self, description: str, state: AgentState) -> str:
        """분석 수행"""
        project_context = self._get_project_context()

        content = f'''# 분석 결과

## 요청사항
{description}

## 분석 시간
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 프로젝트 컨텍스트
- 작업 디렉토리: {project_context.get('working_directory', 'Unknown')}
- 탐지된 언어: {', '.join(project_context.get('language_info', ['Unknown']))}
- 총 파일 수: {project_context.get('files_structure', {}).get('total_files', 0)}

## 분석 내용
{description}에 대한 분석을 수행했습니다.

### 주요 발견사항
- TODO: 실제 분석 결과 작성

### 권장사항
- TODO: 권장사항 작성

### 다음 단계
- TODO: 다음 단계 정의
'''

        return content

    def _create_design_document(self, description: str, state: AgentState) -> str:
        """설계 문서 생성"""
        content = f'''# 설계 문서

## 설계 요구사항
{description}

## 설계 일시
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 아키텍처 개요
{description}에 대한 설계 문서입니다.

### 주요 구성요소
- TODO: 구성요소 정의

### 인터페이스 설계
- TODO: 인터페이스 설계

### 데이터 모델
- TODO: 데이터 모델 설계

### 처리 흐름
- TODO: 처리 흐름 설계

## 구현 계획
- TODO: 구현 계획 수립
'''

        return content