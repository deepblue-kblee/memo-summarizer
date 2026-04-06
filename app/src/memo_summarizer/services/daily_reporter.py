#!/usr/bin/env python3
"""
데일리 리포터 모듈 (PARA 방법론 적용)
일일 처리 내용을 PARA 분류로 요약하여 데일리 리포트를 생성합니다.
"""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class DailyReporter:
    """데일리 리포터 클래스 (PARA 지원)"""

    def __init__(self, vault_path: str):
        """
        Args:
            vault_path: Obsidian Vault의 루트 경로
        """
        self.vault_path = Path(vault_path).resolve()
        self.daily_reports_path = self.vault_path / "02_DAILY_REPORTS"

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
                if agenda.get("topic") and agenda["topic"] not in ["분석 실패", "파싱 실패", "예기치 못한 오류"]:
                    topic_info = {
                        "topic": agenda["topic"],
                        "summary": agenda["summary"],
                        "task_count": len(agenda.get("tasks", []))
                    }

                    category = agenda.get("category", "Areas")
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
                print(f"📊 데일리 리포트 생성: Daily_Report_{today}.md")
                print(f"   🎯 Projects: {len(projects)}개 | 🏢 Areas: {len(areas)}개")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 데일리 리포트 생성 실패: {e}")
            return False

    def _generate_daily_report_content(self, projects: List[Dict], areas: List[Dict], today: str) -> str:
        """Projects/Areas 분류가 적용된 데일리 리포트 내용을 생성합니다."""
        content = f"""# Daily Report - {today}

> 📊 **메모 자동화 일일 처리 보고서**

## 🎯 Projects (목표 지향 프로젝트)

"""

        if projects:
            for i, project in enumerate(projects, 1):
                topic = project["topic"]
                summary = project["summary"]
                task_count = project["task_count"]

                content += f"### {i}. [[Projects/{topic}]]\n"
                content += f"- **할 일**: {task_count}개\n"
                content += f"- **요약**: {summary}\n\n"
        else:
            content += "*오늘 처리된 프로젝트가 없습니다.*\n\n"

        content += """## 🏢 Areas (지속적 관리 영역)

"""

        if areas:
            for i, area in enumerate(areas, 1):
                topic = area["topic"]
                summary = area["summary"]
                task_count = area["task_count"]

                content += f"### {i}. [[Areas/{topic}]]\n"
                content += f"- **할 일**: {task_count}개\n"
                content += f"- **요약**: {summary}\n\n"
        else:
            content += "*오늘 처리된 관리 영역이 없습니다.*\n\n"

        # PARA 통계 섹션
        total_topics = len(projects) + len(areas)
        total_tasks = sum(p['task_count'] for p in projects) + sum(a['task_count'] for a in areas)

        content += f"""## 📈 PARA 처리 통계

| 분류 | 주제 수 | 할 일 수 |
|------|---------|----------|
| 🎯 Projects | {len(projects)}개 | {sum(p['task_count'] for p in projects)}개 |
| 🏢 Areas | {len(areas)}개 | {sum(a['task_count'] for a in areas)}개 |
| **합계** | **{total_topics}개** | **{total_tasks}개** |

## 📝 메타데이터

- **생성 시각**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **PARA 방법론**: Projects (목표) + Areas (책임)
- **자동 생성**: PARA 메모 자동화 에이전트

---
*이 보고서는 PARA 방법론을 적용하여 자동 생성되었습니다.*
"""
        return content

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