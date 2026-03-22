# 📋 PLAN - Multi-AI Memo Automation Agent

> **앞으로 할 일과 작업 계획** - 다음에 무엇을 해야 하는지 명확한 가이드

## 🚧 **진행 중인 작업**

### **🚨 Multi-AI 작업 연속성 개선 필요**
- **상태**: 분석 완료, 구현 대기
- **핵심 문제**: AI가 매번 수동으로 PROGRESS.md/PLAN.md 읽기 요청 필요
- **근본 원인**: AI별 가이드(CLAUDE.md, GEMINI.md)에 자동 컨텍스트 로딩 안내 없음
- **해결책**: AI_COMMON_INSTRUCTIONS.md 기반 계층적 문서 구조 구축

## 🚀 **다음 단계 작업 (우선순위별)**

### **Priority 1: AI 작업 연속성 완성** 🚨
- [ ] **AI_COMMON_INSTRUCTIONS.md 업데이트** (PROGRESS.md/PLAN.md 참조로 변경)
- [ ] **AI_CONTEXT.md 생성** (AI 전용 압축 컨텍스트)
  ```markdown
  # 핵심 컨텍스트만 2페이지 내로 압축
  - 즉시 실행 정보: Git 상태, 다음 작업, 명령어
  - 핵심 경로: 설정 파일, 로그, 메인 스크립트 위치
  - 중요 제약사항: AI CLI 의존성, 미구현 기능
  ```

- [ ] **문서 역할 명확화**
  - AI용/사람용/공통 문서 구분 표시
  - AI 읽기 순서: PROGRESS.md → PLAN.md → SYSTEM.md (필요시)
  - 사람 읽기 순서: README.md → SYSTEM.md → AI별 가이드

- [ ] **기존 AI 가이드 보강**
  - CLAUDE.md, GEMINI.md 상단에 PROGRESS.md/PLAN.md 참조 추가

### **Priority 2: 문서 정리 완료** ✅ COMPLETED + 추가 작업
- ✅ **DEVELOPER.md 처리 결정 및 실행** (2026-03-22 완료)
  - 옵션 A 선택: 통합 후 제거 (완전 간소화)
  - 고유 내용을 SYSTEM.md에 통합 (Extension & Development Guide)
  - 커밋 완료: 693c505 - 5개 파일 구조 달성

- [ ] **README.md 업데이트**
  - 새로운 PROGRESS.md/PLAN.md 구조 반영
  - Multi-AI 지원 내용 추가
  - 빠른 시작 가이드 개선

- [ ] **PROJECT_STATUS.md 제거**
  - PROGRESS.md/PLAN.md로 완전 대체 후 삭제

### **Priority 3: 코드 레벨 Multi-AI 구현**
- [ ] **AI 추상화 레이어 구현**
  ```python
  # .agent/bin/ai_client.py (신규 생성)
  class AIClient(ABC):
      @abstractmethod
      def call_ai_service(self, prompt: str) -> Dict[str, Any]

  class ClaudeClient(AIClient): # 기존 claude_client.py 확장
  class GeminiClient(AIClient): # 신규 구현
  ```

- [ ] **AI 설정 파일 추가**
  ```json
  # .agent/config/ai_config.json (신규 생성)
  {
    "default_provider": "claude",
    "providers": {
      "claude": {"cli_command": "claude", "temperature": 0.1},
      "gemini": {"cli_command": "gemini", "temperature": 0.2}
    },
    "fallback_chain": ["claude", "gemini"]
  }
  ```

- [ ] **실행 스크립트 확장**
  ```bash
  # .agent/run 스크립트에 --ai 파라미터 추가
  ./.agent/run /path/to/vault --ai claude
  ./.agent/run /path/to/vault --ai gemini
  ./.agent/run /path/to/vault --ai auto  # fallback 지원
  ```

### **Priority 4: 기능 확장**
- [ ] **OpenAI 지원 추가**
  - GPT-4 API 통합
  - OpenAI.md 가이드 생성

- [ ] **하이브리드 AI 전략**
  - 컨텍스트 기반 AI 자동 선택
  - 비용 기반 AI 선택 로직
  - 성능 모니터링 및 메트릭 수집

