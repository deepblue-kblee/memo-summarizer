# 🤖 Memo Automation Agent - System Overview

> **Base Reference Document**: This document contains the complete system architecture and common functionality shared by all AI providers (Claude, Gemini, etc.). For AI-specific features, see individual AI guide files.

## 📋 Project Essence

This is an **Obsidian Memo Automation Agent** - an AI-powered note processing pipeline that analyzes unstructured memos from `00_INBOX/` and intelligently organizes them into structured agenda files. The system uses AI to extract multiple topics from single memos, performs automatic classification (Projects vs Areas structure inspired by PARA methodology), and maintains organized project files with enhanced logging and error recovery.

**Key Features**:
- 🔍 **Multi-topic extraction**: Automatic separation of multiple independent topics from single memo
- 📝 **Intelligent task extraction**: Convert natural language text to actionable tasks
- 🎯 **Automatic classification**: Projects (goal-oriented) vs Areas (management-oriented) structure
- 🔧 **External configuration**: Classification keywords and rules managed in `.agent/config/rules.json`
- 🛡️ **Atomic Write pattern**: Backup → Write → Verify to prevent data loss
- 📊 **Comprehensive logging**: Real-time debugging, API cost tracking, detailed audit trail
- 🚀 **Vault portability**: Path-parameterized execution for any Obsidian vault

## 🏗️ System Architecture

### NEW: .agent Package Architecture (Isolated System)

**Directory Structure:**
```
Vault_Root/
├── 00_INBOX/              # 📥 Input: Raw memo files
│   └── _ARCHIVED/         # 🗂️ Processed files (auto-managed)
├── 01_AGENDAS/            # 📋 Output: PARA-classified agenda files
│   ├── Projects/          # 🎯 Goal-oriented projects with deadlines
│   └── Areas/             # 🏢 Ongoing responsibility areas
├── 02_DAILY_REPORTS/      # 📊 Daily summary reports
│
└── .agent/                # 🤖 Agent package (isolated from Obsidian)
    ├── bin/               # 🛠️ Modular Python scripts
    │   ├── main_controller.py     # Main orchestrator
    │   ├── claude_client.py       # AI API integration
    │   ├── file_manager.py        # File I/O with path parameters
    │   ├── memo_analyzer.py       # AI analysis + Projects/Areas classification
    │   ├── markdown_processor.py  # Markdown processing
    │   └── daily_reporter.py      # Daily reports
    ├── config/            # ⚙️ Configuration files
    │   └── rules.json     # Classification keywords & task extraction rules
    ├── venv/              # 🐍 Isolated Python environment
    ├── logs/              # 📋 Daily activity logs
    └── run                # 🚀 Entry point script
```

### Core Modules (Enhanced with PARA & Path Parameters)

1. **`main_controller.py`** - Path-parameterized orchestrator with PARA support
2. **`claude_client.py`** - AI API integration with multiple provider support
3. **`file_manager.py`** - Path-based file operations with PARA directory management
4. **`memo_analyzer.py`** - AI analysis engine with Projects/Areas classification logic
5. **`markdown_processor.py`** - Markdown processing (unchanged)
6. **`daily_reporter.py`** - Enhanced daily reporting with PARA statistics

### Enhanced Data Flow with PARA Classification
```
INPUT: 00_INBOX/*.md →
Path-Parameterized File Scanning →
AI Analysis with PARA Classification →
Multi-Topic Extraction (Projects vs Areas) →
Markdown Processing & Directory-based Merging →
OUTPUT:
  - 01_AGENDAS/Projects/{topic}.md (🎯 Goal-oriented projects)
  - 01_AGENDAS/Areas/{topic}.md (🏢 Ongoing responsibility areas)
  - 02_DAILY_REPORTS/Daily_Report_YYYY-MM-DD.md (📊 PARA statistics)
  - 00_INBOX/_ARCHIVED/{original}.md (🗂️ Safe archival)
  - .agent/logs/YYYY-MM-DD.log (📋 Detailed audit trail)
```

