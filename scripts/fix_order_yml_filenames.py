import os
import yaml

# Paths
YML_PATH = 'data/yml/the_basics-data-order.yml'
MD_DIR = 'data/markdown/Scum_and_villainy/the_basics'

# Load markdown filenames (without .md)
md_files = [f[:-3] for f in os.listdir(MD_DIR) if f.endswith('.md')]

# Load YAML
with open(YML_PATH, 'r', encoding='utf-8') as f:
    yml = yaml.safe_load(f)

updated = 0
unmatched = []
for entry in yml['toc_entries']:
    orig = entry['filename']
    # Find all md_files that end with the YAML filename
    candidates = [f for f in md_files if f.endswith('_' + orig) or f == orig]
    if candidates:
        # Pick the longest match (most specific)
        best = max(candidates, key=len)
        entry['filename'] = best
        updated += 1
    else:
        unmatched.append(orig)

# Save updated YAML
with open(YML_PATH, 'w', encoding='utf-8') as f:
    yaml.dump(yml, f, default_flow_style=False, allow_unicode=True)

print(f"Updated {updated} entries.")
if unmatched:
    print("Unmatched entries:", unmatched)
else:
    print("All entries matched.") 