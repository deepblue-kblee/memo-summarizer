# 🚀 시스템 진입점 가이드

## 📋 개요

memo-summarizer는 app/ 디렉토리 기반의 단일 Python 패키지로 구성되어 있습니다. 모든 기능은 Console Scripts를 통해 접근할 수 있습니다.

## ⚙️ 초기 설정

### 1. 완전 자동 설정 (권장)
```bash
# 모든 환경 자동 설정 (가상환경, 패키지 설치, 디렉토리 생성)
./make_folders.sh
```

### 2. 시스템 검증
```bash
# 설치된 모든 구성 요소 확인
./run_health_check.sh
```

## 🎯 주요 Console Scripts

### 가상환경 활성화 후 사용
```bash
# 1. 가상환경 활성화
source app/venv/bin/activate

# 2. 메인 기능들
memo-processor /path/to/vault          # 메모 분석 및 처리
harness-linter                         # 품질 검증 도구
memo-analyzer                          # 메모 내용 분석
daily-reporter                         # 일일 보고서 생성
```

## 🔧 루트 레벨 래퍼 스크립트 (간편 사용)

### 일반 사용자용 (가상환경 자동 활성화)
```bash
./run_memo_processor.sh /path/to/vault # 메모 처리
./run_linter.sh                        # 품질 검증
./run_health_check.sh                  # 시스템 상태 확인
```

## 📂 시스템 구조

```
memo-summarizer/
├── app/                    # 🎯 단일 Python 패키지
│   ├── src/memo_summarizer/
│   │   ├── cli/           # Console Scripts 구현
│   │   ├── services/      # AI 클라이언트들
│   │   ├── core/          # 핵심 비즈니스 로직
│   │   ├── utils/         # 유틸리티 함수들
│   │   └── types/         # 타입 정의
│   ├── venv/              # Python 가상환경
│   ├── config/            # 설정 파일들
│   ├── logs/              # 런타임 로그
│   ├── tests/             # 테스트 코드
│   ├── scripts/           # 실행 스크립트
│   ├── setup.py           # 패키지 설정 (Console Scripts 정의)
│   └── requirements.txt   # 의존성
│
├── docs/                   # 🤖 문서 (AI + Human)
├── *.sh                   # 🚀 루트 래퍼 스크립트들
└── AGENTS.md              # 🎯 Agent 진입 가이드
```

## 🔄 작업 워크플로우

### 개발자 워크플로우
1. **환경 설정**: `./make_folders.sh`
2. **가상환경 진입**: `source app/venv/bin/activate`
3. **개발 작업**: Console Scripts 사용
4. **품질 검증**: `harness-linter`
5. **테스트 실행**: `python -m pytest app/tests/`

### 일반 사용자 워크플로우
1. **환경 설정**: `./make_folders.sh`
2. **시스템 확인**: `./run_health_check.sh`
3. **메모 처리**: `./run_memo_processor.sh /path/to/vault`
4. **품질 확인**: `./run_linter.sh`

## 🚨 문제 해결

### Console Scripts를 찾을 수 없는 경우
```bash
# 패키지 재설치
cd app
source venv/bin/activate
pip install -e .
```

### 가상환경 문제
```bash
# 가상환경 재생성
rm -rf app/venv
./make_folders.sh
```

### 문제 해결

**Import 오류**: `docs/ai/scenarios/bug-investigation.md` 참조

## 📋 Phase 3-A 준비 상태

- ✅ **단일 진입점**: app/ 패키지 확립
- ✅ **Console Scripts**: 4개 스크립트 설치 완료
- ✅ **자동화**: make_folders.sh 완전 자동 설정
- ✅ **래퍼 스크립트**: 사용 편의성 극대화
- 🔄 **다음 단계**: Observability 시스템 추가

## 🎉 성과

| 항목 | 이전 | 현재 | 개선도 |
|------|------|------|--------|
| **진입점** | .agent/ + app/ 혼재 | app/ 단일 | 100% 통합 |
| **설치** | 복잡한 수동 설정 | ./make_folders.sh | 완전 자동 |
| **사용성** | 경로 혼란 | Console Scripts | 직관적 |
| **유지보수** | 이중 구조 | 단일 패키지 | 대폭 개선 |