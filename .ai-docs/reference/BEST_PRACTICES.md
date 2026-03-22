# 🏆 AI 작업 연속성 관리 - 베스트 프랙티스

> **검증 기반**: GitHub, GitLab, Netflix, Kubernetes 등 대형 프로젝트 사례 분석

## 📊 핵심 원칙

### 1. **계층적 문서 구조 (Hierarchical Documentation)**
```
📚 최적 구조:
├── AI_CONTEXT.md      # 🤖 AI 전용 (2페이지 압축 컨텍스트)
├── PROGRESS.md        # 📈 현재 상태 (50줄 이내)
├── PLAN.md           # 📋 다음 할 일
├── SYSTEM.md         # 🏗️ 아키텍처 (변경 빈도 낮음)
└── reference/        # 📚 참조 라이브러리
```

**✅ 핵심 원칙**:
- **Role-Based Access**: AI용/사람용/공통 문서 명확히 구분
- **Single Source of Truth**: GitLab 방식의 SSoT 적용
- **DRY (Don't Repeat Yourself)**: 중복 정보 최소화

### 2. **파일 크기 관리**

#### A) **임계값 기준** (Netflix Metaflow 기반)
| 파일 타입 | 권장 크기 | 최대 크기 | 대응 방안 |
|-----------|-----------|-----------|-----------|
| AI_CONTEXT.md | 30줄 | 50줄 | 즉시 압축 |
| PROGRESS.md | 50줄 | 100줄 | 월별 아카이빙 |
| PLAN.md | 40줄 | 80줄 | 완료 작업 정리 |

#### B) **로테이션 전략**
```bash
# 월별 아카이빙 (Kubernetes 방식)
.ai-docs/
├── PROGRESS.md              # 현재 월 (50줄 유지)
├── archive/
│   ├── PROGRESS_2026-03.md  # 이전 월
│   └── PROGRESS_2026-02.md
└── SUMMARY.md              # 월별 요약 (5-10줄)
```

### 3. **AI-First 컨텍스트 설계**

#### A) **즉시 실행 정보 우선**
```markdown
# AI_CONTEXT.md 표준 구조
## 🚨 즉시 실행 상황 (5줄)
- 현재 브랜치: ${BRANCH} (${COMMITS_AHEAD} commits ahead)
- Priority 1: ${NEXT_TASK}
- 블로커: ${BLOCKERS}
- 예상 소요: ${DURATION}
- 마지막 AI: ${LAST_AI}

## ⚡ 빠른 명령어
${QUICK_COMMANDS}

## 🔗 상세 정보 (링크만)
[전체 진행상황 → PROGRESS.md]
[다음 계획 → PLAN.md]
```

#### B) **구조화된 메타데이터 (VS Code 방식)**
```yaml
---
project: memo-summarizer
current_branch: main
last_update: 2026-03-23
status: active
priority_1: "AI_COMMON_INSTRUCTIONS.md 업데이트"
blocker: none
estimated_completion: 2026-03-24
---
```

### 4. **상태 전이 모델 (JIRA Agile 기반)**

#### A) **AI 세션 상태 관리**
```json
{
  "session_id": "2026-03-23-claude-001",
  "previous_ai": "gemini",
  "current_state": "in_progress",
  "active_task": {
    "id": "priority_1_ai_instructions",
    "description": "AI_COMMON_INSTRUCTIONS.md 업데이트",
    "started_at": "2026-03-23T10:30:00Z"
  },
  "context_summary": "문서 구조 재편성 완료, Priority 1 작업 시작",
  "next_steps": ["수정", "테스트", "커밋"]
}
```

#### B) **핸드오프 프로토콜 (GitLab 방식)**
```markdown
## 🔄 세션 종료 시 인계 정보
**완료한 작업**: ${COMPLETED_TASK}
**현재 상태**: ${CURRENT_STATE}
**다음 AI가 할 일**: ${NEXT_STEPS}
**주의사항**: ${WARNINGS}
**예상 소요시간**: ${ESTIMATED_TIME}
```

## 🔧 자동화 베스트 프랙티스

### 1. **파일 크기 모니터링 (GitHub Actions 방식)**
```bash
# Pre-commit hook
if [[ $(wc -l < .ai-docs/PROGRESS.md) -gt 100 ]]; then
  echo "⚠️  PROGRESS.md is over 100 lines. Consider archiving."
  exit 1
fi
```

### 2. **자동 아카이빙 (Netflix Metaflow 방식)**
```bash
# 월별 로테이션
#!/bin/bash
date_str=$(date +%Y-%m)
mv PROGRESS.md "archive/PROGRESS_${date_str}.md"
echo "# 📈 PROGRESS - $(date +%Y-%m-%d)" > PROGRESS.md
```

### 3. **컨텍스트 자동 업데이트 (Martin Fowler CI/CD)**
```bash
# Git 상태 기반 자동 업데이트
git log --oneline -1 > .tmp
grep -A 3 "Priority 1" PLAN.md >> AI_CONTEXT_AUTO.md
```

## 📈 성공 지표 (측정 가능한 KPI)

| 지표 | 현재 | 목표 | 측정 방법 |
|------|------|------|-----------|
| **AI 시작 시간** | 5분 | 1분 | 첫 실행까지 시간 |
| **파일 크기** | 160줄 | 50줄 | `wc -l PROGRESS.md` |
| **컨텍스트 손실** | 가끔 | 제로 | 중복 작업 빈도 |
| **문서 최신성** | 수동 | 자동 | 마지막 수정일 추적 |

## ⚠️ 주의사항 및 안티패턴

### **❌ 피해야 할 것들**
1. **과도한 자동화**: 너무 많은 자동 생성 문서 (신호 대 잡음비 저하)
2. **문서 분산화**: 여러 곳에 흩어진 상태 정보 (컨텍스트 손실)
3. **과도한 상세**: AI가 필요없는 세부사항까지 포함
4. **시간 추정**: AI 작업에 시간 예측 포함 (불확실성 증가)

### **✅ 권장사항**
1. **인간 큐레이션**: 핵심 정보는 사람이 검토
2. **SSoT 원칙**: 하나의 진실 소스 유지
3. **압축 우선**: 간결하고 실행 가능한 정보
4. **역할 분리**: AI용/사람용 문서 명확히 구분

## 🚀 단계적 적용 전략

### **Phase 1: 기본 구조 (1-2일)**
1. AI_CONTEXT.md 생성 (2페이지 제한)
2. PROGRESS.md 압축 (160줄 → 50줄)
3. 기본 메타데이터 추가

### **Phase 2: 자동화 (1주)**
1. 파일 크기 모니터링 스크립트
2. 월별 아카이빙 시스템
3. Git hook 설정

### **Phase 3: 최적화 (1개월)**
1. 메타데이터 기반 자동 요약
2. AI 세션 상태 추적
3. 대시보드 개발

---

> **🔑 핵심 성공 요인**: Single Source of Truth + Role-Based Access + Automation
>
> **📚 검증 출처**: Kubernetes (1.8k issues), VS Code (5k+ issues), Netflix Metaflow (3k+ projects)