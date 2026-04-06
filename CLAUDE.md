# 🔵 Claude 환경 가이드

> **🎯 이 파일의 목적**: Claude 환경에서 즉시 개발 작업을 시작할 수 있도록 AI_COMMON_INSTRUCTIONS.md로 연결

## 🚨 **Claude 환경에서 작업 시작**

👉 **[AI 공통 작업 지침](.ai-docs/AI_COMMON_INSTRUCTIONS.md)** ← **모든 작업 전 필수 읽기**

**⚡ Claude 최적화 워크플로우:**
```bash
1. AI_COMMON_INSTRUCTIONS.md → 공통 작업 지침 확인
2. PROGRESS.md → 현재 상태 파악 (Claude의 정밀 분석 활용)
3. PLAN.md → 우선순위 작업 식별
4. Claude Code 환경에서 즉시 코딩 시작 🚀
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