# 범용 LangGraph 에이전트 개발팀

**완전히 도메인 독립적인** 범용 에이전트 개발팀이 구축되었습니다. 사용자 요청을 받아 자동으로 계획 → 구현 → 검증 → 완료 워크플로우를 수행하며, 작업 완료 후 "다음에 무엇을 개발할까요?"라고 묻는 자율적 개발 환경을 제공합니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
# 프로젝트 루트에서 실행
pip install -r requirements.txt
```

### 2. 기본 사용법

```bash
# 단일 요청 처리
./agent-team run "Python 계산기 프로그램을 만들어줘"

# 대화형 모드 (연속적 상호작용)
./agent-team run --interactive

# 상태 조회
./agent-team status

# 히스토리 조회
./agent-team history
```

### 3. 시뮬레이션 테스트

```bash
# 모든 시나리오 실행
./agent-simulate

# 특정 시나리오 실행
./agent-simulate --scenario simple_file_creation

# 시나리오 목록 조회
./agent-simulate --list
```

## 🏗️ 아키텍처

### 핵심 구조

```
agent_team/harness/
├── agent_team.py       # 메인 StateGraph 진입점
├── state.py           # AgentState 및 SQLite 관리
├── simulator.py        # 워크플로우 시뮬레이션
├── user_interface.py   # 사용자 요청 처리
├── nodes/             # 4개 노드 구현
│   ├── base.py        # 공통 노드 베이스
│   ├── planner.py     # 범용 요구사항 분석
│   ├── engineer.py    # 범용 코드 구현
│   └── validator.py   # 범용 품질 검증
└── edges/
    └── gatekeeper.py  # Pass/Retry/Escalate 결정
```

### 워크플로우

1. **Planner**: 사용자 요청을 구체적인 Todo List로 분해
2. **Engineer**: Todo List를 실제 코드로 구현
3. **Validator**: 생성된 코드의 품질을 검증 (harness_linter 통합)
4. **Gatekeeper**: 검증 결과에 따른 Pass/Retry/Escalate 결정
5. **UserInterface**: 작업 완료 후 다음 요청 안내

## 🎯 주요 특징

### ✅ 완전한 범용성
- 프로그래밍 언어 독립적 (Python, JavaScript, Java, Go 등)
- 도메인 독립적 (웹, API, 데스크톱, CLI 등)
- 프레임워크 독립적 (Django, React, Spring 등)

### ✅ 자율적 운영
- 사용자 요청 → 자동 완료 → 다음 요청 대기 사이클
- 에러 발생 시 자동 재시도 및 학습
- 품질 기준 자동 강제 및 검증

### ✅ 품질 보장
- 기존 harness_linter.py 통합
- 구문 검증, 정적 분석, 테스트 실행
- 보안 검사 및 코드 스타일 검증

### ✅ 상태 지속성
- SQLite 기반 체크포인트 시스템
- 중단된 작업 재개 기능
- 전체 히스토리 추적

## 📋 지원하는 작업 타입

### 파일 생성
```bash
./agent-team run "hello.py 파일을 만들어줘"
./agent-team run "React 컴포넌트를 생성해줘"
```

### 기능 구현
```bash
./agent-team run "계산기 함수를 구현해줘"
./agent-team run "REST API를 만들어줘"
```

### 버그 수정
```bash
./agent-team run "broken.py의 오류를 수정해줘"
./agent-team run "메모리 누수를 찾아서 고쳐줘"
```

### 테스트 작성
```bash
./agent-team run "math_utils.py에 대한 테스트를 작성해줘"
./agent-team run "API 엔드포인트 테스트를 추가해줘"
```

### 리팩토링
```bash
./agent-team run "legacy_code.py를 더 깔끔하게 리팩토링해줘"
./agent-team run "중복 코드를 제거하고 최적화해줘"
```

## 🔍 시뮬레이션 시나리오

내장된 검증 시나리오들:

- **simple_file_creation**: 간단한 파일 생성
- **feature_implementation**: 기능 구현 요청
- **complex_project**: 복잡한 멀티파일 프로젝트
- **bug_fix_simulation**: 버그 수정 시뮬레이션
- **test_creation**: 테스트 코드 작성
- **refactoring_request**: 코드 리팩토링

```bash
# 특정 시나리오 정보 조회
./agent-simulate --info bug_fix_simulation

# 모든 시나리오 실행으로 검증
./agent-simulate
```

## ⚙️ 설정 및 커스터마이징

### 품질 임계값 조정
```python
config = {
    "quality_threshold": 7.0,  # 품질 점수 임계값
    "max_retries": 3,         # 최대 재시도 횟수
}

agent_team = AgentTeam(config=config)
```

### 데이터베이스 경로 설정
```bash
./agent-team run --db-path /custom/path/agent_states.db "요청 내용"
```

## 🔧 트러블슈팅

### 의존성 문제
```bash
# LangGraph 설치 확인
pip install langgraph langchain-core langchain-anthropic

# 전체 의존성 재설치
pip install -r requirements.txt --upgrade
```

### 권한 문제
```bash
# 실행 권한 부여
chmod +x agent-team agent-simulate
```

### 상태 초기화
```bash
# 데이터베이스 초기화 (주의: 모든 히스토리 삭제됨)
rm -f agent_team/tracking/agent_states.db
```

## 📊 성능 모니터링

### 상태 조회
```bash
# 전체 상태
./agent-team status

# 특정 요청 상태
./agent-team status req_20240413_143022

# 최근 히스토리
./agent-team history --limit 20
```

### 품질 메트릭
- 품질 점수: 0.0 - 10.0 (7.0 이상 통과)
- 재시도 횟수: 최대 3회
- 생성 파일 수: 작업 복잡도에 따라 가변
- 에러 해결률: 자동 학습으로 개선

## 🚧 향후 개선 사항

### Phase 4 (사용자 인터페이스)
- 웹 기반 대화형 인터페이스
- 실시간 진행상황 모니터링
- 세션 연속성 개선

### Phase 5 (최종 최적화)
- 성능 최적화 및 병렬 처리
- AI 클라이언트 다양화
- 플러그인 시스템 확장

## 📝 라이선스

이 프로젝트는 memo-summarizer 프로젝트의 일부로 개발되었습니다.

## 🤝 기여하기

1. 새로운 시나리오 추가
2. 품질 검증 로직 개선
3. 언어별 특화 기능 확장
4. 문서 개선

---

**🎉 범용 LangGraph 에이전트 개발팀이 준비되었습니다!**

이제 `./agent-team run --interactive`를 실행하고 "다음에 무엇을 개발할까요?"라는 질문을 받아보세요.