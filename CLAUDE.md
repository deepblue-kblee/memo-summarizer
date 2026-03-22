# 🔵 Claude Code Guide for Memo Automation Agent

> **📋 Base System Reference**: For complete system architecture, PARA classification rules, and common functionality, see **[SYSTEM.md](.ai-docs/SYSTEM.md)**

## 🎯 Claude-Specific Overview

This guide covers Claude Code CLI-specific features and optimizations for the Memo Automation Agent. Claude excels at structured analysis and reliable JSON parsing, making it ideal for complex memo classification and task extraction.

## ✨ Claude Advantages

✅ **Superior JSON Parsing**: Reliable structured output with complex nested data
✅ **Advanced Reasoning**: Excellent at ambiguous PARA classification decisions
✅ **Korean Text Analysis**: Superior understanding of Korean business context
✅ **Error Context**: Provides detailed failure information for debugging
✅ **Cost Transparency**: Built-in usage tracking and optimization

## 🚀 Claude-Specific Setup

### Installation & Authentication
```bash
# Install Claude Code CLI (required)
# Visit: https://claude.ai/code for installation

# Verify installation
claude --version

# Initial authentication (one-time setup)
claude auth login

# Verify configuration
claude config show
```

### Claude Configuration
```bash
# Check Claude CLI settings
cat ~/.claude/settings.json

# Verify API access
claude test-connection
```

## ⚡ Claude-Optimized Execution

### Primary Commands
```bash
# Claude-specific execution with precision mode
./.agent/run /path/to/vault --ai claude

# Analysis with Claude's detailed reasoning
./.agent/run /path/to/vault --ai claude --analysis-only

# Claude with detailed logging for debugging
./.agent/run /path/to/vault --ai claude --verbose

# Cost-aware processing for specific dates
./.agent/run /path/to/vault --ai claude --date 2026-02-11
```

### Claude Performance Optimization
```bash
# For complex multi-topic memos (Claude's strength)
./.agent/run /path/to/vault --ai claude --deep-analysis

# For high-accuracy PARA classification
./.agent/run /path/to/vault --ai claude --precision-mode
```

## 🔧 Claude-Specific Configuration

### AI Configuration for Claude
```json
{
  "default_provider": "claude",
  "claude": {
    "cli_command": "claude",
    "temperature": 0.1,
    "max_tokens": 4000,
    "focus": "accuracy",
    "json_validation": "strict",
    "cost_tracking": true,
    "timeout": 30000
  }
}
```

### Claude Prompt Optimization
Claude works best with structured, detailed prompts. The system uses Claude-optimized prompts for:

- **PARA Classification**: Leverages Claude's reasoning for ambiguous cases
- **Task Extraction**: Uses Claude's understanding of Korean action verbs
- **JSON Structure**: Takes advantage of Claude's reliable JSON formatting
- **Error Recovery**: Utilizes Claude's ability to provide detailed error context

## 📊 Claude Cost Management

### Cost Tracking
```bash
# View API cost logs (Claude-specific)
grep "COST" .agent/logs/$(date +%Y-%m-%d).log

# Cost summary for date range
grep "API_COST" .agent/logs/*.log | awk '{sum += $NF} END {print "Total: $" sum}'
```

### Cost Optimization Tips
- Use `--analysis-only` for testing to avoid charges
- Process files in batches during off-peak hours
- Leverage Claude's accuracy to reduce retry costs
- Monitor daily usage with built-in tracking

## 🧠 Claude Analysis Engine Details

### JSON Parsing Excellence
Claude's superior JSON handling includes:

```python
# Claude-optimized JSON parsing (from memo_analyzer.py)
def analyze_memo(self, content: str) -> Dict[str, Any]:
    # Claude-specific prompt with structured output requirements
    prompt = f"""
    분석할 메모: {content}

    **CRITICAL REQUIREMENT - STRICTLY JSON OUTPUT ONLY**

    REQUIRED JSON FORMAT:
    {{
        "agendas": [
            {{
                "topic": "sanitized_topic_name",
                "category": "Projects|Areas",
                "tasks": ["실행 가능한 작업1", "실행 가능한 작업2"],
                "summary": "이 주제에 대한 간단 요약"
            }}
        ]
    }}
    """
```

