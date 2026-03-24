#!/bin/bash
# 문서 정리 완료 마킹 스크립트

echo "✅ 문서 정리 완료 - 날짜 기록 중..."

# 현재 날짜를 .last_cleanup에 저장
date "+%Y-%m-%d %H:%M:%S" > .ai-docs/.last_cleanup

echo "📅 정리 완료 시점: $(cat .ai-docs/.last_cleanup)"
echo "🎯 다음 트리거까지 변경 카운터 리셋됨"

# Git에 .last_cleanup 파일 추가 (선택사항)
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add .ai-docs/.last_cleanup 2>/dev/null || true
    echo "📁 Git tracking에 추가됨"
fi

echo "✨ 완료 - 다음 세션부터 새로운 카운팅 시작"