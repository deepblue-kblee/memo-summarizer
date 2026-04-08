#!/usr/bin/env python3
"""
Scheduler System - Phase 3-B Garbage Collection
정기적 헬스체크 및 유지보수 작업 스케줄링
"""

import time
import threading
import argparse
import atexit
import signal
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import json

from .health_check import HealthChecker
from ..utils.logger import CentralizedLogger
from ..utils.garbage_collector import GarbageCollector


class TaskScheduler:
    """정기적 작업 스케줄러"""

    def __init__(self, app_dir: Optional[Path] = None):
        """
        Args:
            app_dir: app 디렉토리 경로 (기본값: 자동 탐지)
        """
        if app_dir is None:
            # app/src/memo_summarizer/core/ → app/
            app_dir = Path(__file__).parent.parent.parent.parent

        self.app_dir = Path(app_dir)
        self.logger = CentralizedLogger("scheduler")

        # 스케줄러 상태
        self.running = False
        self.thread = None
        self.schedule = []

        # 컴포넌트들
        self.health_checker = HealthChecker(app_dir)
        self.garbage_collector = GarbageCollector(app_dir)

        # 스케줄 파일
        self.schedule_file = self.app_dir / "config" / "schedule.json"

        # 기본 스케줄 정의
        self.default_schedule = [
            {
                "name": "daily_health_check",
                "description": "일일 헬스체크",
                "function": self._run_health_check,
                "interval_minutes": 1440,  # 24시간
                "enabled": True,
                "last_run": None
            },
            {
                "name": "weekly_garbage_collection",
                "description": "주간 가비지 컬렉션",
                "function": self._run_garbage_collection,
                "interval_minutes": 10080,  # 7일
                "enabled": True,
                "last_run": None
            },
            {
                "name": "hourly_log_rotation",
                "description": "시간별 로그 로테이션 체크",
                "function": self._run_log_rotation_check,
                "interval_minutes": 60,  # 1시간
                "enabled": True,
                "last_run": None
            }
        ]

        self._load_schedule()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """시그널 핸들러 설정"""
        def signal_handler(signum, frame):
            self.logger.logger.info(f"Signal {signum} received, shutting down scheduler...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 프로그램 종료 시 자동 정리
        atexit.register(self.stop)

    def _load_schedule(self):
        """스케줄 설정 로드"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    loaded_schedule = json.load(f)

                # 기본 스케줄과 병합 (기능 함수는 다시 연결)
                function_mapping = {
                    "daily_health_check": self._run_health_check,
                    "weekly_garbage_collection": self._run_garbage_collection,
                    "hourly_log_rotation": self._run_log_rotation_check
                }

                for item in loaded_schedule:
                    if item["name"] in function_mapping:
                        item["function"] = function_mapping[item["name"]]

                self.schedule = loaded_schedule
                self.logger.logger.info(f"Loaded schedule from {self.schedule_file}")

            else:
                # 기본 스케줄 사용
                self.schedule = self.default_schedule.copy()
                self._save_schedule()
                self.logger.logger.info("Created default schedule")

        except Exception as e:
            self.logger.logger.error(f"Failed to load schedule: {e}")
            self.schedule = self.default_schedule.copy()

    def _save_schedule(self):
        """스케줄 설정 저장"""
        try:
            # config 디렉토리 생성
            self.schedule_file.parent.mkdir(exist_ok=True)

            # function 제외하고 저장 (JSON 직렬화 불가)
            saveable_schedule = []
            for item in self.schedule:
                save_item = {k: v for k, v in item.items() if k != "function"}
                saveable_schedule.append(save_item)

            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(saveable_schedule, f, indent=2, ensure_ascii=False)

            self.logger.logger.info(f"Saved schedule to {self.schedule_file}")

        except Exception as e:
            self.logger.logger.error(f"Failed to save schedule: {e}")

    def start(self, daemon: bool = True):
        """스케줄러 시작"""
        if self.running:
            self.logger.logger.warning("Scheduler is already running")
            return

        self.running = True

        # 스케줄러 스레드 시작
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=daemon)
        self.thread.start()

        self.logger.logger.info("Task scheduler started")

    def stop(self):
        """스케줄러 정지"""
        if not self.running:
            return

        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        self._save_schedule()
        self.logger.logger.info("Task scheduler stopped")

    def _scheduler_loop(self):
        """스케줄러 메인 루프"""
        self.logger.logger.info("Scheduler loop started")

        while self.running:
            try:
                current_time = datetime.now()

                for task in self.schedule:
                    if not task.get("enabled", True):
                        continue

                    # 마지막 실행 시간 확인
                    last_run = task.get("last_run")
                    if last_run:
                        last_run_time = datetime.fromisoformat(last_run)
                        time_since_last = (current_time - last_run_time).total_seconds() / 60

                        if time_since_last < task["interval_minutes"]:
                            continue

                    # 작업 실행
                    self.logger.logger.info(f"Running scheduled task: {task['name']}")

                    try:
                        with self.logger.log_operation(f"scheduled_task_{task['name']}"):
                            result = task["function"]()

                        task["last_run"] = current_time.isoformat()
                        task["last_result"] = "success"

                        self.logger.logger.info(
                            f"Scheduled task completed: {task['name']} - {result.get('status', 'completed')}"
                        )

                    except Exception as e:
                        task["last_result"] = f"error: {str(e)}"
                        self.logger.logger.error(f"Scheduled task failed: {task['name']} - {e}")

                # 1분마다 체크
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.logger.logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def _run_health_check(self) -> Dict[str, Any]:
        """정기 헬스체크 실행"""
        health_status = self.health_checker.check_system_status(quick=False)

        # 상태가 나쁘면 자동 복구 시도
        if health_status["status"] != "healthy":
            recovery_result = self.health_checker.auto_recovery_attempt(health_status)
            health_status["recovery"] = recovery_result

        return health_status

    def _run_garbage_collection(self) -> Dict[str, Any]:
        """정기 가비지 컬렉션 실행"""
        # 전체 정리 실행 (pip 캐시 제외)
        result = self.garbage_collector.full_cleanup(
            dry_run=False,
            include_pip_cache=False
        )

        return {
            "status": "completed",
            "space_freed_mb": result["summary"]["total_space_freed_mb"],
            "operations": len(result["operations"])
        }

    def _run_log_rotation_check(self) -> Dict[str, Any]:
        """정기 로그 로테이션 체크"""
        from ..utils.logger import rotate_logs

        try:
            rotation_result = rotate_logs(max_age_days=7, max_size_mb=50)
            return {
                "status": "completed",
                "files_rotated": rotation_result["total_processed"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def add_task(self, name: str, description: str, function: Callable,
                 interval_minutes: int, enabled: bool = True) -> bool:
        """새 작업 추가"""
        try:
            # 중복 확인
            for task in self.schedule:
                if task["name"] == name:
                    self.logger.logger.warning(f"Task {name} already exists")
                    return False

            new_task = {
                "name": name,
                "description": description,
                "function": function,
                "interval_minutes": interval_minutes,
                "enabled": enabled,
                "last_run": None
            }

            self.schedule.append(new_task)
            self._save_schedule()

            self.logger.logger.info(f"Added new task: {name}")
            return True

        except Exception as e:
            self.logger.logger.error(f"Failed to add task {name}: {e}")
            return False

    def remove_task(self, name: str) -> bool:
        """작업 제거"""
        try:
            original_length = len(self.schedule)
            self.schedule = [task for task in self.schedule if task["name"] != name]

            if len(self.schedule) < original_length:
                self._save_schedule()
                self.logger.logger.info(f"Removed task: {name}")
                return True
            else:
                self.logger.logger.warning(f"Task not found: {name}")
                return False

        except Exception as e:
            self.logger.logger.error(f"Failed to remove task {name}: {e}")
            return False

    def toggle_task(self, name: str, enabled: Optional[bool] = None) -> bool:
        """작업 활성화/비활성화 토글"""
        try:
            for task in self.schedule:
                if task["name"] == name:
                    if enabled is not None:
                        task["enabled"] = enabled
                    else:
                        task["enabled"] = not task.get("enabled", True)

                    self._save_schedule()
                    status = "enabled" if task["enabled"] else "disabled"
                    self.logger.logger.info(f"Task {name} {status}")
                    return True

            self.logger.logger.warning(f"Task not found: {name}")
            return False

        except Exception as e:
            self.logger.logger.error(f"Failed to toggle task {name}: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """스케줄러 상태 조회"""
        return {
            "running": self.running,
            "total_tasks": len(self.schedule),
            "enabled_tasks": len([t for t in self.schedule if t.get("enabled", True)]),
            "schedule": [
                {
                    "name": task["name"],
                    "description": task["description"],
                    "interval_minutes": task["interval_minutes"],
                    "enabled": task.get("enabled", True),
                    "last_run": task.get("last_run"),
                    "last_result": task.get("last_result", "not_run")
                }
                for task in self.schedule
            ]
        }

    def run_task_now(self, name: str) -> Dict[str, Any]:
        """특정 작업 즉시 실행"""
        try:
            for task in self.schedule:
                if task["name"] == name:
                    self.logger.logger.info(f"Running task immediately: {name}")

                    start_time = datetime.now()
                    result = task["function"]()
                    duration = (datetime.now() - start_time).total_seconds()

                    task["last_run"] = start_time.isoformat()
                    task["last_result"] = "manual_run_success"
                    self._save_schedule()

                    return {
                        "status": "completed",
                        "duration_seconds": duration,
                        "result": result
                    }

            return {
                "status": "error",
                "error": f"Task not found: {name}"
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def run_scheduler_daemon():
    """스케줄러 데몬 실행"""
    scheduler = TaskScheduler()

    print("🕐 Task Scheduler Starting...")
    print("Press Ctrl+C to stop")

    try:
        scheduler.start(daemon=False)

        # 메인 스레드에서 대기
        while scheduler.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutdown signal received")
    finally:
        scheduler.stop()
        print("📋 Task Scheduler stopped")


def main():
    """Console Script 진입점"""
    parser = argparse.ArgumentParser(description="Task Scheduler - 정기 작업 스케줄러")
    parser.add_argument("--start", action="store_true", help="스케줄러 시작 (데몬 모드)")
    parser.add_argument("--status", action="store_true", help="스케줄러 상태 조회")
    parser.add_argument("--list", action="store_true", help="등록된 작업 목록")
    parser.add_argument("--run", type=str, metavar="TASK_NAME", help="특정 작업 즉시 실행")
    parser.add_argument("--enable", type=str, metavar="TASK_NAME", help="작업 활성화")
    parser.add_argument("--disable", type=str, metavar="TASK_NAME", help="작업 비활성화")

    args = parser.parse_args()

    scheduler = TaskScheduler()

    if args.start:
        # 데몬 모드로 스케줄러 실행
        run_scheduler_daemon()

    elif args.status or args.list:
        # 상태 조회
        print("📋 Task Scheduler Status")
        print("=" * 40)

        status = scheduler.get_status()
        print(f"스케줄러 상태: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
        print(f"등록된 작업: {status['total_tasks']}개")
        print(f"활성화된 작업: {status['enabled_tasks']}개")

        if args.list:
            print("\n📋 작업 목록:")
            for task in status["schedule"]:
                status_icon = "✅" if task["enabled"] else "❌"
                last_run = task["last_run"]
                if last_run:
                    last_run_time = datetime.fromisoformat(last_run)
                    time_ago = datetime.now() - last_run_time
                    last_run_str = f"{time_ago.days}일 {time_ago.seconds//3600}시간 전"
                else:
                    last_run_str = "실행된 적 없음"

                print(f"  {status_icon} {task['name']}")
                print(f"      설명: {task['description']}")
                print(f"      주기: {task['interval_minutes']}분")
                print(f"      마지막 실행: {last_run_str}")
                print()

    elif args.run:
        # 특정 작업 실행
        print(f"🚀 Running task: {args.run}")
        result = scheduler.run_task_now(args.run)

        if result["status"] == "completed":
            print(f"✅ Task completed in {result['duration_seconds']:.2f}s")
            if "result" in result:
                print(f"Result: {result['result']}")
        else:
            print(f"❌ Task failed: {result['error']}")

    elif args.enable:
        # 작업 활성화
        if scheduler.toggle_task(args.enable, enabled=True):
            print(f"✅ Task enabled: {args.enable}")
        else:
            print(f"❌ Failed to enable task: {args.enable}")

    elif args.disable:
        # 작업 비활성화
        if scheduler.toggle_task(args.disable, enabled=False):
            print(f"✅ Task disabled: {args.disable}")
        else:
            print(f"❌ Failed to disable task: {args.disable}")

    else:
        print("🕐 Task Scheduler")
        print("사용법:")
        print("  --start       스케줄러 시작 (데몬 모드)")
        print("  --status      스케줄러 상태 조회")
        print("  --list        등록된 작업 목록")
        print("  --run TASK    특정 작업 즉시 실행")
        print("  --enable TASK 작업 활성화")
        print("  --disable TASK작업 비활성화")
        print("")
        print("예시:")
        print("  task-scheduler --start")
        print("  task-scheduler --list")
        print("  task-scheduler --run daily_health_check")

    return 0


if __name__ == "__main__":
    exit(main())