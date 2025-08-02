import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from io import StringIO
from pathlib import Path

# Add parent directory to path to import src modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import src modules directly
from src.hook_parser import HookParser
from src.main import setup_argparse, append_to_log, main


class TestMain(unittest.TestCase):
    """Test cases for main.py functions."""
    
    def test_setup_argparse(self):
        """Test argparse setup."""
        parser = setup_argparse()
        
        # Test with --help (should not raise)
        with patch('sys.stdout', new=StringIO()):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(['--help'])
            self.assertEqual(cm.exception.code, 0)
        
        # Test with --log option
        args = parser.parse_args(['--log', 'test.log'])
        self.assertEqual(args.log, 'test.log')
        
        # Test with no options
        args = parser.parse_args([])
        self.assertIsNone(args.log)
    
    def test_append_to_log(self):
        """Test log file appending."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Test appending to log
            raw_input = '{"hook": "test"}'
            output = "[2025-08-02 15:30:45] Test output"
            
            append_to_log(Path(tmp_path), raw_input, output)
            
            # Read and verify log content
            with open(tmp_path, 'r') as f:
                content = f.read()
            
            self.assertIn("===", content)
            self.assertIn("[20", content)  # Timestamp format check
            self.assertIn("Raw Input:", content)
            self.assertIn(raw_input, content)
            self.assertIn("Output:", content)
            self.assertIn(output, content)
        finally:
            os.unlink(tmp_path)
    
    def test_append_to_log_error_handling(self):
        """Test log file error handling."""
        # Test with invalid path
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            append_to_log(Path("/invalid/path/test.log"), "input", "output")
            stderr_output = mock_stderr.getvalue()
            self.assertIn("Warning: Failed to write to log file", stderr_output)
    
    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_valid_input(self, mock_stdout, mock_stdin):
        """Test main function with valid input."""
        mock_stdin.read.return_value = '{"hook": "response_started"}'
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['main.py']):
                main()
        
        self.assertEqual(cm.exception.code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Claude started generating a response", output)
    
    @patch('sys.stdin')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_empty_input(self, mock_stderr, mock_stdin):
        """Test main function with empty input."""
        mock_stdin.read.return_value = ''
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['main.py']):
                main()
        
        self.assertEqual(cm.exception.code, 1)
        stderr_output = mock_stderr.getvalue()
        self.assertIn("Error: No input received", stderr_output)
    
    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_invalid_json(self, mock_stdout, mock_stdin):
        """Test main function with invalid JSON input."""
        mock_stdin.read.return_value = '{invalid json}'
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['main.py']):
                main()
        
        self.assertEqual(cm.exception.code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("Invalid JSON input", output)
    
    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_logging(self, mock_stdout, mock_stdin):
        """Test main function with logging enabled."""
        mock_stdin.read.return_value = '{"hook": "tool_use_started", "tool_name": "bash", "request_id": "123"}'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['main.py', '--log', tmp_path]):
                    main()
            
            self.assertEqual(cm.exception.code, 0)
            
            # Verify log file was created and contains expected content
            with open(tmp_path, 'r') as f:
                log_content = f.read()
            
            self.assertIn('"hook": "tool_use_started"', log_content)
            self.assertIn("Tool 'bash' started", log_content)
        finally:
            os.unlink(tmp_path)
    
    @patch('sys.stdin')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_stdin_read_error(self, mock_stderr, mock_stdin):
        """Test main function when stdin read fails."""
        mock_stdin.read.side_effect = Exception("Read error")
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['main.py']):
                main()
        
        self.assertEqual(cm.exception.code, 1)
        stderr_output = mock_stderr.getvalue()
        self.assertIn("Error reading input: Read error", stderr_output)
    
    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_whitespace_handling(self, mock_stdout, mock_stdin):
        """Test main function handles whitespace in input."""
        mock_stdin.read.return_value = '  \n{"hook": "response_started"}\n  '
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['main.py']):
                main()
        
        self.assertEqual(cm.exception.code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Claude started generating a response", output)


if __name__ == '__main__':
    unittest.main()