## ⚙️ Core Commands (AI-Agnostic)

### Basic Execution
```bash
# Full pipeline: memo analysis + Projects/Areas classification + archive
./.agent/run /path/to/vault

# Analysis only (read-only, no file modifications)
./.agent/run /path/to/vault --analysis-only

# Process specific date only (YYYY-MM-DD format)
./.agent/run /path/to/vault --date 2026-02-11

# JSON output format with Projects/Areas classification
./.agent/run /path/to/vault --json

# Combined options
./.agent/run /path/to/vault --date 2026-02-11 --analysis-only --json

# Help information
./.agent/run --help

# Example with current directory as vault
./.agent/run $(pwd) --analysis-only
```

### System Setup
```bash
# Create required directories
mkdir -p 00_INBOX 01_AGENDAS

# Activate virtual environment
source venv/bin/activate

# Set executable permissions
chmod +x run_agent.sh start_memo_processor.sh
```

### Development & Debugging
```bash
# View analysis logs (daily files with enhanced logging)
cat logs/memo_analyzer_$(date +%Y-%m-%d).log

# Check directory structure and file counts
ls -la 00_INBOX/ 01_AGENDAS/ 00_INBOX/_ARCHIVED/
find 01_AGENDAS/ -name "*.md" | wc -l

# Date-specific processing for debugging
./.agent/run /path/to/vault --date 2026-02-11 --analysis-only

# JSON validation and structure check
./.agent/run /path/to/vault --date 2026-02-11 --json
```

## 🎯 PARA Classification System (Rule-based)

The AI system automatically classifies topics using configurable rules from `.agent/config/rules.json`:

### External Configuration (`.agent/config/rules.json`)
The system avoids hard-coded logic by loading classification keywords and task extraction rules from an external configuration file:

```json
{
  "para_classification": {
    "projects": {
      "folder": "01_AGENDAS/Projects",
      "keywords": ["~까지", "기한", "데드라인", "출시", "완료", "개발", "셋업", "구축", "배포", "런칭", "(P)"],
      "description": "Goal-oriented projects with deadlines"
    },
    "areas": {
      "folder": "01_AGENDAS/Areas",
      "keywords": ["정기", "관리", "운영", "매달", "지속", "루틴", "1on1", "미팅", "가이드", "정책", "피드백", "(A)"],
      "description": "Ongoing responsibility areas"
    }
  },
  "task_extraction": {
    "action_suffixes": ["해야 함", "하기", "할 것", "확인", "조사", "요청", "문의", "셋업", "배포"],
    "indicators": ["- [ ]", "- "]
  },
  "priority_flags": {
    "(P)": "Projects",
    "(A)": "Areas"
  }
}
```

### Classification Logic

**Projects** (→ `01_AGENDAS/Projects/`):
- Tasks with clear deadlines or completion goals
- **Keywords**: `~까지`, `기한`, `데드라인`, `출시`, `완료`, `개발`, `셋업`, `구축`, `배포`, `런칭`, `(P)`
- **Examples**: "새로운 기능 개발", "시스템 마이그레이션 3월까지", "제품 출시", "API 셋업"

**Areas** (→ `01_AGENDAS/Areas/`):
- Ongoing responsibility areas requiring continuous maintenance
- **Keywords**: `정기`, `관리`, `운영`, `매달`, `지속`, `루틴`, `1on1`, `미팅`, `가이드`, `정책`, `피드백`, `(A)`
- **Examples**: "팀 1on1 관리", "정기 미팅", "성과 피드백", "운영 가이드 업데이트"

**Priority Override**: Use `(P)` or `(A)` flags in memo content to force specific classification regardless of keywords.

## 🧠 Intelligent Task Extraction (Suffix-based)

To support "roughly written" notes, the system automatically converts descriptive bullet points into actionable tasks:

