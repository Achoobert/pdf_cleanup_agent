import unittest
from unittest.mock import patch, MagicMock, mock_open
from agent import run_ollama_prompt, run_ollama_prompt_stream

class TestAgentSmoke(unittest.TestCase):
    @patch('agent.requests.post')
    def test_run_ollama_prompt(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        out = run_ollama_prompt("prompt", "text")
        self.assertEqual(out, "ok")

    @patch('agent.requests.post')
    def test_run_ollama_prompt_stream(self, mock_post):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [b'{"response": "ok"}']
        mock_response.raise_for_status.return_value = None
        mock_post.return_value.__enter__.return_value = mock_response
        with patch('builtins.open', mock_open()):
            run_ollama_prompt_stream("prompt", "text", append=False)

if __name__ == '__main__':
    unittest.main() 