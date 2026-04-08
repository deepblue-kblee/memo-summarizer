#!/usr/bin/env python3
"""
Garbage Collection 시스템 - Phase 3-B
시스템 완성을 위한 통합 정리 및 자동화 기능
"""

import shutil
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from .logger import CentralizedLogger


class GarbageCollector:
    """통합 Garbage Collection 시스템"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Args:
            project_root: 프로젝트 루트 디렉토리 (기본값: app/)
        """
        if project_root is None:
            # app/src/memo_summarizer/utils/ → app/
            project_root = Path(__file__).parent.parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = CentralizedLogger()

        # 주요 디렉토리들
        self.app_dir = self.project_root
        self.logs_dir = self.app_dir / "logs"
        self.venv_dir = self.app_dir / "venv"
        self.build_dir = self.app_dir / "build"
        self.src_dir = self.app_dir / "src"

    def clean_pycache(self, dry_run: bool = False) -> Dict[str, Any]:
        """Python 컴파일 캐시 정리"""
        result = {
            "pycache_dirs_removed": 0,
            "pyc_files_removed": 0,
            "space_freed_mb": 0,
            "removed_paths": []
        }

        with self.logger.log_operation("clean_pycache", dry_run=dry_run):
            # 1. __pycache__ 디렉토리 찾기
            pycache_dirs = []

            # 소스 디렉토리에서 찾기
            if self.src_dir.exists():
                pycache_dirs.extend(self.src_dir.rglob("__pycache__"))

            # venv에서는 제외 (너무 많고 자주 재생성됨)

            for pycache_dir in pycache_dirs:
                try:
                    # 크기 계산
                    size_mb = self._get_directory_size(pycache_dir) / (1024 * 1024)
                    result["space_freed_mb"] += size_mb

                    if not dry_run:
                        shutil.rmtree(pycache_dir)

                    result["pycache_dirs_removed"] += 1
                    result["removed_paths"].append(str(pycache_dir))

                    self.logger.logger.info(f"Removed __pycache__: {pycache_dir} ({size_mb:.1f}MB)")

                except Exception as e:
                    self.logger.logger.warning(f"Failed to remove {pycache_dir}: {e}")

            # 2. 개별 .pyc 파일 찾기 (소스 트리에서)
            if self.src_dir.exists():
                pyc_files = list(self.src_dir.rglob("*.pyc"))
                for pyc_file in pyc_files:
                    try:
                        size_mb = pyc_file.stat().st_size / (1024 * 1024)
                        result["space_freed_mb"] += size_mb

                        if not dry_run:
                            pyc_file.unlink()

                        result["pyc_files_removed"] += 1
                        result["removed_paths"].append(str(pyc_file))

                    except Exception as e:
                        self.logger.logger.warning(f"Failed to remove {pyc_file}: {e}")

        return result

    def clean_build_artifacts(self, dry_run: bool = False) -> Dict[str, Any]:
        """빌드 산출물 정리"""
        result = {
            "directories_removed": 0,
            "files_removed": 0,
            "space_freed_mb": 0,
            "removed_paths": []
        }

        with self.logger.log_operation("clean_build_artifacts", dry_run=dry_run):
            # 빌드 디렉토리들
            build_patterns = [
                self.build_dir,
                self.src_dir / "*.egg-info" if self.src_dir.exists() else None,
                self.app_dir / "dist"
            ]

            for pattern_or_path in build_patterns:
                if pattern_or_path is None:
                    continue

                if isinstance(pattern_or_path, Path) and "*" not in str(pattern_or_path):
                    # 직접 경로
                    paths = [pattern_or_path] if pattern_or_path.exists() else []
                else:
                    # 패턴
                    paths = list(self.app_dir.glob(str(pattern_or_path.relative_to(self.app_dir))))

                for path in paths:
                    try:
                        if path.is_dir():
                            size_mb = self._get_directory_size(path) / (1024 * 1024)
                            result["space_freed_mb"] += size_mb

                            if not dry_run:
                                shutil.rmtree(path)

                            result["directories_removed"] += 1
                            result["removed_paths"].append(str(path))

                            self.logger.logger.info(f"Removed build directory: {path} ({size_mb:.1f}MB)")

                        elif path.is_file():
                            size_mb = path.stat().st_size / (1024 * 1024)
                            result["space_freed_mb"] += size_mb

                            if not dry_run:
                                path.unlink()

                            result["files_removed"] += 1
                            result["removed_paths"].append(str(path))

                    except Exception as e:
                        self.logger.logger.warning(f"Failed to remove {path}: {e}")

        return result

    def clean_temporary_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """임시 파일들 정리"""
        result = {
            "temp_files_removed": 0,
            "space_freed_mb": 0,
            "removed_paths": []
        }

        with self.logger.log_operation("clean_temporary_files", dry_run=dry_run):
            # 임시 파일 패턴들
            temp_patterns = [
                "*.tmp",
                "*.temp",
                "*~",
                "*.swp",
                ".DS_Store",
                "Thumbs.db"
            ]

            for pattern in temp_patterns:
                temp_files = list(self.app_dir.rglob(pattern))

                for temp_file in temp_files:
                    try:
                        # venv 디렉토리는 제외
                        if self.venv_dir in temp_file.parents:
                            continue

                        size_mb = temp_file.stat().st_size / (1024 * 1024)
                        result["space_freed_mb"] += size_mb

                        if not dry_run:
                            temp_file.unlink()

                        result["temp_files_removed"] += 1
                        result["removed_paths"].append(str(temp_file))

                        self.logger.logger.info(f"Removed temp file: {temp_file}")

                    except Exception as e:
                        self.logger.logger.warning(f"Failed to remove {temp_file}: {e}")

        return result

    def run_pip_cache_clean(self, dry_run: bool = False) -> Dict[str, Any]:
        """pip 캐시 정리"""
        result = {
            "success": False,
            "cache_cleared_mb": 0,
            "error": None
        }

        if dry_run:
            result["success"] = True
            result["cache_cleared_mb"] = 0  # dry-run에서는 실제 크기 모름
            return result

        with self.logger.log_operation("pip_cache_clean", dry_run=dry_run):
            try:
                # pip cache 크기 확인 (선택사항)
                try:
                    cache_info = subprocess.run(
                        ["pip", "cache", "info"],
                        capture_output=True, text=True, timeout=30
                    )
                    if cache_info.returncode == 0:
                        # 대략적인 크기 추정 (정확하지 않을 수 있음)
                        for line in cache_info.stdout.split('\n'):
                            if 'MB' in line or 'GB' in line:
                                # 간단한 추정
                                result["cache_cleared_mb"] = 50  # 평균 추정치
                                break
                except:
                    pass

                # pip 캐시 정리 실행
                clean_result = subprocess.run(
                    ["pip", "cache", "purge"],
                    capture_output=True, text=True, timeout=60
                )

                if clean_result.returncode == 0:
                    result["success"] = True
                    self.logger.logger.info("pip cache cleared successfully")
                else:
                    result["error"] = clean_result.stderr
                    self.logger.logger.warning(f"pip cache clean failed: {clean_result.stderr}")

            except subprocess.TimeoutExpired:
                result["error"] = "pip cache clean timeout"
                self.logger.logger.warning("pip cache clean timed out")
            except Exception as e:
                result["error"] = str(e)
                self.logger.logger.warning(f"pip cache clean error: {e}")

        return result

    def full_cleanup(self, dry_run: bool = False, include_pip_cache: bool = False) -> Dict[str, Any]:
        """전체 정리 실행"""
        start_time = datetime.now()

        with self.logger.log_operation("full_cleanup", dry_run=dry_run, include_pip_cache=include_pip_cache):
            results = {
                "start_time": start_time.isoformat(),
                "dry_run": dry_run,
                "operations": {}
            }

            # 1. Python 캐시 정리
            results["operations"]["pycache_cleanup"] = self.clean_pycache(dry_run)

            # 2. 빌드 산출물 정리
            results["operations"]["build_cleanup"] = self.clean_build_artifacts(dry_run)

            # 3. 임시 파일 정리
            results["operations"]["temp_cleanup"] = self.clean_temporary_files(dry_run)

            # 4. pip 캐시 정리 (선택사항)
            if include_pip_cache:
                results["operations"]["pip_cache_cleanup"] = self.run_pip_cache_clean(dry_run)

            # 5. 로그 로테이션 (기존 기능 활용)
            try:
                from .logger import rotate_logs
                results["operations"]["log_rotation"] = rotate_logs()
            except Exception as e:
                self.logger.logger.warning(f"Log rotation failed: {e}")
                results["operations"]["log_rotation"] = {"error": str(e)}

            # 전체 요약
            total_space_freed = sum(
                op.get("space_freed_mb", 0)
                for op in results["operations"].values()
                if isinstance(op, dict)
            )

            results["summary"] = {
                "total_space_freed_mb": total_space_freed,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "end_time": datetime.now().isoformat()
            }

        return results

    def _get_directory_size(self, directory: Path) -> int:
        """디렉토리 크기 계산 (바이트)"""
        total_size = 0
        try:
            for path in directory.rglob('*'):
                if path.is_file():
                    try:
                        total_size += path.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size

    def get_cleanup_report(self) -> Dict[str, Any]:
        """정리 가능한 항목들 분석 (dry-run)"""
        return self.full_cleanup(dry_run=True, include_pip_cache=True)


