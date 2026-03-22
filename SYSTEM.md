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

---

> 📚 **For AI-Specific Information**:
> - **Claude users**: See [CLAUDE.md](CLAUDE.md)
> - **Gemini users**: See [GEMINI.md](GEMINI.md)
> - **AI Comparison**: See [AI_QUICK_START.md](AI_QUICK_START.md)