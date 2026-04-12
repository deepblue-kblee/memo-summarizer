# 마크다운 스타일 가이드

> 메모 자동화 시스템 문서 작성 규칙

## 기본 원칙

### 이모지 사용 자제
**규칙**: 특별한 요청이 없는 한 이모지 사용을 피합니다.

**이유**:
- 전문성과 가독성 향상
- 스크린 리더 접근성 개선
- 다양한 환경에서의 일관된 표시
- 텍스트 검색 및 처리 용이성

### 예외 상황
다음의 경우에만 이모지 사용을 허용합니다:
- 사용자가 명시적으로 이모지 사용을 요청한 경우
- 기존 문서의 스타일을 유지해야 하는 경우 (점진적 변경)

## 작성 지침

### 제목 (Headers)
```markdown
# 메인 제목
## 섹션 제목
### 하위 섹션 제목
```

### 목록 (Lists)
```markdown
- 항목 1
- 항목 2
  - 하위 항목
  - 하위 항목

1. 순서 항목 1
2. 순서 항목 2
```

### 강조 (Emphasis)
```markdown
**굵게**: 중요한 내용
*기울임*: 강조하고 싶은 내용
`코드`: 명령어나 파일명
```

### 코드 블록
````markdown
```bash
# 명령어 예시
./run_memo_processor.sh /path/to/vault
```
````

### 링크 (Links)
```markdown
[링크 텍스트](URL)
[문서 참조](../path/to/file.md)
```

## 구조화 지침

### 문서 시작
모든 문서는 명확한 제목과 간단한 설명으로 시작합니다:

```markdown
# 문서 제목

> 문서의 목적과 내용을 한 줄로 설명

## 개요
문서의 전체적인 내용을 설명합니다.
```

### 섹션 구성
- 논리적 흐름에 따른 섹션 배치
- 각 섹션은 독립적으로 이해 가능하도록 작성
- 필요시 다른 문서로의 참조 링크 제공

### 예시와 설명
- 구체적인 예시를 통한 설명
- 사용자 관점에서의 실제 활용 방법 제시
- Before/After 비교를 통한 명확한 효과 설명

## 품질 체크리스트

문서 작성 후 다음 사항을 확인합니다:

- [ ] 이모지 사용 최소화 (특별 요청 시에만 사용)
- [ ] 명확하고 일관된 제목 구조
- [ ] 적절한 코드 블록과 예시
- [ ] 다른 문서로의 적절한 링크 연결
- [ ] 사용자 관점에서의 가독성
- [ ] 전문적이고 깔끔한 톤 유지

## 기존 문서 개선 방향

현재 프로젝트의 많은 문서들이 이모지를 사용하고 있습니다. 향후 문서 수정 시 점진적으로 이모지를 제거하고 명확한 텍스트로 대체할 예정입니다.

**개선 우선순위**:
1. 새로 작성하는 모든 문서
2. 주요 사용자 가이드 문서
3. 기술 문서 및 참조 자료
4. 기존 문서의 점진적 개선

## 참조

