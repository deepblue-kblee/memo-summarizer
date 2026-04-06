# 🚀 새 기능 개발 가이드

## 🎯 기능 개발 워크플로우

### 1단계: 개발 환경 준비
```bash
# 가상환경 활성화
source app/venv/bin/activate

# 현재 시스템 상태 확인
./run_health_check.sh

# 구조적 테스트 통과 확인
python app/tests/test_harness_structure.py
```

### 2단계: 기능 설계 및 계획
1. **기능 요구사항 정의**
2. **app/ 구조 내 적절한 위치 결정**
3. **Console Script 필요성 검토**
4. **기존 코드와의 통합점 파악**

### 3단계: 구현
1. **코드 작성**
2. **테스트 코드 추가**
3. **문서 업데이트**

## 📂 app/ 구조 기반 개발

### 코드 배치 가이드

```
app/src/memo_summarizer/
├── cli/               # Console Scripts, 사용자 인터페이스
├── services/          # 외부 서비스 (AI 클라이언트 등)
├── core/              # 핵심 비즈니스 로직
├── utils/             # 유틸리티 함수들
└── types/             # 타입 정의, 상수
```

#### 새 기능 배치 기준
- **CLI 도구**: `cli/` 디렉토리 + Console Script 등록
- **AI 서비스**: `services/` 디렉토리
- **비즈니스 로직**: `core/` 디렉토리
- **공통 유틸리티**: `utils/` 디렉토리
- **타입 정의**: `types/` 디렉토리

### Console Scripts 추가

#### 1. 구현 파일 작성
```python
# app/src/memo_summarizer/cli/new_feature.py
#!/usr/bin/env python3
"""새 기능 CLI 도구"""

import argparse
from pathlib import Path

def main():
    """메인 진입점"""
    parser = argparse.ArgumentParser(description="새 기능 설명")
    parser.add_argument("input", help="입력 경로")
    parser.add_argument("--verbose", action="store_true", help="상세 출력")

    args = parser.parse_args()

    # 기능 구현
    print(f"🚀 새 기능을 {args.input}에서 실행합니다...")

    return 0

if __name__ == "__main__":
    exit(main())
```

#### 2. setup.py에 Console Script 등록
```python
# app/setup.py
entry_points = {
    "console_scripts": [
        # 기존 스크립트들...
        "new-feature=memo_summarizer.cli.new_feature:main",  # 추가
    ],
}
```

#### 3. 패키지 재설치
```bash
cd app
pip install -e .
```

#### 4. 루트 래퍼 스크립트 생성 (선택사항)
```bash
# run_new_feature.sh
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/app/venv"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    new-feature "$@"
else
    echo "⚠️ Virtual environment not found. Please run ./make_folders.sh first."
    exit 1
fi
```

## 🧩 기존 시스템과의 통합

### 기존 모듈 활용
```python
# 기존 유틸리티 활용
from memo_summarizer.utils.file_manager import FileManager
from memo_summarizer.utils.markdown_processor import MarkdownProcessor

# 기존 AI 서비스 활용
from memo_summarizer.services.claude_client import ClaudeClient
from memo_summarizer.services.gemini_client import GeminiClient

# 기존 분석 엔진 활용
from memo_summarizer.cli.memo_analyzer import MemoAnalyzer
```

### 로깅 통합
```python
import logging
from pathlib import Path

# app/ 기준 로그 디렉토리
log_dir = Path(__file__).parent.parent.parent.parent / "logs"
log_file = log_dir / "new_feature.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
```

### 설정 파일 활용
```python
import json
from pathlib import Path

# app/config/ 설정 읽기
config_dir = Path(__file__).parent.parent.parent.parent / "config"
rules_file = config_dir / "rules.json"

if rules_file.exists():
    with open(rules_file, 'r') as f:
        rules = json.load(f)
```

## 🧪 테스트 추가

### 단위 테스트 작성
```python
# app/tests/test_new_feature.py
import unittest
from pathlib import Path
from memo_summarizer.cli.new_feature import main

class TestNewFeature(unittest.TestCase):
    def test_basic_functionality(self):
        """기본 기능 테스트"""
        # 테스트 구현
        pass

    def test_error_handling(self):
        """에러 처리 테스트"""
        # 테스트 구현
        pass

if __name__ == "__main__":
    unittest.main()
```

