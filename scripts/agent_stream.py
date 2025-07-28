import requests
import json
import os
import glob
import re
import yaml

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"  # Use the requested model
CHUNK_SIZE = 4000  # Recommended for Llama 3 8B

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'pipeline_config.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Input/output directories from config
INPUT_DIR = config['directories']['txt_output']
OUTPUT_DIR = config['directories']['markdown_output']
PROMPT_FILE = os.path.join(os.path.dirname(__file__), '..', config['settings']['prompt'])

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def chunk_text(text, size):
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

def run_ollama_prompt_stream(prompt, chunk, output_file, append=False):
    full_prompt = f"{prompt.strip()}\n\n{chunk.strip()}"
    with requests.post(
        OLLAMA_API,
        json={"model": MODEL, "prompt": full_prompt, "stream": True},
        stream=True,
        timeout=120
    ) as response:
        response.raise_for_status()
        mode = "a" if append else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    f.write(chunk)
                    f.flush()

def process_file(input_path, prompt):
    base = os.path.basename(input_path)
    name, _ = os.path.splitext(base)
    
    # Create output directory structure based on input path
    rel_path = os.path.relpath(input_path, INPUT_DIR)
    output_subdir = os.path.join(OUTPUT_DIR, os.path.dirname(rel_path))
    os.makedirs(output_subdir, exist_ok=True)
    
    output_path = os.path.join(output_subdir, f"{name}.md")
    
    with open(input_path, "r", encoding="utf-8") as f:
        input_text = f.read()
    
    chunks = chunk_text(input_text, CHUNK_SIZE)
    
    # Process first chunk (no cleaning)
    if chunks:
        print(f"  Processing chunk 1/{len(chunks)} for {base}...")
        run_ollama_prompt_stream(prompt, chunks[0], output_path, append=False)
    
    # Process remaining chunks (no cleaning)
    for i, chunk in enumerate(chunks[1:], 2):
        print(f"  Processing chunk {i}/{len(chunks)} for {base}...")
        run_ollama_prompt_stream(prompt, chunk, output_path, append=True)
    
    print(f"✅ {base} processed and saved to {output_path} (raw LLM output, no post-processing)")

def main():
    import sys
    print("Running Agent Stream") 
    # Get input directory from command line argument, or use config default
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        print(f"🔄 Processing directory: {input_dir}")
    else:
        input_dir = INPUT_DIR
        print(f"🔄 Using default directory: {input_dir}")
    
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # Find all txt files recursively in the specified directory
    txt_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    print(f"Found {len(txt_files)} .txt files in {input_dir}")
    
    for input_path in txt_files:
        process_file(input_path, prompt)
    
    print(f"✅ All files processed and saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
