#!/bin/bash
# 문서 중복 자동 수정 스크립트

echo "🔧 Starting automatic duplication fix..."

# 백업 생성
backup_dir=".ai-docs-backup-$(date +%Y%m%d_%H%M%S)"
cp -r .ai-docs "$backup_dir"
echo "📁 Backup created: $backup_dir"

# 현재 탐지된 중복 확인
echo ""
echo "1. Analyzing current duplications..."

# AI_COMMON_INSTRUCTIONS.md의 'grep -A 10' 중복 수정
duplicates_in_common=$(grep -n "grep -A 10.*Priority 1.*PLAN.md" .ai-docs/AI_COMMON_INSTRUCTIONS.md | wc -l)

if [ "$duplicates_in_common" -gt 1 ]; then
    echo "🔧 Fixing 'grep -A 10' duplication in AI_COMMON_INSTRUCTIONS.md..."

    # 첫 번째 발생 위치 유지, 두 번째 발생을 참조로 변경
    sed -i.bak '
    /# 3\. 다음 해야 할 일 확인 (우선순위별)/,/grep -A 10 "Priority 1" \.ai-docs\/PLAN\.md/{
        s/grep -A 10 "Priority 1" \.ai-docs\/PLAN\.md/# → 상세 명령어는 위 "빠른 상태 파악 명령어" 섹션 참조/
    }
    ' .ai-docs/AI_COMMON_INSTRUCTIONS.md

    # 백업 파일 제거
    rm .ai-docs/AI_COMMON_INSTRUCTIONS.md.bak

    echo "✅ Fixed command duplication - converted to reference"
fi

# 다른 패턴 체크 및 수정
echo ""
echo "2. Checking other duplication patterns..."

# Priority 정보 중복 체크 (정보성 - 수정하지 않음)
priority_files=$(find .ai-docs -name "*.md" -exec grep -l "Priority 1.*Priority 2.*Priority 3" {} \; | wc -l)
if [ "$priority_files" -gt 1 ]; then
    echo "ℹ️  Priority information found in multiple files (acceptable - different contexts)"
fi

# 파일 구조 설명 중복 체크 (정보성)
structure_files=$(find .ai-docs -name "*.md" -exec grep -l "├── \.ai-docs/" {} \; | wc -l)
if [ "$structure_files" -gt 1 ]; then
    echo "ℹ️  File structure descriptions found in multiple files (acceptable - different purposes)"
fi

echo ""
echo "3. Validation check..."

# 수정 후 검증
./.ai-docs/duplication_check.sh > /tmp/duplication_check_result.txt 2>&1
check_result=$?

if [ $check_result -eq 0 ]; then
    echo "✅ Auto-fix successful - no duplications remain"
    rm -rf "$backup_dir"
    echo "🗑️  Backup removed (fix successful)"
    exit 0
else
    echo "⚠️  Some issues remain after auto-fix:"
    cat /tmp/duplication_check_result.txt
    echo ""
    echo "📋 Manual intervention required - see:"
    echo "   .ai-docs/reference/DUPLICATION_PREVENTION_CHECKLIST.md"
    echo ""
    echo "💾 Backup preserved at: $backup_dir"
    exit 1
fi