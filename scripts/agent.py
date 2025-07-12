import requests
import json
import os

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1"  # or whatever model you're running

# Ensure data directories exist
os.makedirs("data/txt_input", exist_ok=True)
os.makedirs("data/output", exist_ok=True)

def run_ollama_prompt(prompt, text):
    full_prompt = f"{prompt.strip()}\n\n{text.strip()}"
    response = requests.post(OLLAMA_API, json={
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"]

def run_ollama_prompt_stream(prompt, chunk, append=False):
    full_prompt = f"{prompt.strip()}\n\n{chunk.strip()}"
    with requests.post(
        OLLAMA_API,
        json={"model": MODEL, "prompt": full_prompt, "stream": True},
        stream=True,
        timeout=120
    ) as response:
        response.raise_for_status()
        mode = "a" if append else "w"
        with open("data/output/output.md", mode, encoding="utf-8") as f:
            total = 0
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    f.write(chunk)
                    f.flush()
                    total += len(chunk)
                    print(f"\rWritten {total} chars in this chunk...", end='', flush=True)
            print()  # Newline after chunk

def main():
    with open("data/txt_input/input.txt", "r", encoding="utf-8") as f:
        input_text = f.read()

    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    output = run_ollama_prompt(prompt, input_text)

    with open("data/output/output.md", "w", encoding="utf-8") as f:
        f.write(output)

    print("✅ Markdown output saved to data/output/output.md")

if __name__ == "__main__":
    main()
