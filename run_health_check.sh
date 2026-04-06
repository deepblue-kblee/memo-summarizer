#!/bin/bash
# System Health Check 실행 스크립트
# Wrapper for future health-check console script

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

# Phase 3-A Observability Health Check
echo "🏥 System Health Check (Phase 3-A)"
echo "=================================="

# 기본 상태 확인
health-check --quick

echo ""
echo "📊 Observability Status:"
echo "  ✅ Performance Monitor: $(observability-monitor --help >/dev/null 2>&1 && echo 'Available' || echo 'Failed')"
echo "  ✅ Health Check System: $(health-check --help >/dev/null 2>&1 && echo 'Available' || echo 'Failed')"
echo "  ✅ Log Analyzer: $(log-analyzer --help >/dev/null 2>&1 && echo 'Available' || echo 'Failed')"

echo ""
echo "📈 Performance Metrics:"
observability-monitor --analyze 2>/dev/null || echo "  (No metrics data yet)"

echo ""
echo "📋 Log Summary:"
log-analyzer --summary 2>/dev/null || echo "  (No log data yet)"