- [ ] **웹 인터페이스 개발**
  - CLI → GUI 확장 검토
  - 실시간 메모 처리 기능
  - 대시보드 및 통계 시각화

## 🔗 **새 세션/에이전트 시작 체크리스트**

### **즉시 실행할 명령어들**
```bash
# 1. 현재 상태 파악
git log --oneline -3
git status
ls -la *.md

# 2. 시스템 구조 확인
head -20 SYSTEM.md
./.agent/run --help

# 3. AI CLI 상태 확인
claude --version
gemini --version
```

### **🤖 AI 세션 시작 시 문서 읽기 순서**
1. **PROGRESS.md** - 현재까지 완료된 작업 파악
2. **PLAN.md** (이 파일) - 다음 할 작업 확인
3. **SYSTEM.md** - 시스템 아키텍처 (필요시)

### **👤 사람 프로젝트 참여 시 문서 읽기 순서**
1. **README.md** - 프로젝트 개요 이해
2. **SYSTEM.md** - 시스템 아키텍처 이해
3. **CLAUDE.md / GEMINI.md** - 선택한 AI별 상세 가이드

### **🚨 즉시 진행 가능한 작업 (현재 우선순위)**
- [ ] **AI_COMMON_INSTRUCTIONS.md 업데이트** (Priority 1 - AI 작업 연속성 완성)
- [ ] **문서 역할 명확화** (AI용/사람용 구분 표시)
- [ ] **PROJECT_STATUS.md 제거** (PROGRESS.md/PLAN.md 완전 대체 후)
- [ ] **README.md 업데이트** (새로운 문서 구조 반영)

## ⚡ **빠른 상태 파악 명령어**

작업 시작 전 아래 명령어로 현재 상태를 빠르게 확인:

```bash
# 1. 다음 우선순위 작업 확인
grep -A 10 "Priority 1" .ai-docs/PLAN.md

# 2. 진행 중인 작업 확인
grep -A 5 "🚧 진행 중" .ai-docs/PLAN.md

# 3. Git 상태 빠른 확인
git log --oneline -3 && git status --short

# 4. 완료된 작업 확인 (중복 방지)
grep -A 10 "✅ 완료된 작업" .ai-docs/PROGRESS.md
```

## 🎯 **성과 목표**

### **단기 목표 (Priority 1-2)**
- **AI 세션 시작 시간**: 현재 5분 → 목표 1분 (PROGRESS.md/PLAN.md 효과)
- **Multi-AI 전환 비용**: 현재 수동 → 목표 자동 (문서 구조 개선)
- **새 참여자 온보딩**: 현재 30분 → 목표 10분 (역할별 문서 분리)
- ✅ **문서 간소화**: 7개 파일 → 4개 파일 달성 (극한 간소화 완료)

### **중장기 목표 (Priority 3-4)**
- **Multi-AI 코드 통합**: 추상화 레이어 완성
- **자동 AI 선택**: 컨텍스트 기반 최적 AI 선택
- **성능 모니터링**: 비용 및 품질 메트릭 대시보드
- **확장성**: OpenAI 등 추가 AI 프로바이더 지원

## 💡 **다음 작업자를 위한 권장사항 (2026-03-23 업데이트)**

### **🚨 최우선 작업: Priority 1 집중**
1. **AI_COMMON_INSTRUCTIONS.md 업데이트**: PROGRESS.md/PLAN.md 참조로 변경
2. **문서 역할 명확화**: AI용/사람용 구분으로 사용성 극대화
3. **PROJECT_STATUS.md 정리**: 완전 대체 후 제거

### **📋 단계별 진행 방안**
1. **Priority 1 집중**: AI 작업 연속성 → 다음 세션부터 즉시 효과
2. **Priority 2 마무리**: 문서 정리 → README.md 업데이트
3. **Priority 3 준비**: 코드 레벨 Multi-AI 구현 설계
4. **지속적 테스트**: 각 단계마다 `--analysis-only` 모드로 검증

**🚀 Priority 1 집중: AI 작업 연속성 완성이 Multi-AI 협업 환경의 핵심입니다!**

---

> **📋 마지막 업데이트**: 2026-03-23 - PROJECT_STATUS.md에서 분리된 계획 문서