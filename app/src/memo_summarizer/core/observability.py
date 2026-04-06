#!/usr/bin/env python3
"""
Performance Monitor - Phase 3-A Observability
실행 시간, 메모리 사용량, API 호출 메트릭을 수집하고 분석합니다.
"""

import time
import psutil
import functools
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager


class PerformanceMonitor:
    """성능 모니터링 클래스"""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Args:
            log_dir: 로그 디렉토리 (기본값: app/logs/)
        """
        if log_dir is None:
            # app/src/memo_summarizer/core/ → app/logs/
            log_dir = Path(__file__).parent.parent.parent.parent / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.metrics_file = self.log_dir / "performance_metrics.json"
        self.session_start = datetime.now()
        self.session_metrics = {
            "session_id": self.session_start.isoformat(),
            "start_time": self.session_start.isoformat(),
            "function_calls": [],
            "api_calls": [],
            "memory_snapshots": []
        }

        print(f"📊 Performance Monitor 초기화됨: {self.log_dir}")

    def track_execution_time(self, func_name: Optional[str] = None):
        """함수 실행 시간 추적 데코레이터"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                start_memory = self._get_memory_usage()

                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = self._get_memory_usage()

                    metric = {
                        "function_name": name,
                        "timestamp": datetime.now().isoformat(),
                        "execution_time": end_time - start_time,
                        "memory_before": start_memory,
                        "memory_after": end_memory,
                        "memory_diff": end_memory - start_memory,
                        "success": success,
                        "error": error
                    }

                    self.session_metrics["function_calls"].append(metric)

                return result
            return wrapper
        return decorator

    def track_memory_usage(self, label: str = "snapshot"):
        """현재 메모리 사용량 기록"""
        memory_info = {
            "timestamp": datetime.now().isoformat(),
            "label": label,
            "memory_mb": self._get_memory_usage(),
            "cpu_percent": psutil.cpu_percent(),
            "available_memory_mb": psutil.virtual_memory().available / 1024 / 1024
        }

        self.session_metrics["memory_snapshots"].append(memory_info)
        return memory_info

    def track_api_call(self, service: str, endpoint: str,
                      response_time: float, success: bool,
                      request_size: Optional[int] = None,
                      response_size: Optional[int] = None):
        """API 호출 메트릭 기록"""
        api_metric = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "endpoint": endpoint,
            "response_time": response_time,
            "success": success,
            "request_size": request_size,
            "response_size": response_size
        }

        self.session_metrics["api_calls"].append(api_metric)

    @contextmanager
    def measure_block(self, block_name: str):
        """코드 블록의 성능 측정"""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()

            metric = {
                "block_name": block_name,
                "timestamp": datetime.now().isoformat(),
                "execution_time": end_time - start_time,
                "memory_before": start_memory,
                "memory_after": end_memory,
                "memory_diff": end_memory - start_memory
            }

            self.session_metrics["function_calls"].append(metric)

    def generate_metrics_report(self) -> Dict[str, Any]:
        """성능 메트릭 보고서 생성"""
        self.session_metrics["end_time"] = datetime.now().isoformat()

        # 세션 요약 계산
        function_calls = self.session_metrics["function_calls"]
        api_calls = self.session_metrics["api_calls"]

        summary = {
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "total_function_calls": len(function_calls),
            "total_api_calls": len(api_calls),
            "average_execution_time": self._calculate_average([f["execution_time"] for f in function_calls]),
            "total_memory_usage": sum(f["memory_diff"] for f in function_calls if f["memory_diff"] > 0),
            "api_success_rate": self._calculate_success_rate(api_calls),
            "slowest_functions": self._get_slowest_functions(function_calls, top_n=5)
        }

        self.session_metrics["summary"] = summary

        # 파일에 저장
        self._save_metrics()

        return self.session_metrics

    def _get_memory_usage(self) -> float:
        """현재 프로세스의 메모리 사용량 (MB)"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def _calculate_average(self, values: List[float]) -> float:
        """평균값 계산"""
        return sum(values) / len(values) if values else 0.0

    def _calculate_success_rate(self, api_calls: List[Dict]) -> float:
        """API 성공률 계산"""
        if not api_calls:
            return 100.0

        successes = sum(1 for call in api_calls if call["success"])
        return (successes / len(api_calls)) * 100

    def _get_slowest_functions(self, function_calls: List[Dict], top_n: int = 5) -> List[Dict]:
        """가장 느린 함수들 반환"""
        sorted_calls = sorted(function_calls, key=lambda x: x["execution_time"], reverse=True)
        return sorted_calls[:top_n]

    def _save_metrics(self):
        """메트릭을 파일에 저장"""
        try:
            # 기존 데이터 로드
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    all_metrics = json.load(f)
            else:
                all_metrics = {"sessions": []}

            # 현재 세션 추가
            all_metrics["sessions"].append(self.session_metrics)

            # 최신 10개 세션만 유지 (파일 크기 관리)
            all_metrics["sessions"] = all_metrics["sessions"][-10:]

            # 파일에 저장
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ 메트릭 저장 실패: {e}")


def analyze_performance_logs(log_dir: Optional[Path] = None) -> Dict[str, Any]:
    """성능 로그 분석"""
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent.parent / "logs"

    metrics_file = Path(log_dir) / "performance_metrics.json"

    if not metrics_file.exists():
        return {"error": "성능 메트릭 파일이 없습니다."}

    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            all_metrics = json.load(f)

        sessions = all_metrics.get("sessions", [])
        if not sessions:
            return {"error": "세션 데이터가 없습니다."}

        # 전체 통계 계산
        total_functions = sum(len(s["function_calls"]) for s in sessions)
        total_api_calls = sum(len(s["api_calls"]) for s in sessions)

        all_execution_times = []
        for session in sessions:
            all_execution_times.extend([f["execution_time"] for f in session["function_calls"]])

        analysis = {
            "total_sessions": len(sessions),
            "total_function_calls": total_functions,
            "total_api_calls": total_api_calls,
            "average_execution_time": sum(all_execution_times) / len(all_execution_times) if all_execution_times else 0,
            "max_execution_time": max(all_execution_times) if all_execution_times else 0,
            "latest_session": sessions[-1]["summary"] if sessions else None
        }

        return analysis

    except Exception as e:
        return {"error": f"분석 실패: {e}"}


def main():
    """Console Script 진입점"""
    parser = argparse.ArgumentParser(description="Performance Monitor")
    parser.add_argument("--analyze", action="store_true", help="성능 로그 분석")
    parser.add_argument("--report", action="store_true", help="성능 보고서 생성")
    parser.add_argument("--benchmark", action="store_true", help="기본 벤치마크 실행")

    args = parser.parse_args()

    if args.analyze:
        # 성능 로그 분석
        analysis = analyze_performance_logs()
        print("📊 Performance Analysis Report")
        print("=" * 40)
        for key, value in analysis.items():
            print(f"{key}: {value}")

    elif args.benchmark:
        # 기본 벤치마크
        monitor = PerformanceMonitor()

        print("🔬 Running benchmark...")

        @monitor.track_execution_time("benchmark_test")
        def benchmark_function():
            """벤치마크용 테스트 함수"""
            import time
            time.sleep(0.1)  # 100ms 대기
            return sum(range(1000))  # 간단한 계산

        # 여러 번 실행
        for i in range(5):
            monitor.track_memory_usage(f"benchmark_iteration_{i}")
            result = benchmark_function()

        # 가짜 API 호출 시뮬레이션
        monitor.track_api_call("claude", "/v1/messages", 0.5, True, 1000, 2000)
        monitor.track_api_call("gemini", "/v1/generateContent", 0.3, True, 800, 1500)

        # 보고서 생성
        report = monitor.generate_metrics_report()

        print("\n📋 Benchmark Results:")
        print(f"Session Duration: {report['summary']['session_duration']:.2f}s")
        print(f"Total Function Calls: {report['summary']['total_function_calls']}")
        print(f"Average Execution Time: {report['summary']['average_execution_time']:.4f}s")
        print(f"API Success Rate: {report['summary']['api_success_rate']:.1f}%")

    else:
        print("📊 observability-monitor")
        print("사용법:")
        print("  --analyze    성능 로그 분석")
        print("  --benchmark  벤치마크 실행")
        print("  --report     성능 보고서 생성")

    return 0


if __name__ == "__main__":
    exit(main())