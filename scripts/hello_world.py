# test whether ollama is up and working

import requests
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
try:
    from model_selector_cli_demo import load_user_selection
except ImportError:
    load_user_selection = None

OLLAMA_API = "http://localhost:11434/api/generate"

# Default model
MODEL = "llama3:8b"

# Try to load user selection
if load_user_selection:
    sel = load_user_selection()
    if sel and sel.get('backend') == 'ollama' and sel.get('ollama_model'):
        MODEL = sel['ollama_model']

def test_ollama():
    try:
        response = requests.post(OLLAMA_API, json={
            "model": MODEL,
            "prompt": "Say hello, world!",
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        data = response.json()
        print("✅ Ollama is up and responded:")
        print(data["response"])
    except Exception as e:
        print("❌ Ollama is not responding or an error occurred:")
        print(e)

if __name__ == "__main__":
    test_ollama()