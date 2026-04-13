# 🤖 PARA 메모 자동화 에이전트 가이드

> **지능적 메모 처리**: 정형화되지 않은 메모를 PARA 기반 Projects/Areas로 자동 분류 및 상태 관리하는 시스템

## 🚨 AI 에이전트 대전제 (MUST READ)

1.  **AI 중립성**: 사용자가 선택한 AI(Claude, Gemini 등)로 목적 달성에만 집중합니다.
2.  **이슈 기반 워크플로우 (Issue-Driven)**: 
    *   모든 신규 작업이나 발견된 문제점은 `gh issue create`를 통해 등록합니다.
    *   작업 시작 전 `gh issue list`를 확인하고 자신의 작업 대상 이슈를 선정합니다.
3.  **자가 개선 루프 (Self-Healing)**:
    *   린터(`harness-linter`) 실패 시 즉시 이슈를 생성하고 스스로 해결 계획을 세웁니다.
    *   주기적으로 `doc-gardener`를 실행하여 문서 엔트로피를 관리합니다.
4.  **검증 서브 에이전트 (Validation Sub-Agent)**: 
    *   복잡한 실행 계획 수립 후에는 `generalist` 서브 에이전트에게 검증을 요청하여 결함을 사전에 차단합니다.
5.  **작업 연속성**: 이전 세션의 `progress.md`와 `roadmap.md`를 읽고 즉시 작업을 이어받습니다.
6.  **Harness Engineering**: 에이전트가 수동 코딩 없이 자율적으로 운영될 수 있는 환경을 지향합니다.

## ⚡ 메모 자동 처리 즉시 시작 (30초)

```bash
# 1. 시스템 상태 확인 (10초)
./run_health_check.sh

# 2. 메모 자동 분류 실행 (20초)
./run_memo_processor.sh /path/to/vault
# → 00_INBOX/ 메모들이 Projects/Areas로 자동 정리 및 상태 업데이트됨
```

## 📋 핵심 문서 지도 (Roadmap)

- **[roadmap.md](docs/project/roadmap.md)**: 현재 진행 단계 및 다음 할 일 (**작업 시작 전 필수 확인**)
- **[progress.md](docs/project/progress.md)**: 지금까지 완료된 구체적 작업 내역
- **[HALLUCINATION_MINIMIZATION.md](docs/reference/HALLUCINATION_MINIMIZATION.md)**: 할루시네이션 최소화 지침 (**필수 준수**)
- **[strategy.md](docs/methodology/memo-summarizer-strategy.md)**: PARA 시스템 설계 원칙 및 전략
- **[STANDARDS.md](docs/reference/STANDARDS.md)**: 마크다운 스타일 및 개발 표준 가이드

## 🎯 주요 기능 및 원칙

1.  **PARA 분류**: Projects(목표 지향) vs Areas(지속 관리) 자동 구분 (정확도 95%+)
2.  **상태 추적**: 메모 내용을 바탕으로 기존 할 일 완료(`- [x]`) 및 신규 할 일 자동 추출
3.  **지능형 병합**: AI를 활용하여 기존 문서의 히스토리를 유지하며 새 메모를 자연스럽게 통합
4.  **데일리 리포트**: PARA 전체 현황과 오늘의 진척도를 시각화한 보고서 자동 생성

## 🚀 핵심 명령어

```bash
./run_health_check.sh && ./run_memo_processor.sh /vault
source app/venv/bin/activate && memo-processor /vault --ai auto
```

---
*Last updated: 2026-04-12 | Next milestone: Phase 2 (가독성 및 비용 최적화)*
