#!/usr/bin/env python3
"""
Agent Team 상태 업데이트 스크립트

이 스크립트는 현재 프로젝트 상태를 업데이트하고 추적하는 도구입니다.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class StatusManager:
    """상태 관리 클래스"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent.parent
        self.tracking_path = self.base_path / "tracking"
        self.status_file = self.tracking_path / "current_status.md"
        self.task_board_file = self.tracking_path / "task_board.md"

    def update_status(self, status: str, details: Optional[str] = None):
        """현재 상태 업데이트"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        status_data = {
            "timestamp": timestamp,
            "status": status,
            "details": details or "",
            "updated_by": "Agent Team Status Manager"
        }

        # 상태 파일 업데이트
        self._update_status_file(status_data)

        print(f"✅ 상태 업데이트 완료: {status}")
        if details:
            print(f"   상세: {details}")
        print(f"   시간: {timestamp}")

    def _update_status_file(self, status_data: Dict[str, Any]):
        """상태 파일 내용 업데이트"""
        if not self.status_file.exists():
            print(f"⚠️  상태 파일이 없습니다: {self.status_file}")
            return

        # 기존 파일 읽기
        content = self.status_file.read_text(encoding='utf-8')

        # 타임스탬프 업데이트
        new_timestamp = f"*마지막 업데이트: {status_data['timestamp']}*"
        lines = content.split('\n')

        # 첫 번째 타임스탬프 라인 찾아서 교체
        for i, line in enumerate(lines):
            if line.startswith('*마지막 업데이트:'):
                lines[i] = new_timestamp
                break

        # 새로운 상태 로그 추가
        log_entry = f"\n### 최근 업데이트 ({status_data['timestamp']})\n"
        log_entry += f"- **상태**: {status_data['status']}\n"
        if status_data['details']:
            log_entry += f"- **상세**: {status_data['details']}\n"
        log_entry += f"- **담당자**: {status_data['updated_by']}\n"

        # 파일 끝에 로그 추가
        updated_content = '\n'.join(lines) + log_entry

        # 파일 저장
        self.status_file.write_text(updated_content, encoding='utf-8')

    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태 정보 반환"""
        if not self.status_file.exists():
            return {"error": "Status file not found"}

        content = self.status_file.read_text(encoding='utf-8')

        # 간단한 상태 파싱 (실제 구현에서는 더 정교하게)
        status_info = {
            "file_exists": True,
            "last_modified": datetime.datetime.fromtimestamp(
                self.status_file.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M"),
            "content_length": len(content),
            "file_path": str(self.status_file)
        }

        return status_info

    def mark_task_completed(self, task_name: str):
        """작업 완료 표시"""
        self.update_status(
            f"작업 완료: {task_name}",
            f"Task '{task_name}' 가 성공적으로 완료되었습니다."
        )

    def mark_task_in_progress(self, task_name: str):
        """작업 진행 중 표시"""
        self.update_status(
            f"작업 진행 중: {task_name}",
            f"Task '{task_name}' 작업을 시작했습니다."
        )

    def add_blocker(self, blocker_description: str):
        """차단 요소 추가"""
        self.update_status(
            "차단 요소 발생",
            f"새로운 차단 요소: {blocker_description}"
        )


def main():
    parser = argparse.ArgumentParser(description="Agent Team 상태 업데이트 도구")
    parser.add_argument("--status", "-s", help="업데이트할 상태", required=False)
    parser.add_argument("--details", "-d", help="상세 설명", required=False)
    parser.add_argument("--completed", "-c", help="완료된 작업 이름", required=False)
    parser.add_argument("--progress", "-p", help="진행 중인 작업 이름", required=False)
    parser.add_argument("--blocker", "-b", help="차단 요소 설명", required=False)
    parser.add_argument("--show", action="store_true", help="현재 상태 표시")

    args = parser.parse_args()

    # StatusManager 인스턴스 생성
    manager = StatusManager()

    if args.show:
        # 현재 상태 표시
        status = manager.get_current_status()
        print("📊 현재 상태 정보:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        return

    if args.completed:
        manager.mark_task_completed(args.completed)
    elif args.progress:
        manager.mark_task_in_progress(args.progress)
    elif args.blocker:
        manager.add_blocker(args.blocker)
    elif args.status:
        manager.update_status(args.status, args.details)
    else:
        # 인터랙티브 모드
        print("🚀 Agent Team 상태 업데이트 도구")
        print("현재 상태를 업데이트하세요:")

        status = input("상태: ")
        details = input("상세 설명 (선택사항): ")

        manager.update_status(status, details if details else None)


if __name__ == "__main__":
    main()