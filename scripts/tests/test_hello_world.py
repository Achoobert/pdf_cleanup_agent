import unittest
from unittest.mock import patch, MagicMock
from hello_world import test_ollama

class TestHelloWorldSmoke(unittest.TestCase):
    @patch('hello_world.requests.post')
    def test_test_ollama(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "hi"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        with patch('builtins.print') as mock_print:
            test_ollama()
            mock_print.assert_any_call("✅ Ollama is up and responded:")

if __name__ == '__main__':
    unittest.main() 