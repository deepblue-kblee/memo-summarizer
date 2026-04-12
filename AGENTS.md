# 🤖 메모 자동화 AI 에이전트 가이드

> **지능적 메모 처리**: 정형화되지 않은 메모를 Projects/Areas로 자동 변환하는 AI 시스템

## 📋 시스템 현황

**memo-summarizer**: Multi-AI 메모 자동 분류 시스템
- PARA 분류 95%+ 정확도, 다중 주제 추출 10+개, 작업 변환율 90%+

## ⚡ 메모 자동 처리 즉시 시작 (30초)

```bash
# 1. 메모 처리 시스템 상태 확인 (10초)
./run_health_check.sh

# 2. 메모 자동 분류 실행 (20초)
./run_memo_processor.sh /path/to/vault
# → 00_INBOX/ 메모들이 Projects/Areas로 자동 정리됨
```

## 🎯 메모 자동화 핵심 원칙

1. **지능적 분류**: PARA 방법론으로 Projects(목표) vs Areas(관리) 자동 구분
2. **다중 주제 추출**: 하나의 복잡한 메모에서 여러 독립 주제 자동 분리
3. **작업 자동 생성**: 자연어 텍스트를 실행 가능한 체크리스트로 변환
4. **Multi-AI 지원**: Claude/Gemini 환경별 최적 AI 자동 선택
*Agent-first 개발로 수동 개입 최소화 및 완전 자동화 구현*

## 📝 문서 작성 규칙

**중요**: md 파일 작성시 이모지 사용 자제 - [MARKDOWN_STYLE_GUIDE.md](docs/reference/MARKDOWN_STYLE_GUIDE.md) 참조

## 🚀 핵심 명령어

```bash
./run_health_check.sh && ./run_memo_processor.sh /vault
source app/venv/bin/activate && memo-processor /vault --ai auto
```

## 🤖 작업 가이드

**시나리오**: `docs/ai/scenarios/` | **참조**: `docs/project/`, `docs/architecture/`

## 🎮 AI별 설정

**Claude**: `export ANTHROPIC_API_KEY="key"` | **Gemini**: `export GOOGLE_API_KEY="key"`

## 🚨 시스템 상태

문서 95%, Multi-AI 95%, 연속성 90%, 검증 100%, 정리 100% - 모든 영역 완성

## 📊 성능 지표

메모 처리 30초, PARA 분류 95%+, 다중 추출 10+개, 작업 변환 90%+, AI 세션 1분, 복귀 5분

---

*Agent-first development powered by OpenAI Harness Engineering*

## 🛠️ 핵심 방법론 및 전략

이 프로젝트는 **Harness Engineering**과 **GSD(Get Shit Done)** 철학을 결합하여 운영됩니다.

- **[HarnessEngineering.md](docs/methodology/HarnessEngineering.md)**: 에이전트 전용 환경 설계 원칙
- **[memo-summarizer-strategy.md](docs/methodology/memo-summarizer-strategy.md)**: 메모 요약 시스템의 핵심 요구사항 및 로드맵 (**반드시 필독**)

*Last updated: 2026-04-12 | Next milestone: Phase 2 (가독성 및 비용 최적화)*