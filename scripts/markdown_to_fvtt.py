import json
import os
import re
import sys
import yaml
from pathlib import Path

# Fix console encoding for Unicode support on Windows
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def markdown_to_html(markdown_text):
    """Convert markdown to HTML for Foundry VTT."""
    # Basic markdown to HTML conversion
    html = markdown_text
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Bullet points
    html = re.sub(r'^• (.*?)$', r'<p>• \1</p>', html, flags=re.MULTILINE)
    
    # Handle ALL CAPS lines as h2 headers
    html = re.sub(r'^([A-Z][A-Z\s]+)$', r'</p><h2>\1</h2><p>', html, flags=re.MULTILINE)
    
    # Handle specific phrases as h2 headers
    html = re.sub(r'Pulp Considerations', r'</p><h2>Pulp Considerations</h2><p>', html)
    html = re.sub(r'Keeper note:', r'</p><h2>Keeper note:</h2><p>', html)
    
    # Paragraphs (group consecutive non-header lines)
    lines = html.split('\n')
    result = []
    current_paragraph = []
    
    for line in lines:
        if line.strip() == '':
            if current_paragraph:
                result.append('<p>' + ' '.join(current_paragraph) + '</p>')
                current_paragraph = []
        elif line.startswith('<h') or line.startswith('<p>'):
            if current_paragraph:
                result.append('<p>' + ' '.join(current_paragraph) + '</p>')
                current_paragraph = []
            result.append(line)
        else:
            current_paragraph.append(line)
    
    if current_paragraph:
        result.append('<p>' + ' '.join(current_paragraph) + '</p>')
    
    return '\n'.join(result)

def create_fvtt_journal_entry(markdown_dir, output_file):
    """Create a Foundry VTT Journal Entry from markdown files."""
    
    # Get directory name for journal entry name
    dir_name = os.path.basename(markdown_dir)
    journal_name = dir_name.replace('_', ' ').title()
    
    # Base journal entry structure (minimal)
    journal_entry = {
        "name": journal_name,
        "pages": [],
        "folder": None,
        "categories": []
    }
    
    # Load data-order.yml if it exists
    sort_order = []
    name_mapping = {}
    
    # Try to find the corresponding YAML file in data/yml
    yml_dir = os.path.join('data', 'yml')
    markdown_dir_name = os.path.basename(markdown_dir)
    
    # Look for YAML files that might match this markdown directory
    yaml_files = []
    if os.path.exists(yml_dir):
        for yml_file in os.listdir(yml_dir):
            if yml_file.endswith('-data-order.yml'):
                yaml_files.append(yml_file)
    
    # Try to find a matching YAML file
    order_file = None
    for yml_file in yaml_files:
        pdf_name = yml_file.replace('-data-order.yml', '')
        # Check if this PDF name matches the markdown directory structure
        if pdf_name in markdown_dir_name or markdown_dir_name in pdf_name:
            order_file = os.path.join(yml_dir, yml_file)
            break
    
    if order_file and os.path.exists(order_file):
        try:
            with open(order_file, 'r', encoding='utf-8') as f:
                order_data = yaml.safe_load(f)
            
            # Build sort order and name mapping from TOC data
            for entry in order_data.get('toc_entries', []):
                filename = f"{entry['filename']}.md"
                sort_order.append(filename)
                name_mapping[filename] = entry['title']
            
            print(f"📄 Using TOC order from: {order_file}")
        except Exception as e:
            print(f"⚠️  Error loading data-order.yml: {e}")
            # Fallback to default behavior
            sort_order = []
            name_mapping = {}
    else:
        print(f"⚠️  No matching data-order.yml found in {yml_dir}, using file order")
        # Fallback: use all .md files in directory order
        for filename in os.listdir(markdown_dir):
            if filename.endswith('.md'):
                sort_order.append(filename)
                name_mapping[filename] = filename.replace('.md', '').replace('_', ' ').title()
    
    page_id_counter = 100000
    
    for filename in sort_order:
        filepath = os.path.join(markdown_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert markdown to HTML
            html_content = markdown_to_html(content)
            
            # Create page
            page = {
                "sort": page_id_counter,
                "name": name_mapping.get(filename, filename.replace('.md', '').replace('_', ' ').title()),
                "type": "text",
                "system": {},
                "title": {
                    "show": True,
                    "level": 1
                },
                "image": {},
                "text": {
                    "format": 1,
                    "content": html_content
                },
                "video": {
                    "controls": True,
                    "volume": 0.5
                },
                "src": None,
                "category": None
            }
            
            journal_entry["pages"].append(page)
            page_id_counter += 100000
    
    # Write the JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(journal_entry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created Foundry VTT Journal Entry: {output_file}")
    print(f"📄 Total pages: {len(journal_entry['pages'])}")

def batch_process_chapters(parent_dir, yml_path):
    """Process each chapter subdir listed in the YAML as a separate JSON file."""
    with open(yml_path, 'r', encoding='utf-8') as f:
        order_data = yaml.safe_load(f)
    toc_entries = order_data.get('toc_entries', [])
    for entry in toc_entries:
        chapter_dir = os.path.join(parent_dir, entry['filename'])
        md_file = os.path.join(chapter_dir, f"{entry['filename']}.md")
        if os.path.exists(md_file):
            output_file = f"data/json/fvtt-JournalEntry-{entry['filename']}.json"
            print(f"\n➡️ Processing chapter: {entry['filename']} -> {output_file}")
            # Use the title from YAML for the journal name
            create_fvtt_journal_entry(
                markdown_dir=chapter_dir,
                output_file=output_file
            )
        else:
            print(f"⚠️  Markdown file not found for chapter: {entry['filename']} at {md_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python markdown_to_fvtt.py <markdown_directory> [output_file]")
        print("Example: python markdown_to_fvtt.py data/markdown/masks_of_nyarlathotep/chapter_two_america")
        print("         python markdown_to_fvtt.py data/markdown/example")
        sys.exit(1)
    
    markdown_dir = sys.argv[1]
    
    if not os.path.exists(markdown_dir):
        print(f"❌ Directory not found: {markdown_dir}")
        sys.exit(1)
    
    # Check for batch mode: look for a matching YAML order file for the parent directory
    dir_name = os.path.basename(markdown_dir.rstrip('/'))
    yml_dir = os.path.join('data', 'yml')
    yml_file = os.path.join(yml_dir, f"{dir_name}-data-order.yml")
    if os.path.isdir(markdown_dir) and os.path.exists(yml_file):
        # Batch mode: process each chapter subdir listed in YAML
        batch_process_chapters(markdown_dir, yml_file)
        return
    
    # Single-directory mode (legacy)
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = f"data/json/fvtt-JournalEntry-{dir_name}.json"
    
    create_fvtt_journal_entry(markdown_dir, output_file)

if __name__ == "__main__":
    main() 