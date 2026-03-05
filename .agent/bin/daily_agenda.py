#!/usr/bin/env python3
"""
데일리 아젠다 모듈
일일 처리 내용을 요약하여 데일리 아젠다 파일을 생성합니다.
"""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from file_manager import FileManager


class DailyAgendaManager:
    """데일리 아젠다 관리 클래스"""

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        print("📅 데일리 아젠다 관리자가 초기화되었습니다.")

    def create_or_update_daily_agenda(self, processed_agendas: List[Dict[str, Any]]) -> bool:
        """데일리 아젠다 서머리 파일을 생성하거나 업데이트합니다."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_file_path = self.file_manager.agendas_path / f"Daily_Agenda_{today}.md"

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
            content = self._generate_daily_content(topics_processed, today)

            # 기존 파일이 있으면 내용 추가, 없으면 새로 생성
            if daily_file_path.exists():
                existing_content = self.file_manager.read_file_content(daily_file_path)
                content = self._merge_daily_content(existing_content, content, topics_processed)

            # 파일 저장
            if self.file_manager.write_file(daily_file_path, content):
                print(f"📅 데일리 아젠다 생성: Daily_Agenda_{today}.md")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 데일리 아젠다 생성 실패: {e}")
            return False

    def _generate_daily_content(self, topics_processed: List[Dict], today: str) -> str:
        """데일리 아젠다 내용을 생성합니다."""
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
        return content

    def _merge_daily_content(self, existing_content: str, new_content: str, topics_processed: List[Dict]) -> str:
        """기존 데일리 아젠다 파일에 새 내용을 병합합니다."""
        # 간단히 덮어쓰기 방식으로 구현
        # 향후 더 정교한 병합 로직이 필요하면 개선 가능
        return new_content