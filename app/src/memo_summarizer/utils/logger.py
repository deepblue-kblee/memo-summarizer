#!/usr/bin/env python3
"""
중앙화된 로깅 시스템 - Phase 3-A Observability
구조화된 로깅, 에러 추적, 성능 분석 및 자동 로그 로테이션
"""

import logging
import logging.handlers
import json
import argparse
import traceback
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager


class CentralizedLogger:
    """중앙화된 로거 클래스"""

    def __init__(self, name: str = "memo_summarizer", log_dir: Optional[Path] = None):
        """
        Args:
            name: 로거 이름
            log_dir: 로그 디렉토리 (기본값: app/logs/)
        """
        self.name = name

        if log_dir is None:
            # app/src/memo_summarizer/utils/ → app/logs/
            log_dir = Path(__file__).parent.parent.parent.parent / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 로그 파일들
        self.main_log = self.log_dir / "memo_summarizer.log"
        self.error_log = self.log_dir / "errors.log"
        self.performance_log = self.log_dir / "performance.log"
        self.api_log = self.log_dir / "api_calls.log"

        # 로거 설정
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """로거 초기 설정"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # 기존 핸들러 제거 (중복 방지)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 파일 핸들러들 설정
        file_handlers = [
            (self.main_log, logging.INFO),
            (self.error_log, logging.ERROR),
        ]

        for log_file, level in file_handlers:
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def setup_structured_logging(self, module_name: str) -> logging.Logger:
        """모듈별 구조화된 로거 설정"""
        module_logger = logging.getLogger(f"{self.name}.{module_name}")
        module_logger.setLevel(logging.DEBUG)

        # JSON 포맷터 (구조화된 로그용)
        json_formatter = JsonFormatter()

        # 모듈별 로그 파일
        module_log_file = self.log_dir / f"{module_name}.log"
        handler = logging.handlers.RotatingFileHandler(
            module_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        handler.setFormatter(json_formatter)
        module_logger.addHandler(handler)

        return module_logger

    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """성능 메트릭 로깅"""
        performance_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "performance",
            **metrics
        }

        with open(self.performance_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(performance_entry, ensure_ascii=False) + "\n")

    def log_error_with_context(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """컨텍스트와 함께 에러 로깅"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }

        # 구조화된 에러 로그
        with open(self.error_log.with_suffix('.json'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_info, ensure_ascii=False) + "\n")

        # 일반 로거에도 기록
        self.logger.error(f"{type(error).__name__}: {error}", exc_info=True)

    def log_api_call(self, service: str, endpoint: str, method: str,
                    response_time: float, status_code: Optional[int] = None,
                    request_size: Optional[int] = None,
                    response_size: Optional[int] = None,
                    error: Optional[str] = None):
        """API 호출 로깅"""
        api_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "status_code": status_code,
            "request_size": request_size,
            "response_size": response_size,
            "success": error is None,
            "error": error
        }

        with open(self.api_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(api_entry, ensure_ascii=False) + "\n")

    @contextmanager
    def log_operation(self, operation_name: str, **context):
        """작업 실행 로깅 컨텍스트"""
        start_time = datetime.now()
        operation_id = f"{operation_name}_{start_time.timestamp()}"

        self.logger.info(f"Starting operation: {operation_name}", extra={
            "operation_id": operation_id,
            "operation": operation_name,
            "context": context
        })

        try:
            yield operation_id
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Completed operation: {operation_name} ({duration:.2f}s)", extra={
                "operation_id": operation_id,
                "operation": operation_name,
                "duration": duration,
                "status": "success"
            })

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.error(f"Failed operation: {operation_name} ({duration:.2f}s)", extra={
                "operation_id": operation_id,
                "operation": operation_name,
                "duration": duration,
                "status": "error",
                "error": str(e)
            })

            self.log_error_with_context(e, {
                "operation": operation_name,
                "operation_id": operation_id,
                **context
            })

            raise

    def auto_rotate_logs(self, max_age_days: int = 30, max_size_mb: int = 100):
        """자동 로그 로테이션"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        rotated_files = []
        compressed_files = []

        for log_file in self.log_dir.glob("*.log"):
            try:
                # 파일 크기 확인
                size_mb = log_file.stat().st_size / (1024 * 1024)

                if size_mb > max_size_mb:
                    # 큰 파일 압축
                    compressed_file = self._compress_log_file(log_file)
                    if compressed_file:
                        compressed_files.append(compressed_file)

                # 오래된 파일 확인
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    rotated_files.append(str(log_file))

            except Exception as e:
                self.logger.warning(f"로그 로테이션 중 오류: {log_file}: {e}")

        # 오래된 압축 파일 삭제
        for gz_file in self.log_dir.glob("*.log.gz"):
            try:
                file_time = datetime.fromtimestamp(gz_file.stat().st_mtime)
                if file_time < cutoff_date:
                    gz_file.unlink()
                    rotated_files.append(str(gz_file))
            except Exception:
                pass

        return {
            "rotated_files": rotated_files,
            "compressed_files": compressed_files,
            "total_processed": len(rotated_files) + len(compressed_files)
        }

    def _compress_log_file(self, log_file: Path) -> Optional[Path]:
        """로그 파일 압축"""
        try:
            compressed_file = log_file.with_suffix(log_file.suffix + '.gz')

            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)

            # 원본 파일 삭제
            log_file.unlink()

            return compressed_file

        except Exception as e:
            self.logger.warning(f"로그 압축 실패: {log_file}: {e}")
            return None

    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """로그 요약 정보"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        summary = {
            "period_hours": hours,
            "cutoff_time": cutoff_time.isoformat(),
            "log_files": {},
            "error_count": 0,
            "warning_count": 0,
            "api_calls": 0,
            "performance_entries": 0
        }

        # 각 로그 파일 분석
        for log_file in self.log_dir.glob("*.log"):
            file_stats = self._analyze_log_file(log_file, cutoff_time)
            summary["log_files"][log_file.name] = file_stats

            # 집계
            summary["error_count"] += file_stats.get("error_count", 0)
            summary["warning_count"] += file_stats.get("warning_count", 0)

        # JSON 로그 파일 분석
        api_log_json = self.api_log
        if api_log_json.exists():
            summary["api_calls"] = self._count_recent_entries(api_log_json, cutoff_time)

        performance_log_json = self.performance_log
        if performance_log_json.exists():
            summary["performance_entries"] = self._count_recent_entries(performance_log_json, cutoff_time)

        return summary

    def _analyze_log_file(self, log_file: Path, cutoff_time: datetime) -> Dict[str, Any]:
        """개별 로그 파일 분석"""
        stats = {
            "size_mb": 0,
            "line_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "recent_entries": 0
        }

        try:
            stats["size_mb"] = log_file.stat().st_size / (1024 * 1024)

            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stats["line_count"] += 1

                    # 시간 기반 필터링 (간단한 구현)
                    if cutoff_time.strftime("%Y-%m-%d") in line:
                        stats["recent_entries"] += 1

                    if "ERROR" in line:
                        stats["error_count"] += 1
                    elif "WARNING" in line:
                        stats["warning_count"] += 1

        except Exception:
            pass

        return stats

    def _count_recent_entries(self, json_log_file: Path, cutoff_time: datetime) -> int:
        """JSON 로그 파일의 최근 엔트리 개수"""
        count = 0
        try:
            with open(json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time > cutoff_time:
                            count += 1
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception:
            pass

        return count


class JsonFormatter(logging.Formatter):
    """JSON 형식 로그 포맷터"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }

        # 추가 필드가 있으면 포함
        if hasattr(record, 'operation_id'):
            log_entry['operation_id'] = record.operation_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'context'):
            log_entry['context'] = record.context

        # 예외 정보
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def analyze_logs(log_dir: Optional[Path] = None, hours: int = 24) -> Dict[str, Any]:
    """로그 분석 함수"""
    logger = CentralizedLogger(log_dir=log_dir)
    return logger.get_log_summary(hours=hours)


def rotate_logs(log_dir: Optional[Path] = None, max_age_days: int = 30, max_size_mb: int = 100) -> Dict[str, Any]:
    """로그 로테이션 함수"""
    logger = CentralizedLogger(log_dir=log_dir)
    return logger.auto_rotate_logs(max_age_days, max_size_mb)


def main():
    """Console Script 진입점"""
    parser = argparse.ArgumentParser(description="Log Analyzer and Manager")
    parser.add_argument("--analyze", action="store_true", help="로그 분석")
    parser.add_argument("--rotate", action="store_true", help="로그 로테이션")
    parser.add_argument("--summary", action="store_true", help="로그 요약")
    parser.add_argument("--hours", type=int, default=24, help="분석할 시간 범위 (시간)")
    parser.add_argument("--max-age", type=int, default=30, help="로그 보관 기간 (일)")
    parser.add_argument("--max-size", type=int, default=100, help="로그 파일 최대 크기 (MB)")

    args = parser.parse_args()

    if args.analyze or args.summary:
        # 로그 분석
        print(f"📊 Log Analysis (최근 {args.hours}시간)")
        print("=" * 40)

        analysis = analyze_logs(hours=args.hours)

        print(f"분석 기간: {analysis['cutoff_time']} ~ 현재")
        print(f"에러: {analysis['error_count']}개")
        print(f"경고: {analysis['warning_count']}개")
        print(f"API 호출: {analysis['api_calls']}개")
        print(f"성능 엔트리: {analysis['performance_entries']}개")

        if args.analyze:
            print("\n📁 로그 파일별 상세:")
            for filename, stats in analysis["log_files"].items():
                print(f"  {filename}:")
                print(f"    크기: {stats['size_mb']:.1f}MB")
                print(f"    라인 수: {stats['line_count']:,}")
                print(f"    최근 엔트리: {stats['recent_entries']}")

    elif args.rotate:
        # 로그 로테이션
        print("🔄 Log Rotation")
        print("=" * 40)

        result = rotate_logs(max_age_days=args.max_age, max_size_mb=args.max_size)

        print(f"처리된 파일: {result['total_processed']}개")
        print(f"로테이션된 파일: {len(result['rotated_files'])}개")
        print(f"압축된 파일: {len(result['compressed_files'])}개")

        if result['rotated_files']:
            print("\n로테이션된 파일들:")
            for f in result['rotated_files']:
                print(f"  - {f}")

        if result['compressed_files']:
            print("\n압축된 파일들:")
            for f in result['compressed_files']:
                print(f"  - {f}")

    else:
        print("📋 log-analyzer")
        print("사용법:")
        print("  --analyze     로그 분석 (상세)")
        print("  --summary     로그 요약")
        print("  --rotate      로그 로테이션")
        print("  --hours N     분석할 시간 범위")
        print("  --max-age N   보관 기간 (일)")
        print("  --max-size N  최대 파일 크기 (MB)")

    return 0


if __name__ == "__main__":
    exit(main())