# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is an **Obsidian Memo Automation Agent** - an AI-powered note processing pipeline that analyzes unstructured memos from `00_INBOX/` and intelligently organizes them into structured agenda files. The system uses Claude AI via the Claude Code CLI to extract multiple topics from single memos, performs automatic classification (Projects vs Areas structure inspired by PARA methodology), and maintains organized project files with enhanced logging and error recovery.

**NEW: Complete System Redesign** - The system has been completely restructured with `.agent/` package isolation, intelligent directory organization, and path-parameterized execution.

## Commands

### NEW: .agent Package Execution (Current System)
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

### Legacy Execution (Deprecated)
```bash
# Old system (still available for comparison)
python agent.py --analysis-only
./run_agent.sh --analysis-only
```

### System Setup
```bash
# Create required directories
mkdir -p 00_INBOX 01_AGENDAS

# Activate virtual environment
source venv/bin/activate

# Verify Claude CLI installation
claude --version

# Set executable permissions
chmod +x run_agent.sh start_memo_processor.sh
```

### Development & Debugging
```bash
# View analysis logs (daily files with enhanced logging)
cat logs/memo_analyzer_$(date +%Y-%m-%d).log

# Real-time API response debugging (terminal output)
python agent.py --analysis-only

# Check directory structure and file counts
ls -la 00_INBOX/ 01_AGENDAS/ 00_INBOX/_ARCHIVED/
find 01_AGENDAS/ -name "*.md" | wc -l

# Date-specific processing for debugging
python agent.py --date 2026-02-11 --analysis-only

# JSON validation and structure check
python agent.py --date 2026-02-11 --json

# Run legacy mono processor (for comparison)
./start_memo_processor.sh
```

## Architecture Overview

### NEW: .agent Package Architecture (Isolated System)
The system has been completely restructured with agent package isolation and PARA methodology:

**Directory Structure:**
```
Vault_Root/
├── 00_INBOX/              # 📥 Input: Raw memo files
│   └── _ARCHIVED/         # 🗂️ Processed files (auto-managed)
├── 01_AGENDAS/            # 📋 Output: PARA-classified agenda files
│   ├── Projects/          # 🎯 Goal-oriented projects with deadlines
│   └── Areas/             # 🏢 Ongoing responsibility areas
├── 02_DAILY_REPORTS/      # 📊 Daily summary reports (NEW!)
│
└── .agent/                # 🤖 Agent package (isolated from Obsidian)
    ├── bin/               # 🛠️ Modular Python scripts
    │   ├── main_controller.py     # Main orchestrator
    │   ├── claude_client.py       # AI API integration
    │   ├── file_manager.py        # File I/O with path parameters
    │   ├── memo_analyzer.py       # AI analysis + Projects/Areas classification
    │   ├── markdown_processor.py  # Markdown processing
    │   └── daily_reporter.py      # Daily reports (replaces daily_agenda.py)
    ├── config/            # ⚙️ Configuration files
    │   └── rules.json     # Classification keywords & task extraction rules
    ├── venv/              # 🐍 Isolated Python environment
    ├── logs/              # 📋 Daily activity logs
    └── run                # 🚀 Entry point script
```

**Core Modules (Enhanced with PARA & Path Parameters):**

1. **`.agent/bin/main_controller.py`** - Path-parameterized orchestrator with PARA support
2. **`.agent/bin/claude_client.py`** - Enhanced AI API integration
3. **`.agent/bin/file_manager.py`** - Path-based file operations with PARA directory management
4. **`.agent/bin/memo_analyzer.py`** - AI analysis engine with Projects/Areas classification logic
5. **`.agent/bin/markdown_processor.py`** - Markdown processing (unchanged)
6. **`.agent/bin/daily_reporter.py`** - Enhanced daily reporting with PARA statistics

### Enhanced Data Flow with PARA Classification
```
INPUT: 00_INBOX/*.md →
Path-Parameterized File Scanning →
AI Analysis (Claude) with PARA Classification →
Multi-Topic Extraction (Projects vs Areas) →
Markdown Processing & Directory-based Merging →
OUTPUT:
  - 01_AGENDAS/Projects/{topic}.md (🎯 Goal-oriented projects)
  - 01_AGENDAS/Areas/{topic}.md (🏢 Ongoing responsibility areas)
  - 02_DAILY_REPORTS/Daily_Report_YYYY-MM-DD.md (📊 PARA statistics)
  - 00_INBOX/_ARCHIVED/{original}.md (🗂️ Safe archival)
  - .agent/logs/YYYY-MM-DD.log (📋 Detailed audit trail)
```

