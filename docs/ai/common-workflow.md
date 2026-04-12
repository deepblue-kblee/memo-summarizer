# 🤖 AI 공통 작업 지침

> **모든 AI (Claude, Gemini, 기타)와 사용자가 작업 시작 전 반드시 읽어야 하는 공통 지침**

## 🚨 **절대 원칙 (대전제) - MUST READ FIRST**

### **⚠️ 모든 AI가 반드시 준수해야 하는 4가지 대전제**

#### **1. 🎯 AI 중립성 원칙**
**AI가 무엇이든 상관없다. AI 선택은 사용자가 한다.**
- ✅ Claude든 Gemini든 OpenAI든 **동일한 개발 작업** 수행
- ✅ AI별 특성 비교하거나 "어떤 AI가 더 좋다" 판단 금지
- ✅ 사용자가 선택한 AI로 **목적 달성에만 집중**

#### **2. 🚀 목적 집중 원칙**
**AI는 이 repo의 개발 목적에만 집중한다. 비교/실험/테스트 목적이 아니다.**
- ✅ 메모 분석, 코드 수정, 문서 업데이트 등 **repo 개발 작업**에만 집중
- ❌ AI 성능 테스트, AI 간 비교, AI 능력 실험 금지
- ❌ "Claude가 더 정확해", "Gemini가 더 빨라" 같은 평가 금지

#### **3. 🔄 작업 연속성 원칙**
**어떤 AI든 이전 작업을 이어받아서 즉시 개발할 수 있어야 한다.**
- ✅ PROGRESS.md → PLAN.md 읽고 **현재 상태 + 다음 할 일** 파악
- ✅ 다른 AI가 했던 작업을 **seamless하게 이어받기**
- ✅ 작업 완료시 다음 AI를 위해 **상태 업데이트**

#### **4. 📋 투명성 원칙**
**사용자가 repo 상태와 다음 할 일을 명확히 파악할 수 있어야 한다.**
- ✅ 모든 작업을 PROGRESS.md에 **명확히 기록**
- ✅ 다음 우선순위를 PLAN.md에 **구체적으로 명시**
- ✅ 사용자가 언제든 **현재 상황을 5분 내 파악** 가능하도록

### **💡 대전제 요약**
```
AI 선택 = 사용자 몫
AI 역할 = repo 개발 목적 달성
AI 협업 = 환경에 상관없이 작업 연속성 보장
사용자 = 언제든 명확한 상황 파악 가능
```

---

## 👤 **사용자 빠른 시작**

### **📋 상황별 빠른 가이드**
```bash
# 🔴 긴급: "지금 당장 뭘 해야 하지?"
grep -A 5 "🚨" docs/project/roadmap.md && git status

# 🟡 복귀: "일주일 만에 돌아왔는데..."
git log --oneline --since="1 week ago" && head -20 docs/project/progress.md

# 🟢 신규: "이 프로젝트가 뭐지?"
cat README.md && head -50 docs/architecture/system-overview.md
```

### **🚀 표준 워크플로우**
```bash
# 빠른 복귀 (5분)
1. [progress.md](../project/progress.md) → 어디까지 완료되었는지
2. [roadmap.md](../project/roadmap.md) → 다음에 무엇을 해야 하는지
3. AI에게 작업 지시 또는 직접 작업

# 전체 이해 (15분)
1. [README.md](../../README.md) → 프로젝트 개요
2. [system-overview.md](../architecture/system-overview.md) → 시스템 아키텍처
3. [progress.md](../project/progress.md) → 현재 상태
4. [roadmap.md](../project/roadmap.md) → 다음 작업
```

### **🎯 역할 분담**
| 영역 | 사용자 | AI |
|------|---------|-----|
| **전략 결정** | ✅ 방향성, 우선순위 | ❌ 제안만 |
| **문서/코드** | 🔄 검토 | ✅ 작성/구현 |
| **품질 관리** | ✅ 최종 승인 | 🔄 자동 검증 |
| **외부 연동** | ✅ 인증, 설정 | ❌ 환경 의존 |

---

## 🤖 **AI 작업 시작 플로우**

