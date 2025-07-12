import os
import re
import yaml
from pathlib import Path

def detect_and_format_headings(markdown_text):
    """Detect and format headings in markdown text."""
    
    # Common heading patterns
    heading_patterns = [
        # ALL CAPS lines (likely section headers)
        (r'^([A-Z][A-Z\s]+)$', r'## \1'),
        
        # Specific phrases that should be headings
        (r'^Pulp Considerations$', r'## Pulp Considerations'),
        (r'^Keeper note:$', r'## Keeper note:'),
        (r'^ARRIVING IN NEW YORK$', r'## ARRIVING IN NEW YORK'),
        (r'^THE NEW YORK POLICE$', r'## THE NEW YORK POLICE'),
        (r'^PROSPERO HOUSE$', r'## PROSPERO HOUSE'),
        (r'^MEETING ERICA CARLYLE$', r'## MEETING ERICA CARLYLE'),
        (r'^THE CARLYLE ESTATE$', r'## THE CARLYLE ESTATE'),
        (r'^AMERICA$', r'## AMERICA'),
        (r'^PRELIMINARY INVESTIGATIONS$', r'## PRELIMINARY INVESTIGATIONS'),
        (r'^THE BIG APPLE$', r'## THE BIG APPLE'),
        (r'^CHARACTERS AND MONSTERS: AMERICA$', r'## CHARACTERS AND MONSTERS: AMERICA'),
        (r'^CULT IN RESIDENCE$', r'## CULT IN RESIDENCE'),
        (r'^HARLEM$', r'## HARLEM'),
        (r'^HORROR AT JU-JU HOUSE$', r'## HORROR AT JU-JU HOUSE'),
        (r'^AN INNOCENT MAN$', r'## AN INNOCENT MAN'),
        (r'^OTHER INQUIRIES$', r'## OTHER INQUIRIES'),
        (r'^CONCLUSION$', r'## CONCLUSION'),
        (r'^DRAMATIS PERSONAE: AMERICA$', r'## DRAMATIS PERSONAE: AMERICA'),
        (r'^THE CARLYLE EXPEDITION PRINCIPALS$', r'## THE CARLYLE EXPEDITION PRINCIPALS'),
        
        # Lines that start with common RPG terms
        (r'^(Link:|• Link:).*$', r'### \1'),
        
        # Lines that look like scene headers
        (r'^[A-Z][A-Z\s]+:$', r'## \1'),
    ]
    
    formatted_text = markdown_text
    
    # Apply heading patterns
    for pattern, replacement in heading_patterns:
        formatted_text = re.sub(pattern, replacement, formatted_text, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    formatted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted_text)
    
    return formatted_text

def process_markdown_directory(markdown_dir):
    """Process all markdown files in a directory for heading formatting."""
    
    if not os.path.exists(markdown_dir):
        print(f"❌ Directory not found: {markdown_dir}")
        return
    
    md_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
    
    if not md_files:
        print(f"⚠️  No markdown files found in {markdown_dir}")
        return
    
    print(f"📝 Processing {len(md_files)} markdown files in {markdown_dir}")
    
    for filename in md_files:
        filepath = os.path.join(markdown_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format headings
        formatted_content = detect_and_format_headings(content)
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        print(f"✅ Formatted headings in {filename}")

def main():
    # Load configuration
    with open('pipeline_config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    markdown_dir = config['directories']['markdown_output']
    
    # Process the markdown directory
    process_markdown_directory(markdown_dir)
    
    print("🎉 Heading formatting complete!")

if __name__ == "__main__":
    main() 