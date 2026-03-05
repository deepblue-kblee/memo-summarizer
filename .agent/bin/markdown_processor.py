#!/usr/bin/env python3
"""
마크다운 처리 모듈
마크다운 파일의 파싱, 병합, 생성 등을 담당합니다.
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path


class MarkdownProcessor:
    """마크다운 처리 클래스"""

    def __init__(self):
        print("📝 마크다운 프로세서가 초기화되었습니다.")

    def parse_markdown_sections(self, content: str) -> Dict[str, Dict]:
        """마크다운 내용을 섹션별로 파싱합니다."""
        sections = {
            "tasks": {"content": [], "start_line": -1, "end_line": -1},
            "history": {"content": [], "start_line": -1, "end_line": -1}
        }

        lines = content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            # 할 일 목록 섹션 감지
            if line.strip().startswith('## 🚀 할 일 목록'):
                current_section = "tasks"
                sections["tasks"]["start_line"] = i
                continue
            # 메모 이력 섹션 감지
            elif line.strip().startswith('## 📝 메모 이력'):
                if current_section == "tasks":
                    sections["tasks"]["end_line"] = i - 1
                current_section = "history"
                sections["history"]["start_line"] = i
                continue
            # 다른 섹션 시작 감지 (## 으로 시작)
            elif line.strip().startswith('## ') and current_section:
                if current_section == "tasks":
                    sections["tasks"]["end_line"] = i - 1
                elif current_section == "history":
                    sections["history"]["end_line"] = i - 1
                current_section = None
                continue

            # 현재 섹션에 내용 추가
            if current_section:
                sections[current_section]["content"].append(line)

        # 마지막 섹션 처리
        if current_section == "tasks" and sections["tasks"]["end_line"] == -1:
            sections["tasks"]["end_line"] = len(lines) - 1
        elif current_section == "history" and sections["history"]["end_line"] == -1:
            sections["history"]["end_line"] = len(lines) - 1

        return sections

    def extract_existing_tasks(self, sections: Dict) -> List[str]:
        """기존 할 일 목록을 추출합니다."""
        existing_tasks = []

        for line in sections["tasks"]["content"]:
            line = line.strip()
            # - 또는 * 로 시작하는 항목들 추출
            if line.startswith('- ') or line.startswith('* '):
                task = line[2:].strip()
                if task:
                    existing_tasks.append(task)

        return existing_tasks

    def create_new_agenda_file_content(self, topic: str, tasks: List[str], summary: str) -> str:
        """새로운 아젠다 파일 내용을 생성합니다."""
        today = datetime.now().strftime("%Y-%m-%d")

        content = f"""# {topic}

## 🚀 할 일 목록

"""

        # 할 일 추가
        for task in tasks:
            content += f"- {task}\n"

        content += f"""
## 📝 메모 이력

[{today}] {summary}
"""

        return content

    def merge_with_existing_content(self, existing_content: str, topic: str, new_tasks: List[str], summary: str) -> str:
        """기존 파일 내용과 새 내용을 병합합니다."""
        if not existing_content:
            # 파일이 비어있으면 새로 생성
            return self.create_new_agenda_file_content(topic, new_tasks, summary)

        # 섹션 파싱
        sections = self.parse_markdown_sections(existing_content)

        # 기존 할 일 목록 추출
        existing_tasks = self.extract_existing_tasks(sections)

        # 중복되지 않은 새 할 일만 필터링
        unique_new_tasks = []
        for task in new_tasks:
            if task not in existing_tasks:
                unique_new_tasks.append(task)

        # 새 내용으로 파일 재구성
        lines = existing_content.split('\n')
        new_lines = []

        today = datetime.now().strftime("%Y-%m-%d")

        # 할 일 섹션에 새 항목 추가
        tasks_section = sections["tasks"]
        if tasks_section["start_line"] >= 0:
            # 기존 할 일 섹션이 있는 경우
            new_lines = lines[:tasks_section["end_line"] + 1]

            # 새 할 일 추가
            for task in unique_new_tasks:
                new_lines.append(f"- {task}")

            # 나머지 내용 추가
            if tasks_section["end_line"] + 1 < len(lines):
                new_lines.extend(lines[tasks_section["end_line"] + 1:])
        else:
            # 할 일 섹션이 없는 경우 - 파일 끝에 추가
            new_lines = lines
            new_lines.append("")
            new_lines.append("## 🚀 할 일 목록")
            new_lines.append("")
            for task in unique_new_tasks:
                new_lines.append(f"- {task}")

        # 메모 이력 섹션에 새 요약 추가
        history_section = sections["history"]
        if history_section["start_line"] >= 0:
            # 기존 이력 섹션이 있는 경우 - 섹션 바로 다음에 추가
            insert_pos = history_section["start_line"] + 1
            # 빈 줄이 있으면 그 다음에 삽입
            while insert_pos < len(new_lines) and new_lines[insert_pos].strip() == "":
                insert_pos += 1

            new_lines.insert(insert_pos, f"[{today}] {summary}")
        else:
            # 이력 섹션이 없는 경우 - 파일 끝에 추가
            new_lines.append("")
            new_lines.append("## 📝 메모 이력")
            new_lines.append("")
            new_lines.append(f"[{today}] {summary}")

        return '\n'.join(new_lines)