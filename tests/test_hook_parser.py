import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hook_parser import HookParser


class TestHookParser(unittest.TestCase):
    """Test cases for HookParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = HookParser()
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON input."""
        input_data = '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}'
        parsed_data, output = self.parser.parse(input_data)
        
        self.assertEqual(parsed_data['hook'], 'tool_use_started')
        self.assertEqual(parsed_data['tool_name'], 'bash')
        self.assertIn("Tool 'bash' started", output)
        self.assertIn("request_id: 123", output)
        # Check timestamp format
        self.assertRegex(output, r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON input."""
        input_data = '{invalid json}'
        parsed_data, output = self.parser.parse(input_data)
        
        self.assertEqual(parsed_data, {})
        self.assertIn("Invalid JSON input", output)
    
    def test_missing_hook_field(self):
        """Test parsing JSON without hook field."""
        input_data = '{"tool_name": "bash"}'
        parsed_data, output = self.parser.parse(input_data)
        
        self.assertIn("Invalid hook input: missing 'hook' or 'hook_event_name' field", output)
    
    def test_unknown_hook_type(self):
        """Test parsing unknown hook type."""
        input_data = '{"hook": "unknown_hook_type"}'
        parsed_data, output = self.parser.parse(input_data)
        
        self.assertIn("Unknown hook type: unknown_hook_type", output)
    
    def test_tool_use_started(self):
        """Test tool_use_started hook parsing."""
        input_data = json.dumps({
            "hook": "tool_use_started",
            "tool_name": "Write",
            "request_id": "abc-123"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Tool 'Write' started", output)
        self.assertIn("request_id: abc-123", output)
    
    def test_tool_use_completed_success(self):
        """Test tool_use_completed hook parsing (success case)."""
        input_data = json.dumps({
            "hook": "tool_use_completed",
            "tool_name": "Bash",
            "request_id": "xyz-789",
            "result": {"is_error": False}
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Tool 'Bash' completed successfully", output)
        self.assertIn("request_id: xyz-789", output)
    
    def test_tool_use_completed_error(self):
        """Test tool_use_completed hook parsing (error case)."""
        input_data = json.dumps({
            "hook": "tool_use_completed",
            "tool_name": "Read",
            "request_id": "def-456",
            "result": {
                "is_error": True,
                "error": "File not found"
            }
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Tool 'Read' failed with error: File not found", output)
        self.assertIn("request_id: def-456", output)
    
    def test_tool_use_blocked(self):
        """Test tool_use_blocked hook parsing."""
        input_data = json.dumps({
            "hook": "tool_use_blocked",
            "tool_name": "Bash",
            "request_id": "blocked-123",
            "reason": "User rejected the action"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Tool 'Bash' was blocked: User rejected the action", output)
        self.assertIn("request_id: blocked-123", output)
    
    def test_prompt_intercepted(self):
        """Test prompt_intercepted hook parsing."""
        input_data = json.dumps({
            "hook": "prompt_intercepted",
            "prompt": "Help me create a Python script"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('User prompt intercepted: "Help me create a Python script"', output)
    
    def test_prompt_intercepted_long(self):
        """Test prompt_intercepted hook with long prompt."""
        long_prompt = "x" * 150
        input_data = json.dumps({
            "hook": "prompt_intercepted",
            "prompt": long_prompt
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('User prompt intercepted: "' + "x" * 100 + '..."', output)
    
    def test_prompt_submitted(self):
        """Test prompt_submitted hook parsing."""
        input_data = json.dumps({
            "hook": "prompt_submitted",
            "prompt": "Create a web server"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('User prompt submitted: "Create a web server"', output)
    
    def test_response_started(self):
        """Test response_started hook parsing."""
        input_data = json.dumps({"hook": "response_started"})
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Claude started generating a response", output)
    
    def test_response_chunk(self):
        """Test response_chunk hook parsing."""
        input_data = json.dumps({
            "hook": "response_chunk",
            "chunk": "Here is the Python code you requested"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('Response chunk received: "Here is the Python code you requested"', output)
    
    def test_response_chunk_long(self):
        """Test response_chunk hook with long chunk."""
        long_chunk = "y" * 100
        input_data = json.dumps({
            "hook": "response_chunk",
            "chunk": long_chunk
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('Response chunk received: "' + "y" * 50 + '..."', output)
    
    def test_response_completed(self):
        """Test response_completed hook parsing."""
        input_data = json.dumps({
            "hook": "response_completed",
            "response": "I've created the Python script as requested."
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn('Claude completed response: "I\'ve created the Python script as requested."', output)
    
    def test_error_hook(self):
        """Test error hook parsing."""
        input_data = json.dumps({
            "hook": "error",
            "error": "Connection timeout",
            "error_type": "network_error"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Error occurred (network_error): Connection timeout", output)
    
    def test_multiline_prompt_handling(self):
        """Test handling of multiline prompts."""
        input_data = json.dumps({
            "hook": "prompt_submitted",
            "prompt": "Line 1\nLine 2\nLine 3"
        })
        _, output = self.parser.parse(input_data)
        
        # Should replace newlines with spaces
        self.assertIn('User prompt submitted: "Line 1 Line 2 Line 3"', output)
    
    def test_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        # Test with minimal data
        input_data = json.dumps({"hook": "tool_use_started"})
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Tool 'unknown' started", output)
        self.assertIn("request_id: unknown", output)
    
    @patch('hook_parser.datetime')
    def test_timestamp_format(self, mock_datetime):
        """Test timestamp format in output."""
        mock_datetime.now.return_value.strftime.return_value = "2025-08-02 15:30:45"
        
        input_data = json.dumps({"hook": "response_started"})
        _, output = self.parser.parse(input_data)
        
        self.assertTrue(output.startswith("[2025-08-02 15:30:45]"))
    
    def test_session_stop_event(self):
        """Test session stop event parsing."""
        input_data = json.dumps({
            "session_id": "173ea15b-0fa8-4742-80dc-3f8a7c8efd2a",
            "cwd": "/Users/test/project",
            "hook_event_name": "Stop"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Session stopped", output)
        self.assertIn("id: 173ea15b...", output)
        self.assertIn("/Users/test/project", output)
    
    def test_session_start_event(self):
        """Test session start event parsing."""
        input_data = json.dumps({
            "session_id": "173ea15b-0fa8-4742-80dc-3f8a7c8efd2a",
            "cwd": "/Users/test/project",
            "hook_event_name": "Start"
        })
        _, output = self.parser.parse(input_data)
        
        self.assertIn("Session started", output)
        self.assertIn("id: 173ea15b...", output)
        self.assertIn("/Users/test/project", output)


if __name__ == '__main__':
    unittest.main()