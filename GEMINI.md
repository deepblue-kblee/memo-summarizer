# 🟡 Gemini 사용 가이드 - 메모 자동화 에이전트

> **📋 기본 시스템 참조**: 전체 시스템 아키텍처, PARA 분류 규칙, 공통 기능은 **[SYSTEM.md](SYSTEM.md)**를 참조하세요

## 🚀 Gemini 특화 개요

이 가이드는 메모 자동화 에이전트에서 Gemini의 특화된 기능과 최적화 방법을 다룹니다. Gemini는 빠른 처리 속도와 뛰어난 한국어 지원으로 대량 파일 처리에 적합합니다.

## ⚡ Gemini 장점

✅ **빠른 처리 속도**: 대량 파일 배치 처리에 최적화
✅ **한국어 특화**: 자연스러운 한국어 문맥 이해
✅ **비용 효율성**: 예산 내에서 더 많은 파일 처리 가능
✅ **안정적 대안**: Claude 장애 시 신뢰할 수 있는 백업
✅ **다국어 지원**: 한국어 외 다른 언어 메모 처리 가능

## 🛠️ Gemini 설치 및 설정

### 설치 및 인증
```bash
# Gemini CLI 설치 (예시 - 실제 설치 방법은 변경될 수 있음)
npm install -g @google-ai/generativelanguage

# 설치 확인
gemini --version

# 인증 설정 (최초 1회)
gemini auth login

# API 키 설정 (대안 방법)
export GEMINI_API_KEY="your-api-key"

# 설정 확인
gemini config show
```

### 내부 의존성 확인
```bash
# 시스템이 내부적으로 사용하는 AI CLI 확인
claude --version   # 시스템이 내부적으로 사용
gemini --version   # Gemini 추가 검증
```

## 🚀 Gemini 최적화 실행

### 기본 명령어
```bash
# Gemini로 전체 파이프라인 실행
./.agent/run /path/to/vault --ai gemini

# Gemini 분석 전용 (빠른 미리보기)
./.agent/run /path/to/vault --ai gemini --analysis-only

# Gemini 배치 모드 (대량 처리 최적화)
./.agent/run /path/to/vault --ai gemini --batch-mode

# 특정 날짜 Gemini 처리
./.agent/run /path/to/vault --ai gemini --date 2026-02-11
```

### Gemini 성능 최적화
```bash
# 빠른 배치 처리 (Gemini 특화)
./.agent/run /path/to/vault --ai gemini --fast-mode

# 비용 최적화 모드
./.agent/run /path/to/vault --ai gemini --cost-optimized

# 한국어 특화 처리
./.agent/run /path/to/vault --ai gemini --korean-enhanced
```

## 🔧 Gemini 특화 설정

### AI 설정 (Gemini용)
```json
{
  "default_provider": "gemini",
  "gemini": {
    "cli_command": "gemini",
    "temperature": 0.2,
    "max_tokens": 3000,
    "focus": "speed",
    "json_recovery": "aggressive",
    "batch_size": 10,
    "cost_optimization": true,
    "korean_mode": true
  }
}
```

### Gemini 프롬프트 최적화

Gemini는 간결하고 직관적인 프롬프트에서 최고 성능을 발휘합니다:

- **PARA 분류**: 빠른 키워드 매칭으로 효율적 분류
- **작업 추출**: 한국어 동작 동사의 자연스러운 이해 활용
- **JSON 안정성**: 추가 검증 로직으로 JSON 오류 최소화
- **배치 처리**: 여러 파일을 효율적으로 연속 처리

## 🌐 Gemini 한국어 특화 기능

### 한국어 마커 및 키워드
```json
{
  "korean_optimization": {
    "projects_markers": ["까지", "완료", "목표", "기한", "데드라인"],
    "areas_markers": ["관리", "운영", "정기", "루틴", "지속"],
    "action_verbs": ["하기", "확인", "조사", "요청", "문의"],
    "completion_indicators": ["완료됨", "처리됨", "해결됨"]
  }
}
```

### 한국어 문맥 이해
- **비즈니스 용어**: 한국 비즈니스 문화의 특수한 용어 이해
- **간접 표현**: 한국어의 우회적 표현 방식 처리
- **존댓말/반말**: 문체에 관계없이 일관된 작업 추출
- **축약형**: "할거임", "해야함" 같은 축약 표현 인식

## 📊 Gemini 비용 효율성

### 비용 추적
```bash
# Gemini API 비용 확인
grep "GEMINI_COST" .agent/logs/$(date +%Y-%m-%d).log

# 일일 처리량 대비 비용 효율성
grep "PROCESSED\|COST" .agent/logs/$(date +%Y-%m-%d).log
```

