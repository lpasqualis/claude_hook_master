#!/usr/bin/env python3
"""
ClaudeHookMaster - Parse and describe Claude Code hook inputs in plain English.
"""

import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

from .hook_parser import HookParser


def setup_argparse():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        prog='ClaudeHookMaster',
        description='Parse Claude Code hook inputs and output plain English descriptions.',
        epilog='Reads hook input from stdin and outputs a timestamped description to stdout.'
    )
    
    parser.add_argument(
        '--log',
        type=str,
        metavar='FILE',
        help='Log raw hook input and output to specified file'
    )
    
    parser.add_argument(
        '--no-human-readable',
        action='store_true',
        help='Disable human-readable format for multiline fields in logs'
    )
    
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Compact log format: no prettification and no human-readable format'
    )
    
    return parser


def append_to_log(log_file: Path, raw_input: str, output: str = None, show_human_readable: bool = True, compact: bool = False):
    """Append raw input and optionally output to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Create separator with timestamp centered
    separator = f"=== [{timestamp}] " + "=" * (60 - len(timestamp) - 7)
    log_entry = f"\n{separator}\n"
    
    # Try to prettify JSON input
    try:
        parsed_json = json.loads(raw_input)
        
        if compact:
            # Compact mode: no prettification
            log_entry += f"Raw Input: {raw_input}\n"
        else:
            # Pretty print JSON
            pretty_json = json.dumps(parsed_json, indent=2)
            log_entry += f"Raw Input:\n{pretty_json}\n"
            
            # Add human-readable format for fields with newlines
            if show_human_readable:
                def extract_multiline_fields(obj, prefix=""):
                    multiline_fields = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            full_key = f"{prefix}.{key}" if prefix else key
                            if isinstance(value, str) and '\n' in value:
                                multiline_fields.append((full_key, value))
                            elif isinstance(value, dict):
                                multiline_fields.extend(extract_multiline_fields(value, full_key))
                    return multiline_fields
                
                multiline_fields = extract_multiline_fields(parsed_json)
                if multiline_fields:
                    log_entry += f"\nHuman-readable format:\n"
                    for field_name, field_value in multiline_fields:
                        log_entry += f"  {field_name}:\n"
                        lines = field_value.split('\n')
                        for line in lines:
                            log_entry += f"    {line}\n"
            
    except json.JSONDecodeError:
        # If it's not valid JSON, just log as-is
        log_entry += f"Raw Input: {raw_input}\n"
    
    if output:
        log_entry += f"Output: {output.rstrip()}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            f.flush()
    except Exception as e:
        print(f"[{timestamp}] Warning: Failed to write to log file: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Read from stdin
    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: No input received", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Log raw input immediately if requested (for safety)
    if args.log:
        log_file = Path(args.log)
        # Create parent directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        # Compact mode overrides no_human_readable
        show_human_readable = not (args.compact or args.no_human_readable)
        append_to_log(log_file, raw_input, show_human_readable=show_human_readable, compact=args.compact)
    
    # Parse and describe the hook input
    hook_parser = HookParser()
    parsed_data, output = hook_parser.parse(raw_input)
    
    # Output the description
    print(output)
    
    # Update log with output if requested
    if args.log:
        # Append the output to the same log entry
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Output: {output.rstrip()}\n")
    
    # Exit with appropriate code
    if "Error" in output or "Invalid" in output:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()