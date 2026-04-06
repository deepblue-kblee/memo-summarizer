#!/usr/bin/env python3
"""
Health Check System - Phase 3-A Observability
시스템 상태 모니터링, 자동 복구 메커니즘 및 알림 시스템
"""

import os
import subprocess
import importlib.util
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class HealthChecker:
    """시스템 헬스체크 클래스"""

    def __init__(self, app_dir: Optional[Path] = None):
        """
        Args:
            app_dir: app 디렉토리 경로 (기본값: 자동 탐지)
        """
        if app_dir is None:
            # app/src/memo_summarizer/core/ → app/
            app_dir = Path(__file__).parent.parent.parent.parent

        self.app_dir = Path(app_dir)
        self.venv_dir = self.app_dir / "venv"
        self.logs_dir = self.app_dir / "logs"
        self.config_dir = self.app_dir / "config"

        self.health_log = self.logs_dir / "health_check.log"
        self.logs_dir.mkdir(exist_ok=True)

    def check_system_status(self, quick: bool = False) -> Dict[str, Any]:
        """전체 시스템 상태 확인"""
        timestamp = datetime.now().isoformat()
        results = {
            "timestamp": timestamp,
            "status": "unknown",
            "checks": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "recommendations": []
        }

        # 기본 체크 항목들
        basic_checks = [
            ("virtual_environment", self._check_virtual_environment),
            ("package_installation", self._check_package_installation),
            ("console_scripts", self._check_console_scripts),
            ("directory_structure", self._check_directory_structure),
            ("config_files", self._check_config_files),
        ]

        # 빠른 체크가 아닌 경우 추가 체크
        if not quick:
            extended_checks = [
                ("api_connectivity", self._check_api_connectivity),
                ("disk_space", self._check_disk_space),
                ("log_rotation", self._check_log_rotation),
                ("structure_tests", self._check_structure_tests),
            ]
            basic_checks.extend(extended_checks)

        # 모든 체크 실행
        for check_name, check_function in basic_checks:
            try:
                check_result = check_function()
                results["checks"][check_name] = check_result

                results["summary"]["total"] += 1
                if check_result["status"] == "pass":
                    results["summary"]["passed"] += 1
                elif check_result["status"] == "warning":
                    results["summary"]["warnings"] += 1
                else:
                    results["summary"]["failed"] += 1

                # 실패한 체크에 대한 권장사항 추가
                if check_result["status"] == "fail" and "recommendation" in check_result:
                    results["recommendations"].append(check_result["recommendation"])

            except Exception as e:
                results["checks"][check_name] = {
                    "status": "error",
                    "message": f"체크 실행 중 오류: {e}",
                    "details": {}
                }
                results["summary"]["total"] += 1
                results["summary"]["failed"] += 1

        # 전체 상태 결정
        if results["summary"]["failed"] > 0:
            results["status"] = "unhealthy"
        elif results["summary"]["warnings"] > 0:
            results["status"] = "degraded"
        else:
            results["status"] = "healthy"

        # 로그 기록
        self._log_health_check(results)

        return results

    def _check_virtual_environment(self) -> Dict[str, Any]:
        """가상환경 상태 확인"""
        if not self.venv_dir.exists():
            return {
                "status": "fail",
                "message": "가상환경이 존재하지 않음",
                "recommendation": "./make_folders.sh를 실행하여 가상환경을 생성하세요"
            }

        # 가상환경 내 Python 실행 파일 확인
        python_exe = self.venv_dir / "bin" / "python"
        if not python_exe.exists():
            return {
                "status": "fail",
                "message": "가상환경 Python 실행파일을 찾을 수 없음",
                "recommendation": "가상환경을 재생성하세요: rm -rf app/venv && ./make_folders.sh"
            }

        return {
            "status": "pass",
            "message": "가상환경 정상",
            "details": {"venv_path": str(self.venv_dir)}
        }

    def _check_package_installation(self) -> Dict[str, Any]:
        """패키지 설치 상태 확인"""
        try:
            # memo_summarizer 패키지 import 시도
            spec = importlib.util.find_spec("memo_summarizer")
            if spec is None:
                return {
                    "status": "fail",
                    "message": "memo_summarizer 패키지가 설치되지 않음",
                    "recommendation": "패키지를 설치하세요: cd app && pip install -e ."
                }

            # 패키지 경로 확인
            package_path = spec.origin if spec.origin else "unknown"

            return {
                "status": "pass",
                "message": "패키지 설치 정상",
                "details": {"package_path": package_path}
            }

        except Exception as e:
            return {
                "status": "fail",
                "message": f"패키지 확인 중 오류: {e}",
                "recommendation": "패키지를 재설치하세요"
            }

    def _check_console_scripts(self) -> Dict[str, Any]:
        """Console Scripts 상태 확인"""
        scripts = [
            "memo-processor",
            "harness-linter",
            "memo-analyzer",
            "daily-reporter"
        ]

        script_status = {}
        failed_scripts = []

        for script in scripts:
            try:
                # which 명령어로 스크립트 위치 확인
                result = subprocess.run(
                    ["which", script],
                    capture_output=True,
                    text=True,
                    cwd=self.app_dir
                )

                if result.returncode == 0:
                    script_status[script] = {
                        "available": True,
                        "path": result.stdout.strip()
                    }
                else:
                    script_status[script] = {"available": False}
                    failed_scripts.append(script)

            except Exception as e:
                script_status[script] = {
                    "available": False,
                    "error": str(e)
                }
                failed_scripts.append(script)

        if failed_scripts:
            return {
                "status": "fail",
                "message": f"Console Scripts 누락: {', '.join(failed_scripts)}",
                "details": script_status,
                "recommendation": "패키지를 재설치하세요: cd app && pip install -e ."
            }

        return {
            "status": "pass",
            "message": "모든 Console Scripts 사용 가능",
            "details": script_status
        }

    def _check_directory_structure(self) -> Dict[str, Any]:
        """디렉토리 구조 확인"""
        required_dirs = [
            "src/memo_summarizer/cli",
            "src/memo_summarizer/services",
            "src/memo_summarizer/core",
            "src/memo_summarizer/utils",
            "src/memo_summarizer/types",
            "config",
            "logs",
            "tests"
        ]

        missing_dirs = []
        existing_dirs = {}

        for dir_path in required_dirs:
            full_path = self.app_dir / dir_path
            if full_path.exists():
                existing_dirs[dir_path] = str(full_path)
            else:
                missing_dirs.append(dir_path)

        if missing_dirs:
            return {
                "status": "warning",
                "message": f"일부 디렉토리 누락: {', '.join(missing_dirs)}",
                "details": {"existing": existing_dirs, "missing": missing_dirs},
                "recommendation": "./make_folders.sh를 실행하여 누락된 디렉토리를 생성하세요"
            }

        return {
            "status": "pass",
            "message": "디렉토리 구조 정상",
            "details": existing_dirs
        }

    def _check_config_files(self) -> Dict[str, Any]:
        """설정 파일 확인"""
        config_files = [
            ("setup.py", True),  # 필수
            (".env", False),      # 선택사항
            ("config/rules.json", False),  # 선택사항
        ]

        file_status = {}
        missing_required = []

        for file_path, required in config_files:
            full_path = self.app_dir / file_path
            exists = full_path.exists()

            file_status[file_path] = {
                "exists": exists,
                "required": required,
                "path": str(full_path) if exists else None
            }

            if required and not exists:
                missing_required.append(file_path)

        if missing_required:
            return {
                "status": "fail",
                "message": f"필수 설정 파일 누락: {', '.join(missing_required)}",
                "details": file_status,
                "recommendation": "누락된 설정 파일을 복원하거나 ./make_folders.sh를 실행하세요"
            }

        return {
            "status": "pass",
            "message": "설정 파일 상태 양호",
            "details": file_status
        }

    def _check_api_connectivity(self) -> Dict[str, Any]:
        """API 연결 상태 확인 (기본 테스트)"""
        # 실제 API 호출 대신 설정 확인으로 대체
        env_file = self.app_dir / ".env"

        if not env_file.exists():
            return {
                "status": "warning",
                "message": "환경 설정 파일(.env)이 없어 API 연결 테스트를 건너뜁니다",
                "recommendation": "app/.env 파일을 생성하고 API 키를 설정하세요"
            }

        try:
            with open(env_file, 'r') as f:
                content = f.read()

            has_claude_key = "CLAUDE_API_KEY" in content
            has_gemini_key = "GEMINI_API_KEY" in content

            return {
                "status": "pass" if (has_claude_key or has_gemini_key) else "warning",
                "message": "API 키 설정 확인됨" if (has_claude_key or has_gemini_key) else "API 키가 설정되지 않음",
                "details": {
                    "claude_configured": has_claude_key,
                    "gemini_configured": has_gemini_key
                }
            }

        except Exception as e:
            return {
                "status": "warning",
                "message": f"환경 설정 파일 읽기 실패: {e}"
            }

    def _check_disk_space(self) -> Dict[str, Any]:
        """디스크 공간 확인"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.app_dir)

            free_mb = free / (1024 * 1024)
            free_percent = (free / total) * 100

            # 1GB 미만이면 경고
            if free_mb < 1024:
                status = "warning"
                message = f"디스크 여유 공간 부족: {free_mb:.1f}MB"
            else:
                status = "pass"
                message = f"디스크 공간 충분: {free_mb:.1f}MB"

            return {
                "status": status,
                "message": message,
                "details": {
                    "total_mb": total / (1024 * 1024),
                    "used_mb": used / (1024 * 1024),
                    "free_mb": free_mb,
                    "free_percent": free_percent
                }
            }

        except Exception as e:
            return {
                "status": "warning",
                "message": f"디스크 공간 확인 실패: {e}"
            }

    def _check_log_rotation(self) -> Dict[str, Any]:
        """로그 로테이션 상태 확인"""
        if not self.logs_dir.exists():
            return {
                "status": "pass",
                "message": "로그 디렉토리가 없어 로테이션 불필요"
            }

        log_files = list(self.logs_dir.glob("*.log"))
        large_logs = []

        # 10MB 초과하는 로그 파일 확인
        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb > 10:
                large_logs.append({"file": log_file.name, "size_mb": size_mb})

        if large_logs:
            return {
                "status": "warning",
                "message": f"큰 로그 파일 발견: {len(large_logs)}개",
                "details": {"large_logs": large_logs},
                "recommendation": "로그 파일을 정리하거나 로그 로테이션을 설정하세요"
            }

        return {
            "status": "pass",
            "message": f"로그 상태 양호 ({len(log_files)}개 파일)",
            "details": {"log_files": [f.name for f in log_files]}
        }

    def _check_structure_tests(self) -> Dict[str, Any]:
        """구조적 테스트 실행"""
        test_file = self.app_dir / "tests" / "test_harness_structure.py"

        if not test_file.exists():
            return {
                "status": "warning",
                "message": "구조적 테스트 파일을 찾을 수 없음",
                "recommendation": "테스트 파일을 복원하세요"
            }

        try:
            # 구조적 테스트 실행
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.app_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "status": "pass",
                    "message": "구조적 테스트 통과",
                    "details": {"output": result.stdout}
                }
            else:
                return {
                    "status": "fail",
                    "message": "구조적 테스트 실패",
                    "details": {"error": result.stderr},
                    "recommendation": "구조적 문제를 수정하고 다시 테스트하세요"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "warning",
                "message": "구조적 테스트 시간 초과"
            }
        except Exception as e:
            return {
                "status": "warning",
                "message": f"구조적 테스트 실행 실패: {e}"
            }

    def auto_recovery_attempt(self, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """자동 복구 시도"""
        recovery_actions = []
        recovery_success = []
        recovery_failures = []

        # 실패한 체크에 대해 자동 복구 시도
        for check_name, check_result in health_status["checks"].items():
            if check_result["status"] in ["fail", "warning"]:
                recovery_action = self._attempt_recovery(check_name, check_result)
                if recovery_action:
                    recovery_actions.append(recovery_action)

                    if recovery_action["success"]:
                        recovery_success.append(recovery_action)
                    else:
                        recovery_failures.append(recovery_action)

        return {
            "attempted_recoveries": len(recovery_actions),
            "successful_recoveries": len(recovery_success),
            "failed_recoveries": len(recovery_failures),
            "actions": recovery_actions
        }

    def _attempt_recovery(self, check_name: str, check_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """특정 체크에 대한 복구 시도"""
        recovery_methods = {
            "directory_structure": self._recover_directory_structure,
            "config_files": self._recover_config_files,
        }

        if check_name in recovery_methods:
            try:
                success = recovery_methods[check_name](check_result)
                return {
                    "check_name": check_name,
                    "action": f"자동 복구 시도: {check_name}",
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "check_name": check_name,
                    "action": f"자동 복구 시도: {check_name}",
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

        return None

    def _recover_directory_structure(self, check_result: Dict[str, Any]) -> bool:
        """디렉토리 구조 복구"""
        missing_dirs = check_result.get("details", {}).get("missing", [])

        for dir_path in missing_dirs:
            full_path = self.app_dir / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                return False

        return True

    def _recover_config_files(self, check_result: Dict[str, Any]) -> bool:
        """기본 설정 파일 생성"""
        # 기본 .env 파일 생성
        env_file = self.app_dir / ".env"
        if not env_file.exists():
            try:
                sample_file = self.app_dir / "_env.sample"
                if sample_file.exists():
                    import shutil
                    shutil.copy(sample_file, env_file)
                    return True
            except Exception:
                pass

        return False

    def _log_health_check(self, results: Dict[str, Any]):
        """헬스체크 결과 로깅"""
        try:
            log_entry = {
                "timestamp": results["timestamp"],
                "status": results["status"],
                "summary": results["summary"],
                "failed_checks": [
                    name for name, result in results["checks"].items()
                    if result["status"] == "fail"
                ]
            }

            with open(self.health_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception:
            pass  # 로깅 실패해도 헬스체크는 계속 진행

    def send_alert_if_needed(self, health_status: Dict[str, Any]):
        """필요시 알림 발송 (현재는 콘솔 출력)"""
        if health_status["status"] == "unhealthy":
            print("🚨 시스템 상태 불량 알림!")
            print(f"실패한 체크: {health_status['summary']['failed']}개")

            if health_status["recommendations"]:
                print("권장 조치:")
                for rec in health_status["recommendations"]:
                    print(f"  - {rec}")


def main():
    """Console Script 진입점"""
    parser = argparse.ArgumentParser(description="System Health Checker")
    parser.add_argument("--quick", action="store_true", help="빠른 체크만 실행")
    parser.add_argument("--full-report", action="store_true", help="상세 보고서 출력")
    parser.add_argument("--auto-recover", action="store_true", help="자동 복구 시도")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")

    args = parser.parse_args()

    checker = HealthChecker()

    print("🏥 System Health Check" + (" (Quick)" if args.quick else ""))
    print("=" * 40)

    # 헬스체크 실행
    health_status = checker.check_system_status(quick=args.quick)

    if args.json:
        # JSON 형식 출력
        print(json.dumps(health_status, indent=2, ensure_ascii=False))
        return 0

    # 일반 형식 출력
    print(f"전체 상태: {'✅' if health_status['status'] == 'healthy' else '⚠️' if health_status['status'] == 'degraded' else '❌'} {health_status['status'].upper()}")
    print(f"체크 결과: {health_status['summary']['passed']}/{health_status['summary']['total']} 통과")

    if health_status['summary']['failed'] > 0:
        print(f"실패: {health_status['summary']['failed']}개")

    if health_status['summary']['warnings'] > 0:
        print(f"경고: {health_status['summary']['warnings']}개")

    # 상세 보고서 출력
    if args.full_report:
        print("\n📋 상세 체크 결과:")
        for check_name, result in health_status["checks"].items():
            status_icon = "✅" if result["status"] == "pass" else "⚠️" if result["status"] == "warning" else "❌"
            print(f"  {status_icon} {check_name}: {result['message']}")

    # 권장사항 출력
    if health_status["recommendations"]:
        print("\n💡 권장 조치:")
        for rec in health_status["recommendations"]:
            print(f"  - {rec}")

    # 자동 복구 시도
    if args.auto_recover and health_status["status"] != "healthy":
        print("\n🔧 자동 복구 시도...")
        recovery_result = checker.auto_recovery_attempt(health_status)
        print(f"복구 시도: {recovery_result['attempted_recoveries']}개")
        print(f"성공: {recovery_result['successful_recoveries']}개")

        if recovery_result['successful_recoveries'] > 0:
            print("일부 문제가 자동으로 해결되었습니다. 다시 헬스체크를 실행해보세요.")

    # 알림 발송
    checker.send_alert_if_needed(health_status)

    # 상태에 따른 종료 코드
    return 0 if health_status["status"] == "healthy" else 1


if __name__ == "__main__":
    exit(main())