### PARA Classification Logic (Rule-based)
The AI system automatically classifies topics using configurable rules from `.agent/config/rules.json`:

**Projects** (→ `01_AGENDAS/Projects/`):
- Tasks with clear deadlines or completion goals
- **Keywords** (from config): `~까지`, `기한`, `데드라인`, `출시`, `완료`, `개발`, `셋업`, `구축`, `배포`, `런칭`, `(P)`
- **Examples**: "새로운 기능 개발", "시스템 마이그레이션 3월까지", "제품 출시", "API 셋업"

**Areas** (→ `01_AGENDAS/Areas/`):
- Ongoing responsibility areas requiring continuous maintenance
- **Keywords** (from config): `정기`, `관리`, `운영`, `매달`, `지속`, `루틴`, `1on1`, `미팅`, `가이드`, `정책`, `피드백`, `(A)`
- **Examples**: "팀 1on1 관리", "정기 미팅", "성과 피드백", "운영 가이드 업데이트"

**Priority Override**: Use `(P)` or `(A)` flags in memo content to force specific classification regardless of keywords.

### Key Architectural Patterns

**Multi-Topic Support**: Single memo can generate multiple independent agenda files
- Input: One memo discussing "Mixpanel issues" and "Blog development"
- Output: `Mixpanel.md` + `블로그_자동화_도구.md` (separate files)

**Safe File Updates**: Atomic write pattern prevents data corruption
- Backup existing → Write new → Delete backup on success → Restore on failure

**Duplicate Detection**: Intelligent task merging prevents accumulation
- Existing tasks preserved, only unique new tasks added

