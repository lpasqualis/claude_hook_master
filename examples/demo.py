#!/usr/bin/env python3
"""
Demonstration script showing ClaudeHookMaster functionality with various hook inputs.
"""

import subprocess
import json

def run_example(description, hook_data):
    """Run an example and print the result."""
    print(f"\n{description}")
    print(f"Input: {json.dumps(hook_data)}")
    
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=json.dumps(hook_data))
    
    if stdout:
        print(f"Output: {stdout.strip()}")
    if stderr:
        print(f"Error: {stderr.strip()}")

def main():
    """Run various example hook inputs."""
    print("ClaudeHookMaster Examples")
    print("=" * 50)
    
    examples = [
        ("Tool use started", {
            "hook": "tool_use_started",
            "tool_name": "Bash",
            "request_id": "example-001"
        }),
        
        ("Tool use completed successfully", {
            "hook": "tool_use_completed",
            "tool_name": "Write",
            "request_id": "example-002",
            "result": {"is_error": False}
        }),
        
        ("Tool use failed", {
            "hook": "tool_use_completed",
            "tool_name": "Read",
            "request_id": "example-003",
            "result": {"is_error": True, "error": "File not found"}
        }),
        
        ("Tool use blocked", {
            "hook": "tool_use_blocked",
            "tool_name": "Bash",
            "request_id": "example-004",
            "reason": "User rejected the operation"
        }),
        
        ("User prompt submitted", {
            "hook": "prompt_submitted",
            "prompt": "Help me create a web server in Python"
        }),
        
        ("Response started", {
            "hook": "response_started"
        }),
        
        ("Response chunk", {
            "hook": "response_chunk",
            "chunk": "I'll help you create a Python web server..."
        }),
        
        ("Error occurred", {
            "hook": "error",
            "error": "Connection timeout",
            "error_type": "network_error"
        })
    ]
    
    for description, hook_data in examples:
        run_example(description, hook_data)

if __name__ == '__main__':
    main()