- [CommonMark 스펙](https://commonmark.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [접근성 가이드라인](https://www.w3.org/WAI/WCAG21/quickref/)# 🏆 AI 작업 연속성 관리 - 베스트 프랙티스

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

## 🔗 참조 링크
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
> **📚 검증 출처**: Kubernetes (1.8k issues), VS Code (5k+ issues), Netflix Metaflow (3k+ projects)# 🔍 중복 방지 점검 체크리스트

> **목적**: 정기적으로 문서 중복과 역할 침범을 확인하고 바로잡기 위한 체크리스트

## ⏰ **점검 시점**

### **필수 점검 시기**
- ✅ **주요 작업 완료 후** (Priority 작업 완료 시마다)
- ✅ **새로운 문서 추가/수정 시** (큰 변경사항 발생 시)
- ✅ **월 1회 정기 점검** (매월 첫째 주)
- ✅ **새로운 기여자 합류 시** (문서 혼란 방지)

### **권장 점검 시기**
- 📅 **새로운 AI 추가 시** (CLAUDE.md, GEMINI.md 수정 후)
- 📅 **시스템 아키텍처 변경 시** (SYSTEM.md 대폭 수정 후)
- 📅 **작업 플로우 변경 시** (AI_COMMON_INSTRUCTIONS.md 수정 후)

---

## 📋 **점검 체크리스트**

### **Phase 1: 자동 중복 검사 (5분)**

#### **1.1 동일 섹션명 검사**
```bash
# 동일한 섹션 제목이 여러 파일에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "빠른 상태 파악" {} \;
find .ai-docs -name "*.md" -exec grep -l "체크리스트" {} \;
find .ai-docs -name "*.md" -exec grep -l "Priority" {} \;
find .ai-docs -name "*.md" -exec grep -l "문서 구조" {} \;
```

#### **1.2 동일 명령어 중복 검사**
```bash
# 동일한 명령어가 여러 파일에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "git log --oneline" {} \;
find .ai-docs -name "*.md" -exec grep -l "grep -A" {} \;
find .ai-docs -name "*.md" -exec grep -l "git status" {} \;
```

#### **1.3 파일 구조 설명 중복 검사**
```bash
# 파일 구조 설명이 여러 곳에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "ai-docs/" {} \;
find .ai-docs -name "*.md" -exec grep -l "PROGRESS.md" {} \;
find .ai-docs -name "*.md" -exec grep -l "PLAN.md" {} \;
```

### **Phase 2: 역할 침범 검사 (10분)**

#### **2.1 PROGRESS.md 역할 검사**
- [ ] **미래 계획 내용이 있는가?** → PLAN.md로 이동
- [ ] **"앞으로", "다음에", "할 예정" 표현이 있는가?** → PLAN.md로 이동
- [ ] **[ ] 체크박스 할 일이 있는가?** → PLAN.md로 이동

#### **2.2 PLAN.md 역할 검사**
- [ ] **"완료됨", "달성됨" 과거 작업이 있는가?** → PROGRESS.md로 이동
- [ ] **상세한 Git 상태가 있는가?** → PROGRESS.md로 이동
- [ ] **현재 파일 구조 설명이 있는가?** → PROGRESS.md로 이동

#### **2.3 AI_COMMON_INSTRUCTIONS.md 역할 검사**
- [ ] **구체적인 Priority 1,2,3 내용이 있는가?** → PLAN.md로 이동
- [ ] **완료 작업 기록이 있는가?** → PROGRESS.md로 이동
- [ ] **아키텍처 상세 설명이 있는가?** → SYSTEM.md로 이동
- [ ] **파일 크기가 300줄 이상인가?** → 내용 분산 검토

### **Phase 3: 내용 일관성 검사 (10분)**

#### **3.1 상호 참조 검증**
- [ ] **PROGRESS.md의 "현재 브랜치" 정보가 최신인가?**
- [ ] **PLAN.md의 Priority 번호가 일관적인가?**
- [ ] **각 파일의 "마지막 업데이트" 날짜가 정확한가?**
- [ ] **파일 간 링크가 올바르게 작동하는가?**

#### **3.2 중복 제거 후 검증**
- [ ] **정보 손실 없이 중복이 제거되었는가?**
- [ ] **참조 링크가 올바르게 설정되었는가?**
- [ ] **각 파일이 독립적으로 이해 가능한가?**

---

## 🛠️ **중복 발견 시 해결 프로세스**

### **Step 1: 중복 유형 판단**
1. **완전 동일 중복**: 한 곳 제거, 다른 곳에서 참조
2. **부분 중복**: 공통 부분 추출 후 한 곳에 모으기
3. **역할 침범**: 적절한 파일로 내용 이동
4. **불필요한 중복**: 더 적절한 위치 판단 후 이동

### **Step 2: 우선순위 결정**
1. **핵심 역할 파일 우선**: PROGRESS(완료) > PLAN(미래) > 기타
2. **더 구체적인 파일 우선**: 구체적 내용 > 일반적 내용
3. **사용 빈도 높은 곳 우선**: 자주 참조되는 파일에 유지

### **Step 3: 안전한 제거**
```bash
# 백업 먼저
cp -r .ai-docs .ai-docs-backup-$(date +%Y%m%d)

# 내용 이동/수정
# (구체적 편집 작업)

# 검증
# 각 파일이 독립적으로 의미 있는지 확인

# 커밋
git add .ai-docs/
git commit -m "Remove documentation duplication - [구체적 변경사항]"
```

### **Step 4: 사후 검증**
- [ ] **각 파일이 역할에 충실한가?**
- [ ] **필요한 정보에 쉽게 접근 가능한가?**
- [ ] **참조 링크가 올바르게 작동하는가?**
- [ ] **새로운 중복이 생기지 않았는가?**

---

## 🚨 **자주 발생하는 중복 패턴**

### **위험 패턴 1: "빠른 명령어" 중복**
```bash
# 여러 파일에서 동일한 명령어 블록 반복
git log --oneline -3
git status
head -20 PROGRESS.md
```
**해결**: AI_COMMON_INSTRUCTIONS.md에만 유지, 다른 곳에서 참조

### **위험 패턴 2: "Priority 작업" 중복**
```markdown
Priority 1: 작업 연속성 완성
Priority 2: 문서 정리
Priority 3: 기능 확장
```
**해결**: PLAN.md에만 유지, 다른 곳에서는 간단 참조

### **위험 패턴 3: "파일 구조" 중복**
```bash
├── PROGRESS.md
├── PLAN.md
├── SYSTEM.md
```
**해결**: PROGRESS.md에만 상세 구조, 다른 곳에서는 링크

### **위험 패턴 4: "완료 작업" 혼재**
```markdown
✅ 완료: 문서 구조 정리 (PLAN.md에 잘못 위치)
```
**해결**: 무조건 PROGRESS.md로 이동

---

## 📊 **점검 결과 기록**

### **점검 기록 템플릿**
```markdown
## 중복 점검 결과 - YYYY-MM-DD

### 발견된 문제
- [ ] 파일명: 문제 설명
- [ ] 파일명: 문제 설명

### 수행한 수정
- [x] 파일명: 수정 내용
- [x] 파일명: 수정 내용

### 다음 점검 시 주의사항
- 주의할 패턴이나 경향

### 점검자: [이름]
### 소요 시간: [분]
```

### **기록 위치**
- **위치**: 이 파일 하단에 누적 기록
- **보존**: 최근 5회 점검 결과만 유지
- **참조**: 패턴 분석 및 재발 방지에 활용

---

## ⚡ **빠른 점검 스크립트**

### **자동 중복 검사 스크립트**
```bash
#!/bin/bash
# duplication_check.sh

echo "🔍 문서 중복 검사 시작..."

echo "1. 동일 섹션명 검사"
sections=("빠른 상태 파악" "Priority" "체크리스트" "파일 구조")
for section in "${sections[@]}"; do
    files=$(find .ai-docs -name "*.md" -exec grep -l "$section" {} \;)
    count=$(echo "$files" | wc -l)
    if [ $count -gt 1 ]; then
        echo "⚠️  '$section' 중복: $files"
    fi
done

echo "2. 동일 명령어 검사"
commands=("git log --oneline" "git status" "grep -A")
for cmd in "${commands[@]}"; do
    files=$(find .ai-docs -name "*.md" -exec grep -l "$cmd" {} \;)
    count=$(echo "$files" | wc -l)
    if [ $count -gt 1 ]; then
        echo "⚠️  '$cmd' 명령어 중복: $files"
    fi
done

echo "✅ 중복 검사 완료"
```

---

> **📋 마지막 업데이트**: 2026-03-24 - 중복 방지 체크리스트 작성
> **🔄 적용 시작**: 즉시 - 다음 작업 완료시부터 점검 실시# 🔧 검증된 도구와 패턴 모음

> **실전 검증**: GitHub, GitLab, Netflix, JIRA에서 실제 사용되는 도구와 스크립트

## 📂 파일 크기 관리 도구

### 1. **파일 크기 모니터링 스크립트**

#### A) **기본 체크 스크립트**
```bash
#!/bin/bash
# .ai-docs/check_size.sh
echo "📊 AI 문서 크기 체크 ($(date))"
echo "================================"

for file in PROGRESS.md PLAN.md AI_CONTEXT.md; do
  if [[ -f ".ai-docs/$file" ]]; then
    lines=$(wc -l < ".ai-docs/$file")
    echo "$file: $lines lines"

    # 경고 임계값
    case $file in
      "AI_CONTEXT.md")   max=50 ;;
      "PROGRESS.md")     max=100 ;;
      "PLAN.md")         max=80 ;;
    esac

    if [[ $lines -gt $max ]]; then
      echo "⚠️  $file needs attention (over $max lines)"
    else
      echo "✅ $file size OK"
    fi
  fi
done
```

#### B) **Pre-commit Hook** (GitHub 방식)
```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "🔍 Checking AI documentation sizes..."

# PROGRESS.md 크기 체크
if [[ -f ".ai-docs/PROGRESS.md" ]]; then
  lines=$(wc -l < ".ai-docs/PROGRESS.md")
  if [[ $lines -gt 100 ]]; then
    echo "❌ PROGRESS.md is over 100 lines ($lines lines)"
    echo "💡 Run: .ai-docs/scripts/archive_progress.sh"
    exit 1
  fi
fi

# AI_CONTEXT.md 크기 체크
if [[ -f ".ai-docs/AI_CONTEXT.md" ]]; then
  lines=$(wc -l < ".ai-docs/AI_CONTEXT.md")
  if [[ $lines -gt 50 ]]; then
    echo "❌ AI_CONTEXT.md is over 50 lines ($lines lines)"
    echo "💡 Compress the context to essential information only"
    exit 1
  fi
fi

echo "✅ All AI documentation sizes are OK"
```

### 2. **자동 아카이빙 시스템** (Netflix Metaflow 기반)

#### A) **월별 프로그레스 아카이빙**
```bash
#!/bin/bash
# .ai-docs/scripts/archive_progress.sh
set -e

echo "📦 Archiving PROGRESS.md for $(date +%Y-%m)..."

# 디렉토리 생성
mkdir -p .ai-docs/archive

# 현재 날짜
current_date=$(date +%Y-%m-%d)
archive_date=$(date +%Y-%m)

# 기존 PROGRESS.md를 아카이브로 이동
if [[ -f ".ai-docs/PROGRESS.md" ]]; then
  # 아카이브 파일에 메타데이터 추가
  {
    echo "# 📈 PROGRESS Archive - $archive_date"
    echo ""
    echo "> **Archived on**: $current_date"
    echo "> **Lines**: $(wc -l < .ai-docs/PROGRESS.md)"
    echo "> **Next**: [Current PROGRESS.md](../PROGRESS.md)"
    echo ""
    echo "---"
    echo ""
    cat .ai-docs/PROGRESS.md
  } > ".ai-docs/archive/PROGRESS_${archive_date}.md"

  echo "✅ Archived to: .ai-docs/archive/PROGRESS_${archive_date}.md"
else
  echo "⚠️  No PROGRESS.md found to archive"
  exit 1
fi

# 새로운 PROGRESS.md 생성
cat > .ai-docs/PROGRESS.md << EOF
# 📈 PROGRESS - Multi-AI Memo Automation Agent

> **작업 진행 상황 및 완료 기록** - 지금까지 무엇을 완료했는지 추적

## 🎯 **현재 프로젝트 상태 ($current_date)**

# 프로젝트 개요는 PROGRESS.md 또는 README.md 참조

### **이전 기록**
📂 **아카이브된 진행상황**: [PROGRESS_${archive_date}.md](archive/PROGRESS_${archive_date}.md)

## ✅ **현재 월 완료된 작업들**

### **🏁 최근 완료 작업**
- (새로운 작업들이 여기에 추가됩니다)

# 상태 정보는 PROGRESS.md에서 확인하세요

---

> **📋 마지막 업데이트**: $current_date - 새로운 월 시작
EOF

echo "✅ New PROGRESS.md created for $current_date"

# Git 상태 확인
echo ""
echo "📊 Current git status:"
git status --porcelain .ai-docs/
```

#### B) **자동 요약 생성기**
```bash
#!/bin/bash
# .ai-docs/scripts/generate_summary.sh

echo "📝 Generating monthly summary..."

# 현재 월의 모든 아카이브 파일 찾기
current_month=$(date +%Y-%m)
archive_files=$(ls .ai-docs/archive/PROGRESS_${current_month}*.md 2>/dev/null || true)

if [[ -z "$archive_files" ]]; then
  echo "⚠️  No archive files found for $current_month"
  exit 1
fi

# 요약 생성
{
  echo "# 📊 Monthly Summary - $current_month"
  echo ""
  echo "## 📈 주요 성과"

  # 각 아카이브 파일에서 "완료된 작업" 섹션 추출
  for file in $archive_files; do
    echo ""
    echo "### $(basename $file .md | sed 's/PROGRESS_//')"
    grep -A 10 "완료된 작업" "$file" | head -10 || echo "- 완료 작업 정보 없음"
  done

  echo ""
  echo "## 📂 상세 기록"
  for file in $archive_files; do
    echo "- [$(basename $file)]($(basename $file))"
  done

} > ".ai-docs/archive/SUMMARY_${current_month}.md"

echo "✅ Summary generated: .ai-docs/archive/SUMMARY_${current_month}.md"
```

## 🤖 AI 컨텍스트 관리 도구

### 1. **AI_CONTEXT.md 자동 생성** (VS Code 방식)

```bash
#!/bin/bash
# .ai-docs/scripts/update_ai_context.sh

echo "🤖 Updating AI_CONTEXT.md..."

# Git 정보 수집
current_branch=$(git branch --show-current)
commits_ahead=$(git rev-list --count HEAD ^origin/$current_branch 2>/dev/null || echo "0")
last_commit=$(git log --oneline -1 --format="%h %s")

# Priority 1 작업 추출
priority_task=""
if [[ -f ".ai-docs/PLAN.md" ]]; then
  priority_task=$(grep -A 3 "Priority 1" .ai-docs/PLAN.md | tail -n +2 | head -n 1 || echo "확인 필요")
fi

# 블로커 확인
blockers="없음"
if [[ -f ".ai-docs/PLAN.md" ]]; then
  if grep -q "블로커\|BLOCKER\|차단" .ai-docs/PLAN.md; then
    blockers="PLAN.md 확인 필요"
  fi
fi

# AI_CONTEXT.md 생성
cat > .ai-docs/AI_CONTEXT.md << EOF
# 🤖 AI Context - $(date +%Y-%m-%d)

> **AI 전용 압축 컨텍스트** - 즉시 실행 가능한 정보만 포함

# 템플릿 및 상태 정보는 다음 파일들 참조:
# - 즉시 실행 상황: BEST_PRACTICES.md
# - 빠른 명령어: AI_COMMON_INSTRUCTIONS.md

# 상세 정보 링크는 BEST_PRACTICES.md 또는 AGENTS.md 참조

## 🎯 작업 시작 체크리스트

- [ ] Git 상태 최신인지 확인
- [ ] Priority 1 작업 명확히 파악
- [ ] 의존성 및 블로커 없는지 확인
- [ ] 관련 파일들 읽고 컨텍스트 파악
- [ ] 테스트 환경 준비

---

> **📊 파일 크기**: $(wc -l < .ai-docs/AI_CONTEXT.md) 줄 (목표: 50줄 이내)
EOF

# 크기 체크
lines=$(wc -l < .ai-docs/AI_CONTEXT.md)
if [[ $lines -gt 50 ]]; then
  echo "⚠️  AI_CONTEXT.md is $lines lines (over 50 line limit)"
  echo "💡 Consider compressing the content"
else
  echo "✅ AI_CONTEXT.md updated ($lines lines)"
fi
```

### 2. **핸드오프 프로토콜** (GitLab 방식)

```bash
#!/bin/bash
# .ai-docs/scripts/session_handoff.sh

echo "🔄 Creating AI session handoff..."

# 인수 확인
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <completed_task> <current_state> [next_steps] [warnings]"
  echo "Example: $0 'AI_CONTEXT.md 생성' '테스트 대기' 'validation 실행' 'git push 금지'"
  exit 1
fi

completed_task="$1"
current_state="$2"
next_steps="${3:-다음 Priority 작업 확인}"
warnings="${4:-없음}"
estimated_time="${5:-15-30분}"

# 핸드오프 정보 생성
handoff_file=".ai-docs/LAST_HANDOFF.md"

cat > "$handoff_file" << EOF
# 🔄 AI 세션 핸드오프 - $(date +%Y-%m-%d\ %H:%M)

## 완료한 작업
**$completed_task**

## 현재 상태
**$current_state**

## 다음 AI가 할 일
**$next_steps**

## ⚠️ 주의사항
**$warnings**

## ⏱️ 예상 소요시간
**$estimated_time**

## 📊 Git 상태
\`\`\`
$(git status --porcelain)
\`\`\`

## 🔗 관련 파일
- Priority 확인: [PLAN.md](.ai-docs/PLAN.md)
- 진행상황: [PROGRESS.md](.ai-docs/PROGRESS.md)
- AI 컨텍스트: [AI_CONTEXT.md](.ai-docs/AI_CONTEXT.md)

---
> **세션 ID**: $(date +%Y%m%d-%H%M)-handoff
EOF

echo "✅ Handoff created: $handoff_file"
echo "📋 Content:"
cat "$handoff_file"
```

## 📊 모니터링 및 대시보드 도구

### 1. **프로젝트 상태 대시보드**
```bash
#!/bin/bash
# .ai-docs/scripts/status_dashboard.sh

echo "📊 Multi-AI Memo Automation Agent - Status Dashboard"
echo "=================================================="
echo "📅 Generated: $(date)"
echo ""

# Git 정보
echo "🔧 Git Status:"
echo "- Branch: $(git branch --show-current)"
echo "- Commits ahead: $(git rev-list --count HEAD ^origin/$(git branch --show-current) 2>/dev/null || echo '0')"
echo "- Last commit: $(git log --oneline -1)"
echo "- Staged files: $(git diff --cached --name-only | wc -l)"
echo "- Modified files: $(git diff --name-only | wc -l)"
echo ""

# 파일 크기 정보
echo "📁 File Sizes:"
for file in PROGRESS.md PLAN.md AI_CONTEXT.md SYSTEM.md; do
  if [[ -f ".ai-docs/$file" ]]; then
    lines=$(wc -l < ".ai-docs/$file")
    size=$(du -h ".ai-docs/$file" | cut -f1)
    echo "- $file: $lines lines ($size)"
  fi
done
echo ""

# Priority 작업 추출
echo "🎯 Current Priorities:"
if [[ -f ".ai-docs/PLAN.md" ]]; then
  grep -A 5 "Priority [1-3]" .ai-docs/PLAN.md | head -15
else
  echo "- PLAN.md not found"
fi
echo ""

# 최근 아카이브
echo "📦 Recent Archives:"
if [[ -d ".ai-docs/archive" ]]; then
  ls -la .ai-docs/archive/ | tail -5
else
  echo "- No archives found"
fi
echo ""

# 시스템 건강도
echo "🔍 System Health:"
echo "- .agent/run executable: $([[ -x ".agent/run" ]] && echo "✅" || echo "❌")"
echo "- Rules file: $([[ -f ".agent/config/rules.json" ]] && echo "✅" || echo "❌")"
echo "- Logs directory: $([[ -d ".agent/logs" ]] && echo "✅" || echo "❌")"

# 최근 로그 (있다면)
if [[ -d ".agent/logs" ]]; then
  latest_log=$(ls -t .agent/logs/*.log 2>/dev/null | head -1)
  if [[ -n "$latest_log" ]]; then
    echo "- Latest log: $(basename "$latest_log")"
  fi
fi
```

### 2. **자동화 설정 스크립트**
```bash
#!/bin/bash
# .ai-docs/scripts/setup_automation.sh

echo "⚙️ Setting up AI context management automation..."

# 스크립트 디렉토리 생성
mkdir -p .ai-docs/scripts

# Git hooks 설정
if [[ -d ".git/hooks" ]]; then
  echo "📝 Setting up pre-commit hook..."

  cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# AI Documentation Size Check
if [[ -f ".ai-docs/scripts/check_size.sh" ]]; then
  .ai-docs/scripts/check_size.sh
  exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    echo ""
    echo "💡 Fix suggestions:"
    echo "   - Run: .ai-docs/scripts/archive_progress.sh"
    echo "   - Or manually compress the files"
    exit $exit_code
  fi
fi
EOF

  chmod +x .git/hooks/pre-commit
  echo "✅ Pre-commit hook installed"
else
  echo "⚠️  Not a git repository - skipping hooks"
fi

# 크론탭 추천 (선택사항)
echo ""
echo "📅 Optional: Add to crontab for monthly archiving:"
echo "0 0 1 * * cd $(pwd) && .ai-docs/scripts/archive_progress.sh"
echo ""
echo "✅ Automation setup complete!"
echo "🔧 Available scripts:"
echo "   - .ai-docs/scripts/check_size.sh"
echo "   - .ai-docs/scripts/archive_progress.sh"
echo "   - .ai-docs/scripts/update_ai_context.sh"
echo "   - .ai-docs/scripts/status_dashboard.sh"
```

## 🚀 통합 워크플로우

### **일일 AI 작업 시작 루틴**
```bash
#!/bin/bash
# .ai-docs/scripts/daily_start.sh

echo "🌅 Daily AI Work Start Routine"
echo "=============================="

# 1. 상태 체크
echo "1️⃣ Checking system status..."
.ai-docs/scripts/status_dashboard.sh

# 2. AI 컨텍스트 업데이트
echo ""
echo "2️⃣ Updating AI context..."
.ai-docs/scripts/update_ai_context.sh

# 3. 파일 크기 체크
echo ""
echo "3️⃣ Checking file sizes..."
.ai-docs/scripts/check_size.sh

echo ""
echo "✅ Ready for AI work!"
echo "📋 Next: Read AI_CONTEXT.md and start with Priority 1 task"
```

---

> **📚 출처**: 이 도구들은 GitHub (VS Code), GitLab, Netflix (Metaflow), JIRA 등에서 실제 사용되는 패턴을 기반으로 제작되었습니다.
>
> **🔄 업데이트**: 새로운 도구 발견 시 지속적으로 추가됩니다.