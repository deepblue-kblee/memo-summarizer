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
        """기존 할 일 목록을 추출합니다. (체크박스 포함 유지)"""
        existing_tasks = []

        for line in sections["tasks"]["content"]:
            line = line.strip()
            # - [ ] 또는 - [x] 로 시작하는 항목들 추출
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                existing_tasks.append(line)
            # 일반 리스트 항목도 일단 포함
            elif line.startswith('- ') or line.startswith('* '):
                existing_tasks.append(line)

        return existing_tasks

    def create_new_agenda_file_content(self, topic: str, tasks: List[str], summary: str) -> str:
        """새로운 아젠다 파일 내용을 생성합니다."""
        today = datetime.now().strftime("%Y-%m-%d")

        content = f"""# {topic}

## 🚀 할 일 목록

"""

        # 할 일 추가
        for task in tasks:
            if task.startswith('- ') or task.startswith('* '):
                content += f"{task}\n"
            else:
                content += f"- {task}\n"

        content += f"""
## 📝 메모 이력

[{today}] {summary}
"""

        return content

    def merge_with_existing_content(self, existing_content: str, topic: str, new_tasks: List[str], summary: str) -> str:
        """기존 파일 내용과 새 내용을 병합합니다 (레거시/백업용)."""
        if not existing_content:
            return self.create_new_agenda_file_content(topic, new_tasks, summary)

        sections = self.parse_markdown_sections(existing_content)
        existing_tasks = self.extract_existing_tasks(sections)

        unique_new_tasks = []
        for task in new_tasks:
            found = False
            for existing in existing_tasks:
                if task in existing:
                    found = True
                    break
            if not found:
                unique_new_tasks.append(task)

        lines = existing_content.split('\n')
        new_lines = []
        today = datetime.now().strftime("%Y-%m-%d")

        tasks_section = sections["tasks"]
        if tasks_section["start_line"] >= 0:
            new_lines = lines[:tasks_section["end_line"] + 1]
            for task in unique_new_tasks:
                if task.startswith('- ') or task.startswith('* '):
                    new_lines.append(f"{task}")
                else:
                    new_lines.append(f"- {task}")
            if tasks_section["end_line"] + 1 < len(lines):
                new_lines.extend(lines[tasks_section["end_line"] + 1:])
        else:
            new_lines = lines
            new_lines.append("")
            new_lines.append("## 🚀 할 일 목록")
            new_lines.append("")
            for task in unique_new_tasks:
                if task.startswith('- ') or task.startswith('* '):
                    new_lines.append(f"{task}")
                else:
                    new_lines.append(f"- {task}")

        # 이력 추가 (이미 history 섹션이 있는 경우 고려)
        history_section = self.parse_markdown_sections('\n'.join(new_lines))["history"]
        if history_section["start_line"] >= 0:
            current_lines = '\n'.join(new_lines).split('\n')
            insert_pos = history_section["start_line"] + 1
            while insert_pos < len(current_lines) and current_lines[insert_pos].strip() == "":
                insert_pos += 1
            current_lines.insert(insert_pos, f"[{today}] {summary}")
            return '\n'.join(current_lines)
        else:
            new_lines.append("")
            new_lines.append("## 📝 메모 이력")
            new_lines.append("")
            new_lines.append(f"[{today}] {summary}")
            return '\n'.join(new_lines)

    def get_task_counts(self, content: str) -> Dict[str, int]:
        """할 일 목록에서 완료/미완료 개수를 세어 반환합니다."""
        sections = self.parse_markdown_sections(content)
        tasks = sections["tasks"]["content"]
        
        counts = {"total": 0, "pending": 0, "completed": 0}
        
        for line in tasks:
            line = line.strip()
            if line.startswith('- [ ]'):
                counts["pending"] += 1
                counts["total"] += 1
            elif line.startswith('- [x]'):
                counts["completed"] += 1
                counts["total"] += 1
            elif line.startswith('- ') or line.startswith('* '):
                # 일반 리스트 항목은 미완료로 취급
                counts["pending"] += 1
                counts["total"] += 1
                
        return counts