def main():
    """Console Script 진입점"""
    parser = argparse.ArgumentParser(description="Garbage Collector - 시스템 정리 도구")
    parser.add_argument("--clean", action="store_true", help="전체 정리 실행")
    parser.add_argument("--pycache", action="store_true", help="Python 캐시만 정리")
    parser.add_argument("--build", action="store_true", help="빌드 산출물만 정리")
    parser.add_argument("--temp", action="store_true", help="임시 파일만 정리")
    parser.add_argument("--pip-cache", action="store_true", help="pip 캐시 정리 포함")
    parser.add_argument("--report", action="store_true", help="정리 가능한 항목 보고서")
    parser.add_argument("--dry-run", action="store_true", help="실제 삭제하지 않고 시뮬레이션")

    args = parser.parse_args()

    gc = GarbageCollector()

    if args.report:
        # 정리 가능한 항목 보고서
        print("🧹 Garbage Collection Report")
        print("=" * 40)

        report = gc.get_cleanup_report()

        print(f"분석 시간: {report['summary']['duration_seconds']:.2f}초")
        print(f"정리 가능한 총 용량: {report['summary']['total_space_freed_mb']:.1f}MB")
        print()

        for operation, result in report["operations"].items():
            if isinstance(result, dict) and "space_freed_mb" in result:
                print(f"📁 {operation}:")
                print(f"  정리 가능 용량: {result['space_freed_mb']:.1f}MB")
                if "removed_paths" in result and result["removed_paths"]:
                    print(f"  대상 파일/디렉토리: {len(result['removed_paths'])}개")
                print()

    elif args.clean:
        # 전체 정리
        print("🧹 Full System Cleanup")
        if args.dry_run:
            print("(DRY RUN - 실제 삭제하지 않음)")
        print("=" * 40)

        result = gc.full_cleanup(dry_run=args.dry_run, include_pip_cache=args.pip_cache)

        print(f"정리 완료: {result['summary']['total_space_freed_mb']:.1f}MB")
        print(f"소요 시간: {result['summary']['duration_seconds']:.2f}초")

        for operation, op_result in result["operations"].items():
            if isinstance(op_result, dict) and "space_freed_mb" in op_result:
                print(f"  {operation}: {op_result['space_freed_mb']:.1f}MB")

    elif args.pycache:
        # Python 캐시만
        print("🐍 Python Cache Cleanup")
        if args.dry_run:
            print("(DRY RUN)")
        print("=" * 40)

        result = gc.clean_pycache(dry_run=args.dry_run)
        print(f"정리된 __pycache__ 디렉토리: {result['pycache_dirs_removed']}개")
        print(f"정리된 .pyc 파일: {result['pyc_files_removed']}개")
        print(f"확보된 용량: {result['space_freed_mb']:.1f}MB")

    elif args.build:
        # 빌드 산출물만
        print("🔨 Build Artifacts Cleanup")
        if args.dry_run:
            print("(DRY RUN)")
        print("=" * 40)

        result = gc.clean_build_artifacts(dry_run=args.dry_run)
        print(f"정리된 디렉토리: {result['directories_removed']}개")
        print(f"정리된 파일: {result['files_removed']}개")
        print(f"확보된 용량: {result['space_freed_mb']:.1f}MB")

    elif args.temp:
        # 임시 파일만
        print("📄 Temporary Files Cleanup")
        if args.dry_run:
            print("(DRY RUN)")
        print("=" * 40)

        result = gc.clean_temporary_files(dry_run=args.dry_run)
        print(f"정리된 임시 파일: {result['temp_files_removed']}개")
        print(f"확보된 용량: {result['space_freed_mb']:.1f}MB")

    else:
        print("🧹 Garbage Collector")
        print("사용법:")
        print("  --report      정리 가능한 항목 보고서")
        print("  --clean       전체 정리 실행")
        print("  --pycache     Python 캐시 정리")
        print("  --build       빌드 산출물 정리")
        print("  --temp        임시 파일 정리")
        print("  --pip-cache   pip 캐시도 정리 (--clean과 함께)")
        print("  --dry-run     실제 삭제하지 않고 시뮬레이션")
        print("")
        print("예시:")
        print("  garbage-collector --report")
        print("  garbage-collector --clean --dry-run")
        print("  garbage-collector --clean --pip-cache")

    return 0


if __name__ == "__main__":
    exit(main())