#!/bin/bash
# PARA 메모 자동화 에이전트 실행 스크립트
# Wrapper for memo-processor console script

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
VENV_DIR="$SCRIPT_DIR/app/venv"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "⚠️ Virtual environment not found. Please run ./make_folders.sh first."
    exit 1
fi

# Run memo-processor with all arguments
memo-processor "$@"