* **Action Suffixes**: Lines ending with `해야 함`, `하기`, `할 것`, `확인`, `조사`, `요청`, `문의`, `셋업`, `배포` are converted to checkbox tasks (`- [ ]`)
* **Deduplication Logic**: Tasks are matched against existing agenda files to prevent duplicate entries
* **Natural Language Processing**: The AI identifies action items even in conversational Korean text

## 🛡️ Smart Merging & Atomic Write Operations

The system ensures data integrity through sophisticated file handling patterns:

### History Preservation
The `## 📝 메모 이력` section is append-only with timestamps and links to archived source files

### Atomic Write Pattern
1. Rename existing file to `_filename.md` (backup)
2. Write new merged content to original location
3. Delete backup only upon verified success
4. Restore backup if any step fails

### Source Traceability
Every merge includes a link back to the archived source: `[[00_INBOX/_ARCHIVED/filename|View Source]]`

## 🔄 Multi-Topic Support

**Key Architectural Patterns**:
- Single memo can generate multiple independent agenda files
- Input: One memo discussing "Mixpanel issues" and "Blog development"
- Output: `Mixpanel.md` + `블로그_자동화_도구.md` (separate files)

## 📊 Generated File Formats

### Agenda Files (`01_AGENDAS/{Projects|Areas}/{sanitized_topic_name}.md`)
```markdown
# Topic Name

## 🚀 할 일 목록
- Task 1
- Task 2

## 📝 메모 이력
[2026-02-12] Summary of today's additions
```

### Daily Summary (`02_DAILY_REPORTS/Daily_Report_YYYY-MM-DD.md`)
```markdown
# Daily Report - 2026-02-12

## 📋 오늘 처리된 주제들

### 🎯 Projects
#### 1. [[Projects/Topic1]]
- **할 일**: 3개
- **요약**: Brief summary

### 🏢 Areas
#### 1. [[Areas/Topic2]]
- **할 일**: 2개
- **요약**: Brief summary

## 📊 처리 통계
- **총 주제 수**: 2개
- **총 할 일**: 5개
```

## 🔧 Dependencies & Requirements

### External Dependencies
- **AI CLI Tool**: Must be installed and on PATH (varies by AI provider)
- **Python 3.x**: Standard library only, no external packages required
- **Directory Structure**: `00_INBOX/` and `01_AGENDAS/` must exist

### Configuration
- **AI CLI**: Uses respective CLI settings automatically
- **Rules Configuration**: `.agent/config/rules.json` contains classification keywords and task extraction rules
- **`.env` file** (optional): API key, scheduling, logging configuration
- **Virtual Environment**: `venv/` recommended but not required

## 🎯 Path Portability & Vault-Agnostic Design

Every module calculates paths relative to the **Vault Root Path** provided at runtime:

* **No Hard-coded Paths**: All file operations use vault_path parameter for complete portability
* **Relative Path Resolution**: `.agent/` package maintains isolation while supporting any vault location
* **Cross-Platform Compatibility**: Uses `pathlib.Path` for Windows/macOS/Linux compatibility
* **Multiple Vault Support**: Same system can process different vaults by changing the path parameter

## 🛠️ Error Handling Philosophy

The system prioritizes **graceful degradation** over strict validation:
- API failures → Continue with error topic instead of stopping
- JSON parse errors → Log raw response and continue
- File operation failures → Restore backups and continue
- Individual file failures → Skip file but process remaining

## 📈 Testing Approach

Use `--analysis-only` mode for safe testing:
```bash
# Preview what would happen without modifying files
./.agent/run /path/to/vault --analysis-only
```

## 📋 Debugging Workflow

1. **Check logs**: `.agent/logs/memo_analyzer_YYYY-MM-DD.log` for detailed trace
2. **Terminal output**: Real-time AI responses printed during execution
3. **JSON validation**: Raw AI responses logged for inspection
4. **File state**: Verify directory contents before/after processing

## 🚀 System Health Checks

```bash
# Verify agent package structure
ls -la .agent/bin/

# Check virtual environment
.agent/venv/bin/python --version

# Validate PARA directory structure
ls -la 01_AGENDAS/Projects/ 01_AGENDAS/Areas/ 02_DAILY_REPORTS/

# Test system structure
./.agent/run $(pwd) --help
```

