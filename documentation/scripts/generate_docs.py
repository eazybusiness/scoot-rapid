#!/usr/bin/env python3
"""
Master Documentation Generator for ScootRapid
Generates diagrams and converts to DOCX
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def generate_diagrams():
    """Generate all diagrams"""
    print("🎨 Generating diagrams...")
    try:
        subprocess.check_call([sys.executable, "generate_diagrams.py"])
        print("✅ Diagrams generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate diagrams: {e}")
        return False

def convert_to_docx():
    """Convert HTML to DOCX"""
    print("📄 Converting to DOCX...")
    try:
        subprocess.check_call([sys.executable, "html_to_docx.py"])
        print("✅ DOCX conversion completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to convert to DOCX: {e}")
        return False

def main():
    """Main generation process"""
    print("🚀 Starting ScootRapid documentation generation...")
    
    # Change to scripts directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Generate diagrams
    if not generate_diagrams():
        return False
    
    # Step 3: Convert to DOCX
    if not convert_to_docx():
        return False
    
    print("🎉 ScootRapid documentation generation completed!")
    print("📁 Generated files:")
    print("   - diagrams/*.png (Professional diagrams)")
    print("   - generated/ScootRapid_Dokumentation.docx (Final documentation)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
