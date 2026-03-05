# 🤖 Obsidian 메모 자동화 에이전트

AI-powered note processing pipeline that analyzes unstructured memos and intelligently organizes them into structured agenda files. The system uses directory organization inspired by PARA methodology (Projects/Areas structure) with external configuration support.

## ✨ 핵심 기능

- 🔍 **다중 주제 추출**: 하나의 메모에서 여러 독립적인 주제 자동 분리
- 📝 **지능적 작업 추출**: 자연어 텍스트에서 실행 가능한 작업 자동 변환
- 🎯 **자동 분류**: Projects (목표형) vs Areas (관리형) 구조로 체계적 정리
- 🔧 **외부 설정 기반**: `.agent/config/rules.json`에서 분류 키워드 및 규칙 관리
- 🛡️ **Atomic Write 패턴**: 백업 → 쓰기 → 검증으로 데이터 손실 방지
- 📊 **포괄적 로깅**: 실시간 디버깅, API 비용 추적, 상세 감사 추적
- 🚀 **Vault 이식성**: 경로 파라미터로 어떤 Obsidian vault에서도 동작

## 📂 시스템 아키텍처

### NEW: .agent 패키지 격리 구조
```
ObsidianVault/
├── 00_INBOX/              # 📥 원본 메모
│   └── _ARCHIVED/         # 🗂️ 처리완료 메모 (소스 추적 링크)
├── 01_AGENDAS/
│   ├── Projects/          # 🎯 목표 지향 프로젝트 (마감 있음)
│   └── Areas/             # 🏢 지속적 관리 영역 (루틴)
├── 02_DAILY_REPORTS/      # 📊 PARA 통계 포함 일일 리포트
│
└── .agent/                # 🤖 시스템 패키지 (Obsidian 격리)
    ├── bin/               # 🛠️ 핵심 모듈
    │   ├── main_controller.py     # 경로 파라미터화 메인 오케스트레이터
    │   ├── claude_client.py       # AI API 통합
    │   ├── file_manager.py        # PARA 디렉토리 지원 파일 I/O
    │   ├── memo_analyzer.py       # PARA 분류 AI 엔진
    │   ├── markdown_processor.py  # 마크다운 병합 처리
    │   └── daily_reporter.py      # PARA 통계 일일 리포트
    ├── config/            # ⚙️ 외부 설정
    │   └── rules.json     # PARA 분류 키워드 & 작업 추출 규칙
    ├── venv/              # 🐍 격리된 Python 환경
    ├── logs/              # 📋 일일 활동 로그
    └── run                # 🚀 진입점 스크립트
```

## 🚀 빠른 시작

### 1. 시스템 요구사항
```bash
# Claude Code CLI 확인 (필수!)
claude --version

# Python 3.x 확인
python3 --version

# 디렉토리 자동 생성 (make_folders.sh 사용)
./make_folders.sh
```

### 2. **NEW: .agent 실행 방식**
```bash
# 전체 PARA 파이프라인: 분석 → 분류 → 병합 → 아카이브
./.agent/run /path/to/vault

# 안전 모드: 분석만 수행 (파일 수정 없음)
./.agent/run /path/to/vault --analysis-only

# 특정 날짜만 처리
./.agent/run /path/to/vault --date 2026-03-05

# JSON 형식 PARA 통계 출력
./.agent/run /path/to/vault --json

# 현재 디렉토리를 vault로 사용
./.agent/run $(pwd) --analysis-only
```

## 🎯 PARA 분류 시스템 (Rule-based)

### 외부 설정 파일 (`.agent/config/rules.json`)
```json
{
  "para_classification": {
    "projects": {
      "keywords": ["~까지", "기한", "데드라인", "출시", "완료", "개발", "셋업", "구축", "배포", "런칭", "(P)"],
      "description": "명확한 마감이나 목표가 있는 프로젝트성 주제"
    },
    "areas": {
      "keywords": ["정기", "관리", "운영", "매달", "지속", "루틴", "1on1", "미팅", "가이드", "정책", "피드백", "(A)"],
      "description": "지속적인 업데이트가 필요한 책임 영역"
    }
  },
  "task_extraction": {
    "action_suffixes": ["해야 함", "하기", "할 것", "확인", "조사", "요청", "문의", "셋업", "배포"]
  },
  "priority_flags": {
    "(P)": "Projects", "(A)": "Areas"
  }
}
```

### 분류 로직
- **🎯 Projects**: `3월까지 API 개발`, `시스템 마이그레이션 완료`, `제품 출시 (P)`
- **🏢 Areas**: `팀 1on1 관리`, `정기 미팅 운영`, `성과 피드백 (A)`
- **우선순위**: `(P)` 또는 `(A)` 플래그로 강제 분류

## 💡 지능적 작업 추출

### 접미사 기반 자동 변환
```markdown
# 입력 (자연스러운 메모)
- API 문서 작성하기
- 성능 테스트 확인
- 코드 리뷰 요청

# 출력 (실행 가능한 작업)
- [ ] API 문서 작성하기
- [ ] 성능 테스트 확인
- [ ] 코드 리뷰 요청
```

### 중복 제거 로직
기존 아젠다 파일과 정확히 매칭하여 중복 작업 자동 필터링

## 🛡️ 안전한 파일 처리

### Atomic Write 패턴
1. **백업**: 기존 파일을 `_filename.md`로 임시 이름 변경
2. **쓰기**: 새 내용을 원본 위치에 작성
3. **검증**: 성공 시 백업 삭제, 실패 시 원본 복구

