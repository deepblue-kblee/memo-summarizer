# 🔄 AI Quick Start & Comparison Guide

> **📋 System Base**: See [SYSTEM.md](SYSTEM.md) for complete system architecture and common functionality

## 🎯 Which AI Should You Choose?

### 📊 Quick Decision Matrix

| Your Scenario | Recommended AI | Reason |
|---------------|----------------|---------|
| 복잡한 한국어 메모 분석 | **Claude** 🔵 | Superior reasoning & context understanding |
| 대량 파일 배치 처리 | **Gemini** 🟡 | Speed advantage & cost efficiency |
| 정확한 JSON 출력 필요 | **Claude** 🔵 | Reliable structured parsing |
| 비용 최적화가 중요 | **Gemini** 🟡 | Budget-friendly processing |
| 처음 시스템 테스트 | **Claude** 🔵 | More predictable results |
| 실시간 처리 필요 | **Gemini** 🟡 | Faster response time |

## 🔵 Claude Characteristics

### ✅ **Best For**
- **Complex Analysis**: Multi-layered memo understanding
- **Accurate Classification**: Reliable PARA categorization
- **JSON Reliability**: Consistent structured output
- **Error Diagnosis**: Detailed failure context
- **Korean Business Context**: Deep understanding of business terminology

### 💰 **Cost Considerations**
- Higher per-token cost
- Premium accuracy reduces retry overhead
- Cost-effective for complex analysis

### 🚀 **Quick Setup**
```bash
# Install & authenticate
claude auth login

# Test with Claude
./.agent/run $(pwd) --ai claude --analysis-only
```

## 🟡 Gemini Characteristics

### ✅ **Best For**
- **Batch Processing**: Handle many files quickly
- **Cost Efficiency**: More processing within budget
- **Korean Language**: Natural Korean expression understanding
- **Real-time Processing**: Immediate memo analysis
- **Backup Solution**: Reliable fallback when Claude fails

### 💰 **Cost Considerations**
- Lower per-token cost
- Excellent for high-volume processing
- Budget-friendly for large vaults

### 🚀 **Quick Setup**
```bash
# Install & authenticate
gemini auth login

# Test with Gemini
./.agent/run $(pwd) --ai gemini --analysis-only
```

## ⚡ Performance Comparison

| Metric | Claude 🔵 | Gemini 🟡 | Winner |
|--------|-----------|-----------|---------|
| **JSON Accuracy** | 95%+ | 90%+ | 🔵 Claude |
| **Processing Speed** | Standard | Fast | 🟡 Gemini |
| **Cost Efficiency** | Premium | Budget | 🟡 Gemini |
| **Korean Context** | Excellent | Excellent | 🤝 Tie |
| **PARA Classification** | 97%+ | 92%+ | 🔵 Claude |
| **Error Recovery** | Detailed | Aggressive | 🔵 Claude |
| **Batch Processing** | Good | Excellent | 🟡 Gemini |

## 🛠️ Configuration Differences

### Claude Configuration
```json
{
  "claude": {
    "temperature": 0.1,
    "focus": "accuracy",
    "json_validation": "strict",
    "cost_tracking": true
  }
}
```

### Gemini Configuration
```json
{
  "gemini": {
    "temperature": 0.2,
    "focus": "speed",
    "json_recovery": "aggressive",
    "batch_size": 10,
    "cost_optimization": true
  }
}
```

## 📊 Use Case Examples

### 🎯 **Scenario 1: Daily Memo Processing**
```bash
# Few complex memos with nuanced content
./.agent/run /path/to/vault --ai claude

# Many simple memos requiring quick processing
./.agent/run /path/to/vault --ai gemini --batch-mode
```

### 📈 **Scenario 2: Project Scaling**

#### **Small Team (< 50 memos/day)**
- **Recommended**: Claude
- **Reason**: Quality over quantity, cost manageable

#### **Large Team (100+ memos/day)**
- **Recommended**: Gemini + Claude hybrid
- **Reason**: Gemini for bulk, Claude for complex cases

### 🔄 **Scenario 3: Fallback Strategy**
```bash
# Auto-fallback configuration
{
  "fallback_chain": ["claude", "gemini"],
  "fallback_triggers": ["timeout", "quota_exceeded", "json_error"]
}
```

## 🎛️ Advanced Features Comparison

