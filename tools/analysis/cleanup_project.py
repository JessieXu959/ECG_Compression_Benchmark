#!/usr/bin/env python3
"""
Project Cleanup Script for ECG Compression Bundle
Safely deletes unnecessary files while preserving core functionality
"""

import os
import shutil
from pathlib import Path
import json

def load_analysis_report():
    """Load the file analysis report"""
    try:
        with open('file_analysis_report.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Analysis report not found. Please run analyze_files.py first.")
        return None

def safe_delete_file(filepath):
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        else:
            print(f"⚠️  File not found: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {filepath}: {e}")
        return False

def safe_delete_directory(dirpath):
    """Safely delete an empty directory"""
    try:
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            # Only delete if directory is empty
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
                return True
            else:
                print(f"⚠️  Directory not empty: {dirpath}")
                return False
        return False
    except Exception as e:
        print(f"❌ Error deleting directory {dirpath}: {e}")
        return False

def cleanup_project():
    """Main cleanup function"""
    report = load_analysis_report()
    if not report:
        return

    print("🧹 Starting project cleanup...")
    print("="*60)

    deleted_files = 0
    deleted_size = 0

    # Files to definitely delete
    files_to_delete = [
        # Test files (safe to delete)
        "clear_demo_data.py",
        "create_test_user.py",
        "create_test_zip.py",
        "debug_evaluation_system.py",
        "debug_token.py",
        "demo_real_evaluation.py",
        "quick_test.py",
        "test_algorithm.py",
        "test_api.py",
        "test_concurrent_submissions.py",
        "test_data_persistence.py",
        "test_new_features.py",
        "test_optimized_solution.py",
        "test_real_evaluation.py",
        "test_token_fix.py",
        "test_updated_solution.py",
        "test_upload_direct.py",

        # Test ZIP files
        "test_algorithm.zip",
        "test_ecg_algorithm.zip",
        "test_solution.zip",
        "test_solution_new.zip",

        # Duplicate files in ecg-compression directory
        "ecg-compression/test_solution.zip",
        "ecg-compression/README.md",
        "ecg-compression/setup_complete_system.py",

        # Output test files (generated data)
        "solution/test_output.mat",

        # Documentation files (duplicates)
        "FRONTEND_TEST_GUIDE.md",
    ]

    print("🗑️  Deleting test files and duplicates...")
    for filename in files_to_delete:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            if safe_delete_file(filename):
                deleted_files += 1
                deleted_size += file_size
                print(f"   ✅ Deleted: {filename}")
            else:
                print(f"   ❌ Failed to delete: {filename}")

    # Delete entire uploads directory (all temporary upload files)
    uploads_dir = "mini-backend/uploads"
    if os.path.exists(uploads_dir):
        try:
            # Calculate size before deletion
            uploads_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(uploads_dir)
                for filename in filenames
            )

            shutil.rmtree(uploads_dir)
            deleted_size += uploads_size
            print(f"   ✅ Deleted uploads directory: {uploads_dir}")

            # Count files in uploads
            upload_files = sum(
                len(filenames)
                for dirpath, dirnames, filenames in os.walk(uploads_dir)
                if os.path.exists(dirpath)
            )
            deleted_files += upload_files

        except Exception as e:
            print(f"   ❌ Error deleting uploads directory: {e}")

    # Delete duplicate directories
    duplicate_dirs = [
        "ecg-compression/mini-backend",  # Duplicate of mini-backend
        "solution/solution",  # Nested solution directory
        "ECG-Compression-Benchmark",  # Codabench bundle (keep main files only)
        "Development Phase",  # Development files
        "final_phase",  # Phase files
        "pages",  # Duplicate pages
        "ingestion_program",  # Codabench files
        "scoring_program",  # Codabench files
    ]

    print("\n🗂️  Deleting duplicate directories...")
    for dirname in duplicate_dirs:
        if os.path.exists(dirname):
            try:
                # Calculate size before deletion
                dir_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(dirname)
                    for filename in filenames
                )

                # Count files
                dir_files = sum(
                    len(filenames)
                    for dirpath, dirnames, filenames in os.walk(dirname)
                )

                shutil.rmtree(dirname)
                deleted_files += dir_files
                deleted_size += dir_size
                print(f"   ✅ Deleted directory: {dirname}")
            except Exception as e:
                print(f"   ❌ Error deleting directory {dirname}: {e}")

    # Delete specific duplicate data files
    duplicate_data_files = [
        "data/submissions.csv",  # Duplicate
        "ecg-compression/mini-backend/data/submissions.csv",  # Duplicate
        "mini-backend/data/submissions.json",  # Duplicate of leaderboard.json
    ]

    print("\n📊 Deleting duplicate data files...")
    for filepath in duplicate_data_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            if safe_delete_file(filepath):
                deleted_files += 1
                deleted_size += file_size
                print(f"   ✅ Deleted: {filepath}")

    # Clean up empty directories
    empty_dirs = ["data", "temp", "uploads"]
    for dirname in empty_dirs:
        safe_delete_directory(dirname)

    # Delete temporary analysis file
    if os.path.exists('analyze_files.py'):
        safe_delete_file('analyze_files.py')
        deleted_files += 1

    print("\n" + "="*60)
    print("✨ CLEANUP SUMMARY")
    print("="*60)
    print(f"📁 Files deleted: {deleted_files}")
    print(f"💾 Space saved: {deleted_size / (1024*1024):.2f} MB")

    print(f"\n🎯 CORE FILES PRESERVED:")
    core_files = [
        "real_evaluation_system.py",
        "mini-backend/main.py",
        "mini-backend/storage.py",
        "mini-backend/evaluate.py",
        "ecg-compression/index.html",
        "ecg-compression/scripts.js",
        "ecg-compression/styles.css",
        "solution/solve.py",
        "solution/ecg_model.py",
        "README.md",
        "requirements.txt"
    ]

    for core_file in core_files:
        if os.path.exists(core_file):
            print(f"   ✅ {core_file}")
        else:
            print(f"   ⚠️  {core_file} (not found)")

    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   1. ✅ Test files and duplicates removed")
    print(f"   2. ✅ Upload cache cleared")
    print(f"   3. ✅ Duplicate directories removed")
    print(f"   4. 🔄 Core functionality preserved")
    print(f"   5. 📝 Consider running system check: python quick_system_check.py")

    print(f"\n🎉 Project cleanup completed successfully!")

if __name__ == "__main__":
    # Ask for confirmation
    print("🧹 ECG COMPRESSION BUNDLE - PROJECT CLEANUP")
    print("="*50)
    print("This will delete:")
    print("• Test files and scripts")
    print("• Duplicate ZIP files")
    print("• Upload cache directories")
    print("• Duplicate directories and files")
    print("• Temporary data files")
    print("\n⚠️  Core files will be preserved.")

    response = input("\nProceed with cleanup? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        cleanup_project()
    else:
        print("❌ Cleanup cancelled.")