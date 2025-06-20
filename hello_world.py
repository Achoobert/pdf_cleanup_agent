# test whether ollama is up and working

import requests

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1"  # or whatever model you're running

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