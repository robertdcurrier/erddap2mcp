# 🧠 ERDDAP2MCP Memory Bank

**MANDATORY**: Check this memory bank BEFORE making any changes to the project!

## Purpose
This memory bank preserves critical knowledge about the ERDDAP MCP servers to prevent repeating past mistakes and forgetting hard-won solutions.

## Structure

### 📜 domain-knowledge/
- `critical-rules.md` - SACRED parameters and rules that must NEVER be changed
- `bob-says.md` - Direct requirements and wisdom from Bob
- `system-behavior.md` - How ERDDAP actually works (vs how we wish it worked)

### 🔧 technical-specs/
- `working-parameters.md` - Parameters that WORK (don't change!)
- `architecture.md` - System design decisions
- `dependencies.md` - Required tools/libraries

### 🏆 debugging-victories/
- `solved-issues.md` - Problems we've already fixed
- `known-errors.json` - Error -> Solution mapping
- `lessons-learned.jsonl` - Timestamped lessons

### 📊 current-state/
- `last-working-config.json` - Last known good configuration
- `processing-stats.jsonl` - Performance history
- `active-tasks.md` - What we're currently doing

### 🎯 project-specific/
- Custom files specific to ERDDAP MCP implementation

## Golden Rules
1. **Check Memory FIRST, Debug SECOND**
2. **Bob's Words Are IMMUTABLE**
3. **Working Configs Are SACRED**
4. **Solved Problems Stay SOLVED**
5. **Domain Knowledge Is FOREVER**

## Quick Commands
```bash
# Check critical rules
cat memory-bank/domain-knowledge/critical-rules.md

# See what Bob said
cat memory-bank/domain-knowledge/bob-says.md

# Check known issues
grep -r "error" memory-bank/debugging-victories/

# View last working config
cat memory-bank/current-state/last-working-config.json
```

**REMEMBER**: A project without memory is doomed to repeat its failures!