# 🛡️ 에이전트 할루시네이션(Hallucination) 최소화 가이드

> **Principle**: 에이전트는 추측하지 않으며, 오직 검증된 사실과 주어진 컨텍스트에 기반하여 행동한다.

## 🎯 핵심 원칙

1.  **근거 기반 생성 (Grounded Generation)**:
    *   모든 답변과 코드 생성은 프로젝트 내 파일(`docs/`, `src/`, `AGENTS.md`)의 실질적인 내용에 기반해야 한다.
    *   모호한 부분은 추측하지 말고 `grep_search`나 `read_file`을 통해 직접 확인한다.

2.  **단계별 사고 (Chain-of-Thought, CoT)**:
    *   복잡한 논리가 필요한 작업(예: 리팩토링, 시스템 설계)은 즉시 실행하지 않고, 내부적으로 '생각(Thought)' 단계를 거쳐 논리적 모순이 없는지 먼저 검토한다.

3.  **자가 검증 루프 (Chain-of-Verification, CoVe)**:
    *   중요한 결정을 내린 후에는 스스로 "이 결정이 기존 `roadmap.md`나 `STANDARDS.md`와 충돌하지 않는가?"라는 질문을 던지고 검증한다.

4.  **모르면 모른다고 말하기 (Explicit Abstention)**:
    *   주어진 컨텍스트 내에서 정보를 찾을 수 없거나, 실행 결과가 예상과 다를 경우 억지로 끼워 맞추지 말고 사용자에게 즉시 보고하고 추가 정보를 요청한다.

## 🛠️ 실천 지침

### 1. 검색 및 읽기 전략
*   **Parallel Search**: `grep_search`를 활용하여 관련 키워드를 다각도로 검색하여 단편적인 정보에 매몰되지 않도록 한다.
*   **Context Volume**: 코드 수정 전 최소한 해당 함수/클래스의 전체 맥락을 파악할 수 있을 만큼 충분한 라인을 `read_file`로 읽는다.

### 2. 코드 및 문서 수정
*   **Surgical Update**: `replace` 도구를 사용할 때 `old_string`을 충분히 길게 잡아 수정 대상이 유일함을 보장한다.
*   **Validation First**: 코드 수정 후에는 반드시 린터(`run_linter.sh`)와 테스트 코드를 실행하여 할루시네이션에 의한 부작용을 즉시 감지한다.

### 3. 온도 조절 (Temperature)
*   에이전트 내부 설정이 가능하다면, 사실 관계 확인 및 코드 작성 시에는 낮은 온도(0.1~0.3)를 유지하여 결정론적 결과를 지향한다.

## 🤖 할루시네이션 감지 및 개선 장치

1.  **Feedback Loop**: 작업 중 할루시네이션으로 인한 오류(예: 존재하지 않는 함수 호출, 잘못된 문서 참조) 발견 시, 즉시 `gh issue create`를 통해 해당 사례를 기록하고 개선 방안을 `progress.md`에 반영한다.
2.  **Validation Agent**: 복잡한 작업은 반드시 `generalist` 또는 향후 도입될 `Hallucination-Validator` 에이전트에게 검토를 맡긴다.
3.  **System Prompt Refinement**: 반복되는 할루시네이션 패턴이 발견되면 `AGENTS.md`나 본 가이드라인을 즉시 업데이트하여 재발을 방지한다.

---
*최종 업데이트: 2026-04-13 | 할루시네이션 제로를 향한 Harness Engineering의 핵심 지침*
