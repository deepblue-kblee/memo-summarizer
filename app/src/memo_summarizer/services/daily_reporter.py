#!/usr/bin/env python3
"""
데일리 리포터 모듈 (PARA 방법론 적용)
일일 처리 내용을 PARA 분류로 요약하여 데일리 리포트를 생성합니다.
"""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from memo_summarizer.utils.markdown_processor import MarkdownProcessor


class DailyReporter:
    """데일리 리포터 클래스 (PARA 지원)"""

    def __init__(self, vault_path: str):
        """
        Args:
            vault_path: Obsidian Vault의 루트 경로
        """
        self.vault_path = Path(vault_path).resolve()
        self.daily_reports_path = self.vault_path / "02_DAILY_REPORTS"
        self.markdown_processor = MarkdownProcessor()

        # 디렉토리 생성
        self.daily_reports_path.mkdir(exist_ok=True)

        print("📊 데일리 리포터가 초기화되었습니다.")

    def create_or_update_daily_report(self, processed_agendas: List[Dict[str, Any]]) -> bool:
        """PARA 분류가 적용된 데일리 리포트를 생성하거나 업데이트합니다."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_file_path = self.daily_reports_path / f"Daily_Report_{today}.md"

            # PARA 분류별로 주제들 수집
            projects = []
            areas = []

            for agenda in processed_agendas:
                topic = agenda.get("topic")
                category = agenda.get("category", "Areas")
                
                if topic and topic not in ["분석 실패", "파싱 실패", "예기치 못한 오류"]:
                    # 실제 파일에서 최신 상태 읽기
                    agenda_file_path = self.vault_path / "01_AGENDAS" / category / f"{topic}.md"
                    
                    task_counts = {"total": 0, "pending": 0, "completed": 0}
                    if agenda_file_path.exists():
                        with open(agenda_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            task_counts = self.markdown_processor.get_task_counts(content)
                    
                    topic_info = {
                        "topic": topic,
                        "summary": agenda["summary"],
                        "task_counts": task_counts
                    }

                    if category == "Projects":
                        projects.append(topic_info)
                    else:
                        areas.append(topic_info)

            if not projects and not areas:
                print("📊 처리된 유효한 주제가 없어 데일리 리포트를 생성하지 않습니다.")
                return True

            # 데일리 리포트 내용 생성
            content = self._generate_daily_report_content(projects, areas, today)

            # 파일 저장 (일일 단위 덮어쓰기)
            if self._write_file(daily_file_path, content):
                print(f"📊 데일리 리포트 생성 완료: Daily_Report_{today}.md")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 데일리 리포트 생성 실패: {e}")
            return False

    def _generate_daily_report_content(self, projects: List[Dict], areas: List[Dict], today: str) -> str:
        """최종 상태(State)가 반영된 데일리 리포트 내용을 생성합니다."""
        content = f"""# Daily Report - {today}

> 📊 **메모 자동화 일일 처리 보고서 (PARA State Report)**

## 🎯 Projects (목표 지향 프로젝트)

"""

        if projects:
            for i, project in enumerate(projects, 1):
                topic = project["topic"]
                summary = project["summary"]
                counts = project["task_counts"]

                content += f"### {i}. [[Projects/{topic}|{topic}]]\n"
                content += f"- **오늘의 진척**: {summary}\n"
                content += f"- **할 일 상태**: 총 {counts['total']}개 (남음: {counts['pending']}, 완료: {counts['completed']})\n\n"
        else:
            content += "*오늘 업데이트된 프로젝트가 없습니다.*\n\n"

        content += """## 🏢 Areas (지속적 관리 영역)

"""

        if areas:
            for i, area in enumerate(areas, 1):
                topic = area["topic"]
                summary = area["summary"]
                counts = area["task_counts"]

                content += f"### {i}. [[Areas/{topic}|{topic}]]\n"
                content += f"- **오늘의 요약**: {summary}\n"
                content += f"- **할 일 상태**: 총 {counts['total']}개 (남음: {counts['pending']}, 완료: {counts['completed']})\n\n"
        else:
            content += "*오늘 업데이트된 관리 영역이 없습니다.*\n\n"

        # PARA 통계 섹션
        total_projects_tasks = sum(p['task_counts']['total'] for p in projects)
        pending_projects_tasks = sum(p['task_counts']['pending'] for p in projects)
        completed_projects_tasks = sum(p['task_counts']['completed'] for p in projects)
        
        total_areas_tasks = sum(a['task_counts']['total'] for a in areas)
        pending_areas_tasks = sum(a['task_counts']['pending'] for a in areas)
        completed_areas_tasks = sum(a['task_counts']['completed'] for a in areas)

        content += f"""## 📈 PARA 종합 통계 (오늘 업데이트 항목 기준)

| 분류 | 주제 수 | 전체 할 일 | 남은 일 | 완료된 일 | 진척도 |
|------|---------|------------|---------|-----------|--------|
| 🎯 Projects | {len(projects)}개 | {total_projects_tasks}개 | {pending_projects_tasks}개 | {completed_projects_tasks}개 | {self._calc_percent(completed_projects_tasks, total_projects_tasks)}% |
| 🏢 Areas | {len(areas)}개 | {total_areas_tasks}개 | {pending_areas_tasks}개 | {completed_areas_tasks}개 | {self._calc_percent(completed_areas_tasks, total_areas_tasks)}% |
| **합계** | **{len(projects) + len(areas)}개** | **{total_projects_tasks + total_areas_tasks}개** | **{pending_projects_tasks + pending_areas_tasks}개** | **{completed_projects_tasks + completed_areas_tasks}개** | **{self._calc_percent(completed_projects_tasks + completed_areas_tasks, total_projects_tasks + total_areas_tasks)}%** |

## 📝 메타데이터

- **생성 시각**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **PARA 방법론**: Projects (목표) + Areas (책임)
- **상태 관리**: AI 기반 지능형 병합 및 상태 추적 적용

---
*이 보고서는 PARA 방법론과 GSD 철학을 결합하여 자동 생성되었습니다.*
"""
        return content

    def _calc_percent(self, completed: int, total: int) -> int:
        """진척도 백분율을 계산합니다."""
        if total == 0:
            return 0
        return int((completed / total) * 100)

    def _write_file(self, file_path: Path, content: str) -> bool:
        """파일에 내용을 씁니다."""
        try:
            # 디렉토리가 없으면 생성
            file_path.parent.mkdir(exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패 {file_path.name}: {e}")
            return False
