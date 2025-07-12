#!/usr/bin/env python3
"""
PDF Cleanup Agent Pipeline
Complete data flow from PDF to Foundry VTT JSON
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

# Activate virtual environment
def get_venv_python():
    """Get the Python executable from the virtual environment."""
    venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python')
    if os.path.exists(venv_python):
        return venv_python
    else:
        # Fallback to system Python if venv not found
        return sys.executable

def load_config():
    """Load pipeline configuration."""
    with open('pipeline_config.yml', 'r') as f:
        return yaml.safe_load(f)

def run_step(step_name, description, pdf_path, pdf_stem):
    """Run a pipeline step with error handling."""
    print(f"\n🔄 Step: {step_name}")
    print(f"📝 {description}")
    
    # Get Python executable from venv
    python_exe = get_venv_python()
    
    try:
        if step_name == "pdf_segmentation":
            # Run PDF segmentation on all PDFs in the data/pdf directory
            print(f"🔄 Processing PDF: {pdf_path}")
            result = subprocess.run([
                python_exe, 'pdf_segmenter.py', 
                pdf_path,
                '--output-dir', 'data/txt_input'
            ], capture_output=True, text=True, check=True)
            print(f"✅ PDF segmentation complete for {pdf_path}")
            
        elif step_name == "llm_cleaning":
            # agent_stream.py uses config file, no arguments needed
            result = subprocess.run([
                python_exe, 'agent_stream.py'
            ], capture_output=True, text=True, check=True)
            print(f"✅ LLM cleaning complete for {pdf_stem}")
            
        elif step_name == "post_processing_cleanup":
            # Run post-processing cleanup
            md_dir = os.path.join('data/markdown', pdf_stem)
            
            # Check if there are subdirectories with markdown files
            subdirs_with_md = []
            if os.path.exists(md_dir):
                for item in os.listdir(md_dir):
                    item_path = os.path.join(md_dir, item)
                    if os.path.isdir(item_path):
                        # Check if this subdirectory contains .md files
                        md_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
                        if md_files:
                            subdirs_with_md.append(item_path)
            
            if subdirs_with_md:
                # Process each subdirectory that contains markdown files
                for subdir in subdirs_with_md:
                    print(f"🔄 Post-processing cleanup for subdirectory: {os.path.basename(subdir)}")
                    result = subprocess.run([
                        python_exe, 'run_post_processing.py', subdir
                    ], capture_output=True, text=True, check=True)
                    print(f"✅ Post-processing cleanup complete for {os.path.basename(subdir)}")
            else:
                # Fallback to processing the main directory
                result = subprocess.run([
                    python_exe, 'run_post_processing.py', md_dir
                ], capture_output=True, text=True, check=True)
                print(f"✅ Post-processing cleanup complete for {pdf_stem}")
            
        elif step_name == "post_processing_formatting":
            # Run heading formatting
            md_dir = os.path.join('data/markdown', pdf_stem)
            
            # Check if there are subdirectories with markdown files
            subdirs_with_md = []
            if os.path.exists(md_dir):
                for item in os.listdir(md_dir):
                    item_path = os.path.join(md_dir, item)
                    if os.path.isdir(item_path):
                        # Check if this subdirectory contains .md files
                        md_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
                        if md_files:
                            subdirs_with_md.append(item_path)
            
            if subdirs_with_md:
                # Process each subdirectory that contains markdown files
                for subdir in subdirs_with_md:
                    print(f"🔄 Heading formatting for subdirectory: {os.path.basename(subdir)}")
                    result = subprocess.run([
                        python_exe, 'post_processing_formatting.py', subdir
                    ], capture_output=True, text=True, check=True)
                    print(f"✅ Heading formatting complete for {os.path.basename(subdir)}")
            else:
                # Fallback to processing the main directory
                result = subprocess.run([
                    python_exe, 'post_processing_formatting.py', md_dir
                ], capture_output=True, text=True, check=True)
                print(f"✅ Heading formatting complete for {pdf_stem}")
            
        elif step_name == "vtt_conversion":
            # Convert markdown directories to VTT JSON
            md_dir = os.path.join('data/markdown', pdf_stem)
            
            # Check if there are subdirectories with markdown files
            subdirs_with_md = []
            if os.path.exists(md_dir):
                for item in os.listdir(md_dir):
                    item_path = os.path.join(md_dir, item)
                    if os.path.isdir(item_path):
                        # Check if this subdirectory contains .md files
                        md_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
                        if md_files:
                            subdirs_with_md.append(item_path)
            
            if subdirs_with_md:
                # Process each subdirectory that contains markdown files
                for subdir in subdirs_with_md:
                    print(f"🔄 Converting subdirectory: {os.path.basename(subdir)}")
                    result = subprocess.run([
                        python_exe, 'markdown_to_fvtt.py', subdir
                    ], capture_output=True, text=True, check=True)
                    print(f"✅ VTT conversion complete for {os.path.basename(subdir)}")
            else:
                # Fallback to processing the main directory
                result = subprocess.run([
                    python_exe, 'markdown_to_fvtt.py', md_dir
                ], capture_output=True, text=True, check=True)
                print(f"✅ VTT conversion complete for {pdf_stem}")
            
        else:
            print(f"❌ Unknown step: {step_name}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in step {step_name}: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in step {step_name}: {e}")
        return False
    
    return True

def main():
    """Run the complete pipeline."""
    print("🚀 Starting PDF Cleanup Agent Pipeline")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Get PDF argument (default to example.pdf)
    if len(sys.argv) > 1:
        pdf_filename = sys.argv[1]
    else:
        pdf_filename = "example.pdf"
    pdf_path = os.path.join("data/pdf", pdf_filename)
    pdf_stem = Path(pdf_filename).stem
    
    # Define pipeline steps
    pipeline_steps = [
        ("pdf_segmentation", f"Segmenting PDF {pdf_filename} into text files"),
        ("llm_cleaning", f"Cleaning text for {pdf_stem} with LLM"),
        ("post_processing_cleanup", f"Removing LLM artifacts for {pdf_stem}"),
        ("post_processing_formatting", f"Formatting headings for {pdf_stem}"),
        ("vtt_conversion", f"Converting {pdf_stem} to Foundry VTT JSON")
    ]
    
    # Run each step
    for step_name, description in pipeline_steps:
        success = run_step(step_name, description, pdf_path, pdf_stem)
        if not success:
            print(f"\n❌ Pipeline failed at step: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Pipeline completed successfully!")
    print("📁 Check data/json/ for Foundry VTT files")

if __name__ == "__main__":
    main() 