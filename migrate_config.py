#!/usr/bin/env python3
"""
Config Migration Helper

This script helps migrate and consolidate config files to the new structure.
All config files should be in data/config/ directory.
"""

import os
import shutil
from pathlib import Path

def migrate_configs():
    """Migrate config files to the consolidated data/config structure."""
    
    print("PDF Power Converter - Config Migration")
    print("=" * 40)
    
    # Ensure data/config directory exists
    config_dir = Path("data/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Config files that should be in data/config
    config_files = [
        "pipeline_config.yml",
        "data-order.yml"
    ]
    
    moved_files = []
    
    for config_file in config_files:
        root_file = Path(config_file)
        dest_file = config_dir / config_file
        
        # If file exists in root but not in data/config, move it
        if root_file.exists() and not dest_file.exists():
            try:
                shutil.copy2(root_file, dest_file)
                print(f"Copied {config_file} to data/config/")
                moved_files.append(config_file)
            except Exception as e:
                print(f"ERROR: Could not copy {config_file}: {e}")
        elif dest_file.exists():
            print(f"{config_file} already exists in data/config/")
        else:
            print(f"WARNING: {config_file} not found")
    
    # Check for any other .yml files in root that might be config files
    for yml_file in Path(".").glob("*.yml"):
        if yml_file.name not in config_files and "config" in yml_file.name.lower():
            dest_file = config_dir / yml_file.name
            if not dest_file.exists():
                try:
                    shutil.copy2(yml_file, dest_file)
                    print(f"Found and copied {yml_file.name} to data/config/")
                    moved_files.append(yml_file.name)
                except Exception as e:
                    print(f"ERROR: Could not copy {yml_file.name}: {e}")
    
    print("\n" + "=" * 40)
    if moved_files:
        print(f"Migration complete! Moved {len(moved_files)} files.")
        print("\nMoved files:")
        for file in moved_files:
            print(f"  - {file}")
        print(f"\nAll config files are now in: {config_dir.absolute()}")
    else:
        print("No migration needed. All config files are already in place.")
    
    print(f"\nConfig directory contents:")
    if config_dir.exists():
        for file in config_dir.glob("*"):
            print(f"  - {file.name}")
    
    return len(moved_files) > 0

if __name__ == "__main__":
    migrate_configs()