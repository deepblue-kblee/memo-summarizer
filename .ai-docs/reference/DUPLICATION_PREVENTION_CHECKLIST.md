# 🔍 중복 방지 점검 체크리스트

> **목적**: 정기적으로 문서 중복과 역할 침범을 확인하고 바로잡기 위한 체크리스트

## ⏰ **점검 시점**

### **필수 점검 시기**
- ✅ **주요 작업 완료 후** (Priority 작업 완료 시마다)
- ✅ **새로운 문서 추가/수정 시** (큰 변경사항 발생 시)
- ✅ **월 1회 정기 점검** (매월 첫째 주)
- ✅ **새로운 기여자 합류 시** (문서 혼란 방지)

### **권장 점검 시기**
- 📅 **새로운 AI 추가 시** (CLAUDE.md, GEMINI.md 수정 후)
- 📅 **시스템 아키텍처 변경 시** (SYSTEM.md 대폭 수정 후)
- 📅 **작업 플로우 변경 시** (AI_COMMON_INSTRUCTIONS.md 수정 후)

---

## 📋 **점검 체크리스트**

### **Phase 1: 자동 중복 검사 (5분)**

#### **1.1 동일 섹션명 검사**
```bash
# 동일한 섹션 제목이 여러 파일에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "빠른 상태 파악" {} \;
find .ai-docs -name "*.md" -exec grep -l "체크리스트" {} \;
find .ai-docs -name "*.md" -exec grep -l "Priority" {} \;
find .ai-docs -name "*.md" -exec grep -l "문서 구조" {} \;
```

#### **1.2 동일 명령어 중복 검사**
```bash
# 동일한 명령어가 여러 파일에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "git log --oneline" {} \;
find .ai-docs -name "*.md" -exec grep -l "grep -A" {} \;
find .ai-docs -name "*.md" -exec grep -l "git status" {} \;
```

#### **1.3 파일 구조 설명 중복 검사**
```bash
# 파일 구조 설명이 여러 곳에 있는지 확인
find .ai-docs -name "*.md" -exec grep -l "ai-docs/" {} \;
find .ai-docs -name "*.md" -exec grep -l "PROGRESS.md" {} \;
find .ai-docs -name "*.md" -exec grep -l "PLAN.md" {} \;
```

### **Phase 2: 역할 침범 검사 (10분)**

#### **2.1 PROGRESS.md 역할 검사**
- [ ] **미래 계획 내용이 있는가?** → PLAN.md로 이동
- [ ] **"앞으로", "다음에", "할 예정" 표현이 있는가?** → PLAN.md로 이동
- [ ] **[ ] 체크박스 할 일이 있는가?** → PLAN.md로 이동

#### **2.2 PLAN.md 역할 검사**
- [ ] **"완료됨", "달성됨" 과거 작업이 있는가?** → PROGRESS.md로 이동
- [ ] **상세한 Git 상태가 있는가?** → PROGRESS.md로 이동
- [ ] **현재 파일 구조 설명이 있는가?** → PROGRESS.md로 이동

#### **2.3 AI_COMMON_INSTRUCTIONS.md 역할 검사**
- [ ] **구체적인 Priority 1,2,3 내용이 있는가?** → PLAN.md로 이동
- [ ] **완료 작업 기록이 있는가?** → PROGRESS.md로 이동
- [ ] **아키텍처 상세 설명이 있는가?** → SYSTEM.md로 이동
- [ ] **파일 크기가 300줄 이상인가?** → 내용 분산 검토

### **Phase 3: 내용 일관성 검사 (10분)**

#### **3.1 상호 참조 검증**
- [ ] **PROGRESS.md의 "현재 브랜치" 정보가 최신인가?**
- [ ] **PLAN.md의 Priority 번호가 일관적인가?**
- [ ] **각 파일의 "마지막 업데이트" 날짜가 정확한가?**
- [ ] **파일 간 링크가 올바르게 작동하는가?**

#### **3.2 중복 제거 후 검증**
- [ ] **정보 손실 없이 중복이 제거되었는가?**
- [ ] **참조 링크가 올바르게 설정되었는가?**
- [ ] **각 파일이 독립적으로 이해 가능한가?**

---

## 🛠️ **중복 발견 시 해결 프로세스**

