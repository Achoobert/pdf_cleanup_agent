import sys
import os
import yaml
import requests
import json

if len(sys.argv) < 2:
    print('Usage: python reprocess_markdown_with_llm.py <markdown_file>')
    sys.exit(1)

md_path = sys.argv[1]
if not os.path.exists(md_path):
    print(f'File not found: {md_path}')
    sys.exit(1)

# Load config for model and API
with open(os.path.join(os.path.dirname(__file__), '../pipeline_config.yml'), 'r') as f:
    config = yaml.safe_load(f)
OLLAMA_API = config['settings']['ollama_api']
MODEL = config['settings']['model']
PROMPT_FILE = os.path.join(os.path.dirname(__file__), '../prompts/parse_pdf_text')

with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    prompt = f.read()

with open(md_path, 'r', encoding='utf-8') as f:
    input_text = f.read()

full_prompt = f"{prompt.strip()}\n\n{input_text.strip()}"

try:
    response = requests.post(OLLAMA_API, json={
        'model': MODEL,
        'prompt': full_prompt,
        'stream': False
    })
    response.raise_for_status()
    llm_output = response.json().get('response', '')
except Exception as e:
    print(f'LLM request failed: {e}', file=sys.stderr)
    sys.exit(1)

# Save output as <original_name>_reprocessed.md
base, ext = os.path.splitext(md_path)
out_path = base + '_reprocessed.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(llm_output)
print(f'Successfully re-processed markdown: {out_path}') 