### Enhanced Error Recovery
Claude provides detailed error context:

```python
# Multi-stage JSON parsing with Claude-specific recovery
try:
    # Stage 1: Direct JSON parse (Claude's strength)
    result = json.loads(response_content)
except JSONDecodeError:
    # Stage 2: Regex extraction with Claude context
    json_match = re.search(r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}', response_text)
    # Stage 3: Claude-specific error context extraction
    error_context = self._extract_claude_error_context(response_text)
```

## 🚨 Claude-Specific Troubleshooting

### Common Issues & Solutions

#### Authentication Issues
```bash
# ❌ claude: command not found
# → Install Claude Code CLI: https://claude.ai/code

# ❌ Authentication failed
# → Re-authenticate: claude auth login

# ❌ API quota exceeded
# → Check usage: claude usage --current-month
```

#### Claude API Issues
```bash
# ❌ Request timeout
# → Increase timeout in config or retry with shorter content

# ❌ Rate limiting
# → Use --batch-mode with delays between requests

# ❌ JSON parsing issues (rare with Claude)
# → Check logs: grep "JSON_PARSE_FAILED" .agent/logs/$(date +%Y-%m-%d).log
```

#### PARA Classification Issues
```bash
# ❌ Incorrect classification
# → Review .agent/config/rules.json keywords
# → Use (P) or (A) flags in memo content for override

# ❌ Missing tasks
# → Check action_suffixes in rules.json
# → Use more explicit action verbs in Korean
```

## 📈 Claude Development Patterns

### Leveraging Claude's Strengths
1. **Complex Analysis**: Use Claude for multi-layered memo analysis
2. **Reasoning Tasks**: Leverage Claude's ability to handle ambiguous PARA classification
3. **Structured Output**: Take advantage of Claude's reliable JSON formatting
4. **Error Diagnosis**: Use Claude's detailed error reporting for debugging

### Claude-Optimized Workflows
```bash
# For development and testing
./.agent/run $(pwd) --ai claude --analysis-only --verbose

# For production with cost monitoring
./.agent/run /path/to/production/vault --ai claude --cost-alert

# For complex memo analysis
./.agent/run /path/to/vault --ai claude --deep-reasoning
```

### Advanced Claude Features
- **Context Retention**: Claude maintains context across multiple API calls
- **Incremental Processing**: Efficient handling of large memo batches
- **Quality Assurance**: Built-in validation of classification accuracy
- **Cost Prediction**: Estimate processing costs before execution

## 🔗 Integration with Common System

Claude integrates seamlessly with the common system components:

- **File Operations**: Uses standard file_manager.py with Claude-specific error handling
- **PARA Classification**: Applies common rules.json with Claude's reasoning enhancement
- **Logging System**: Integrates with common logging while adding Claude-specific metrics
- **Path Management**: Follows common vault path patterns with Claude optimizations

---

> 📚 **Additional Resources**:
> - **System Architecture**: [SYSTEM.md](.ai-docs/SYSTEM.md) - Complete system overview
> - **AI Comparison**: [AI_QUICK_START.md](.ai-docs/AI_QUICK_START.md) - When to use Claude vs other AIs
> - **Project Status**: [PROJECT_STATUS.md](.ai-docs/PROJECT_STATUS.md) - Current work context

> 💡 **Claude Best Practices**:
> - Use Claude for complex, ambiguous memo analysis requiring reasoning
> - Leverage Claude's JSON reliability for critical data processing
> - Monitor costs but trust Claude's accuracy to reduce retry overhead
> - Take advantage of Claude's detailed error context for debugging