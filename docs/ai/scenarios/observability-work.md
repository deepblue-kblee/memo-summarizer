# 🔍 Phase 3-A Observability 작업 가이드

## 🎯 목표: 90/100 → 95/100 (고도화된 관찰 가능성)

### 📋 구현할 관찰 가능성 시스템

#### 1. Performance Monitor 구축
```python
# app/src/memo_summarizer/core/observability.py
class PerformanceMonitor:
    def track_execution_time(self, func_name: str)
    def track_memory_usage(self)
    def track_api_calls(self, service: str, endpoint: str)
    def generate_metrics_report(self)
```

#### 2. Health Check System
```python
# app/src/memo_summarizer/core/health_check.py
class HealthChecker:
    def check_system_status(self) -> Dict[str, str]
    def check_service_availability(self) -> bool
    def auto_recovery_attempt(self)
    def send_alert_if_needed(self)
```

#### 3. 중앙화된 로깅
```python
# app/src/memo_summarizer/utils/logger.py
class CentralizedLogger:
    def setup_structured_logging(self)
    def log_performance_metrics(self, metrics: Dict)
    def log_error_with_context(self, error: Exception)
    def auto_rotate_logs(self)
```

## 🚀 구현 순서

### Phase 1: 기본 관찰 가능성 (1-2시간)
1. **Performance Monitor 기초**
   - 실행 시간 추적 데코레이터
   - 메모리 사용량 모니터링
   - 기본 메트릭 수집

2. **로깅 시스템 통합**
   - `app/logs/` 구조화
   - 에러 추적 개선
   - 로그 레벨 설정

### Phase 2: 헬스체크 시스템 (2-3시간)
1. **시스템 상태 모니터**
   - Console Scripts 상태 확인
   - 패키지 의존성 검증
   - 설정 파일 무결성 확인

2. **자동 복구 메커니즘**
   - 일반적 문제 자동 해결
   - 알림 시스템 기초

### Phase 3: 고도화 (1시간)
1. **Console Scripts 추가**
   - `observability-monitor` 명령어
   - `health-check` 명령어
   - `log-analyzer` 명령어

2. **자동화 통합**
   - Pre-commit hook 연동
   - CI/CD 파이프라인 추가

## 🔧 기존 시스템 활용

### 현재 구조 기반
```
app/src/memo_summarizer/
├── cli/               # 기존 진입점들
├── services/          # AI 클라이언트들
├── core/              # ⭐ observability.py, health_check.py 추가
├── utils/             # ⭐ logger.py 확장
└── types/             # 메트릭 타입 정의 추가
```

### Console Scripts 확장
```python
# app/setup.py에 추가
entry_points = {
    "console_scripts": [
        # 기존
        "memo-processor=memo_summarizer.cli.main_controller:main",
        "harness-linter=memo_summarizer.cli.harness_linter:main",
        "memo-analyzer=memo_summarizer.cli.memo_analyzer:main",
        "daily-reporter=memo_summarizer.cli.daily_reporter:main",

        # ⭐ Phase 3-A 추가
        "observability-monitor=memo_summarizer.core.observability:main",
        "health-check=memo_summarizer.core.health_check:main",
        "log-analyzer=memo_summarizer.utils.logger:analyze_logs",
    ],
}
```

## 📊 메트릭 수집 전략

### 성능 메트릭
- **실행 시간**: 각 주요 함수별
- **메모리 사용량**: 처리 전후 비교
- **API 호출**: Claude/Gemini 호출 횟수 및 응답 시간
- **파일 처리**: 처리된 메모 수, 크기, 소요 시간

### 시스템 메트릭
- **디스크 사용량**: `app/logs/`, `vault/` 크기
- **프로세스 상태**: CPU, 메모리 사용률
- **에러 발생률**: 시간대별 에러 추이

## 🏥 헬스체크 전략

### 자동 검증 항목
1. **패키지 상태**
   ```python
   import memo_summarizer
   # Console Scripts 실행 가능 여부
   ```

2. **설정 파일**
   ```python
   # app/.env 존재 및 유효성
   # app/config/ 구성 확인
   ```

3. **서비스 연결**
   ```python
   # Claude API 연결 테스트
   # Gemini API 연결 테스트
   ```

4. **디렉토리 구조**
   ```python
   # vault/ 경로 접근 가능성
   # app/logs/ 쓰기 권한
   ```

## 🔗 자동화 통합

### Pre-commit Hook 확장
```bash
# .git/hooks/pre-commit에 추가
echo "Running health check..."
health-check --quick

echo "Checking observability metrics..."
observability-monitor --validate
```

### CI/CD 파이프라인 추가
```yaml
# .github/workflows/observability.yml
name: Observability Check
on: pull_request
jobs:
  health_check:
    - name: System Health Check
      run: health-check --full-report

  performance_test:
    - name: Performance Metrics
      run: observability-monitor --benchmark
```

## 📈 예상 성과

| 메트릭 | 현재 | Phase 3-A 완료 후 |
|--------|------|-------------------|
| **모니터링** | 수동 확인 | 자동 실시간 |
| **에러 추적** | 기본 로그 | 구조화된 추적 |
| **성능 분석** | 없음 | 상세 메트릭 |
| **자동 복구** | 없음 | 기본 복구 |
| **전체 진행률** | 90/100 | 95/100 |

## 🔍 구현 체크리스트

### ✅ 사전 조건 확인
- [x] app/ 단일 구조 완성
- [x] Console Scripts 작동
- [x] 가상환경 및 패키지 설치
- [x] docs/ 구조 완성

### 🎯 구현 단계
- [ ] `observability.py` 기본 구현
- [ ] `health_check.py` 기본 구현
- [ ] `logger.py` 확장
- [ ] Console Scripts 추가
- [ ] 자동화 통합 (Pre-commit, CI/CD)
- [ ] 문서 업데이트

### ⚡ 테스트 및 검증
- [ ] 성능 모니터링 동작 확인
- [ ] 헬스체크 명령어 테스트
- [ ] 로그 구조화 확인
- [ ] 전체 시스템 통합 테스트

## 💡 구현 팁

### 기존 코드 활용
- `app/src/memo_summarizer/cli/memo_analyzer.py`의 로깅 패턴 참조
- `app/src/memo_summarizer/services/`의 API 호출 패턴 확장
- 기존 테스트 구조 (`app/tests/`) 활용

### HarnessEngineering 원칙
- **자동화 우선**: 수동 개입 최소화
- **단일 진입점**: Console Scripts 통해서만 접근
- **관찰 가능성**: 모든 작업 추적 및 메트릭화
- **자가 복구**: 일반적 문제 자동 해결

---

**🎯 목표**: 이 가이드 완료 후 memo-summarizer는 95/100 진행률 달성