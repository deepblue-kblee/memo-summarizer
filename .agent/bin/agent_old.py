#!/usr/bin/env python3
"""
Obsidian 메모 분석 및 병합 에이전트 (Multi-Topic 지원)
00_INBOX의 .md 파일들을 분석하여 다중 주제를 추출하고,
각 주제별로 01_AGENDAS의 파일들과 자동 병합합니다.

주요 기능:
- 하나의 메모에서 여러 독립적인 주제 추출
- 각 주제별로 별도 아젠다 파일 생성/병합
- 데일리 서머리 자동 생성 (Daily_Agenda_YYYY-MM-DD.md)
- 업무/의사결정 관련 내용만 필터링 (노이즈 제거)

사용법:
    python agent.py              # 분석 + 자동 병합 (기본)
    python agent.py --analysis-only  # 분석만 수행
    python agent.py --json       # JSON 형식으로 결과 출력

Claude Code CLI 기반으로 동작하므로 ~/.claude/settings.json 설정을 자동으로 사용합니다.
"""

import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys

class MemoAnalyzer:
    def __init__(self):
        # 경로 설정
        self.base_path = Path(__file__).parent
        self.inbox_path = self.base_path / "00_INBOX"
        self.archived_path = self.base_path / "00_INBOX" / "_ARCHIVED"
        self.agendas_path = self.base_path / "01_AGENDAS"

        # Claude Code CLI 사용 가능 확인
        self._check_claude_code_available()

        print("📋 다중 주제 메모 분석 에이전트가 초기화되었습니다.")

    def _check_claude_code_available(self):
        """Claude Code CLI 사용 가능성을 확인합니다."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude Code 실행 실패: {result.stderr}")

            print(f"✅ Claude Code 연결 확인: {result.stdout.strip()}")

        except FileNotFoundError:
            raise RuntimeError("Claude Code가 설치되어 있지 않습니다. 'claude --version'을 실행해보세요.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code 응답 시간 초과")
        except Exception as e:
            raise RuntimeError(f"Claude Code 확인 실패: {e}")

    def call_claude_code(self, prompt: str) -> Dict[str, Any]:
        """Claude Code CLI를 통해 AI API 호출"""
        try:
            # Claude Code 명령어 실행
            result = subprocess.run([
                "claude",
                "--print",  # 응답 출력하고 종료
                "--output-format", "json",  # JSON 형식으로 출력
                prompt
            ],
            capture_output=True,  # stdout/stderr 캡처
            text=True,  # 문자열로 반환
            timeout=120  # 2분 타임아웃
            )

            # 실행 성공 확인
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                raise RuntimeError(f"Claude Code 실행 실패: {error_msg}")

            # JSON 파싱
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Claude Code JSON 응답 파싱 실패: {e}\n응답: {result.stdout[:200]}")

            return {
                "success": True,
                "content": response_data.get("result", ""),
                "cost": response_data.get("total_cost_usd", 0),
                "session_id": response_data.get("session_id", ""),
                "raw": response_data
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Claude Code 호출 타임아웃 (2분 초과)"}
        except Exception as e:
            return {"success": False, "error": f"Claude Code 호출 실패: {e}"}

    def get_md_files(self) -> List[Path]:
        """00_INBOX 폴더에서 .md 파일 목록을 가져옵니다. (_ARCHIVED 제외)"""
        md_files = []

        if not self.inbox_path.exists():
            print(f"❌ INBOX 폴더가 존재하지 않습니다: {self.inbox_path}")
            return md_files

        for file_path in self.inbox_path.iterdir():
            # _ARCHIVED 폴더는 제외
            if file_path.name == "_ARCHIVED":
                continue

            # .md 파일만 선택
            if (file_path.is_file() and
                file_path.suffix.lower() == '.md' and
                not file_path.name.startswith('.')):
                md_files.append(file_path)

        return sorted(md_files)

    def read_file_content(self, file_path: Path) -> str:
        """파일 내용을 읽어옵니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            print(f"❌ 파일 읽기 실패 {file_path.name}: {e}")
            return ""

    def analyze_memo(self, content: str) -> Dict[str, Any]:
        """Claude Code CLI를 사용하여 메모를 분석합니다 (다중 주제 지원)."""

        prompt = f"""
다음 메모 내용을 분석하여 독립적인 업무/의사결정 관련 주제들을 모두 추출해주세요.

메모 내용:
{content}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "agendas": [
        {{
            "topic": "주제1 (간결하게)",
            "tasks": ["할일1", "할일2"],
            "summary": "주제1의 핵심 내용 요약"
        }},
        {{
            "topic": "주제2 (간결하게)",
            "tasks": ["할일3"],
            "summary": "주제2의 핵심 내용 요약"
        }}
    ]
}}

규칙:
1. 메모에서 독립적인 업무/프로젝트/의사결정 관련 주제들을 모두 찾아 분리해주세요
2. 단순 인사치레, 개인적 낙서, 의미 없는 메모는 제외하고 실제 '업무'나 '의사결정'과 관련된 내용만 포함
3. 각 topic은 파일명으로 사용 가능한 간결한 형태로 작성 (예: "믹스패널", "조직개편", "프로젝트A" 등)
4. tasks는 해당 주제에서 추출할 수 있는 구체적인 행동 항목들 (없으면 빈 배열 [])
5. summary는 해당 주제의 핵심 내용을 2-3 문장으로 요약
6. 주제가 하나뿐이면 배열에 하나만 포함, 관련 내용이 없으면 빈 배열 []
7. 반드시 유효한 JSON 형식으로만 응답
"""

        # Claude Code CLI 호출
        response = self.call_claude_code(prompt)

        if not response["success"]:
            print(f"❌ Claude Code 호출 실패: {response['error']}")
            return {
                "agendas": [{
                    "topic": "분석 실패",
                    "tasks": [],
                    "summary": f"메모 분석 중 오류가 발생했습니다: {response['error']}"
                }]
            }

        try:
            # AI 응답에서 JSON 추출
            response_text = response["content"].strip()

            # JSON 블록 찾기 (```json이 있는 경우 처리)
            if "```json" in response_text:
                start_idx = response_text.find("```json") + 7
                end_idx = response_text.find("```", start_idx)
                if end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()
            elif "```" in response_text:
                start_idx = response_text.find("```") + 3
                end_idx = response_text.find("```", start_idx)
                if end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()

            # JSON 파싱
            result = json.loads(response_text)

            # 필수 필드 검증
            if "agendas" not in result or not isinstance(result["agendas"], list):
                raise ValueError("agendas 필드가 누락되었거나 잘못된 형식입니다.")

            # 각 아젠다 항목 검증
            for agenda in result["agendas"]:
                if not all(key in agenda for key in ["topic", "tasks", "summary"]):
                    raise ValueError("아젠다 항목에 필수 필드가 누락되었습니다.")
                # tasks가 리스트인지 확인
                if not isinstance(agenda["tasks"], list):
                    agenda["tasks"] = []

            # 비용 정보 로그 (있는 경우)
            if response.get("cost", 0) > 0:
                print(f"💰 API 비용: ${response['cost']:.6f}")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ 응답 파싱 오류: {e}")
            print(f"응답 내용: {response_text[:200]}")
            return {
                "agendas": [{
                    "topic": "파싱 실패",
                    "tasks": [],
                    "summary": f"응답 파싱 중 오류가 발생했습니다: {str(e)}"
                }]
            }

    def sanitize_filename(self, topic: str) -> str:
        """주제를 파일명에 적합하게 변환합니다."""
        # 파일명에 사용할 수 없는 문자 제거/변환
        sanitized = re.sub(r'[<>:"/\\|?*]', '', topic)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    def get_agenda_file_path(self, topic: str) -> Path:
        """주제를 기반으로 아젠다 파일 경로를 생성합니다."""
        filename = f"{self.sanitize_filename(topic)}.md"
        return self.agendas_path / filename

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

    def create_new_agenda_file(self, topic: str, tasks: List[str], summary: str) -> str:
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

    def merge_with_existing_file(self, file_path: Path, new_tasks: List[str], summary: str) -> str:
        """기존 파일과 새 내용을 병합합니다."""
        # 기존 파일 읽기
        existing_content = self.read_file_content(file_path)
        if not existing_content:
            # 파일이 비어있으면 새로 생성
            return self.create_new_agenda_file(file_path.stem, new_tasks, summary)

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

    def write_agenda_file(self, file_path: Path, content: str) -> bool:
        """아젠다 파일에 내용을 씁니다."""
        try:
            # 디렉토리가 없으면 생성
            file_path.parent.mkdir(exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패 {file_path.name}: {e}")
            return False

    def archive_file(self, file_path: Path) -> bool:
        """파일을 아카이브로 이동합니다."""
        try:
            # 아카이브 폴더가 없으면 생성
            self.archived_path.mkdir(exist_ok=True)

            # 파일명에 타임스탬프 추가하여 중복 방지
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archived_file_path = self.archived_path / archived_name

            shutil.move(str(file_path), str(archived_file_path))
            print(f"📦 아카이브 완료: {file_path.name} -> {archived_name}")
            return True

        except Exception as e:
            print(f"❌ 아카이브 실패 {file_path.name}: {e}")
            return False

    def create_or_update_daily_agenda(self, processed_agendas: List[Dict[str, Any]]) -> bool:
        """데일리 아젠다 서머리 파일을 생성하거나 업데이트합니다."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_file_path = self.agendas_path / f"Daily_Agenda_{today}.md"

            # 오늘 처리된 주제들 수집
            topics_processed = []
            for agenda in processed_agendas:
                if agenda.get("topic") and agenda["topic"] not in ["분석 실패", "파싱 실패"]:
                    topics_processed.append({
                        "topic": agenda["topic"],
                        "summary": agenda["summary"],
                        "task_count": len(agenda.get("tasks", []))
                    })

            if not topics_processed:
                print("📅 처리된 유효한 주제가 없어 데일리 아젠다를 생성하지 않습니다.")
                return True

            # 데일리 서머리 내용 생성
            content = f"""# Daily Agenda - {today}

## 📋 오늘 처리된 주제들

"""
            for i, topic_info in enumerate(topics_processed, 1):
                topic = topic_info["topic"]
                summary = topic_info["summary"]
                task_count = topic_info["task_count"]

                content += f"### {i}. [[{topic}]]\n"
                content += f"- **할 일**: {task_count}개\n"
                content += f"- **요약**: {summary}\n\n"

            content += f"""## 📊 처리 통계

- **총 주제 수**: {len(topics_processed)}개
- **총 할 일**: {sum(t['task_count'] for t in topics_processed)}개
- **처리 시각**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
*자동 생성된 데일리 아젠다 서머리*
"""

            # 기존 파일이 있으면 내용 추가, 없으면 새로 생성
            if daily_file_path.exists():
                existing_content = self.read_file_content(daily_file_path)
                # 기존 내용에 새 항목들을 추가하는 로직 구현 (간단히 덮어쓰기)
                content = content

            # 파일 저장
            if self.write_agenda_file(daily_file_path, content):
                print(f"📅 데일리 아젠다 생성: Daily_Agenda_{today}.md")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 데일리 아젠다 생성 실패: {e}")
            return False

    def process_and_merge(self, file_path: Path, analysis: Dict[str, Any]) -> bool:
        """분석 결과를 아젠다 파일들에 병합합니다 (다중 주제 지원)."""
        try:
            agendas = analysis.get("agendas", [])

            if not agendas:
                print("⚠️ 처리할 주제가 없습니다.")
                return False

            successful_merges = 0

            for agenda in agendas:
                topic = agenda["topic"]
                tasks = agenda["tasks"]
                summary = agenda["summary"]

                # 분석/파싱 실패한 항목은 건너뛰기
                if topic in ["분석 실패", "파싱 실패"]:
                    print(f"⚠️ 실패한 주제 건너뛰기: {topic}")
                    continue

                # 아젠다 파일 경로 생성
                agenda_file_path = self.get_agenda_file_path(topic)

                print(f"📝 병합 대상: {agenda_file_path.name} (주제: {topic})")

                # 파일 존재 여부에 따라 처리
                if agenda_file_path.exists():
                    print(f"🔄 기존 파일과 병합 중...")
                    merged_content = self.merge_with_existing_file(agenda_file_path, tasks, summary)
                else:
                    print(f"📄 새 파일 생성 중...")
                    merged_content = self.create_new_agenda_file(topic, tasks, summary)

                # 파일 저장
                if self.write_agenda_file(agenda_file_path, merged_content):
                    print(f"✅ 완료: {topic} - {len(tasks)}개 할일, 요약 1개 추가됨")
                    successful_merges += 1
                else:
                    print(f"❌ 파일 저장 실패: {topic}")

            # 모든 주제 처리 완료 후 원본 파일 아카이브
            if successful_merges > 0:
                if self.archive_file(file_path):
                    print(f"📦 총 {successful_merges}개 주제 처리 완료, 원본 파일 아카이브됨")

                    # 데일리 아젠다 업데이트
                    self.create_or_update_daily_agenda(agendas)
                    return True
                else:
                    print(f"⚠️ 병합은 완료되었지만 아카이브에 실패했습니다.")
                    return False
            else:
                print("❌ 처리된 주제가 없어서 아카이브하지 않습니다.")
                return False

        except Exception as e:
            print(f"❌ 병합 처리 실패: {e}")
            return False

    def analyze_all_files(self) -> List[Dict[str, Any]]:
        """모든 .md 파일을 분석합니다."""

        md_files = self.get_md_files()

        if not md_files:
            print("📂 처리할 .md 파일이 없습니다.")
            return []

        print(f"📁 {len(md_files)}개의 .md 파일을 발견했습니다.")

        results = []

        for i, file_path in enumerate(md_files, 1):
            print(f"\n🔍 [{i}/{len(md_files)}] 분석 중: {file_path.name}")

            content = self.read_file_content(file_path)
            if not content:
                print("⚠️  빈 파일이거나 읽을 수 없습니다. 건너뜁니다.")
                continue

            analysis = self.analyze_memo(content)

            # 파일 정보 추가
            analysis["filename"] = file_path.name
            analysis["filepath"] = str(file_path)

            results.append(analysis)

            agendas = analysis.get("agendas", [])
            print(f"✅ 분석 완료 - {len(agendas)}개 주제 발견")
            for i, agenda in enumerate(agendas, 1):
                print(f"   {i}. {agenda['topic']} - {len(agenda['tasks'])}개 할 일")

        return results

    def analyze_and_merge_all_files(self) -> List[Dict[str, Any]]:
        """모든 .md 파일을 분석하고 아젠다 파일에 병합합니다."""

        md_files = self.get_md_files()

        if not md_files:
            print("📂 처리할 .md 파일이 없습니다.")
            return []

        print(f"📁 {len(md_files)}개의 .md 파일을 발견했습니다.")
        print("🚀 분석 및 병합을 시작합니다...\n")

        results = []
        successful_merges = 0

        for i, file_path in enumerate(md_files, 1):
            print(f"🔍 [{i}/{len(md_files)}] 처리 중: {file_path.name}")

            content = self.read_file_content(file_path)
            if not content:
                print("⚠️  빈 파일이거나 읽을 수 없습니다. 건너뜁니다.")
                continue

            # 분석 수행
            analysis = self.analyze_memo(content)

            # 파일 정보 추가
            analysis["filename"] = file_path.name
            analysis["filepath"] = str(file_path)

            agendas = analysis.get("agendas", [])
            print(f"✅ 분석 완료 - {len(agendas)}개 주제 발견")
            for j, agenda in enumerate(agendas, 1):
                print(f"   {j}. {agenda['topic']} - {len(agenda['tasks'])}개 할 일")

            # 병합 수행
            if self.process_and_merge(file_path, analysis):
                analysis["merged"] = True
                successful_merges += 1
            else:
                analysis["merged"] = False

            results.append(analysis)
            print("")  # 빈 줄 추가

        print(f"🎉 처리 완료!")
        print(f"   📊 총 {len(results)}개 파일 분석")
        print(f"   ✅ {successful_merges}개 파일 병합 성공")

        return results

    def print_results(self, results: List[Dict[str, Any]]):
        """분석 결과를 보기 좋게 출력합니다 (다중 주제 지원)."""

        if not results:
            print("\n📋 분석 결과가 없습니다.")
            return

        # 전체 통계 계산
        total_files = len(results)
        total_agendas = sum(len(result.get("agendas", [])) for result in results)
        total_tasks = sum(len(agenda.get("tasks", []))
                         for result in results
                         for agenda in result.get("agendas", []))

        print(f"\n{'='*60}")
        print(f"📊 메모 분석 결과")
        print(f"📁 파일: {total_files}개 | 📋 주제: {total_agendas}개 | ✅ 할 일: {total_tasks}개")
        print(f"{'='*60}")

        for i, result in enumerate(results, 1):
            print(f"\n📄 [{i}] {result['filename']}")

            agendas = result.get("agendas", [])
            if not agendas:
                print("   ⚠️ 추출된 주제가 없습니다.")
                continue

            for j, agenda in enumerate(agendas, 1):
                print(f"\n   🏷️ 주제 {j}: {agenda['topic']}")
                print(f"   📝 요약: {agenda['summary']}")

                tasks = agenda.get('tasks', [])
                if tasks:
                    print(f"   ✅ 할 일 목록 ({len(tasks)}개):")
                    for k, task in enumerate(tasks, 1):
                        print(f"      {k}. {task}")
                else:
                    print("   ✅ 할 일: 없음")

            print("-" * 50)

def main():
    """메인 실행 함수"""
    try:
        analyzer = MemoAnalyzer()

        # 실행 모드 결정
        analysis_only = '--analysis-only' in sys.argv

        if analysis_only:
            print("🔍 분석 전용 모드로 실행합니다...\n")
            # 분석만 수행
            results = analyzer.analyze_all_files()

            # 결과 출력
            analyzer.print_results(results)

            print(f"\n🎉 분석 완료! 총 {len(results)}개 파일 처리됨")
        else:
            print("🚀 메모 분석 및 병합을 시작합니다...\n")
            # 분석 + 병합 수행
            results = analyzer.analyze_and_merge_all_files()

        # JSON 형태로도 출력 (필요한 경우)
        if results and '--json' in sys.argv:
            print(f"\n📋 JSON 형식 결과:")
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n👋 분석을 중단합니다...")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())