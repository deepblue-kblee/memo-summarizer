# 🏗️ Harness Engineering 전환 계획서

> **목표**: `memo-summarizer`를 OpenAI Harness Engineering 철학에 따라 **에이전트가 0라인의 수동 코딩 없이도 100% 자율적으로 운영할 수 있는 환경**으로 완성

## 📊 현황 요약

**전체 진행률**: 72/100 (B+ 등급)
- ✅ **문서 체계화**: 95% (4개 파일로 극한 간소화, 70% 중복 제거)
- ✅ **Agent Legibility**: 80% (문서 기반 설정, 명확한 구조)
- ✅ **Multi-AI 지원**: 95% (코드+문서 레벨 완성)
- ⚠️ **자동화 & 강제**: 40% (기본 규칙만, 린터 없음)
- ⚠️ **엔트로피 관리**: 60% (수동 정리, 자동화 부분)

**핵심**: 철학적 기초는 완성. 마지막 10%는 기계적 강제 메커니즘.

---

## 🎯 Phase 1: Context Management 완성 (즉시 실행)

### 1.1 AGENTS.md 전환 전략

**현재**: `GEMINI.md` (38줄) + `AI_COMMON_INSTRUCTIONS.md` (187줄)
**목표**: `AGENTS.md` (100줄 이하) + 체계적 `docs/` 구조

```markdown
# 전환 방식 (Decoupling)
GEMINI.md → AGENTS.md (목차 역할만)
    ├── AI_COMMON_INSTRUCTIONS.md → docs/workflows/agent-instructions.md
    ├── SYSTEM.md 일부 → docs/architecture/
    └── 새로운 구조 → docs/harness/
```

**구체적 작업**:
1. **AGENTS.md 생성** (100줄 이하)
   - 4가지 대전제 요약
   - docs/ 디렉토리 로드맵
   - 에이전트별 진입점 (Claude, Gemini, OpenAI 준비)

2. **docs/ 디렉토리 재구성**
   ```
   docs/
   ├── architecture/          # 시스템 설계
   │   ├── overview.md        # SYSTEM.md에서 이관
   │   ├── para-system.md     # PARA 분류 상세
   │   └── multi-ai-design.md # Multi-AI 아키텍처
   ├── workflows/             # 작업 흐름
   │   ├── agent-instructions.md  # AI_COMMON_INSTRUCTIONS.md 이관
   │   ├── development.md     # 개발 워크플로우
   │   └── deployment.md      # 배포 프로세스
   ├── harness/               # Harness Engineering 적용
   │   ├── principles.md      # HarnessEngineering.md 요약
   │   ├── enforcement.md     # 린터 및 검증 규칙
   │   └── garbage-collection.md  # 정리 프로세스
   ├── exec-plans/
   │   ├── active/            # 진행 중인 계획
   │   └── completed/         # 완료된 계획
   └── reference/             # 기존 .ai-docs/reference/ 유지
   ```

3. **Progressive Disclosure 구현**
   - 각 섹션에 "더 자세한 정보" 링크
   - 에이전트가 필요한 정보만 점진적으로 로드
   - 인지 부하 최소화 (Harness 원칙 1)

---

## 🔧 Phase 2: Mechanical Enforcement 구현 (1일 내)

### 2.1 Layered Domain Architecture 정의

**현재**: PARA 분류만 (Projects vs Areas)
**목표**: 전체 시스템 계층 구조 강제

```python
# 계층 구조 (의존성 방향 ↓)
Types      # 데이터 모델 (.agent/types/)
Config     # 설정 관리 (.agent/config/)
Repo       # 저장소 로직 (.agent/repo/)
Service    # 비즈니스 로직 (.agent/services/)
Runtime    # 실행 환경 (.agent/runtime/)
UI         # 사용자 인터페이스 (.agent/ui/)
```

**구체적 작업**:
1. **계층별 디렉토리 생성**
2. **기존 코드 재구성** (의존성 방향 준수)
3. **Import 규칙 정의** (상위 계층 → 하위 계층 금지)

### 2.2 Custom Linter 구현

**파일**: `.agent/bin/harness_linter.py`

```python
class HarnessLinter:
    def validate_document_size(self):
        """문서 크기 제한 (AGENTS.md < 100줄)"""

    def detect_duplication(self):
        """중복 내용 감지 (토큰 레벨)"""

    def verify_markdown_links(self):
        """깨진 링크 검증"""

    def enforce_layer_dependencies(self):
        """계층 의존성 강제 (import 검사)"""

    def validate_para_classification(self):
        """PARA 분류 규칙 준수 검증"""
```

**통합**: Pre-commit hook + CI/CD 파이프라인

### 2.3 구조적 테스트 구현

**파일**: `.agent/tests/test_harness_structure.py`

```python
def test_agents_md_size_limit():
    """AGENTS.md가 100줄 초과하면 실패"""

def test_no_duplication_in_docs():
    """문서 간 중복 내용 검사"""

def test_layer_boundary_violations():
    """계층 경계 위반 검사"""

def test_para_rules_consistency():
    """PARA 분류 규칙 일관성 검사"""
```

---

## 🔄 Phase 3: Feedback Loop 구현 (2일 내)

### 3.1 Observability Stack 구축

**목표**: 에이전트가 직접 성능을 관측하고 최적화

```python
# .agent/bin/observability.py
class SystemObserver:
    def measure_memo_processing_time(self):
        """메모 처리 시간 측정"""

    def track_ai_api_performance(self):
        """AI API 응답 시간 및 성공률"""

    def monitor_file_operations(self):
        """파일 I/O 성능 모니터링"""

    def detect_performance_regressions(self):
        """성능 저하 자동 감지"""
```

