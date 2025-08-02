#!/usr/bin/env python3
"""
ClaudeHookMaster - Parse and describe Claude Code hook inputs in plain English.
"""

import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

from hook_parser import HookParser


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
    
    return parser


def append_to_log(log_file: Path, raw_input: str, output: str):
    """Append raw input and output to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n{'='*60}\n"
    log_entry += f"Timestamp: {timestamp}\n"
    log_entry += f"Raw Input:\n{raw_input}\n"
    log_entry += f"Output:\n{output}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
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
    
    # Parse and describe the hook input
    hook_parser = HookParser()
    parsed_data, output = hook_parser.parse(raw_input)
    
    # Output the description
    print(output)
    
    # Log if requested
    if args.log:
        log_file = Path(args.log)
        append_to_log(log_file, raw_input, output)
    
    # Exit with appropriate code
    if "Error" in output or "Invalid" in output:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()