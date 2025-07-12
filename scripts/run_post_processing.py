import os
import yaml
from post_processing import clean_llm_output

# Load configuration
with open('pipeline_config.yml', 'r') as f:
    config = yaml.safe_load(f)

TARGET_DIR = config['directories']['markdown_output']

def process_markdown_files_recursively(target_dir):
    """Process all markdown files recursively in the target directory."""
    
    if not os.path.exists(target_dir):
        print(f"❌ Directory not found: {target_dir}")
        return
    
    # Find all markdown files recursively
    md_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    if not md_files:
        print(f"⚠️  No markdown files found in {target_dir}")
        return
    
    print(f"🧹 Cleaning {len(md_files)} markdown files...")
    
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = clean_llm_output(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        rel_path = os.path.relpath(filepath, target_dir)
        print(f'✅ Cleaned {rel_path}')

if __name__ == "__main__":
    process_markdown_files_recursively(TARGET_DIR)
    print("🎉 Post-processing cleanup complete!") 