**Error Recovery**: Enhanced multi-level JSON parsing with graceful degradation
- 1st attempt: Direct JSON parse from extracted content
- 2nd attempt: Regex extraction (`r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'`) + whitespace cleaning
- 3rd attempt: Manual cleaning of newlines, tabs, extra spaces
- Failure: Log full raw response and continue with error topic (system doesn't crash)

**Enhanced Logging System**: Daily append-only logs with detailed tracing
- Real-time terminal output of AI responses for immediate debugging
- Structured log levels: SUCCESS, ERROR, WARNING, INFO
- Full API response preservation for troubleshooting
- Cost tracking and performance metrics

## Core Logic & Rules

### 1. External Configuration (`.agent/config/rules.json`)
The system avoids hard-coded logic by loading classification keywords and task extraction rules from an external configuration file. This enables easy customization without code modifications:

* **Projects Keywords**: `~까지`, `기한`, `데드라인`, `출시`, `완료`, `개발`, `셋업`, `구축`, `배포`, `런칭`, `(P)`
* **Areas Keywords**: `정기`, `관리`, `운영`, `매달`, `지속`, `루틴`, `1on1`, `미팅`, `가이드`, `정책`, `피드백`, `(A)`
* **Priority Flags**: `(P)` forces Projects classification, `(A)` forces Areas classification

### 2. Intelligent Task Extraction (Suffix-based)
To support "roughly written" notes, the system automatically converts descriptive bullet points into actionable tasks:

* **Action Suffixes**: Lines ending with `해야 함`, `하기`, `할 것`, `확인`, `조사`, `요청`, `문의`, `셋업`, `배포` are converted to checkbox tasks (`- [ ]`)
* **Deduplication Logic**: Tasks are matched against existing agenda files to prevent duplicate entries
* **Natural Language Processing**: The AI identifies action items even in conversational Korean text

### 3. Smart Merging & Atomic Write Operations
The system ensures data integrity through sophisticated file handling patterns:

* **History Preservation**: The `## 📝 메모 이력` section is append-only with timestamps and links to archived source files
* **Atomic Write Pattern**:
    1. Rename existing file to `_filename.md` (backup)
    2. Write new merged content to original location
    3. Delete backup only upon verified success
    4. Restore backup if any step fails
* **Source Traceability**: Every merge includes a link back to the archived source: `[[00_INBOX/_ARCHIVED/filename|View Source]]`

### 4. Path Portability & Vault-Agnostic Design
Every module calculates paths relative to the **Vault Root Path** provided at runtime:

* **No Hard-coded Paths**: All file operations use vault_path parameter for complete portability
* **Relative Path Resolution**: `.agent/` package maintains isolation while supporting any vault location
* **Cross-Platform Compatibility**: Uses `pathlib.Path` for Windows/macOS/Linux compatibility
* **Multiple Vault Support**: Same system can process different vaults by changing the path parameter

## Dependencies & Requirements

### External Dependencies
- **Claude Code CLI**: Must be installed and on PATH (`claude` command)
- **Python 3.x**: Standard library only, no external packages required
- **Directory Structure**: `00_INBOX/` and `01_AGENDAS/` must exist

### Configuration
- **Claude CLI**: Uses `~/.claude/settings.json` automatically
- **Rules Configuration**: `.agent/config/rules.json` contains classification keywords and task extraction rules
- **`.env` file** (optional): API key, scheduling, logging configuration
- **Virtual Environment**: `venv/` recommended but not required

## File Organization Patterns

### Generated File Formats

**Agenda Files** (`01_AGENDAS/{sanitized_topic_name}.md`):
```markdown
# Topic Name

## 🚀 할 일 목록
- Task 1
- Task 2

## 📝 메모 이력
[2026-02-12] Summary of today's additions
```

**Daily Summary** (`01_AGENDAS/Daily_Agenda_YYYY-MM-DD.md`):
```markdown
# Daily Agenda - 2026-02-12

## 📋 오늘 처리된 주제들

### 1. [[Topic1]]
- **할 일**: 3개
- **요약**: Brief summary

## 📊 처리 통계
- **총 주제 수**: 2개
- **총 할 일**: 5개
```

## Module Responsibilities

### `memo_analyzer.py` - AI Analysis Engine (Enhanced!)
- **Primary Function**: Extract multiple topics from single memo using Claude AI
- **Enhanced JSON Parsing**: 2-stage robust extraction with regex fallback
- **Error Handling**: Comprehensive logging and graceful degradation (never crashes pipeline)
- **Logging System**: Daily append-only logs with structured levels and real-time terminal output
- **Performance Tracking**: API cost monitoring and processing statistics

**Key Methods**:
- `analyze_memo(content)`: Main analysis with hardened AI prompt (STRICTLY JSON OUTPUT)
- `_extract_json_from_response()`: Advanced regex-based extraction (`r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'`)
- `_log_to_file()`: Timestamped structured logging to `logs/memo_analyzer_YYYY-MM-DD.log`

**Enhanced Features**:
- **Strengthened AI Prompt**: "CRITICAL REQUIREMENT - STRICTLY JSON OUTPUT ONLY"
- **Real-time Debugging**: Terminal output of raw API responses
- **2-Stage Parsing**: Regex extraction → Whitespace cleaning → Final parse attempt
- **Cost Transparency**: Live API cost display during processing

### `markdown_processor.py` - Content Merging
- **Primary Function**: Parse existing agenda files and merge new content
- **Deduplication**: Prevent duplicate tasks using exact string matching
- **Structure Preservation**: Maintain consistent markdown format across files

**Key Methods**:
- `merge_with_existing_content()`: Smart merge preserving existing tasks
- `extract_existing_tasks()`: Parse markdown to identify current tasks
- `create_new_agenda_file_content()`: Generate new agenda from scratch

### `file_manager.py` - File Operations
- **Primary Function**: All file I/O with safety guarantees
- **Safe Updates**: Atomic write pattern prevents data loss
- **Archive Management**: Collision-free archiving with counter suffixes
- **Path Sanitization**: Convert AI topics to valid filenames

**Key Methods**:
- `safe_update_file()`: Atomic write with rollback capability
- `archive_file()`: Move to `_ARCHIVED/` with collision handling
- `sanitize_filename()`: Remove invalid filesystem characters

## Development Patterns

### Error Handling Philosophy
The system prioritizes **graceful degradation** over strict validation:
- API failures → Continue with error topic instead of stopping
- JSON parse errors → Log raw response and continue
- File operation failures → Restore backups and continue
- Individual file failures → Skip file but process remaining

### Testing Approach
Use `--analysis-only` mode for safe testing:
```bash
# Preview what would happen without modifying files
python agent.py --analysis-only
```

### Debugging Workflow
1. **Check logs**: `logs/memo_analyzer_YYYY-MM-DD.log` for detailed trace
2. **Terminal output**: Real-time API responses printed during execution
3. **JSON validation**: Raw AI responses logged for inspection
4. **File state**: Verify directory contents before/after processing

## Legacy System

The monolithic `memo_processor.py` (577 lines) is deprecated but maintained for reference. It implements single-topic extraction only. Use the modular system (`agent.py`) for new development.

Key differences:
- **Legacy**: Single topic per memo, monolithic structure
- **Current**: Multi-topic support, modular architecture, enhanced error handling

## Recent Enhancements (Major System Redesign)

### 🎯 PARA Methodology Integration
- **Automatic Classification**: AI now distinguishes between Projects (goal-oriented) and Areas (ongoing responsibilities)
- **Separate Directories**: `01_AGENDAS/Projects/` and `01_AGENDAS/Areas/` for organized file management
- **Enhanced Prompts**: AI training to recognize Projects/Areas classification patterns
- **Visual Indicators**: 🎯 for Projects, 🏢 for Areas in all system outputs

### 🏗️ Agent Package Isolation
- **Clean Obsidian Vault**: All system files isolated in `.agent/` hidden directory
- **Path Parameterization**: System accepts vault root path as mandatory parameter
- **Isolated Environment**: Dedicated virtual environment in `.agent/venv/`
- **Modular Structure**: Clear separation between system components and user data

### 📊 Enhanced Reporting System
- **Daily Reports**: Comprehensive daily summaries in `02_DAILY_REPORTS/`
- **PARA Statistics**: Breakdown of Projects vs Areas in all reports
- **Obsidian Links**: Automatic `[[Projects/topic]]` and `[[Areas/topic]]` linking
- **Processing Metrics**: Detailed statistics on task counts, categories, and processing time

### 🛡️ Bulletproof JSON Processing
- **Regex-based Extraction**: Handles malformed AI responses with nested braces
- **Multi-stage Recovery**: 3-level parsing attempts before graceful failure
- **Debugging Transparency**: Real-time display of raw AI responses and extracted JSON
- **Never-fail Pipeline**: Individual file failures don't crash entire batch

### 📊 Production-Ready Logging
- **Daily Log Files**: `logs/memo_analyzer_YYYY-MM-DD.log` with append-only writes
- **Structured Logging**: SUCCESS/ERROR/WARNING/INFO levels for easy parsing
- **Performance Metrics**: API costs, processing times, success rates
- **Full Audit Trail**: Every AI request/response permanently recorded

## Usage Patterns for Development

### Safe Testing Workflow (NEW System)
```bash
# 1. Preview PARA classification without modifications
./.agent/run /path/to/vault --analysis-only

# 2. Test specific date with PARA classification
./.agent/run /path/to/vault --date 2026-02-11 --analysis-only

# 3. Validate JSON structure with PARA categories
./.agent/run /path/to/vault --date 2026-02-11 --json

# 4. Full PARA processing after validation
./.agent/run /path/to/vault --date 2026-02-11

# 5. Test with current directory as vault
./.agent/run $(pwd) --analysis-only
```

### Path Parameter Requirements
```bash
# ✅ Correct: Always provide vault path as first argument
./.agent/run /Users/user/Documents/MyVault --date 2026-02-11

# ❌ Wrong: No path parameter
./.agent/run --date 2026-02-11

# ✅ Correct: Using current directory
./.agent/run $(pwd) --analysis-only
```

### Debugging JSON Issues (NEW Logging System)
```bash
# Check logs for parsing failures (NEW path)
grep "ERROR" .agent/logs/$(date +%Y-%m-%d).log

# See raw AI responses with PARA classification
grep "RAW_RESPONSE" .agent/logs/$(date +%Y-%m-%d).log

# Monitor API costs and PARA statistics
grep "COST" .agent/logs/$(date +%Y-%m-%d).log

# Check PARA classification accuracy
grep "PARA" .agent/logs/$(date +%Y-%m-%d).log

# View daily report generation logs
grep "Daily_Report" .agent/logs/$(date +%Y-%m-%d).log
```

### System Health Checks
```bash
# Verify agent package structure
ls -la .agent/bin/

# Check virtual environment
.agent/venv/bin/python --version

# Validate PARA directory structure
ls -la 01_AGENDAS/Projects/ 01_AGENDAS/Areas/ 02_DAILY_REPORTS/

# Test system without processing files
./.agent/run $(pwd) --help
```

## Future Enhancement Areas

### PARA System Extensions
1. **Resources & Archive Support**: Add PARA Resources and Archive categories
2. **PARA Validation Rules**: Enhanced AI training for more accurate classification
3. **Cross-PARA Relationships**: Link related Projects and Areas
4. **PARA Performance Metrics**: Track completion rates by category

### System Improvements
5. **Cumulative Daily Reports**: Time-series reporting instead of daily overwrites
6. **Task Completion Tracking**: Mark tasks as done vs. pending with checkboxes
7. **Recurring Task Management**: Smart handling of repeated tasks across days
8. **Batch Date Processing**: `--date-range 2026-02-01:2026-02-28` support
9. **Interactive Mode**: File-by-file confirmation before processing

### Infrastructure & Integration
10. **Web Interface**: Current system is CLI-only
11. **Alternative AI Providers**: Support for OpenAI, Gemini, local models
12. **Obsidian Plugin**: Native integration with Obsidian
13. **Multi-Vault Support**: Process multiple vaults simultaneously
14. **Remote Sync**: Cloud-based processing and synchronization
