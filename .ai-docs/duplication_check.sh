#!/bin/bash
# 문서 중복 검사 스크립트

echo "🔍 문서 중복 검사 시작..."

echo ""
echo "1. 빠른 상태 파악 명령어 중복 검사"
files=$(find .ai-docs -name "*.md" -exec grep -l "grep -A 10" {} \;)
count=$(echo "$files" | grep -v '^$' | wc -l)
if [ $count -gt 1 ]; then
    echo "⚠️  'grep -A 10' 명령어 중복 발견: $files"
else
    echo "✅ 명령어 중복 없음"
fi

echo ""
echo "2. Priority 정보 중복 검사"
files=$(find .ai-docs -name "*.md" -exec grep -l "Priority 1.*Priority 2.*Priority 3" {} \;)
count=$(echo "$files" | grep -v '^$' | wc -l)
if [ $count -gt 1 ]; then
    echo "⚠️  상세 Priority 정보 중복 발견: $files"
else
    echo "✅ Priority 정보 중복 없음"
fi

echo ""
echo "3. 파일 구조 설명 중복 검사"
files=$(find .ai-docs -name "*.md" -exec grep -l "├── .ai-docs/" {} \;)
count=$(echo "$files" | grep -v '^$' | wc -l)
if [ $count -gt 1 ]; then
    echo "⚠️  파일 구조 설명 중복 발견: $files"
else
    echo "✅ 파일 구조 중복 없음"
fi

echo ""
echo "✅ 중복 검사 완료"