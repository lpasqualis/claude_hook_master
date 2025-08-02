# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Purpose

ClaudeHookMaster is a Python utility that translates Claude Code hook JSON inputs into human-readable descriptions with timestamps. It processes all Claude Code hook types as defined at https://docs.anthropic.com/en/docs/claude-code/hooks#hook-input.

## Key Commands

### Running the utility
```bash
# Basic usage - reads from stdin
echo '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}' | python src/main.py

# With logging to file
echo '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}' | python src/main.py --log activity.log

# From within any Claude Code hook
./your-hook-script | python src/main.py --log hook_activity.log
```

### Testing
```bash
# Run all unit tests
./unittest

# Run specific test module
python -m unittest tests.test_hook_parser

# Run specific test
python -m unittest tests.test_hook_parser.TestHookParser.test_tool_use_started

# Run demonstration examples
python examples/demo.py
```

### Development setup
```bash
cd claude_hook_master
pip install -e .
```

## Architecture

The codebase follows a simple two-layer architecture:

1. **HookParser** (`src/hook_parser.py`): Core parsing logic
   - Maps hook types to handler methods via `hook_handlers` dictionary
   - Each handler extracts relevant fields and formats them into plain English
   - All output is timestamped with `[YYYY-MM-DD HH:MM:SS]` format
   - Handles edge cases: long text truncation (100 chars for prompts, 50 for chunks), missing fields, invalid JSON

2. **Main Entry Point** (`src/main.py`): CLI interface
   - Reads JSON from stdin
   - Calls HookParser for processing
   - Optionally logs raw input + output to file with `--log` option
   - Returns appropriate exit codes (0 for success, 1 for errors)

## Hook Input/Output Examples

Input: `{"hook": "tool_use_completed", "tool_name": "Write", "request_id": "abc", "result": {"is_error": true, "error": "Permission denied"}}`
Output: `[2025-08-02 14:30:45] Tool 'Write' failed with error: Permission denied (request_id: abc)`

Input: `{"hook": "prompt_submitted", "prompt": "Very long prompt that exceeds 100 characters..."}`
Output: `[2025-08-02 14:30:45] User prompt submitted: "Very long prompt that exceeds 100 characters..."`