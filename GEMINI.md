# GEMINI.md

이 파일은 이 저장소에서 작업할 때 Gemini CLI에 대한 지침을 제공합니다.

## 시스템 개요

이 시스템은 **Obsidian Memo 자동화 에이전트**입니다. `00_INBOX/`의 구조화되지 않은 메모를 분석하고 이를 구조화된 의제(Agenda) 파일로 지능적으로 정리하는 AI 기반 노트 처리 파이프라인입니다. 시스템은 내부적으로 `claude` CLI를 통해 Claude AI를 사용하여 단일 메모에서 여러 주제를 추출하고, PARA 방법론에 기반한 자동 분류(Projects vs Areas)를 수행하며, 향상된 로깅 및 오류 복구 기능을 갖춘 프로젝트 파일을 유지 관리합니다.

**새로운 기능: 전체 시스템 재설계** - 시스템은 `.agent/` 패키지 격리, 지능형 디렉토리 구성 및 경로 매개변수화된 실행으로 완전히 구조화되었습니다.

## 명령 (Commands)

### `.agent` 패키지 실행 (현재 시스템)
```bash
# 전체 파이프라인: 메모 분석 + Projects/Areas 분류 + 아카이브
./.agent/run /path/to/vault

# 분석 전용 (읽기 전용, 파일 수정 없음)
./.agent/run /path/to/vault --analysis-only

# 특정 날짜만 처리 (YYYY-MM-DD 형식)
./.agent/run /path/to/vault --date 2026-02-11

# JSON 출력 형식 (Projects/Areas 분류 포함)
./.agent/run /path/to/vault --json

# 옵션 조합
./.agent/run /path/to/vault --date 2026-02-11 --analysis-only --json

# 도움말 정보
./.agent/run --help

# 현재 디렉토리를 보관소(vault)로 사용하는 예시
./.agent/run $(pwd) --analysis-only
```

### 레거시 실행 (권장되지 않음)
```bash
python agent.py --analysis-only
./run_agent.sh --analysis-only
```

### 시스템 설정
```bash
# 필수 디렉토리 생성
mkdir -p 00_INBOX 01_AGENDAS

# 가상 환경 활성화
source venv/bin/activate

# 내부 의존성 확인 (시스템은 내부적으로 claude CLI를 사용함)
claude --version
gemini --version

# 실행 권한 설정
chmod +x run_agent.sh start_memo_processor.sh
```

### 개발 및 디버깅
```bash
# 분석 로그 확인 (향상된 로깅이 포함된 일일 파일)
cat logs/memo_analyzer_$(date +%Y-%m-%d).log

# 실시간 API 응답 디버깅 (터미널 출력)
python agent.py --analysis-only

# 디렉토리 구조 및 파일 수 확인
ls -la 00_INBOX/ 01_AGENDAS/ 00_INBOX/_ARCHIVED/
find 01_AGENDAS/ -name "*.md" | wc -l

# 디버깅을 위한 특정 날짜 처리
python agent.py --date 2026-02-11 --analysis-only
```

## 아키텍처 개요

### `.agent` 패키지 아키텍처 (격리된 시스템)
시스템은 에이전트 패키지 격리 및 PARA 방법론을 사용하여 완전히 재구조화되었습니다.

**디렉토리 구조:**
```
Vault_Root/
├── 00_INBOX/              # 📥 입력: 원본 메모 파일
│   └── _ARCHIVED/         # 🗂️ 처리된 파일 (자동 관리)
├── 01_AGENDAS/            # 📋 출력: PARA로 분류된 의제 파일
│   ├── Projects/          # 🎯 마감일이 있는 목표 지향적 프로젝트
│   └── Areas/             # 🏢 지속적인 책임 영역
├── 02_DAILY_REPORTS/      # 📊 일일 요약 보고서
│
└── .agent/                # 🤖 에이전트 패키지 (Obsidian과 격리)
    ├── bin/               # 🛠️ 모듈형 Python 스크립트
    │   ├── main_controller.py     # 메인 오케스트레이터
    │   ├── claude_client.py       # AI API 연동 (claude CLI 사용)
    │   ├── file_manager.py        # 경로 매개변수를 사용한 파일 I/O
    │   ├── memo_analyzer.py       # AI 분석 + Projects/Areas 분류
    │   ├── markdown_processor.py  # 마크다운 처리
    │   └── daily_reporter.py      # 일일 보고서
    ├── config/            # ⚙️ 설정 파일
    │   └── rules.json     # 분류 키워드 및 작업 추출 규칙
    ├── venv/              # 🐍 격리된 Python 환경
    ├── logs/              # 📋 일일 활동 로그
    └── run                # 🚀 진입점 스크립트
```

## 핵심 로직 및 규칙

### 1. 외부 설정 (`.agent/config/rules.json`)
시스템은 외부 구성 파일에서 분류 키워드 및 작업 추출 규칙을 로드하여 하드코딩된 로직을 피합니다.

* **Projects 키워드**: `~까지`, `기한`, `데드라인`, `출시`, `완료`, `개발`, `셋업`, `구축`, `배포`, `런칭`, `(P)`
* **Areas 키워드**: `정기`, `관리`, `운영`, `매달`, `지속`, `루틴`, `1on1`, `미팅`, `가이드`, `정책`, `피드백`, `(A)`
* **우선순위 플래그**: `(P)`는 Projects 분류 강제, `(A)`는 Areas 분류 강제

### 2. 지능형 작업 추출 (접미사 기반)
"대충 작성된" 노트를 지원하기 위해 시스템은 서술형 글머리 기호를 실행 가능한 작업으로 자동으로 변환합니다.

* **동작 접미사**: `해야 함`, `하기`, `할 것`, `확인`, `조사`, `요청`, `문의`, `셋업`, `배포`로 끝나는 줄은 체크박스 작업(`- [ ]`)으로 변환됩니다.

### 3. 스마트 병합 및 원자적 쓰기 작업
시스템은 정교한 파일 처리 패턴을 통해 데이터 무결성을 보장합니다.

* **이력 보존**: `## 📝 메모 이력` 섹션은 타임스탬프와 아카이브된 소스 파일 링크가 포함된 추가 전용(append-only) 섹션입니다.
* **원자적 쓰기 패턴**: 백업 생성 -> 새 내용 쓰기 -> 성공 시 백업 삭제 -> 실패 시 백업 복구.

## 개발 패턴

### 오류 처리 철학
시스템은 엄격한 검증보다 **단계적 성능 저하(graceful degradation)**를 우선시합니다.
- API 실패 -> 중단 대신 오류 주제로 계속 진행
- JSON 파싱 오류 -> 원본 응답 로깅 후 계속 진행
- 파일 작업 실패 -> 백업 복구 후 계속 진행

### 테스트 방법
안전한 테스트를 위해 `--analysis-only` 모드를 사용하세요.
```bash
python agent.py --analysis-only
```

## 최근 향상된 기능

- **PARA 방법론 통합**: AI가 이제 Projects와 Areas를 구분합니다.
- **에이전트 패키지 격리**: 모든 시스템 파일이 `.agent/` 디렉토리에 격리됩니다.
- **향상된 보고 시스템**: `02_DAILY_REPORTS/`에 종합적인 일일 요약이 생성됩니다.
- **견고한 JSON 처리**: 정규표현식 기반 추출 및 다단계 복구 로직이 적용되었습니다.