**로그 구조화**:
```json
{
  "timestamp": "2026-04-06T10:30:00Z",
  "operation": "memo_analysis",
  "ai_provider": "claude",
  "processing_time_ms": 2341,
  "tokens_used": 1502,
  "success": true,
  "file_path": "/vault/00_INBOX/meeting-notes.md"
}
```

### 3.2 자동 검증 프로세스

**파일**: `.agent/bin/auto_validator.py`

```python
def validate_processed_memos():
    """처리된 메모의 품질 검증"""

def check_para_classification_accuracy():
    """PARA 분류 정확도 검사"""

def verify_markdown_output_format():
    """출력 마크다운 형식 검증"""

def generate_quality_report():
    """품질 보고서 자동 생성"""
```

---

## 🗑️ Phase 4: Garbage Collection 구현 (3일 내)

### 4.1 자동 정리 에이전트

**파일**: `.agent/bin/garbage_collector.py`

```python
class GarbageCollector:
    def detect_technical_debt(self):
        """기술 부채 자동 감지"""
        # - 큰 함수 (50줄 이상)
        # - 중복 코드 패턴
        # - 죽은 코드 (사용되지 않는 함수)
        # - 오래된 TODO 주석

    def cleanup_old_logs(self):
        """30일 이상된 로그 정리"""

    def optimize_documentation(self):
        """문서 최적화 (중복 제거, 링크 정리)"""

    def generate_refactoring_pr(self):
        """자동 리팩토링 PR 생성"""
```

### 4.2 주기적 정리 작업

**스케줄링**: 매주 일요일 자동 실행

```bash
# .agent/bin/weekly_cleanup.sh
#!/bin/bash
python .agent/bin/garbage_collector.py
python .agent/bin/harness_linter.py --fix
git add . && git commit -m "🧹 Weekly automated cleanup

- Remove technical debt
- Optimize documentation
- Fix linting issues

Co-Authored-By: Harness Agent <harness@memo-summarizer.local>"
```

---

## 📋 Phase 5: Execution Planning 완성 (1일 내)

### 5.1 exec-plans/ 디렉토리 구조

```
docs/exec-plans/
├── active/
│   ├── harness-transformation-plan.md    # 현재 문서
│   ├── openai-integration-plan.md        # Priority 4 준비
│   └── performance-optimization-plan.md  # 성능 최적화
├── completed/
│   ├── multi-ai-implementation.md        # Priority 3 완료
│   ├── documentation-optimization.md     # Priority 2 완료
│   └── ai-continuity-system.md           # Priority 1 완료
└── templates/
    ├── execution-plan-template.md
    └── technical-debt-template.md
```

### 5.2 계획 추적 시스템

**파일**: `.agent/bin/plan_tracker.py`

```python
def track_active_plans():
    """진행 중인 계획 상태 추적"""

def update_progress():
    """진행률 자동 업데이트"""

def detect_blocked_tasks():
    """블로킹된 작업 감지"""

def generate_status_report():
    """상태 보고서 생성"""
```

---

## 🚀 즉시 실행 작업 (다음 30분)

### Step 1: 디렉토리 구조 생성

```bash
mkdir -p docs/{architecture,workflows,harness,exec-plans/{active,completed,templates}}
mkdir -p .agent/bin/{types,config,repo,services,runtime,ui}
```

### Step 2: HarnessEngineering.md 커밋

```bash
git add HarnessEngineering.md
git commit -m "📚 Add Harness Engineering philosophy guide

- OpenAI engineering blog reference
- Agent-first development principles
- Foundation for repo transformation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

### Step 3: AGENTS.md 생성 (100줄 제한)

**핵심 내용**:
- 4가지 대전제
- docs/ 네비게이션
- 에이전트별 진입점
- 즉시 시작 가이드

---

## 📊 성공 지표

### 정량적 목표

| 지표 | 현재 | 목표 | 기한 |
|------|------|------|------|
| **에이전트 세션 시작** | 1분 | 30초 | 1주일 |
| **문서 중복률** | 30% | <10% | 2주일 |
| **자동화 커버리지** | 40% | 90% | 3주일 |
| **기술 부채 해결** | 수동 | 자동 (일일) | 2주일 |
| **코드 품질 검증** | 없음 | 100% 자동 | 1주일 |

### 정성적 목표

- ✅ **Agent Legibility**: 에이전트가 repo 내 모든 정보를 이해 가능
- ✅ **Zero Manual Coding**: 에이전트가 0라인 수동 코딩으로 작업 수행
- ✅ **Self-Healing System**: 시스템이 스스로 문제를 감지하고 수정
- ✅ **Golden Principles**: 핵심 원칙이 기계적으로 강제됨

---

## ⚡ 다음 행동 (즉시)

1. **현재 문서 커밋** (HarnessEngineering.md)
2. **디렉토리 구조 생성** (docs/, .agent/bin 재구성)
3. **AGENTS.md 작성** (100줄 제한)
4. **Phase 1 린터 구현 시작**

**예상 완성 시점**: 1주일 (Phase 1-2 완성)

---

## 🎯 핵심 철학

> "Humans steer. Agents execute."
> — OpenAI Harness Engineering

- **사람**: 방향 설정, 우선순위, 품질 기준
- **에이전트**: 실행, 검증, 최적화, 유지보수

**이 계획의 완성**: 사람이 "메모를 처리해줘"라고 말하면, 에이전트가 0라인의 수동 코딩 없이 모든 것을 자율적으로 수행하는 환경.

---

*Generated: 2026-04-06 by Claude Opus 4.6*
*Next Review: Phase 1 완성 후 (예상 3-4일)*