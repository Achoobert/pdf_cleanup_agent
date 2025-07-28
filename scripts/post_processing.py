import re
import os
import sys

# Fix console encoding for Unicode support on Windows
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def clean_llm_output(text):
    """Remove common LLM output artifacts and meta-text."""
    # Remove lines that are exactly 'Here is the cleaned text:' or 'Here is the cleaned and repaired text:'
    lines = text.splitlines()
    filtered_lines = []
    for line in lines:
        if line.strip() in [
            'Here is the cleaned text:',
            'Here is the cleaned and repaired text:',
            'Here is the cleaned text content:',
            'Here is the cleaned and normalized text:',
            'Here is the cleaned content:',
        ]:
            continue  # skip this line
        filtered_lines.append(line)
    cleaned_text = '\n'.join(filtered_lines)

    # Remove any line starting with 'Here is the cleaned'
    cleaned_text = re.sub(r'^Here is the cleaned.*$', '', cleaned_text, flags=re.MULTILINE)

    # Remove common LLM prefixes and meta-text (only at the start of a line)
    patterns_to_remove = [
        r"^Here'?s the normalized text:\s*",
        r"^Here is the normalized text:\s*",
        r"^\*\*Output format:\*\*\s*",
        r"^Output format:\s*",
        r"^Return only the fully normalized text\.\s*",
        r"^Do NOT include any explanations, commentary, or meta-text.*$",
        r"^I'll get to work on cleaning and repairing.*$",
        r"^No artifacts removed yet.*$",
        r"^Here is the cleaned-up Markdown:\s*",
        r"^Here'?s the fully normalized text:\s*",
        r"^Here is the fully normalized text:\s*",
        r"^Removing page artifacts.*$",
        r"^I removed the page header and footer.*$",
        r"^And so on\.\.\.Here is the normalized text:\s*",
        r"^Meeting the good friends of Hilton Adams\.Here is the normalized text:\s*",
        r"^Hilton Adams, an innocent manHere'?s the fully normalized text:\s*",
        r"^MASKS OF NYARLATHOTEPHere is the normalized text:\s*",
        r"^\*\*CHAPTER 2: HORROR AT JU-JU HOUSE\*\*\s*",
        r"^As evidence mounts.*$",
        r"^This African art emporium.*$",
        r"^On meeting nights.*$",
        r"^\*\*CASING THE JOINT\*\*\s*",
        r"^\*\*BLACKWATER CREEK\*\*\s*",
        # General LLM artefacts (line-based, not greedy)
        r"^Here (is|are|was|were) the cleaned( and repaired)? text:?\s*$",
        r"^Here (is|are|was|were) the cleaned content:?\s*$",
        r"^Here (is|are|was|were) the output:?\s*$",
        r"^Here'?s the cleaned( and repaired)? text:?\s*$",
        r"^Here'?s the output:?\s*$",
        r"^Here is the cleaned and normalized text:?\s*$",
        r"^Here is the cleaned text content:?\s*$",
        r"^Here is the cleaned and repaired text:?\s*$",
        r"^Here is the cleaned text:?\s*$",
        r"^Here is the output:?\s*$",
        r"^Here'?s the cleaned text:?\s*$",
        r"^Here'?s the cleaned content:?\s*$",
        r"^Here is the normalized output:?\s*$",
        r"^Here is the normalized content:?\s*$",
    ]

    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove artifacts that appear anywhere in the text (line-based)
    artifacts_to_remove = [
        r"^\*\*Output format:\*\*\s*$",
        r"^Return only the fully normalized text\.\s*$",
        r"^Do NOT include any explanations.*$",
        r"^Here is the normalized text:\s*$",
        r"^Here'?s the normalized text:\s*$",
        r"^Here is the cleaned-up Markdown:\s*$",
        r"^Here'?s the fully normalized text:\s*$",
        r"^Here is the fully normalized text:\s*$",
        r"^I'll get to work on cleaning and repairing.*$",
        r"^No artifacts removed yet.*$",
        r"^Removing page artifacts.*$",
        r"^I removed the page header and footer.*$",
        r"^And so on\.\.\.Here is the normalized text:\s*$",
        r"^Meeting the good friends of Hilton Adams\.Here is the normalized text:\s*$",
        r"^Hilton Adams, an innocent manHere'?s the fully normalized text:\s*$",
        r"^MASKS OF NYARLATHOTEPHere is the normalized text:\s*$",
        r"^\*\*CHAPTER 2: HORROR AT JU-JU HOUSE\*\*\s*$",
        r"^As evidence mounts.*$",
        r"^This African art emporium.*$",
        r"^On meeting nights.*$",
        r"^\*\*CASING THE JOINT\*\*\s*$",
        # General LLM artefacts (line-based, not greedy)
        r"^Here (is|are|was|were) the cleaned( and repaired)? text:?\s*$",
        r"^Here (is|are|was|were) the cleaned content:?\s*$",
        r"^Here (is|are|was|were) the output:?\s*$",
        r"^Here'?s the cleaned( and repaired)? text:?\s*$",
        r"^Here'?s the output:?\s*$",
        r"^Here is the cleaned and normalized text:?\s*$",
        r"^Here is the cleaned text content:?\s*$",
        r"^Here is the cleaned and repaired text:?\s*$",
        r"^Here is the cleaned text:?\s*$",
        r"^Here is the output:?\s*$",
        r"^Here'?s the cleaned text:?\s*$",
        r"^Here'?s the cleaned content:?\s*$",
        r"^Here is the normalized output:?\s*$",
        r"^Here is the normalized content:?\s*$",
    ]

    for artifact in artifacts_to_remove:
        cleaned_text = re.sub(artifact, '', cleaned_text, flags=re.MULTILINE | re.IGNORECASE)

    # Clean up multiple newlines and extra whitespace
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
    cleaned_text = re.sub(r' +', ' ', cleaned_text)

    return cleaned_text.strip()