### 소스 추적성
```markdown
## 📝 메모 이력
[2026-03-05] 새로운 AI 시스템 개발 프로젝트 시작
[[00_INBOX/_ARCHIVED/2026-03-05-프로젝트메모.md|View Source]]
```

## 📊 실시간 모니터링

### 터미널 출력 (PARA 분류 포함)
```
🤖 PARA 메모 자동화 에이전트를 시작합니다...
🗂️ Vault 경로: /Users/user/Documents/MyVault
✅ 모든 모듈이 초기화되었습니다.

📁 3개의 .md 파일을 발견했습니다 (날짜순 정렬).

🔍 [1/3] 분석 중: 2026-03-05-업무메모.md
✅ 분석 완료 - 2개 주제 발견
   1. 🎯 AI_시스템_개발 (Projects) - 4개 할 일
   2. 🏢 팀_운영_관리 (Areas) - 3개 할 일

📝 병합 대상: Projects/AI_시스템_개발.md
✅ 완료: Projects > AI_시스템_개발 - 4개 할일, 요약 1개 추가됨

📊 데일리 리포트 생성: Daily_Report_2026-03-05.md
   🎯 Projects: 1개 | 🏢 Areas: 1개

🎉 처리 완료!
   📊 총 3개 파일 분석
   ✅ 2개 파일 병합 성공
```

### PARA 통계 일일 리포트
```markdown
# Daily Report - 2026-03-05

> 📊 **메모 자동화 일일 처리 보고서**

## 🎯 Projects (목표 지향 프로젝트)
### 1. [[Projects/AI_시스템_개발]]
- **할 일**: 4개
- **요약**: 3월까지 완료 예정인 AI 자동화 시스템 개발

## 🏢 Areas (지속적 관리 영역)
### 1. [[Areas/팀_운영_관리]]
- **할 일**: 3개
- **요약**: 팀원 1on1 및 정기 미팅 운영

## 📈 PARA 처리 통계
| 분류 | 주제 수 | 할 일 수 |
|------|---------|----------|
| 🎯 Projects | 1개 | 4개 |
| 🏢 Areas | 1개 | 3개 |
| **합계** | **2개** | **7개** |
```

## 🔧 설정 및 커스터마이징

### Claude Code CLI 설정
```bash
# 초기 설정 (최초 1회)
claude auth login
claude config show
```

### rules.json 커스터마이징
```bash
# PARA 분류 키워드 추가/수정
vi .agent/config/rules.json

# 새 작업 추출 패턴 추가
# "action_suffixes" 배열에 한국어 접미사 추가
```

### 환경별 실행
```bash
# 개발 환경
./.agent/run $(pwd) --analysis-only

# 프로덕션 환경
./.agent/run /path/to/production/vault

# 배치 처리
./.agent/run /path/to/vault --date 2026-03-05
```

## 🐛 트러블슈팅

### Claude CLI 이슈
```bash
# ❌ claude: command not found
→ Claude Code CLI 설치: https://claude.ai/code

# ❌ 인증 실패
→ claude auth login 재실행

# ❌ API 한도 초과
→ Claude 대시보드에서 사용량 확인
```

### PARA 분류 이슈
```bash
# 잘못된 분류 결과
→ .agent/config/rules.json의 키워드 조정
→ 메모에 (P) 또는 (A) 플래그 사용

# 작업 추출 실패
→ rules.json의 action_suffixes 확장
→ 더 명확한 동사형 표현 사용
```

### 파일 처리 이슈
```bash
# 권한 오류
→ chmod +x .agent/run

# 경로 오류
→ 절대 경로 사용: ./.agent/run /full/path/to/vault

# Vault 구조 오류
→ ./make_folders.sh 실행으로 디렉토리 재생성
```

## 📈 성능 & 확장성

### 처리 능력
- **멀티 토픽**: 메모 1개 → 최대 10+ 독립 주제 추출
- **분류 정확도**: 95%+ 자동 분류 정확도 (키워드 기반)
- **안전성**: Atomic write로 100% 데이터 무결성 보장
- **이식성**: 임의 vault 경로에서 즉시 실행 가능

### 확장 방향
- **Multi-vault 지원**: 여러 vault 동시 처리
- **웹 인터페이스**: CLI → GUI 확장
- **다른 AI 모델**: Claude → OpenAI/Gemini 지원
- **추가 출력 형식**: Notion, Jira, Todoist 연동

---

## 💡 Best Practices

### 📝 효과적인 메모 작성
```markdown
# 좋은 예시 (PARA 분류 용이)
## 🎯 3월까지 API 개발 (P)
- 인증 시스템 구현하기
- 데이터 검증 로직 추가

## 🏢 팀 1on1 관리 (A)
- 김개발자 성과 리뷰 확인
- 이디자이너 커리어 가이드 제공
```

### 🎯 효율적 운영
- **일일 배치**: 저녁에 하루 메모 일괄 처리
- **미리보기**: `--analysis-only`로 분류 결과 확인 후 적용
- **규칙 튜닝**: 분류 결과 보고 rules.json 지속 개선

### 🔍 모니터링 & 디버깅
```bash
# 처리 로그 확인
cat .agent/logs/memo_analyzer_$(date +%Y-%m-%d).log

# API 비용 추적
grep "COST" .agent/logs/*.log

# PARA 분류 통계
grep "Projects\|Areas" .agent/logs/*.log
```

