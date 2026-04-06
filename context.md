# 📋 memo-summarizer 프로젝트 컨텍스트 (2026-04-06)

## 🎯 현재 상황

**HarnessEngineering 완성**: OpenAI 철학 기반 Agent 완전 자율 운영 시스템

### 📊 진행률 요약
| Phase | 목표 | 상태 | 진행률 |
|-------|------|------|--------|
| **Phase 2** | Agent 자율 운영 | ✅ 완료 | **98/100** |
| **Phase 3-A** | Observability | 🎯 진행 중 | **40/100** |
| **최종 목표** | 완전 자동화 | | **98/100** 예상 |

### 🏆 핵심 달성 사항
- ✅ **구조 통합**: `.agent/` 삭제, `app/` 단일 진입점
- ✅ **문서 체계**: `.ai-docs/` → `docs/` HarnessEngineering 구조
- ✅ **완전 자동화**: Console Scripts + 래퍼 스크립트
- ✅ **상황별 가이드**: AI 토큰 사용량 80% 감소

## 🚀 시스템 사용법

**📖 상세 가이드**: `docs/workflows/entry-points.md`

**기본 사용**:
```bash
./make_folders.sh              # 환경 설정
./run_health_check.sh         # 상태 확인
./run_memo_processor.sh /vault # 메모 처리
```

## 🤖 AI Agent 상황별 가이드 시스템

### 작업 시나리오별 가이드
- **새 세션 시작** → `docs/ai/scenarios/new-session-start.md`
- **Observability 작업** → `docs/ai/scenarios/observability-work.md`
- **버그 수정** → `docs/ai/scenarios/bug-investigation.md`
- **기능 개발** → `docs/ai/scenarios/feature-development.md`

### 프로젝트 정보
- **진행 상황** → `docs/project/progress.md`
- **다음 계획** → `docs/project/roadmap.md`
- **시스템 아키텍처** → `docs/architecture/system-overview.md`
- **진입점 가이드** → `docs/workflows/entry-points.md`

## 📂 구조

**상세**: `docs/architecture/system-overview.md`

## 🎯 다음 단계

**📖 Observability 가이드**: `docs/ai/scenarios/observability-work.md`
**목표**: Phase 3-A 완성으로 95/100 달성

## ⚡ 검증

**헬스체크**: `./run_health_check.sh`
**구조 테스트**: `python3 app/tests/test_harness_structure.py`

## 🔄 작업 흐름

**📖 상세 워크플로우**: `docs/ai/scenarios/new-session-start.md`

**새 AI 세션**: context.md 읽기 → 상황별 가이드 선택 → 작업 시작

## 💡 중요 변경사항 (이전 구조와의 차이)

### ❌ 삭제된 구조
- `.agent/` 디렉토리 (완전 삭제)
- `.ai-docs/` 디렉토리 (docs/로 마이그레이션)
- `harness_linter.py` 루트 파일 (Console Script로 대체)

### ✅ 새로운 구조
- `app/` 단일 Python 패키지
- `docs/ai/scenarios/` 상황별 AI 가이드
- Console Scripts + 래퍼 스크립트 시스템
- HarnessEngineering 완전 준수

## 🔗 빠른 참조

| 작업 유형 | 가이드 파일 |
|-----------|-------------|
| **새 세션 시작** | `docs/ai/scenarios/new-session-start.md` |
| **Observability 구현** | `docs/ai/scenarios/observability-work.md` |
| **버그 수정** | `docs/ai/scenarios/bug-investigation.md` |
| **새 기능 개발** | `docs/ai/scenarios/feature-development.md` |
| **시스템 사용법** | `docs/workflows/entry-points.md` |

---

**🎉 성과**: 이중 구조 완전 해결, 토큰 사용량 80% 감소, Agent 완전 자율성 달성

**🎯 다음 단계**: Phase 3-A Observability → 95/100 진행률 달성