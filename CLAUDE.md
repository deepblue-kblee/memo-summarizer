# 🔵 Claude 환경 가이드

## 🚀 **즉시 시작**

👉 **[AGENTS.md](./AGENTS.md)** ← **모든 AI 공통 가이드**

Claude Code 환경에서는 AGENTS.md의 지침을 그대로 따르면 됩니다.

## ⚙️ **Claude 전용 명령어**

```bash
# 기본 사용
./run_health_check.sh         # 시스템 상태 확인
./run_memo_processor.sh /vault # 메모 처리

# Claude Code 통합 환경에서
source app/venv/bin/activate
memo-processor /vault --ai claude
```

---

**💡 핵심**: HarnessEngineering 완성으로 AI별 차이 없이 동일한 워크플로우 사용