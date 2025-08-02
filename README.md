# ClaudeHookMaster

## Description

ClaudeHookMaster is a Python utility that reads Claude Code hook inputs from standard input and outputs human-readable descriptions of what's happening.

## Installation

```bash
cd claude_hook_master
pip install -e .
```

## Usage

Basic usage:
```bash
echo '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}' | python src/main.py
```

With logging:
```bash
echo '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}' | python src/main.py --log activity.log
```

Show help:
```bash
python src/main.py --help
```

## Supported Hook Types

- `tool_use_started`: When a tool starts execution
- `tool_use_completed`: When a tool finishes execution
- `tool_use_blocked`: When a tool use is blocked
- `prompt_intercepted`: When a user prompt is intercepted
- `prompt_submitted`: When a user prompt is submitted
- `response_started`: When Claude starts generating a response
- `response_chunk`: When a chunk of response is received
- `response_completed`: When Claude completes a response
- `error`: When an error occurs

## Example Output

```
[2025-08-02 14:30:45] Tool 'bash' started (request_id: 123)
[2025-08-02 14:30:46] Tool 'bash' completed successfully (request_id: 123)
[2025-08-02 14:30:47] User prompt submitted: "Help me create a Python script..."
[2025-08-02 14:30:48] Claude started generating a response
```

## Log File Format

When using the `--log` option, the tool appends entries in this format:

```
============================================================
Timestamp: 2025-08-02 14:30:45
Raw Input:
{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}
Output:
[2025-08-02 14:30:45] Tool 'bash' started (request_id: 123)
```