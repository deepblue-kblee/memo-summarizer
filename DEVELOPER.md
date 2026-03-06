# 📦 Module Architecture Guide

Developer documentation for the Obsidian Memo Automation Agent's modular architecture.

## 🏗️ System Architecture Overview

The system follows a **modular, path-parameterized architecture** with clear separation of concerns and external configuration support.

```
.agent/
├── bin/                   # Core modules
│   ├── main_controller.py     # Orchestrator
│   ├── claude_client.py       # AI integration
│   ├── file_manager.py        # File operations
│   ├── memo_analyzer.py       # AI analysis engine
│   ├── markdown_processor.py  # Content processing
│   └── daily_reporter.py      # PARA reporting
├── config/                # External configuration
│   └── rules.json         # Classification & extraction rules
├── logs/                  # Runtime logs
└── run                    # Entry point wrapper
```

## 🎯 Core Modules

### 1. `main_controller.py` - System Orchestrator

**Purpose**: Path-parameterized main controller with PARA methodology integration.

**Key Features**:
- Vault path parameterization
- Module dependency injection
- PARA classification orchestration
- Comprehensive error handling

**Key Classes**:
```python
class AgentController:
    def __init__(self, vault_path: str)
    def analyze_all_files(self, date_filter: str = None) -> List[Dict[str, Any]]
    def analyze_and_merge_all_files(self, date_filter: str = None) -> List[Dict[str, Any]]
    def process_and_merge(self, file_path: Path, analysis: Dict[str, Any]) -> bool
```

**Usage**:
```python
controller = AgentController("/path/to/vault")
results = controller.analyze_and_merge_all_files("2026-03-05")
```

**Dependencies**: All other modules, operates as central orchestrator.

---

### 2. `claude_client.py` - AI API Integration

**Purpose**: Claude Code CLI wrapper with structured error handling and cost tracking.

**Key Features**:
- Claude Code CLI integration
- JSON output formatting
- Timeout handling
- Cost tracking

**Key Classes**:
```python
class ClaudeClient:
    def __init__(self)
    def call_claude_code(self, prompt: str) -> Dict[str, Any]
    def _check_claude_code_available(self)
```

**Response Format**:
```python
{
    "success": True,
    "content": "AI response content",
    "cost": 0.025591,
    "session_id": "session_123",
    "raw": {...}  # Full Claude response
}
```

**Error Handling**: Graceful degradation with structured error messages.

---

### 3. `file_manager.py` - PARA-aware File Operations

**Purpose**: Path-parameterized file I/O with PARA directory structure support and atomic operations.

**Key Features**:
- PARA directory management (Projects/Areas)
- Atomic write operations
- Safe file archival
- Path sanitization
- Collision-free naming

**Key Classes**:
```python
class FileManager:
    def __init__(self, base_path: str)
    def get_md_files(self, date_filter: str = None) -> List[Path]
    def get_agenda_file_path(self, topic: str, category: str = "Areas") -> Path
    def safe_update_file(self, file_path: Path, new_content: str) -> bool
    def archive_file(self, file_path: Path) -> bool
```

**PARA Directory Structure**:
- `01_AGENDAS/Projects/` - Goal-oriented projects with deadlines
- `01_AGENDAS/Areas/` - Ongoing responsibility areas

**Atomic Write Pattern**:
1. Rename existing → `_filename.md`
2. Write new content to original location
3. Delete backup on success, restore on failure

---

### 4. `memo_analyzer.py` - AI Analysis Engine

**Purpose**: AI-powered memo analysis with PARA classification and robust JSON parsing.

**Key Features**:
- External rules configuration loading
- Multi-stage JSON parsing with regex fallback
- PARA classification logic
- Comprehensive logging
- Cost tracking

**Key Classes**:
```python
class MemoAnalyzer:
    def __init__(self, vault_path: str = None)
    def analyze_memo(self, content: str) -> Dict[str, Any]
    def _extract_json_from_response(self, response_text: str) -> str
    def _log_to_file(self, message: str)
```

**AI Prompt Structure** (with PARA):
```python
prompt = f"""
분석할 메모: {content}

**PARA 분류 기준**:
- "Projects": {projects_keywords}
- "Areas": {areas_keywords}

REQUIRED JSON FORMAT:
{{
    "agendas": [
        {{
            "topic": "주제명",
            "category": "Projects|Areas",
            "tasks": ["할일1", "할일2"],
            "summary": "요약"
        }}
    ]
}}
"""
```

**JSON Parsing Pipeline**:
1. Direct JSON parse attempt
2. Regex extraction (`r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'`)
3. Whitespace cleaning + retry
4. Graceful failure with error topic

