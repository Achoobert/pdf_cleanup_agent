#!/usr/bin/env python3
"""
Clean portable distribution directory

This script forcefully removes the portable_dist directory to fix permission issues.
"""

import os
import sys
import shutil
import time
from pathlib import Path

def force_remove_directory(path):
    """Force remove a directory with better Windows handling."""
    if not Path(path).exists():
        print(f"Directory {path} doesn't exist, nothing to clean.")
        return True
    
    print(f"Attempting to remove {path}...")
    
    # First try normal removal
    try:
        shutil.rmtree(path)
        print(f"Successfully removed {path}")
        return True
    except PermissionError:
        print("Permission error encountered, trying alternative methods...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try to change permissions and remove
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.chmod(file_path, 0o777)
                    os.remove(file_path)
                except:
                    pass
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.chmod(dir_path, 0o777)
                    os.rmdir(dir_path)
                except:
                    pass
        
        # Try to remove the root directory
        os.chmod(path, 0o777)
        os.rmdir(path)
        print(f"Successfully removed {path} after permission fix")
        return True
    except Exception as e:
        print(f"Still couldn't remove: {e}")
    
    # Last resort: rename and try again
    try:
        backup_name = f"{path}_backup_{int(time.time())}"
        os.rename(path, backup_name)
        print(f"WARNING: Renamed {path} to {backup_name}")
        print("You may need to manually delete this directory later.")
        return True
    except Exception as e:
        print(f"❌ Could not even rename directory: {e}")
        return False

def main():
    """Main cleanup function."""
    print("Cleaning PDF Power Converter Portable Distribution...")
    print("=" * 50)
    
    portable_dir = "portable_dist"
    
    if force_remove_directory(portable_dir):
        print("\n✅ Cleanup successful! You can now run portable_setup.py")
    else:
        print("\n❌ Cleanup failed. You may need to:")
        print("1. Close any applications that might be using files in portable_dist")
        print("2. Restart your command prompt as administrator")
        print("3. Manually delete the portable_dist directory")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())