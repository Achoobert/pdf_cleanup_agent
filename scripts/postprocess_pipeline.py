import sys
import os
from pathlib import Path
import yaml

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from post_processing import clean_llm_output
import post_processing_formatting
import markdown_to_fvtt

def clean_all_markdown(md_dir):
    """Clean all markdown files in a directory recursively."""
    for root, dirs, files in os.walk(md_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                cleaned = clean_llm_output(content)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                print(f"✅ Cleaned {os.path.relpath(path, md_dir)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/postprocess_pipeline.py <markdown_dir>")
        sys.exit(1)
    md_dir = sys.argv[1]
    if not os.path.exists(md_dir):
        print(f"❌ Directory not found: {md_dir}")
        sys.exit(1)

    # 1. Clean up LLM artifacts
    print(f"🧹 Cleaning markdown in {md_dir}")
    clean_all_markdown(md_dir)

    # 2. Format headings
    print(f"📝 Formatting headings in {md_dir}")
    post_processing_formatting.process_markdown_directory(md_dir)

    # 3. Convert to Foundry VTT JSON
    print(f"🔄 Converting to Foundry VTT JSON")
    dir_name = os.path.basename(md_dir.rstrip('/'))
    yml_dir = os.path.join(os.path.dirname(__file__), '../data/yml')
    yml_file = os.path.join(yml_dir, f"{dir_name}-data-order.yml")
    if os.path.exists(yml_file):
        markdown_to_fvtt.batch_process_chapters(md_dir, yml_file)
    else:
        output_file = f"data/json/fvtt-JournalEntry-{dir_name}.json"
        markdown_to_fvtt.create_fvtt_journal_entry(md_dir, output_file)
    print(f"🎉 Postprocessing complete! Check data/json/")

if __name__ == "__main__":
    main() 