---

### 5. `markdown_processor.py` - Content Merging

**Purpose**: Intelligent markdown processing with duplicate detection and structure preservation.

**Key Features**:
- Section-based parsing
- Task deduplication
- History preservation
- Template generation

**Key Classes**:
```python
class MarkdownProcessor:
    def __init__(self)
    def parse_markdown_sections(self, content: str) -> Dict[str, Dict]
    def merge_with_existing_content(self, existing_content: str, topic: str,
                                   new_tasks: List[str], summary: str) -> str
    def create_new_agenda_file_content(self, topic: str, tasks: List[str], summary: str) -> str
```

**Generated File Structure**:
```markdown
# {topic}

## 🚀 할 일 목록
- Task 1
- Task 2 (new, non-duplicate)

## 📝 메모 이력
[2026-03-05] Latest summary
[2026-03-04] Previous entry
```

---

### 6. `daily_reporter.py` - PARA Statistics Reporting

**Purpose**: Generate comprehensive daily reports with PARA classification statistics.

**Key Features**:
- PARA-categorized statistics
- Obsidian link generation
- Comprehensive metadata
- Daily file management

**Key Classes**:
```python
class DailyReporter:
    def __init__(self, vault_path: str)
    def create_or_update_daily_report(self, processed_agendas: List[Dict[str, Any]]) -> bool
    def _generate_daily_report_content(self, projects: List[Dict], areas: List[Dict], today: str) -> str
```

**Report Structure**:
```markdown
# Daily Report - YYYY-MM-DD

## 🎯 Projects (목표 지향 프로젝트)
### 1. [[Projects/ProjectName]]
- **할 일**: N개
- **요약**: Summary

## 🏢 Areas (지속적 관리 영역)
### 1. [[Areas/AreaName]]
- **할 일**: N개
- **요약**: Summary

## 📈 PARA 처리 통계
| 분류 | 주제 수 | 할 일 수 |
|------|---------|----------|
| 🎯 Projects | X개 | Y개 |
| 🏢 Areas | X개 | Y개 |
```

---

## ⚙️ External Configuration

### `rules.json` - Classification & Extraction Rules

**Location**: `.agent/config/rules.json`

**Structure**:
```json
{
  "para_classification": {
    "projects": {
      "folder": "01_AGENDAS/Projects",
      "keywords": ["~까지", "기한", "데드라인", "출시", "완료", "(P)"],
      "description": "명확한 마감이나 목표가 있는 프로젝트성 주제"
    },
    "areas": {
      "folder": "01_AGENDAS/Areas",
      "keywords": ["정기", "관리", "운영", "1on1", "미팅", "(A)"],
      "description": "지속적인 업데이트가 필요한 책임 영역"
    }
  },
  "task_extraction": {
    "action_suffixes": ["해야 함", "하기", "할 것", "확인", "조사"],
    "indicators": ["- [ ]", "- "]
  },
  "priority_flags": {
    "(P)": "Projects",
    "(A)": "Areas"
  }
}
```

