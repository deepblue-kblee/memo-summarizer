#!/bin/bash

# Obsidian 메모 자동 처리기 실행 스크립트

echo "🚀 Obsidian 메모 프로세서를 시작합니다..."

# 현재 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다. 먼저 setup.sh를 실행해주세요."
    exit 1
fi

# API 키 확인
if grep -q "your_api_key_here" .env 2>/dev/null; then
    echo "⚠️  .env 파일에 Anthropic API 키를 설정해주세요."
    echo "    ANTHROPIC_API_KEY=your_actual_api_key"
    exit 1
fi

# Python 스크립트 실행
echo "▶️  메모 프로세서 실행 중..."
python memo_processor.py