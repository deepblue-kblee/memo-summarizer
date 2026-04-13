# 역할 및 책임 정의 (Roles and Responsibilities)

## 1. Planner Node (기획자)

### 핵심 책임
- **요구사항 분석**: 사용자 요청을 구체적이고 실행 가능한 작업으로 분해
- **Todo List 생성**: 우선순위가 명확한 작업 목록을 State에 저장
- **리소스 계획**: 각 작업에 필요한 시간, 도구, 종속성 분석
- **위험 관리**: 잠재적 문제점 식별 및 대안 계획 수립

### 주요 기능
```python
def analyze_requirements(user_request: str) -> List[Task]:
    """사용자 요청을 분석하여 구체적인 작업 목록 생성"""

def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    """작업 우선순위 설정 및 종속성 관리"""

def estimate_resources(task: Task) -> ResourceEstimate:
    """작업 수행에 필요한 리소스 추정"""
```

### 입력/출력
- **입력**: 사용자 요구사항, 현재 프로젝트 상태, 이전 작업 히스토리
- **출력**: 구조화된 Todo List, 작업 우선순위, 리소스 계획

### 성공 기준
- 생성된 Todo List의 완료율 90% 이상
- 예상 작업 시간 대비 실제 소요 시간 편차 20% 이내
- 사용자 요구사항 반영률 95% 이상

---

## 2. Core Engineer (핵심 개발자)

### 핵심 책임
- **코드 구현**: Todo List의 작업을 실제 코드로 구현
- **기존 코드 통합**: 기존 시스템과의 호환성 유지하며 새로운 기능 추가
- **에러 해결**: 이전 실패 이력을 학습하여 개선된 해결책 제시
- **코드 품질**: 가독성, 유지보수성, 성능을 고려한 코드 작성

### 주요 기능
```python
def implement_feature(task: Task, context: ProjectContext) -> CodeChanges:
    """할당된 작업을 실제 코드로 구현"""

def fix_errors(error_history: List[Error], current_error: Error) -> CodeFix:
    """이전 에러 히스토리를 학습하여 개선된 수정안 제시"""

def integrate_with_existing(new_code: Code, existing_system: System) -> Integration:
    """기존 시스템과의 원활한 통합 보장"""
```

### 입력/출력
- **입력**: Todo List, 프로젝트 컨텍스트, 에러 히스토리, 기존 코드베이스
- **출력**: 구현된 코드, 변경사항 요약, 테스트 가능한 모듈

### 성공 기준
- 첫 번째 구현에서 기본 테스트 통과율 80% 이상
- 코드 리뷰 통과율 95% 이상
- 기존 코드와의 통합 성공률 100%

---

## 3. Validator Node (검증자)

### 핵심 책임
- **자동 테스트**: pytest, npm test 등 프로젝트별 검증 도구 실행
- **정적 분석**: 린터, 타입 체커, 보안 스캔 도구 실행
- **결과 분석**: 테스트 결과를 구조화된 JSON 형식으로 변환
- **품질 보고**: 코드 품질 지표 및 개선 사항 제안

### 주요 기능
```python
def run_tests(project_path: str, test_type: TestType) -> TestResults:
    """프로젝트별 맞춤형 테스트 실행"""

def static_analysis(code_files: List[str]) -> AnalysisResults:
    """정적 분석 및 품질 검사"""

def security_scan(codebase: str) -> SecurityReport:
    """보안 취약점 스캔 및 보고"""
```

### 입력/출력
- **입력**: 수정된 코드, 프로젝트 설정, 테스트 구성
- **출력**: 테스트 결과 JSON, 품질 지표, 보안 리포트

### 성공 기준
- 테스트 실행 성공률 100%
- 결과 분석 정확도 98% 이상
- 보안 취약점 탐지율 95% 이상

---

## 4. Gatekeeper (관문지기)

### 핵심 책임
- **결과 판단**: 테스트 결과에 따른 Pass/Retry/Escalate 결정
- **재시도 관리**: 재시도 횟수 추적 및 무한 루프 방지
- **에스컬레이션**: 치명적 오류 시 인간 개입 요청
- **플로우 제어**: 다음 노드로의 전환 결정

### 주요 기능
```python
def evaluate_results(test_results: TestResults, retry_count: int) -> Decision:
    """테스트 결과 평가 및 다음 액션 결정"""

def manage_retries(error: Error, history: List[Attempt]) -> RetryStrategy:
    """재시도 전략 수립 및 관리"""

def escalate_issue(critical_error: Error, context: Context) -> EscalationRequest:
    """치명적 문제 시 인간 개입 요청"""
```

### 입력/출력
- **입력**: 테스트 결과, 재시도 히스토리, 에러 컨텍스트
- **출력**: 다음 액션 결정, 재시도 지시, 에스컬레이션 요청

### 성공 기준
- 정확한 판단 비율 98% 이상
- 무한 루프 발생률 0%
- 적절한 에스컬레이션 비율 5-10%

---

## 협업 프로토콜

### 1. 정보 공유
- **State Management**: 모든 에이전트는 SQLite State를 통해 정보 공유
- **Error History**: 실패 이력을 State에 기록하여 학습 효과 극대화
- **Context Preservation**: 작업 컨텍스트를 완전히 보존하여 연속성 보장

### 2. 작업 흐름
```
User Request → Planner → Engineer → Validator → Gatekeeper → [Pass|Retry|Escalate]
                 ↑                                ↓
                 └─────── Retry Loop ──────────┘
```

### 3. 의사소통 규칙
- **명확성**: 모든 메시지는 구체적이고 실행 가능해야 함
- **완전성**: 필요한 모든 컨텍스트 정보를 포함해야 함
- **추적가능성**: 모든 의사결정 과정을 State에 기록해야 함

### 4. 품질 관리
- **코드 리뷰**: Engineer가 작성한 코드는 Validator의 검증을 필수로 거침
- **테스트 우선**: 모든 변경사항은 테스트 통과를 전제로 함
- **문서화**: 중요한 결정사항은 반드시 문서로 기록

---

*최초 작성: 2026-04-13*
*최종 업데이트: 2026-04-13*