### 구조적 테스트 업데이트
```python
# app/tests/test_harness_structure.py에 추가
def test_new_feature_console_script(self):
    """새 기능 Console Script 테스트"""
    result = subprocess.run(
        ['new-feature', '--help'],
        capture_output=True,
        text=True
    )
    self.assertEqual(result.returncode, 0)
```

## 🔄 HarnessEngineering 원칙

### 자동화 우선
- **수동 단계 최소화**: Console Script로 모든 기능 접근
- **자동 검증**: 품질 검증이 자동화되도록 구현
- **자가 문서화**: --help, 명확한 메시지 출력

### 단일 진입점 유지
- **app/ 구조 준수**: .agent/ 스타일 복원 금지
- **Console Scripts**: 모든 기능은 Console Script로 노출
- **패키지 통합**: memo_summarizer 패키지 내부에서만 구현

### 관찰 가능성
- **로깅 통합**: 모든 중요 작업 로그 기록
- **에러 추적**: 구체적인 에러 메시지 및 복구 가이드
- **성능 모니터링**: 실행 시간, 리소스 사용량 추적

## 📋 개발 체크리스트

### 설계 단계
- [ ] 기능 요구사항 명확화
- [ ] app/ 구조 내 적절한 위치 결정
- [ ] 기존 코드 재사용 가능성 확인
- [ ] Console Script 필요성 검토

### 구현 단계
- [ ] 코드 작성 (app/src/memo_summarizer/ 내)
- [ ] Import 경로 확인 (패키지 기반)
- [ ] 로깅 통합
- [ ] 에러 처리 및 사용자 메시지

### Console Script 등록
- [ ] setup.py에 entry_points 추가
- [ ] 패키지 재설치 (`pip install -e app/`)
- [ ] 기능 테스트 (`new-feature --help`)
- [ ] 루트 래퍼 스크립트 생성 (선택사항)

### 테스트 및 검증
- [ ] 단위 테스트 작성
- [ ] 구조적 테스트 업데이트
- [ ] 전체 시스템 테스트 (`./run_health_check.sh`)
- [ ] 품질 검증 (`harness-linter`)

### 문서화
- [ ] 기능 설명 문서 작성
- [ ] docs/workflows/entry-points.md 업데이트
- [ ] README.md 업데이트 (필요 시)
- [ ] 사용법 예시 추가

## 💡 개발 팁

### 기존 패턴 따르기
```python
# CLI 모듈 기본 구조 (memo_analyzer.py 참고)
#!/usr/bin/env python3
"""모듈 설명"""

import argparse
from pathlib import Path
from memo_summarizer.services.claude_client import ClaudeClient

class NewFeature:
    def __init__(self, config_path: str = None):
        # 초기화
        pass

    def process(self, input_path: str) -> bool:
        # 주요 로직
        return True

def main():
    parser = argparse.ArgumentParser()
    # 인자 정의
    args = parser.parse_args()

    feature = NewFeature()
    success = feature.process(args.input)

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
```

### 점진적 개발
1. **최소 기능으로 시작**: Console Script만 먼저 구현
2. **테스트 추가**: 기본 동작 확인
3. **기능 확장**: 단계별로 기능 추가
4. **성능 최적화**: 마지막에 최적화

### 통합 테스트
```bash
# 개발 중 자주 실행할 명령어들
source app/venv/bin/activate
pip install -e .
new-feature --help
python app/tests/test_harness_structure.py
harness-linter
```

## 🔗 참고 자료

- **기존 구현**: `app/src/memo_summarizer/cli/` 디렉토리 참조
- **Console Script 패턴**: `memo_analyzer.py`, `main_controller.py`
- **서비스 패턴**: `services/claude_client.py`, `services/gemini_client.py`
- **유틸리티 패턴**: `utils/file_manager.py`, `utils/markdown_processor.py`

---

**🎯 목표**: HarnessEngineering 원칙에 따른 체계적이고 자동화된 기능 개발