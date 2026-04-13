#!/usr/bin/env python3
"""
Agent Team 할 일 목록 조회 스크립트

현재 진행 중인 작업과 대기 중인 작업을 조회하고 관리하는 도구입니다.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import re


class TaskReader:
    """할 일 목록 조회 클래스"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent.parent
        self.tracking_path = self.base_path / "tracking"
        self.task_board_file = self.tracking_path / "task_board.md"
        self.current_status_file = self.tracking_path / "current_status.md"
        self.roadmap_file = self.base_path / "planning" / "roadmap.md"

    def read_tasks_from_status(self) -> Dict[str, List[str]]:
        """현재 상태 파일에서 작업 목록 추출"""
        if not self.current_status_file.exists():
            return {"error": ["Status file not found"]}

        content = self.current_status_file.read_text(encoding='utf-8')
        tasks = {
            "completed": [],
            "in_progress": [],
            "pending": [],
            "blocked": []
        }

        # 체크박스 패턴으로 작업 추출
        completed_pattern = r'- \[x\] (.+)'
        progress_pattern = r'- 🔄 (.+)'
        pending_pattern = r'- \[ \] (.+)'

        for line in content.split('\n'):
            line = line.strip()

            if re.match(completed_pattern, line):
                task = re.match(completed_pattern, line).group(1)
                tasks["completed"].append(task)
            elif '🔄' in line:
                task = line.replace('🔄', '').replace('-', '').strip()
                tasks["in_progress"].append(task)
            elif re.match(pending_pattern, line):
                task = re.match(pending_pattern, line).group(1)
                tasks["pending"].append(task)

        return tasks

    def read_roadmap_tasks(self) -> Dict[str, Any]:
        """로드맵에서 전체 계획 정보 추출"""
        if not self.roadmap_file.exists():
            return {"error": "Roadmap file not found"}

        content = self.roadmap_file.read_text(encoding='utf-8')

        # Phase별 정보 추출
        phases = {}
        current_phase = None

        for line in content.split('\n'):
            line = line.strip()

            # Phase 제목 찾기
            if line.startswith('## Phase'):
                phase_match = re.match(r'## (Phase \d+: .+)', line)
                if phase_match:
                    current_phase = phase_match.group(1)
                    phases[current_phase] = {
                        "tasks": [],
                        "status": "planned"
                    }

            # 작업 항목 찾기
            elif current_phase and (line.startswith('- [x]') or line.startswith('- [ ]')):
                task_match = re.match(r'- \[(.)\] (.+)', line)
                if task_match:
                    status = "completed" if task_match.group(1) == 'x' else "pending"
                    task_text = task_match.group(2)
                    phases[current_phase]["tasks"].append({
                        "text": task_text,
                        "status": status
                    })

        return phases

    def get_next_priority_tasks(self, limit: int = 5) -> List[Dict[str, str]]:
        """다음 우선순위 작업 목록 반환"""
        tasks = self.read_tasks_from_status()
        roadmap = self.read_roadmap_tasks()

        priority_tasks = []

        # 현재 진행 중인 작업
        for task in tasks.get("in_progress", []):
            priority_tasks.append({
                "task": task,
                "priority": "high",
                "status": "in_progress",
                "type": "current"
            })

        # 대기 중인 작업
        for task in tasks.get("pending", []):
            priority_tasks.append({
                "task": task,
                "priority": "medium",
                "status": "pending",
                "type": "next"
            })

        return priority_tasks[:limit]

    def get_completion_stats(self) -> Dict[str, Any]:
        """완료 통계 정보 반환"""
        tasks = self.read_tasks_from_status()

        total_tasks = sum(len(task_list) for task_list in tasks.values() if task_list != "error")
        completed_tasks = len(tasks.get("completed", []))

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": len(tasks.get("in_progress", [])),
            "pending_tasks": len(tasks.get("pending", [])),
            "completion_rate": round(completion_rate, 2)
        }

    def display_task_summary(self):
        """작업 요약 정보 출력"""
        print("📋 Agent Team 할 일 목록 요약\n")

        # 완료 통계
        stats = self.get_completion_stats()
        print(f"📊 전체 진행률: {stats['completion_rate']}%")
        print(f"   - 완료: {stats['completed_tasks']}개")
        print(f"   - 진행중: {stats['in_progress_tasks']}개")
        print(f"   - 대기: {stats['pending_tasks']}개")
        print(f"   - 총계: {stats['total_tasks']}개\n")

        # 다음 우선순위 작업
        priority_tasks = self.get_next_priority_tasks()
        print("🎯 다음 우선순위 작업:")
        for i, task in enumerate(priority_tasks, 1):
            status_icon = "🔄" if task["status"] == "in_progress" else "⏳"
            print(f"   {i}. {status_icon} {task['task']}")

        print()

    def display_detailed_tasks(self):
        """상세 작업 목록 출력"""
        tasks = self.read_tasks_from_status()

        print("📝 상세 작업 목록\n")

        if tasks.get("in_progress"):
            print("🔄 진행 중인 작업:")
            for task in tasks["in_progress"]:
                print(f"   • {task}")
            print()

        if tasks.get("pending"):
            print("⏳ 대기 중인 작업:")
            for task in tasks["pending"]:
                print(f"   • {task}")
            print()

        if tasks.get("completed"):
            print("✅ 완료된 작업:")
            for task in tasks["completed"][-5:]:  # 최근 5개만
                print(f"   • {task}")
            print()

    def display_roadmap_progress(self):
        """로드맵 진행 상황 출력"""
        roadmap = self.read_roadmap_tasks()

        if "error" in roadmap:
            print(f"❌ 로드맵 파일 오류: {roadmap['error']}")
            return

        print("🗺️ 로드맵 진행 상황\n")

        for phase_name, phase_info in roadmap.items():
            total_tasks = len(phase_info["tasks"])
            completed_tasks = sum(1 for task in phase_info["tasks"] if task["status"] == "completed")

            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            print(f"📍 {phase_name}")
            print(f"   진행률: {progress:.1f}% ({completed_tasks}/{total_tasks})")

            # 최근 작업 몇 개 표시
            for task in phase_info["tasks"][:3]:
                status_icon = "✅" if task["status"] == "completed" else "⏳"
                print(f"   {status_icon} {task['text']}")

            print()


def main():
    parser = argparse.ArgumentParser(description="Agent Team 할 일 목록 조회 도구")
    parser.add_argument("--summary", "-s", action="store_true", help="작업 요약 표시")
    parser.add_argument("--detailed", "-d", action="store_true", help="상세 작업 목록 표시")
    parser.add_argument("--roadmap", "-r", action="store_true", help="로드맵 진행 상황 표시")
    parser.add_argument("--next", "-n", type=int, default=5, help="다음 우선순위 작업 개수")

    args = parser.parse_args()

    reader = TaskReader()

    if args.roadmap:
        reader.display_roadmap_progress()
    elif args.detailed:
        reader.display_detailed_tasks()
    elif args.summary or not any([args.detailed, args.roadmap]):
        reader.display_task_summary()

    # 다음 작업 표시 (항상 표시)
    if not args.roadmap:
        priority_tasks = reader.get_next_priority_tasks(args.next)
        if priority_tasks:
            print(f"⚡ 우선순위 상위 {len(priority_tasks)}개 작업:")
            for i, task in enumerate(priority_tasks, 1):
                status_icon = "🔄" if task["status"] == "in_progress" else "⏳"
                priority_icon = "🔥" if task["priority"] == "high" else "📍"
                print(f"   {i}. {priority_icon} {status_icon} {task['task']}")


if __name__ == "__main__":
    main()