### Claude-Exclusive Features
- **Deep Reasoning**: Complex logical analysis
- **Cost Prediction**: Estimate processing costs
- **Context Retention**: Maintain state across calls
- **Detailed Logging**: Comprehensive error context

### Gemini-Exclusive Features
- **Batch Optimization**: Process multiple files efficiently
- **Real-time Mode**: Immediate processing capability
- **Korean Enhancement**: Special Korean language processing
- **Aggressive Recovery**: Force JSON from broken responses

## 🚀 Getting Started Workflows

### 🔵 **Claude Workflow**
```bash
# Step 1: Setup
claude auth login
claude test-connection

# Step 2: Test Analysis
./.agent/run $(pwd) --ai claude --analysis-only

# Step 3: Process with monitoring
./.agent/run $(pwd) --ai claude --verbose

# Step 4: Production use
./.agent/run /path/to/vault --ai claude
```

### 🟡 **Gemini Workflow**
```bash
# Step 1: Setup
gemini auth login
export GEMINI_API_KEY="your-key"

# Step 2: Test speed
./.agent/run $(pwd) --ai gemini --analysis-only

# Step 3: Batch test
./.agent/run $(pwd) --ai gemini --batch-mode --analysis-only

# Step 4: Production batch
./.agent/run /path/to/vault --ai gemini --batch-mode
```

## 🔄 Hybrid Strategies

### **Strategy 1: AI Selection by Content**
```bash
# Complex business memos → Claude
find 00_INBOX -name "*meeting*" -o -name "*strategy*" | xargs ./.agent/run --ai claude

# Simple task lists → Gemini
find 00_INBOX -name "*todo*" -o -name "*checklist*" | xargs ./.agent/run --ai gemini
```

### **Strategy 2: Time-based Selection**
```bash
# Peak hours (fast processing) → Gemini
if [ $(date +%H) -ge 9 ] && [ $(date +%H) -le 17 ]; then
    AI_PROVIDER="gemini"
else
    AI_PROVIDER="claude"
fi

./.agent/run /path/to/vault --ai $AI_PROVIDER
```

### **Strategy 3: Cost-based Selection**
```bash
# Budget remaining check
BUDGET_REMAINING=$(check_daily_budget.sh)
if [ $BUDGET_REMAINING -gt 50 ]; then
    ./.agent/run /path/to/vault --ai claude
else
    ./.agent/run /path/to/vault --ai gemini
fi
```

## 🚨 Troubleshooting Quick Guide

### 🔵 **Claude Issues**
```bash
# Authentication
claude auth login

# Cost monitoring
grep "COST" .agent/logs/$(date +%Y-%m-%d).log

# JSON debugging
grep "JSON_PARSE_FAILED" .agent/logs/$(date +%Y-%m-%d).log
```

### 🟡 **Gemini Issues**
```bash
# Authentication
export GEMINI_API_KEY="new-key"

# Batch size tuning
./.agent/run /path/to/vault --ai gemini --batch-size 5

# JSON recovery
./.agent/run /path/to/vault --ai gemini --json-recovery aggressive
```

## 🎯 Migration Strategies

### **From Claude to Gemini**
1. Test batch processing capability
2. Verify JSON parsing stability
3. Adjust batch sizes for performance
4. Monitor cost savings

### **From Gemini to Claude**
1. Prepare for higher costs
2. Expect improved accuracy
3. Leverage detailed error reporting
4. Optimize for complex analysis

## 📈 Performance Optimization Tips

### **For Claude**
- Use `--analysis-only` for testing
- Monitor daily costs with built-in tracking
- Leverage detailed error context
- Optimize prompts for structured output

### **For Gemini**
- Use `--batch-mode` for multiple files
- Enable `--korean-enhanced` for Korean memos
- Set appropriate `--batch-size` (5-10)
- Use `--cost-optimized` for budget constraints

---

> 📚 **Deep Dive Resources**:
> - **Claude Specifics**: [CLAUDE.md](CLAUDE.md) - Detailed Claude guide
> - **Gemini Specifics**: [GEMINI.md](GEMINI.md) - Detailed Gemini guide
> - **System Foundation**: [SYSTEM.md](SYSTEM.md) - Common architecture
> - **Implementation**: [DEVELOPER.md](DEVELOPER.md) - Technical details

> 💡 **Quick Decision**: Not sure? Start with **Claude** for reliability, then try **Gemini** for cost optimization!