## 🔧 Extension & Development Guide

### 🚀 Adding New AI Providers

Extend the system to support additional AI providers by following this pattern:

```python
# Extend claude_client.py for new providers
class OpenAIClient(ClaudeClient):
    def call_ai_service(self, prompt: str) -> Dict[str, Any]:
        # OpenAI API implementation
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            temperature=0.1
        )
        return {
            "success": True,
            "content": response.choices[0].text,
            "cost": calculate_openai_cost(response.usage),
            "session_id": f"openai_{uuid.uuid4()}",
            "raw": response
        }

class GeminiClient(ClaudeClient):
    def call_ai_service(self, prompt: str) -> Dict[str, Any]:
        # Gemini API implementation
        pass
```

### 📋 Custom PARA Categories

Add new PARA categories by modifying `.agent/config/rules.json`:

```json
{
  "para_classification": {
    "resources": {
      "folder": "01_AGENDAS/Resources",
      "keywords": ["참고", "자료", "링크", "문서", "(R)"],
      "description": "참조 자료 및 리소스"
    },
    "archive": {
      "folder": "01_AGENDAS/Archive",
      "keywords": ["완료", "종료", "마감", "보관", "(X)"],
      "description": "완료된 프로젝트 보관소"
    }
  }
}
```

### 🔄 Alternative Output Formats

Extend `markdown_processor.py` for different output formats:

```python
class NotionProcessor(MarkdownProcessor):
    def generate_notion_page(self, topic: str, tasks: List[str]) -> Dict:
        return {
            "object": "page",
            "properties": {
                "title": {"title": [{"text": {"content": topic}}]},
                "tasks": {"rich_text": [{"text": {"content": task}} for task in tasks]}
            }
        }

class JiraProcessor(MarkdownProcessor):
    def create_jira_issue(self, topic: str, tasks: List[str]) -> Dict:
        return {
            "summary": topic,
            "description": "\n".join(f"* {task}" for task in tasks),
            "issuetype": {"name": "Task"}
        }
```

### ⚡ Performance Optimization

#### Caching Strategy
```python
from functools import lru_cache

# Cache frequently accessed rules
@lru_cache(maxsize=1)
def get_classification_rules() -> dict:
    return load_rules_json()

# Cache AI responses for identical content
@lru_cache(maxsize=100)
def cached_analyze_memo(content_hash: str, content: str) -> Dict[str, Any]:
    return memo_analyzer.analyze_memo(content)
```

#### Scalability Considerations
```python
# Lazy loading for large vaults
def get_md_files_generator(vault_path: Path, date_filter: str = None):
    """Memory-efficient file iteration for large vaults"""
    for file_path in vault_path.glob("00_INBOX/*.md"):
        if matches_date_filter(file_path, date_filter):
            yield file_path

# Batch processing for API efficiency
def analyze_batch(contents: List[str], batch_size: int = 5) -> List[Dict]:
    """Process multiple memos in batches to optimize API calls"""
    results = []
    for i in range(0, len(contents), batch_size):
        batch = contents[i:i + batch_size]
        batch_results = [analyzer.analyze_memo(content) for content in batch]
        results.extend(batch_results)
    return results
```

#### Resource Management
- **File Locking**: Prevent concurrent access issues with `fcntl` (Unix) or `msvcrt` (Windows)
- **Memory Monitoring**: Use `psutil` for memory usage tracking in large vault processing
- **Cleanup**: Automatic removal of temporary files and backup cleanup

### 🧪 Testing Strategy

