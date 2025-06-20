import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1"  # or your preferred model
CHUNK_SIZE = 3000  # Adjust as needed for your model/context

def chunk_text(text, size):
    # Split text into chunks of approximately 'size' characters, on paragraph boundaries if possible
    paragraphs = text.split('\n\n')
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current += (para + '\n\n')
        else:
            if current:
                chunks.append(current.strip())
            current = para + '\n\n'
    if current:
        chunks.append(current.strip())
    return chunks

def run_ollama_prompt_stream(prompt, chunk, append=False):
    full_prompt = f"{prompt.strip()}\n\n{chunk.strip()}"
    with requests.post(
        OLLAMA_API,
        json={"model": MODEL, "prompt": full_prompt, "stream": True},
        stream=True,
        timeout=120  # Increase timeout for slow hardware/large chunks
    ) as response:
        response.raise_for_status()
        mode = "a" if append else "w"
        with open("output.md", mode, encoding="utf-8") as f:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    f.write(chunk)
                    f.flush()  # Ensure it's written to disk immediately

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        input_text = f.read()
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    chunks = chunk_text(input_text, CHUNK_SIZE)
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        run_ollama_prompt_stream(prompt, chunk, append=(i != 0))
    print("✅ All chunks processed and saved to output.md (streamed)")

if __name__ == "__main__":
    main()
