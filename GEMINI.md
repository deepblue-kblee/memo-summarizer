# 🟡 Gemini 환경 가이드

> **🎯 이 파일의 목적**: Gemini 환경에서 작업할 때 Gemini의 특장점과 최적 사용법만 설명. 공통 작업 지침은 [AI_COMMON_INSTRUCTIONS.md](.ai-docs/AI_COMMON_INSTRUCTIONS.md) 참조.

## 🚨 **필수 읽기 순서**
1. **[AI 공통 작업 지침](.ai-docs/AI_COMMON_INSTRUCTIONS.md)** ← 모든 작업 전 필수
2. **[PROGRESS.md](.ai-docs/PROGRESS.md)** ← 현재 완료 상태
3. **[PLAN.md](.ai-docs/PLAN.md)** ← 다음 우선순위 작업
4. 아래 Gemini 특화 내용

---

## ⚡ **Gemini 특장점**

✅ **빠른 처리**: 대량 파일 배치 처리에 최적화
✅ **비용 효율성**: 제한된 예산으로 최대 처리량 달성
✅ **한국어 특화**: 자연스러운 한국어 언어 처리 능력
✅ **실시간 처리**: 새로운 메모의 즉시 분류 및 처리

## 🎯 **Gemini 최적 사용 시기**

**🔥 Gemini를 선택해야 하는 경우:**
- 대량의 메모 파일을 빠르게 배치 처리
- 비용 효율성이 중요한 환경
- 실시간 메모 처리 및 분류 필요
- 한국어 자연어 처리의 정확도가 중요

**⚡ 기본 실행 명령어:**
```bash
# 표준 실행 (속도 우선)
./.agent/run /path/to/vault --ai gemini

# 대량 배치 처리 (Gemini 특화)
./.agent/run /path/to/vault --ai gemini --batch-mode

# 비용 최적화 모드
./.agent/run /path/to/vault --ai gemini --cost-optimized
```

## 💡 **Gemini vs 다른 AI**

| 작업 유형 | Gemini 추천도 | 이유 |
|-----------|---------------|------|
| **대량 배치 처리** | ⭐⭐⭐ | 빠른 속도와 효율적 처리 |
| **비용 최적화** | ⭐⭐⭐ | 높은 가성비와 토큰 효율성 |
| **한국어 자연어** | ⭐⭐⭐ | 한국어 특화 언어 모델 |
| **실시간 처리** | ⭐⭐⭐ | 빠른 응답 시간 |
| **복잡한 추론** | ⭐⭐ | 기본적인 분석은 가능하지만 Claude 대비 단순 |

## 🌐 **Gemini 한국어 특화 기능**

**한국어 최적화 키워드:**
- **프로젝트 마커**: "까지", "완료", "목표", "기한", "데드라인"
- **영역 마커**: "관리", "운영", "정기", "루틴", "지속"
- **행동 동사**: "하기", "확인", "조사", "요청", "문의"

**한국어 문맥 이해:**
- 비즈니스 용어 및 간접 표현 처리
- 존댓말/반말 구분 없이 일관된 작업 추출
- "할거임", "해야함" 같은 축약 표현 인식

## 🔧 **Gemini 특화 설정 (선택사항)**

고급 사용자를 위한 Gemini 최적화:
```json
{
  "gemini": {
    "temperature": 0.2,
    "focus": "speed",
    "korean_mode": true,
    "batch_size": 10
  }
}
```

---

## 📋 **참고 문서**
- **공통 워크플로우**: [AI_COMMON_INSTRUCTIONS.md](.ai-docs/AI_COMMON_INSTRUCTIONS.md)
- **시스템 아키텍처**: [SYSTEM.md](.ai-docs/SYSTEM.md)
- **다른 AI와 비교**: [CLAUDE.md](CLAUDE.md)

> **💡 Gemini 모범 사례**: 대량 처리나 비용 효율성이 중요한 작업에 집중 사용하고, 복잡한 분석이 필요한 경우 Claude 고려