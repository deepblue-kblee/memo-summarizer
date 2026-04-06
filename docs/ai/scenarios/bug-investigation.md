# 🐛 버그 조사 및 수정 가이드

## 🎯 버그 수정 워크플로우

### 1단계: 현재 시스템 상태 파악
```bash
# 시스템 전체 상태 확인
./run_health_check.sh

# 구조적 무결성 확인
source app/venv/bin/activate
python app/tests/test_harness_structure.py

# 품질 검증
harness-linter
```

### 2단계: 버그 재현 및 분석
```bash
# 가상환경 활성화
source app/venv/bin/activate

# 관련 Console Script 직접 실행
memo-processor --debug /path/to/test/vault
memo-analyzer --verbose
daily-reporter --dry-run
```

### 3단계: 로그 분석
```bash
# 최근 로그 확인
tail -50 app/logs/*.log

# 에러 패턴 검색
grep -r "ERROR\|Exception\|Traceback" app/logs/

# 특정 시간 범위 로그
find app/logs/ -name "*.log" -newermt "2026-04-06"
```

## 🔍 일반적인 문제 해결

### Import 오류
**증상**: `ModuleNotFoundError`, `ImportError`

**해결 방법**:
1. **패키지 재설치**
   ```bash
   cd app
   source venv/bin/activate
   pip install -e .
   ```

2. **Import 경로 확인**
   ```python
   # 올바른 형태
   from memo_summarizer.services.claude_client import ClaudeClient
   from memo_summarizer.utils.file_manager import FileManager

   # 잘못된 형태 (구 .agent/ 스타일)
   from claude_client import ClaudeClient
   from file_manager import FileManager
   ```

### Console Scripts 오류
**증상**: `command not found: memo-processor`

**해결 방법**:
1. **가상환경 확인**
   ```bash
   source app/venv/bin/activate
   which memo-processor
   ```

2. **패키지 재설치**
   ```bash
   pip install -e app/
   ```

### 경로 문제
**증상**: `FileNotFoundError`, 잘못된 경로 참조

**해결 방법**:
1. **절대 경로 사용**
   ```python
   from pathlib import Path
   vault_path = Path(vault_path).resolve()
   ```

2. **로그 디렉토리 경로 수정**
   ```python
   # 현재 구조 기준 (app/src/memo_summarizer/ 내부에서)
   log_dir = Path(__file__).parent.parent.parent.parent / "logs"
   ```

### API 연결 오류
**증상**: Claude/Gemini API 호출 실패

**해결 방법**:
1. **환경 설정 확인**
   ```bash
   cat app/.env
   # CLAUDE_API_KEY=...
   # GEMINI_API_KEY=...
   ```

2. **API 키 유효성 테스트**
   ```bash
   memo-analyzer --test-connection
   ```

## 🛠️ 디버깅 전략

### 상세 로깅 활성화
```python
# 임시 디버그 로깅 추가
import logging
logging.basicConfig(level=logging.DEBUG)

# 또는 파일 내에서
print(f"DEBUG: vault_path = {vault_path}")
print(f"DEBUG: current_dir = {Path.cwd()}")
```

### 단계적 테스트
```bash
# 1. 패키지 Import 테스트
python -c "import memo_summarizer; print('Package OK')"

# 2. 개별 모듈 테스트
python -c "from memo_summarizer.services.claude_client import ClaudeClient; print('Claude OK')"

# 3. Console Script 도움말 확인
memo-processor --help
harness-linter --help
```

### 가상환경 격리 테스트
```bash
# 새로운 가상환경에서 테스트
python3 -m venv test_env
source test_env/bin/activate
pip install -e app/
memo-processor --version
```

## 🔧 구조 관련 버그

### .agent/ 경로 참조 문제
**문제**: 구 코드에서 .agent/ 경로 참조

**해결**:
```python
# 변경 전
agent_dir = Path(__file__).parent.parent  # .agent/
logs_dir = agent_dir / "logs"

# 변경 후
app_dir = Path(__file__).parent.parent.parent.parent  # app/
logs_dir = app_dir / "logs"
```

### 설정 파일 경로 변경
**문제**: .agent/config/ → app/config/

**해결**:
```python
# 변경 전
config_path = Path(".agent/config/rules.json")

# 변경 후
from pathlib import Path
app_dir = Path(__file__).parent.parent.parent.parent
config_path = app_dir / "config" / "rules.json"
```

### Import 경로 업데이트
**문제**: 상대 import vs 패키지 import

**해결**:
```python
# CLI 모듈에서 다른 모듈 import
from memo_summarizer.services.claude_client import ClaudeClient
from memo_summarizer.utils.file_manager import FileManager
from memo_summarizer.core.memo_analyzer import MemoAnalyzer
```

## 📋 체크리스트

### 버그 보고 시 포함할 정보
- [ ] Python 버전: `python --version`
- [ ] 패키지 버전: `pip show memo-summarizer`
- [ ] 가상환경 상태: `which python`
- [ ] Console Scripts 상태: `which memo-processor`
- [ ] 에러 메시지 전문
- [ ] 재현 단계
- [ ] 관련 로그 파일

### 수정 후 검증
- [ ] 해당 기능 단위 테스트
- [ ] Console Scripts 정상 작동
- [ ] 구조적 테스트 통과
- [ ] 품질 검증 (harness-linter) 통과
- [ ] 전체 시스템 smoke test

## 🚨 긴급 복구

### 시스템 완전 재설정
```bash
# 1. 가상환경 재생성
rm -rf app/venv
./make_folders.sh

# 2. 구조 확인
./run_health_check.sh

# 3. 기본 기능 테스트
source app/venv/bin/activate
memo-processor --help
```

### 백업 복원 (필요 시)
```bash
# Git 상태 확인
git status
git log --oneline -5

# 특정 커밋으로 복원
git checkout <commit-hash>

# 또는 파일별 복원
git checkout HEAD~1 -- app/src/memo_summarizer/cli/main_controller.py
```

## 📖 관련 참고 자료

- **시스템 구조**: `docs/architecture/system-overview.md`
- **진입점 가이드**: `docs/workflows/entry-points.md`
- **테스트 가이드**: `app/tests/test_harness_structure.py`
- **설정 참조**: `app/_env.sample`

---

**💡 핵심**: app/ 단일 구조를 기반으로 한 체계적인 디버깅 접근