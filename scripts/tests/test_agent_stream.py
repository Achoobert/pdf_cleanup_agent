import unittest
from unittest.mock import patch, MagicMock, mock_open
from agent_stream import chunk_text, run_ollama_prompt_stream

class TestAgentStreamSmoke(unittest.TestCase):
    def test_chunk_text(self):
        chunks = chunk_text("a\n\nb\n\nc", 10)
        self.assertTrue(isinstance(chunks, list))
        self.assertGreaterEqual(len(chunks), 1)

    @patch('agent_stream.requests.post')
    def test_run_ollama_prompt_stream(self, mock_post):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [b'{"response": "ok"}']
        mock_response.raise_for_status.return_value = None
        mock_post.return_value.__enter__.return_value = mock_response
        with patch('builtins.open', mock_open()):
            run_ollama_prompt_stream("prompt", "text", append=False)

if __name__ == '__main__':
    unittest.main() 