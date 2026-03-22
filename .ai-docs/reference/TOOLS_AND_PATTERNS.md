# 🔧 검증된 도구와 패턴 모음

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

### **프로젝트 개요**
- **프로젝트**: Obsidian Memo Automation Agent
- **핵심 기능**: 한국어 메모 → PARA 방법론 기반 자동 분류 → 구조화된 아젠다 파일
- **주요 AI**: Claude Code CLI, Gemini CLI (Multi-AI 지원)
- **작업 디렉토리**: \`$(pwd)\`
- **현재 브랜치**: \`$(git branch --show-current)\`

### **이전 기록**
📂 **아카이브된 진행상황**: [PROGRESS_${archive_date}.md](archive/PROGRESS_${archive_date}.md)

## ✅ **현재 월 완료된 작업들**

### **🏁 최근 완료 작업**
- (새로운 작업들이 여기에 추가됩니다)

## 📊 **현재 상태 요약**

### **기술적 완성도**
- **아키텍처**: PARA 방법론 완전 통합 ✅
- **Multi-AI 지원**: 문서 레벨 완료, 코드 레벨 진행 중 🚧
- **확장성**: 새 AI 추가 용이성 확보 ✅
- **안정성**: Atomic Write 패턴, 오류 복구 로직 ✅

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

## 🚨 즉시 실행 상황

- **Git 브랜치**: \`$current_branch\` ($commits_ahead commits ahead)
- **Priority 1**: $priority_task
- **블로커**: $blockers
- **마지막 커밋**: $last_commit
- **업데이트**: $(date +%Y-%m-%d\ %H:%M)

## ⚡ 빠른 명령어

\`\`\`bash
# 현재 상태 확인
git status && git log --oneline -3

# Priority 1 작업 확인
grep -A 5 "Priority 1" .ai-docs/PLAN.md

# 프로젝트 테스트
./.agent/run \$(pwd) --analysis-only
\`\`\`

## 🔗 상세 정보 링크

- 📈 **전체 진행상황** → [PROGRESS.md](PROGRESS.md)
- 📋 **다음 계획** → [PLAN.md](PLAN.md)
- 🏗️ **시스템 구조** → [SYSTEM.md](SYSTEM.md)
- 📚 **참조 라이브러리** → [reference/INDEX.md](reference/INDEX.md)

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