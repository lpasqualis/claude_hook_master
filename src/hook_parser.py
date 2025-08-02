import json
from typing import Dict, Any, Optional
from datetime import datetime


class HookParser:
    """Parse and describe Claude Code hook inputs in plain English."""
    
    def __init__(self):
        self.hook_handlers = {
            'tool_use_started': self._handle_tool_use_started,
            'tool_use_completed': self._handle_tool_use_completed,
            'tool_use_blocked': self._handle_tool_use_blocked,
            'prompt_intercepted': self._handle_prompt_intercepted,
            'prompt_submitted': self._handle_prompt_submitted,
            'response_started': self._handle_response_started,
            'response_chunk': self._handle_response_chunk,
            'response_completed': self._handle_response_completed,
            'error': self._handle_error,
        }
    
    def parse(self, input_data: str) -> tuple[Dict[str, Any], str]:
        """Parse hook input and return both the parsed data and description."""
        try:
            data = json.loads(input_data)
            hook_type = data.get('hook')
            
            if not hook_type:
                return data, self._format_output("Invalid hook input: missing 'hook' field")
            
            if hook_type not in self.hook_handlers:
                return data, self._format_output(f"Unknown hook type: {hook_type}")
            
            description = self.hook_handlers[hook_type](data)
            return data, self._format_output(description)
            
        except json.JSONDecodeError as e:
            return {}, self._format_output(f"Invalid JSON input: {str(e)}")
        except Exception as e:
            return {}, self._format_output(f"Error parsing hook input: {str(e)}")
    
    def _format_output(self, description: str) -> str:
        """Format output with timestamp prefix."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {description}"
    
    def _handle_tool_use_started(self, data: Dict[str, Any]) -> str:
        """Handle tool_use_started hook."""
        tool_name = data.get('tool_name', 'unknown')
        request_id = data.get('request_id', 'unknown')
        return f"Tool '{tool_name}' started (request_id: {request_id})"
    
    def _handle_tool_use_completed(self, data: Dict[str, Any]) -> str:
        """Handle tool_use_completed hook."""
        tool_name = data.get('tool_name', 'unknown')
        request_id = data.get('request_id', 'unknown')
        result = data.get('result', {})
        
        # Check if there was an error
        if result.get('is_error'):
            error_msg = result.get('error', 'Unknown error')
            return f"Tool '{tool_name}' failed with error: {error_msg} (request_id: {request_id})"
        
        return f"Tool '{tool_name}' completed successfully (request_id: {request_id})"
    
    def _handle_tool_use_blocked(self, data: Dict[str, Any]) -> str:
        """Handle tool_use_blocked hook."""
        tool_name = data.get('tool_name', 'unknown')
        request_id = data.get('request_id', 'unknown')
        reason = data.get('reason', 'No reason provided')
        return f"Tool '{tool_name}' was blocked: {reason} (request_id: {request_id})"
    
    def _handle_prompt_intercepted(self, data: Dict[str, Any]) -> str:
        """Handle prompt_intercepted hook."""
        prompt = data.get('prompt', '')
        prompt_preview = prompt[:100] + '...' if len(prompt) > 100 else prompt
        prompt_preview = prompt_preview.replace('\n', ' ')
        return f"User prompt intercepted: \"{prompt_preview}\""
    
    def _handle_prompt_submitted(self, data: Dict[str, Any]) -> str:
        """Handle prompt_submitted hook."""
        prompt = data.get('prompt', '')
        prompt_preview = prompt[:100] + '...' if len(prompt) > 100 else prompt
        prompt_preview = prompt_preview.replace('\n', ' ')
        return f"User prompt submitted: \"{prompt_preview}\""
    
    def _handle_response_started(self, data: Dict[str, Any]) -> str:
        """Handle response_started hook."""
        return "Claude started generating a response"
    
    def _handle_response_chunk(self, data: Dict[str, Any]) -> str:
        """Handle response_chunk hook."""
        chunk = data.get('chunk', '')
        chunk_preview = chunk[:50] + '...' if len(chunk) > 50 else chunk
        chunk_preview = chunk_preview.replace('\n', ' ')
        return f"Response chunk received: \"{chunk_preview}\""
    
    def _handle_response_completed(self, data: Dict[str, Any]) -> str:
        """Handle response_completed hook."""
        response = data.get('response', '')
        response_preview = response[:100] + '...' if len(response) > 100 else response
        response_preview = response_preview.replace('\n', ' ')
        return f"Claude completed response: \"{response_preview}\""
    
    def _handle_error(self, data: Dict[str, Any]) -> str:
        """Handle error hook."""
        error = data.get('error', 'Unknown error')
        error_type = data.get('error_type', 'unknown')
        return f"Error occurred ({error_type}): {error}"