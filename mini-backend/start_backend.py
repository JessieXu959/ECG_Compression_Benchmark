#!/usr/bin/env python3
"""
ECG Compression Challenge - Backend Startup Script
Launches the FastAPI backend server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting ECG Compression Challenge Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("\n" + "="*50)

    try:
        # Import and run the FastAPI app
        import uvicorn
        from main import app

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🔧 ECG Compression Challenge - Backend Startup")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found in current directory")
        print("Please run this script from the mini-backend directory")
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Create necessary directories
    directories = ["uploads", "temp", "scoring", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created/verified directory: {directory}")

    print("\n🎯 Starting backend server...")
    start_server()

if __name__ == "__main__":
    main()