#### Unit Testing Examples
```python
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

def test_para_classification():
    """Test PARA classification accuracy"""
    analyzer = MemoAnalyzer()

    # Test Projects classification
    project_content = "3월까지 API 개발 완료하기"
    result = analyzer.analyze_memo(project_content)
    assert result["agendas"][0]["category"] == "Projects"

    # Test Areas classification
    area_content = "팀 1on1 미팅 정기 진행"
    result = analyzer.analyze_memo(area_content)
    assert result["agendas"][0]["category"] == "Areas"

def test_atomic_write_failure_recovery():
    """Test backup restoration on write failure"""
    file_manager = FileManager("/tmp/test_vault")
    test_path = Path("/tmp/test_vault/test.md")

    # Create initial file
    test_path.write_text("original content")

    # Mock write failure
    with patch('builtins.open', side_effect=IOError("Write failed")):
        with pytest.raises(IOError):
            file_manager.safe_update_file(test_path, "new content")

    # Verify backup restoration
    assert test_path.read_text() == "original content"
```

#### Integration Testing
```python
def test_full_pipeline():
    """Test complete memo processing pipeline"""
    controller = AgentController("/tmp/test_vault")

    # Setup test environment
    setup_test_vault("/tmp/test_vault")
    create_test_memo("/tmp/test_vault/00_INBOX/test_memo.md",
                    "API 셋업하기\n팀 미팅 정기 진행")

    # Run analysis
    results = controller.analyze_and_merge_all_files()

    # Verify outputs
    assert len(results) == 2
    assert Path("/tmp/test_vault/01_AGENDAS/Projects/API_셋업.md").exists()
    assert Path("/tmp/test_vault/01_AGENDAS/Areas/팀_미팅.md").exists()
    assert Path("/tmp/test_vault/00_INBOX/_ARCHIVED/test_memo.md").exists()
```

#### Configuration Testing
```python
def test_rules_validation():
    """Test rules.json structure validation"""
    rules = load_rules("/tmp/test_vault")

    # Validate required structure
    assert "para_classification" in rules
    assert "projects" in rules["para_classification"]
    assert "areas" in rules["para_classification"]
    assert len(rules["para_classification"]["projects"]["keywords"]) > 0

    # Test keyword functionality
    keywords = rules["para_classification"]["projects"]["keywords"]
    assert "기한" in keywords or "완료" in keywords
```

### 📚 Development Guidelines

#### Code Style Standards
```python
# ✅ Good: Use pathlib.Path consistently
from pathlib import Path

def process_file(file_path: Path) -> bool:
    """Process markdown file with proper path handling"""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    return True

# ❌ Bad: Mixed string/Path usage
def process_file(file_path: str) -> bool:
    import os
    if not os.path.exists(file_path):  # Inconsistent with Path usage elsewhere
        return False
```

#### Error Handling Patterns
```python
# ✅ Good: Structured error messages with context
try:
    result = analyzer.analyze_memo(content)
except APIError as e:
    logger.error(f"AI_API_FAILED: {e.message} | Content length: {len(content)} | Provider: Claude")
    return create_error_agenda(content, str(e))

# ❌ Bad: Generic error handling
try:
    result = analyzer.analyze_memo(content)
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

#### Module Dependencies
- **No Circular Imports**: Maintain clear dependency hierarchy (`main_controller` → modules → utilities)
- **Minimal Coupling**: Each module should be independently testable with mock dependencies
- **Vault Path Injection**: Never hard-code absolute paths; always use vault_path parameter

#### Type Hints & Documentation
```python
from typing import Dict, List, Any, Optional
from pathlib import Path

def analyze_and_merge_files(
    vault_path: Path,
    date_filter: Optional[str] = None,
    analysis_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Analyze memo files and merge results into agenda files.

    Args:
        vault_path: Root path of the Obsidian vault
        date_filter: Process only files matching YYYY-MM-DD format
        analysis_only: If True, perform read-only analysis without file modifications

    Returns:
        List of processed agenda dictionaries with topics, categories, and tasks

    Raises:
        VaultNotFoundError: If vault_path doesn't exist
        ConfigurationError: If rules.json is invalid
    """
```

---

> 📚 **For AI-Specific Information**:
> - **Claude users**: See [CLAUDE.md](CLAUDE.md)
> - **Gemini users**: See [GEMINI.md](GEMINI.md)