def process_markdown_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for root, dirs, files in os.walk(input_dir):
        rel_root = os.path.relpath(root, input_dir)
        out_root = os.path.join(output_dir, rel_root) if rel_root != '.' else output_dir
        os.makedirs(out_root, exist_ok=True)
        for file in files:
            if file.endswith('.md'):
                in_path = os.path.join(root, file)
                out_path = os.path.join(out_root, file)
                with open(in_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                cleaned = clean_llm_output(text)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                print(f"✅ Cleaned: {in_path} -> {out_path}")


def process_markdown_file(input_file, output_path):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    cleaned = clean_llm_output(text)
    # If output_path is a directory, write to same filename in that dir
    if os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        out_file = os.path.join(output_path, os.path.basename(input_file))
    else:
        # If output_path ends with .md or .txt, treat as file
        if output_path.endswith('.md') or output_path.endswith('.txt'):
            out_file = output_path
        else:
            # Default: treat as directory
            os.makedirs(output_path, exist_ok=True)
            out_file = os.path.join(output_path, os.path.basename(input_file))
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"✅ Cleaned: {input_file} -> {out_file}")


def main():
    if len(sys.argv) < 2:
        input_path = 'data/markdown'
        output_path = 'data/processed_markdown'
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else 'data/processed_markdown'

    if os.path.isdir(input_path):
        print(f"🔄 Cleaning all markdown in {input_path} -> {output_path}")
        process_markdown_dir(input_path, output_path)
        print("🎉 All markdown files cleaned and saved.")
    elif os.path.isfile(input_path):
        print(f"🔄 Cleaning single markdown file {input_path} -> {output_path}")
        process_markdown_file(input_path, output_path)
        print("🎉 File cleaned and saved.")
    else:
        print(f"❌ Input path not found: {input_path}")

if __name__ == "__main__":
    main() 