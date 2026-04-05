# 🤖 AI AGENTS 운영 가이드

> **Agent-First Development**: 사람은 방향을 제시하고, 에이전트는 실행한다.

## ⚡ 즉시 시작 (30초)

```bash
# 1. 작업 연속성 파악 (5초)
cat .ai-docs/PROGRESS.md .ai-docs/PLAN.md

# 2. 다음 우선순위 확인 (5초)
ls docs/exec-plans/active/

# 3. 개발 작업 시작 (20초)
./.agent/run /path/to/vault --ai [claude|gemini|auto]
```

## 🎯 4가지 대전제

1. **AI 중립성**: AI 선택은 사용자 몫, AI는 목적 달성만 집중
2. **목적 집중**: 메모 분석, 코드 수정 등 repo 개발 작업만
3. **작업 연속성**: 어떤 AI든 이전 작업을 seamless하게 이어받기
4. **투명성**: 사용자가 언제든 현재 상황을 5분 내 파악 가능

## 🗂️ 문서 네비게이션

### 📋 작업 관리
- **현재 상태**: `.ai-docs/PROGRESS.md` (완료된 작업)
- **다음 계획**: `.ai-docs/PLAN.md` (우선순위 작업)
- **실행 계획**: `docs/exec-plans/active/` (진행 중인 복잡한 작업)

### 🏗️ 시스템 아키텍처
- **전체 개요**: `docs/architecture/overview.md` → `.ai-docs/SYSTEM.md`
- **PARA 시스템**: `docs/architecture/para-system.md`
- **Multi-AI**: `docs/architecture/multi-ai-design.md`

### ⚙️ 작업 흐름
- **공통 워크플로우**: `docs/workflows/agent-instructions.md` → `.ai-docs/AI_COMMON_INSTRUCTIONS.md`
- **개발 프로세스**: `docs/workflows/development.md`

### 🔧 Harness Engineering
- **핵심 철학**: `docs/harness/principles.md` → `HarnessEngineering.md`
- **자동 검증**: `docs/harness/enforcement.md` (린터, 테스트)
- **정리 시스템**: `docs/harness/garbage-collection.md`

### 📚 참조 자료
- **색인**: `.ai-docs/reference/INDEX.md`
- **패턴 모음**: `.ai-docs/reference/TOOLS_AND_PATTERNS.md`
- **베스트 프래스티스**: `.ai-docs/reference/BEST_PRACTICES.md`

## 🎮 AI별 진입점

### 🔵 Claude
```bash
# 환경 가이드
cat CLAUDE.md

# 인증 설정 (anthropic-sdk)
export ANTHROPIC_API_KEY="your-key"
```

### 🟡 Gemini
```bash
# 환경 가이드
cat GEMINI.md

# 인증 설정 (google-generativeai)
export GOOGLE_API_KEY="your-key"
```

### 🟠 OpenAI (준비 중)
```bash
# TODO: Priority 4에서 구현 예정
export OPENAI_API_KEY="your-key"
```

## 🚨 에이전트 자율 운영 상태

| 영역 | 진행률 | 상태 |
|------|--------|------|
| 문서 체계 | 95% | ✅ 완성 |
| Multi-AI | 95% | ✅ 완성 |
| 작업 연속성 | 90% | ✅ 완성 |
| 자동 검증 | 40% | 🔄 구현 중 |
| 정리 시스템 | 50% | 🔄 구현 중 |

**목표**: 에이전트가 0라인의 수동 코딩 없이 100% 자율 운영

## 📊 성능 지표 (2026-04-06 기준)

- **AI 세션 시작**: 5분 → **1분** (80% 단축) ✅
- **사용자 복귀**: 15분 → **5분** (67% 단축) ✅
- **문서 중복**: 70% → **30%** (중복 제거) ✅
- **자동화 커버리지**: 40% → **90%** (목표, Phase 2)

---

*Agent-first development powered by OpenAI Harness Engineering*
*Last updated: 2026-04-06 | Next milestone: Phase 2 (린터 구현)*