**Usage in Code**:
```python
import json
from pathlib import Path

def load_rules(vault_path: str) -> dict:
    rules_path = Path(vault_path) / ".agent" / "config" / "rules.json"
    with open(rules_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

---

## 🔄 Data Flow Architecture

### 1. Input Processing
```
00_INBOX/*.md → FileManager.get_md_files() → List[Path]
```

### 2. AI Analysis Pipeline
```
Memo Content → MemoAnalyzer.analyze_memo() →
Claude API → JSON Parsing → PARA Classification →
{agendas: [{topic, category, tasks, summary}]}
```

### 3. PARA File Generation
```
Analysis Results → FileManager.get_agenda_file_path(topic, category) →
MarkdownProcessor.merge_with_existing_content() →
FileManager.safe_update_file() → Projects/Areas/*.md
```

### 4. Reporting & Archival
```
Processed Agendas → DailyReporter.create_or_update_daily_report() →
02_DAILY_REPORTS/Daily_Report_YYYY-MM-DD.md

Original Files → FileManager.archive_file() →
00_INBOX/_ARCHIVED/ (with collision handling)
```

---

## 🛡️ Error Handling & Resilience

### 1. Graceful Degradation Hierarchy
```python
# Level 1: Individual file failure
try:
    analysis = analyzer.analyze_memo(content)
except Exception:
    # Continue with next file, log error

# Level 2: JSON parsing failure
try:
    result = json.loads(extracted_json)
except JSONDecodeError:
    # Return error topic, don't crash pipeline

# Level 3: File operation failure
try:
    file_manager.safe_update_file(path, content)
except Exception:
    # Restore backup, continue processing
```

### 2. Atomic Operations
All file modifications use the **rename-before-delete** pattern:
```python
def safe_update_file(self, file_path: Path, new_content: str) -> bool:
    if file_path.exists():
        backup_path = file_path.parent / f"_{file_path.name}"
        shutil.move(str(file_path), str(backup_path))  # 1. Backup
        try:
            with open(file_path, 'w') as f:
                f.write(new_content)  # 2. Write
            backup_path.unlink()  # 3. Delete backup on success
        except Exception:
            shutil.move(str(backup_path), str(file_path))  # 4. Restore on failure
            raise
```

### 3. Logging System
```python
# Structured logging levels
SUCCESS - PARSING_COMPLETE: 3 agendas found
ERROR - JSON_PARSE_FAILED: Invalid JSON structure
WARNING - DUPLICATE_TASK: Task already exists
INFO - API_COST: $0.025591
```

---

## 🔧 Extension Points

### 1. Adding New AI Providers
Extend `claude_client.py`:
```python
class OpenAIClient(ClaudeClient):
    def call_ai_service(self, prompt: str) -> Dict[str, Any]:
        # OpenAI implementation
        pass
```

### 2. Custom PARA Categories
Modify `rules.json`:
```json
{
  "para_classification": {
    "resources": {
      "folder": "01_AGENDAS/Resources",
      "keywords": ["참고", "자료", "링크", "(R)"],
      "description": "참조 자료 및 리소스"
    }
  }
}
```

### 3. Alternative Output Formats
Extend `markdown_processor.py`:
```python
class NotionProcessor(MarkdownProcessor):
    def generate_notion_page(self, topic: str, tasks: List[str]) -> Dict:
        # Notion API format
        pass
```

### 4. Custom Task Extraction
Modify `rules.json`:
```json
{
  "task_extraction": {
    "action_suffixes": ["검토", "승인", "배포", "테스트"],
    "priority_markers": ["urgent:", "asap:", "low:"],
    "due_date_patterns": ["by \\d{4}-\\d{2}-\\d{2}", "until .+"]
  }
}
```

---

## 📊 Performance Considerations

### 1. Scalability
- **File Processing**: Sequential (safe) vs Parallel (risky)
- **Memory Usage**: Streaming large files vs Loading entirely
- **API Costs**: Batch optimization vs Real-time processing

### 2. Optimization Points
```python
# Caching frequently accessed rules
@lru_cache(maxsize=1)
def get_classification_rules() -> dict:
    return load_rules_json()

# Lazy loading for large vaults
def get_md_files_generator(date_filter: str = None):
    for file_path in vault_path.glob("00_INBOX/*.md"):
        if matches_filter(file_path, date_filter):
            yield file_path
```

### 3. Resource Management
- **Vault Path Validation**: Early failure detection
- **File Locking**: Prevent concurrent access issues
- **Cleanup**: Automatic temp file removal

---

## 🧪 Testing Strategy

### 1. Unit Testing
```python
def test_para_classification():
    analyzer = MemoAnalyzer()
    content = "3월까지 API 개발 완료하기"
    result = analyzer.analyze_memo(content)
    assert result["agendas"][0]["category"] == "Projects"

def test_atomic_write_failure_recovery():
    file_manager = FileManager("/tmp/test")
    # Test backup restoration on write failure
```

### 2. Integration Testing
```python
def test_full_pipeline():
    controller = AgentController("/tmp/test_vault")
    # Create test memo → Run pipeline → Verify PARA output
```

### 3. Configuration Testing
```python
def test_rules_validation():
    rules = load_rules("/tmp/test_vault")
    assert "para_classification" in rules
    assert len(rules["para_classification"]["projects"]["keywords"]) > 0
```

---

## 📚 Development Guidelines

### 1. Code Style
- **Path Handling**: Always use `pathlib.Path`
- **Error Messages**: Include context and actionable steps
- **Logging**: Structured format with appropriate levels
- **Type Hints**: Full typing for all public methods

### 2. Module Dependencies
- **No Circular Imports**: Maintain clear dependency hierarchy
- **Minimal Coupling**: Each module should be independently testable
- **Vault Path Injection**: Never hard-code absolute paths

### 3. External Configuration
- **JSON Schema Validation**: Validate rules.json structure
- **Graceful Defaults**: Handle missing configuration gracefully
- **Hot Reloading**: Support configuration changes without restart

---

🔧 **This modular architecture enables easy extension, testing, and maintenance of the memo automation agent.**