### 비용 최적화 전략
- 배치 처리로 API 호출 수 최소화
- 짧은 프롬프트로 토큰 사용량 절약
- 캐시 활용으로 중복 분석 방지
- 오프피크 시간대 대량 처리

## 🛡️ Gemini JSON 안정성 강화

### JSON 검증 및 복구
```python
# Gemini 특화 JSON 처리 (안정성 강화)
def parse_gemini_response(self, response_text: str) -> dict:
    try:
        # Stage 1: 기본 JSON 파싱
        return json.loads(response_text)
    except JSONDecodeError:
        # Stage 2: 정규식 추출 (Gemini 특화)
        json_pattern = r'\{.*?\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        # Stage 3: 적극적 복구 (aggressive recovery)
        cleaned = self._clean_gemini_json(response_text)
        return json.loads(cleaned)
```

### Gemini 응답 정제
- 불완전한 JSON 구조 자동 완성
- 한국어 문자열의 따옴표 오류 수정
- 중첩 구조의 누락된 괄호 복구
- 인코딩 오류 자동 처리

## 🚨 Gemini 특화 문제 해결

### 일반적인 문제 및 해결책

#### 인증 관련 문제
```bash
# ❌ gemini: command not found
# → Gemini CLI 설치 확인 및 재설치

# ❌ API 키 인증 실패
# → API 키 재설정: export GEMINI_API_KEY="new-key"

# ❌ 할당량 초과
# → 사용량 확인 및 배치 크기 조정
```

#### Gemini API 관련 문제
```bash
# ❌ JSON 파싱 오류 (Gemini 특성상 가끔 발생)
# → 적극적 복구 모드 활성화: --json-recovery aggressive

# ❌ 응답 속도 저하
# → 배치 크기 줄이기: --batch-size 5

# ❌ 한국어 인식 오류
# → 한국어 모드 활성화: --korean-enhanced
```

#### PARA 분류 특화 문제
```bash
# ❌ 빠른 처리로 인한 분류 정확도 저하
# → 정확도 모드: --ai gemini --accuracy-mode

# ❌ 한국어 키워드 놓침
# → rules.json의 한국어 키워드 확장
# → 문맥 단서 추가: "이것은 프로젝트입니다" 같은 명시적 표현 사용
```

## ⚡ Gemini 워크플로우 패턴

### Gemini 특화 작업 흐름
1. **대량 처리**: 많은 파일을 빠르게 배치로 처리
2. **실시간 분석**: 실시간으로 들어오는 메모 즉시 처리
3. **비용 최적화**: 제한된 예산으로 최대한 많은 파일 처리
4. **한국어 집중**: 한국어 메모의 뉘앙스까지 정확히 파악

### Gemini 추천 사용 사례
```bash
# 대량 백로그 처리
./.agent/run /path/to/vault --ai gemini --batch-mode --date-range 2026-01-01:2026-02-28

# 실시간 처리 (새 메모 감지시)
./.agent/run /path/to/vault --ai gemini --watch-mode

# 비용 제한 환경
./.agent/run /path/to/vault --ai gemini --budget-mode --max-cost 10
```

### Gemini와 Claude 협업
- Claude 실패시 Gemini 자동 백업
- 복잡한 분석은 Claude, 빠른 처리는 Gemini
- 비용 대비 성능 최적화로 두 AI 혼합 사용

## 🔗 공통 시스템과의 연동

Gemini는 공통 시스템 구성요소와 완벽하게 통합됩니다:

- **파일 작업**: 표준 file_manager.py와 Gemini 특화 오류 처리
- **PARA 분류**: 공통 rules.json 적용 + Gemini 한국어 강화
- **로깅 시스템**: 공통 로깅 + Gemini 특화 성능 메트릭
- **경로 관리**: 공통 vault 경로 패턴 + Gemini 최적화

---

> 📚 **추가 자료**:
> - **시스템 아키텍처**: [SYSTEM.md](SYSTEM.md) - 전체 시스템 개요
> - **AI 비교**: [AI_QUICK_START.md](AI_QUICK_START.md) - Claude vs Gemini 선택 가이드
> - **개발자 상세**: [DEVELOPER.md](DEVELOPER.md) - 구현 세부사항
> - **모듈 구조**: [ARCHITECTURE.md](ARCHITECTURE.md) - 모듈 아키텍처

> 💡 **Gemini 모범 사례**:
> - 대량 파일 처리나 비용 최적화가 필요할 때 Gemini 사용
> - JSON 안정성을 위해 적극적 복구 모드 활용
> - 한국어 특화 기능으로 자연스러운 언어 처리 활용
> - Claude와 협업하여 각각의 장점 최대한 활용