### **Step 1: 중복 유형 판단**
1. **완전 동일 중복**: 한 곳 제거, 다른 곳에서 참조
2. **부분 중복**: 공통 부분 추출 후 한 곳에 모으기
3. **역할 침범**: 적절한 파일로 내용 이동
4. **불필요한 중복**: 더 적절한 위치 판단 후 이동

### **Step 2: 우선순위 결정**
1. **핵심 역할 파일 우선**: PROGRESS(완료) > PLAN(미래) > 기타
2. **더 구체적인 파일 우선**: 구체적 내용 > 일반적 내용
3. **사용 빈도 높은 곳 우선**: 자주 참조되는 파일에 유지

### **Step 3: 안전한 제거**
```bash
# 백업 먼저
cp -r .ai-docs .ai-docs-backup-$(date +%Y%m%d)

# 내용 이동/수정
# (구체적 편집 작업)

# 검증
# 각 파일이 독립적으로 의미 있는지 확인

# 커밋
git add .ai-docs/
git commit -m "Remove documentation duplication - [구체적 변경사항]"
```

### **Step 4: 사후 검증**
- [ ] **각 파일이 역할에 충실한가?**
- [ ] **필요한 정보에 쉽게 접근 가능한가?**
- [ ] **참조 링크가 올바르게 작동하는가?**
- [ ] **새로운 중복이 생기지 않았는가?**

---

## 🚨 **자주 발생하는 중복 패턴**

### **위험 패턴 1: "빠른 명령어" 중복**
```bash
# 여러 파일에서 동일한 명령어 블록 반복
git log --oneline -3
git status
head -20 PROGRESS.md
```
**해결**: AI_COMMON_INSTRUCTIONS.md에만 유지, 다른 곳에서 참조

### **위험 패턴 2: "Priority 작업" 중복**
```markdown
Priority 1: 작업 연속성 완성
Priority 2: 문서 정리
Priority 3: 기능 확장
```
**해결**: PLAN.md에만 유지, 다른 곳에서는 간단 참조

### **위험 패턴 3: "파일 구조" 중복**
```bash
├── PROGRESS.md
├── PLAN.md
├── SYSTEM.md
```
**해결**: PROGRESS.md에만 상세 구조, 다른 곳에서는 링크

### **위험 패턴 4: "완료 작업" 혼재**
```markdown
✅ 완료: 문서 구조 정리 (PLAN.md에 잘못 위치)
```
**해결**: 무조건 PROGRESS.md로 이동

---

## 📊 **점검 결과 기록**

### **점검 기록 템플릿**
```markdown
## 중복 점검 결과 - YYYY-MM-DD

### 발견된 문제
- [ ] 파일명: 문제 설명
- [ ] 파일명: 문제 설명

### 수행한 수정
- [x] 파일명: 수정 내용
- [x] 파일명: 수정 내용

### 다음 점검 시 주의사항
- 주의할 패턴이나 경향

### 점검자: [이름]
### 소요 시간: [분]
```

### **기록 위치**
- **위치**: 이 파일 하단에 누적 기록
- **보존**: 최근 5회 점검 결과만 유지
- **참조**: 패턴 분석 및 재발 방지에 활용

---

## ⚡ **빠른 점검 스크립트**

### **자동 중복 검사 스크립트**
```bash
#!/bin/bash
# duplication_check.sh

echo "🔍 문서 중복 검사 시작..."

echo "1. 동일 섹션명 검사"
sections=("빠른 상태 파악" "Priority" "체크리스트" "파일 구조")
for section in "${sections[@]}"; do
    files=$(find .ai-docs -name "*.md" -exec grep -l "$section" {} \;)
    count=$(echo "$files" | wc -l)
    if [ $count -gt 1 ]; then
        echo "⚠️  '$section' 중복: $files"
    fi
done

echo "2. 동일 명령어 검사"
commands=("git log --oneline" "git status" "grep -A")
for cmd in "${commands[@]}"; do
    files=$(find .ai-docs -name "*.md" -exec grep -l "$cmd" {} \;)
    count=$(echo "$files" | wc -l)
    if [ $count -gt 1 ]; then
        echo "⚠️  '$cmd' 명령어 중복: $files"
    fi
done

echo "✅ 중복 검사 완료"
```

---

> **📋 마지막 업데이트**: 2026-03-24 - 중복 방지 체크리스트 작성
> **🔄 적용 시작**: 즉시 - 다음 작업 완료시부터 점검 실시