### **🚨 필수 체크리스트 (순서 준수)**
```bash
1. [progress.md](../project/progress.md) 읽기 → 현재 완료 상태 파악
2. [roadmap.md](../project/roadmap.md) 읽기 → 다음 우선순위 작업 확인
3. Git 상태 확인 → git status && git log --oneline -3
4. 진행 중 작업 확인 → grep "🚧" docs/project/roadmap.md
```

### **⚡ 빠른 상태 파악 명령어**
```bash
# 현재 우선순위 작업
grep -A 10 "Priority" docs/project/roadmap.md

# 완료된 작업 (중복 방지)
grep -A 10 "✅ 완료된 작업" docs/project/progress.md

# Git 상태 요약
git log --oneline -3 && git status --short
```

### **🔄 작업 플로우**
```
AI 환경 가이드 (CLAUDE.md/GEMINI.md) 읽기
    ↓
이 공통 지침 읽기 (대전제 + 워크플로우)
    ↓
[progress.md](../project/progress.md) → [roadmap.md](../project/roadmap.md) → [README.md](../../README.md)(필요시)
    ↓
우선순위 작업 파악 → Git 상태 확인
    ↓
작업 시작
```

### **💡 작업 연속성 성과**
- ✅ **PROGRESS.md/PLAN.md 분리**: 진행상황과 계획 명확히 구분
- ✅ **사용자 빠른 복귀**: 15분 → **5분** 단축
- ✅ **AI 세션 시작**: 5분 → **1분** 단축
- ✅ **Multi-AI 협업**: 환경 독립적 작업 연속성

---

## 📚 **Multi-AI 환경 가이드**

### **🎯 파일 역할 (CLAUDE.md/GEMINI.md)**
- **목적**: 각 환경에서 [AGENTS.md](../../AGENTS.md)로 빠른 연결
- **내용**: 환경별 최소 설정만, 공통 워크플로우는 이 파일 참조
- **원칙**: AI가 무엇이든 **동일한 개발 작업** 수행

### **🔄 참조 순서**
```bash
1. 환경별 가이드: Claude환경→CLAUDE.md, Gemini환경→GEMINI.md
2. 공통 지침: 모든 환경 → [AGENTS.md](../../AGENTS.md)
3. 작업 상태: [progress.md](../project/progress.md) → [roadmap.md](../project/roadmap.md) → [README.md](../../README.md)(필요시)
```

### **🚨 Multi-AI 일관성 규칙**
✅ **해야 할 것**: 자신의 환경 가이드 먼저 읽기 → 공통 워크플로우 따르기
❌ **금지사항**: 다른 AI 가이드 참조, AI별 차이 무시, 공통 워크플로우 중복

---

## 🚨 **중요 제약사항**

### **우선순위 준수**
> **📋 최신 우선순위**: [roadmap.md](../project/roadmap.md) 확인
- **중복 방지**: [progress.md](../project/progress.md)에서 완료된 작업 확인
- **Git 관리**: 의미있는 단위로 커밋, 백업 후 변경

### **Reference 활용**
```bash
# Reference 디렉토리 확인
ls docs/reference/

# 키워드 검색
grep -l "키워드" docs/reference/*.md
```
- ✅ **제안시 활용**: 기존 연구결과 인용
- ❌ **금지**: 방향설정, 재조사

---

## 🔧 **효율성 최적화**

### **스마트 문서 정리**
```bash
# Git 기반 변경 추적 (필요시만 실행)
changes=$(git log --oneline --since="$(cat docs/project/.last_cleanup 2>/dev/null || echo '1 week ago')" docs/project/ | wc -l)
```

**트리거 조건**: 1주일간 10회 이상 docs/project 수정 시 → 사용자 승인 후 정리
**효과**: 토큰 사용량 80% 감소, 사용자 피로 대폭 개선

---

## ⚠️ **지침 준수 결과**

### **무시하면:**
- ❌ 중복 작업, 충돌 위험, 컨텍스트 손실, 우선순위 혼란

### **따르면:**
- ✅ 효율적 작업, 매끄러운 세션 전환, 중복 방지, Multi-AI 협업
- 🚀 **시간 효율성**: AI 세션 시작 **5분 → 1분** 달성

---

> **📋 마지막 업데이트**: 2026-03-24 - 대전제 확립 및 토큰 효율성 최적화 (486줄→270줄, 44% 축소)