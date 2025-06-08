#!/usr/bin/env python3
"""
Script to copy Codabench bundle files to the backend directory
"""

import shutil
import os
from pathlib import Path

def copy_files():
    """Copy files from bundle directories to backend structure"""
    print("📁 Copying Codabench bundle files...")

    # Define source and destination mappings
    files_to_copy = [
        # (source_path, destination_path)
        ("ingestion_program/ingestion.py", "ecg-compression/codabench_bundle/ingestion.py"),
        ("scoring_program/scoring.py", "ecg-compression/codabench_bundle/scoring.py"),
        ("solution/ecg_model.py", "ecg-compression/codabench_bundle/ecg_model.py"),
        ("solution/solve.py", "ecg-compression/codabench_bundle/solve.py"),
        ("competition.yaml", "ecg-compression/codabench_bundle/competition.yaml"),
        ("scoring_program/requirements.txt", "ecg-compression/mini-backend/codabench_requirements.txt")
    ]

    # Create destination directories
    Path("ecg-compression/codabench_bundle").mkdir(parents=True, exist_ok=True)
    Path("ecg-compression/mini-backend").mkdir(parents=True, exist_ok=True)

    # Copy files
    copied_files = []
    for source, destination in files_to_copy:
        source_path = Path(source)
        destination_path = Path(destination)

        if source_path.exists():
            try:
                # Create parent directory if it doesn't exist
                destination_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(source_path, destination_path)
                copied_files.append(destination)
                print(f"✅ Copied: {source} → {destination}")
            except Exception as e:
                print(f"❌ Failed to copy {source}: {e}")
        else:
            print(f"⚠️  File not found: {source}")

    print(f"\n📋 Summary: {len(copied_files)} files copied successfully")

    # List what was copied
    print("\n📂 Files copied to ecg-compression/codabench_bundle/:")
    for file_path in copied_files:
        if "codabench_bundle" in file_path:
            print(f"  - {Path(file_path).name}")

    return copied_files

def main():
    """Main function"""
    print("🔄 ECG Compression Bundle File Organizer")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("ecg_compression_bundle.zip").exists() and not Path("competition.yaml").exists():
        print("❌ This script should be run from the ecg_compression_bundle directory")
        print("   Make sure you're in the directory containing competition.yaml")
        return

    # Copy files
    copied_files = copy_files()

    if copied_files:
        print("\n🎉 Bundle files organized successfully!")
        print("\nNext steps:")
        print("1. cd ecg-compression")
        print("2. python setup_backend.py")
        print("3. cd mini-backend && python start_backend.py")
    else:
        print("\n❌ No files were copied. Please check the file paths.")

if __name__ == "__main__":
    main()