# 🔵 Claude 환경 가이드

> **🎯 이 파일의 목적**: Claude 환경에서 즉시 개발 작업을 시작할 수 있도록 AI_COMMON_INSTRUCTIONS.md로 연결

## 🚨 **Claude 환경에서 작업 시작**

👉 **[AI 공통 작업 지침](.ai-docs/AI_COMMON_INSTRUCTIONS.md)** ← **모든 작업 전 필수 읽기**

**⚡ 작업 시작 흐름:**
```bash
1. 위 AI_COMMON_INSTRUCTIONS.md 읽기 (공통 워크플로우)
2. PROGRESS.md 읽기 (현재 완료 상태)
3. PLAN.md 읽기 (다음 우선순위 작업)
4. 즉시 개발 작업 시작 🚀
```

## ⚙️ **Claude 환경 전용 설정** (필요시만)

**기본 실행:**
```bash
# repo 개발 작업 (메모 분석, 코드 수정, 문서 업데이트 등)
./.agent/run /path/to/vault --ai claude
```

**고급 설정** (선택사항):
```json
{
  "claude": {
    "temperature": 0.1,
    "json_validation": "strict"
  }
}
```

---

**💡 핵심**: Claude든 다른 AI든 상관없이 **동일한 개발 작업** 수행. AI 선택은 사용자 몫.