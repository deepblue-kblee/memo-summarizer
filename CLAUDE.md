# 🔵 Claude 환경 가이드

> **🎯 이 파일의 목적**: Claude 환경에서 작업할 때 Claude의 특장점과 최적 사용법만 설명. 공통 작업 지침은 [AI_COMMON_INSTRUCTIONS.md](.ai-docs/AI_COMMON_INSTRUCTIONS.md) 참조.

## 🚨 **필수 읽기 순서**
1. **[AI 공통 작업 지침](.ai-docs/AI_COMMON_INSTRUCTIONS.md)** ← 모든 작업 전 필수
2. **[PROGRESS.md](.ai-docs/PROGRESS.md)** ← 현재 완료 상태
3. **[PLAN.md](.ai-docs/PLAN.md)** ← 다음 우선순위 작업
4. 아래 Claude 특화 내용

---

## ⚡ **Claude 특장점**

✅ **복잡한 분석**: 다층적 메모 분석 및 상세한 추론
✅ **높은 정확도**: 애매한 PARA 분류에서 뛰어난 판단력
✅ **구조화된 출력**: 안정적인 JSON 포맷 및 오류 복구
✅ **상세한 디버깅**: 문제 발생 시 구체적인 컨텍스트 제공

## 🎯 **Claude 최적 사용 시기**

**🔥 Claude를 선택해야 하는 경우:**
- 복잡하고 애매한 내용의 메모 분석
- 정확도가 중요한 PARA 분류 작업
- 오류 발생 시 상세한 디버깅 정보 필요
- JSON 구조가 복잡하거나 안정성이 중요한 경우

**⚡ 기본 실행 명령어:**
```bash
# 표준 실행 (정확도 우선)
./.agent/run /path/to/vault --ai claude

# 분석만 (테스트용)
./.agent/run /path/to/vault --ai claude --analysis-only

# 상세 로깅 (디버깅용)
./.agent/run /path/to/vault --ai claude --verbose
```

## 💡 **Claude vs 다른 AI**

| 작업 유형 | Claude 추천도 | 이유 |
|-----------|---------------|------|
| **복잡한 메모 분석** | ⭐⭐⭐ | 상세한 추론과 컨텍스트 이해 |
| **애매한 PARA 분류** | ⭐⭐⭐ | 뛰어난 판단력과 정확도 |
| **오류 디버깅** | ⭐⭐⭐ | 상세한 오류 컨텍스트 제공 |
| **대량 배치 처리** | ⭐⭐ | 정확하지만 상대적으로 느림 |
| **비용 최적화** | ⭐ | 고품질이지만 상대적으로 비쌈 |

## 🔧 **Claude 특화 설정 (선택사항)**

고급 사용자를 위한 Claude 최적화:
```json
{
  "claude": {
    "temperature": 0.1,
    "focus": "accuracy",
    "json_validation": "strict"
  }
}
```

---

## 📋 **참고 문서**
- **공통 워크플로우**: [AI_COMMON_INSTRUCTIONS.md](.ai-docs/AI_COMMON_INSTRUCTIONS.md)
- **시스템 아키텍처**: [SYSTEM.md](.ai-docs/SYSTEM.md)
- **다른 AI와 비교**: [GEMINI.md](GEMINI.md)

> **💡 Claude 모범 사례**: 정확도가 중요한 작업에 집중 사용하고, 대량 처리나 비용 최적화가 필요한 경우 Gemini 고려