#!/bin/bash

# 생성할 디렉터리 목록 정의
folders=(
    "01_AGENDAS/Areas"
    "01_AGENDAS/Projects"
    "02_DAILY_REPORTS"
)

echo "📂 디렉터리 구조 생성을 시작합니다..."

# 각 폴더 생성 루프
for folder in "${folders[@]}"; do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "✅ 생성 완료: $folder"
    else
        echo "⚠️ 이미 존재함: $folder"
    fi
done

echo "🚀 모든 구조가 준비되었습니다!"
