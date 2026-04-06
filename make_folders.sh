#!/bin/bash

# 생성할 디렉터리 목록 정의 (vault/ 하위)
folders=(
    "vault/00_INBOX/_ARCHIVED"
    "vault/01_AGENDAS/Areas"
    "vault/01_AGENDAS/Projects"
    "vault/02_DAILY_REPORTS"
)

# 생성할 app/ 디렉터리 목록
app_folders=(
    "app/logs"
    "app/build"
    "app/config"
)

echo "📂 디렉터리 구조 생성을 시작합니다..."

# vault/ 폴더 생성 루프
for folder in "${folders[@]}"; do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "✅ 생성 완료: $folder"
    else
        echo "⚠️ 이미 존재함: $folder"
    fi
done

echo "🔧 앱 환경 초기화를 시작합니다..."

# app/ 폴더 생성 루프
for folder in "${app_folders[@]}"; do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "✅ 생성 완료: $folder"
    else
        echo "⚠️ 이미 존재함: $folder"
    fi
done

# Python 가상환경 생성
if [ ! -d "app/venv" ]; then
    echo "🐍 Python 가상환경 생성 중..."
    python3 -m venv app/venv
    if [ $? -eq 0 ]; then
        echo "✅ 가상환경 생성 완료: app/venv"
    else
        echo "❌ 가상환경 생성 실패"
    fi
else
    echo "⚠️ 가상환경이 이미 존재함: app/venv"
fi

# 가상환경 활성화 및 패키지 설치
if [ -d "app/venv" ] && [ -f "app/setup.py" ]; then
    echo "📦 패키지 설치 중..."
    source app/venv/bin/activate
    pip install --upgrade pip
    pip install -e app/
    if [ -f "app/requirements.txt" ]; then
        pip install -r app/requirements.txt
    fi
    deactivate
    echo "✅ 패키지 설치 완료"
fi

# 환경 설정 파일 초기화
if [ ! -f "app/.env" ] && [ -f "app/scripts/_env.sample" ]; then
    echo "⚙️ 환경 설정 파일 생성 중..."
    cp app/scripts/_env.sample app/.env
    echo "✅ 환경 설정 파일 생성 완료: app/.env"
    echo "💡 app/.env 파일에서 API 키와 설정을 수정하세요"
else
    if [ -f "app/.env" ]; then
        echo "⚠️ 환경 설정 파일이 이미 존재함: app/.env"
    fi
fi

# Console Scripts 확인
echo "🔧 Console Scripts 확인 중..."
source app/venv/bin/activate
if command -v memo-processor >/dev/null 2>&1; then
    echo "✅ memo-processor: 사용 가능"
else
    echo "❌ memo-processor: 설치 실패"
fi

if command -v harness-linter >/dev/null 2>&1; then
    echo "✅ harness-linter: 사용 가능"
else
    echo "❌ harness-linter: 설치 실패"
fi

if command -v memo-analyzer >/dev/null 2>&1; then
    echo "✅ memo-analyzer: 사용 가능"
else
    echo "❌ memo-analyzer: 설치 실패"
fi

if command -v daily-reporter >/dev/null 2>&1; then
    echo "✅ daily-reporter: 사용 가능"
else
    echo "❌ daily-reporter: 설치 실패"
fi
deactivate

echo ""
echo "🚀 모든 구조와 환경이 준비되었습니다!"
echo ""
echo "📝 다음 단계:"
echo "   1. app/.env에서 API 키 설정"
echo "   2. 구조적 테스트 실행: python3 app/tests/test_harness_structure.py"
echo "   3. 시스템 검증: ./run_health_check.sh"
echo "   4. 메모 처리기 실행: ./run_memo_processor.sh /path/to/vault"
echo "   5. 품질 검증: ./run_linter.sh"
echo ""
echo "🎯 Console Scripts (가상환경 활성화 후):"
echo "   - memo-processor /path/to/vault"
echo "   - harness-linter"
echo "   - memo-analyzer"
echo "   - daily-reporter"
