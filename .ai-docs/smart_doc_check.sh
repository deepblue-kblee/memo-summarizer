#!/bin/bash
# 스마트 문서 정리 체크 시스템

# 색상 정의
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Smart Documentation Check${NC}"

# .last_cleanup 파일에서 마지막 정리 날짜 읽기
CLEANUP_FILE=".ai-docs/.last_cleanup"
if [ -f "$CLEANUP_FILE" ]; then
    LAST_CLEANUP=$(cat "$CLEANUP_FILE")
    echo -e "📅 마지막 정리: ${LAST_CLEANUP}"
else
    LAST_CLEANUP="1 week ago"
    echo -e "${YELLOW}⚠️  초기 실행 - 기본값: 1주일 전부터 확인${NC}"
fi

# Git 로그에서 .ai-docs 변경 횟수 계산
CHANGES=$(git log --oneline --since="$LAST_CLEANUP" .ai-docs/ 2>/dev/null | wc -l | tr -d ' ')

echo -e "📊 누적 변경: ${CHANGES}회 (.ai-docs 디렉토리)"

# 개별 파일별 변경 횟수 (상위 3개만 표시)
echo -e "\n📁 파일별 변경 현황:"
git log --oneline --since="$LAST_CLEANUP" --name-only .ai-docs/ 2>/dev/null | \
grep "^\.ai-docs/.*\.md$" | \
sort | uniq -c | sort -nr | head -3 | \
while read count file; do
    if [ "$count" -ge 5 ]; then
        echo -e "  ${RED}⚠️  $file: ${count}회${NC}"
    elif [ "$count" -ge 3 ]; then
        echo -e "  ${YELLOW}📝 $file: ${count}회${NC}"
    else
        echo -e "  ${GREEN}📄 $file: ${count}회${NC}"
    fi
done

# 트리거 조건 확인
TRIGGER_THRESHOLD=10
INDIVIDUAL_FILE_THRESHOLD=5

echo -e "\n🎯 트리거 조건 평가:"
echo -e "  전체 변경: ${CHANGES}회 (기준: ${TRIGGER_THRESHOLD}회)"

# 개별 파일 중 임계값 초과 확인
HIGH_CHANGE_FILES=$(git log --oneline --since="$LAST_CLEANUP" --name-only .ai-docs/ 2>/dev/null | \
grep "^\.ai-docs/.*\.md$" | sort | uniq -c | \
awk -v threshold="$INDIVIDUAL_FILE_THRESHOLD" '$1 >= threshold {print $2}' | wc -l | tr -d ' ')

# 결과 출력 및 권장사항
echo ""
if [ "$CHANGES" -ge "$TRIGGER_THRESHOLD" ] || [ "$HIGH_CHANGE_FILES" -gt 0 ]; then
    echo -e "${YELLOW}📋 문서 정리 권장${NC}"
    echo -e "  이유: "
    if [ "$CHANGES" -ge "$TRIGGER_THRESHOLD" ]; then
        echo -e "    - 전체 변경 횟수 임계값 초과 (${CHANGES} >= ${TRIGGER_THRESHOLD})"
    fi
    if [ "$HIGH_CHANGE_FILES" -gt 0 ]; then
        echo -e "    - 개별 파일 고빈도 변경: ${HIGH_CHANGE_FILES}개 파일"
    fi
    echo ""
    echo -e "${BLUE}🤔 문서 정리를 진행하시겠습니까?${NC}"
    echo -e "  ${GREEN}예${NC}: 의미론적 중복 분석 및 정리 실행"
    echo -e "  ${RED}아니오${NC}: 다음 세션까지 대기"
    echo ""
    echo -e "💡 정리 실행 명령어:"
    echo -e "  ${GREEN}./.ai-docs/duplication_check.sh${NC} (기본 중복 검사)"
    echo -e "  ${GREEN}AI에게 '문서 의미론적 정리 해줘'${NC} (전체 분석)"
    exit 1  # 권장 상태 (정리 필요)
else
    echo -e "${GREEN}✅ 문서 상태 양호${NC}"
    echo -e "  변경량이 적어 정리 불필요"
    exit 0  # 정상 상태
fi