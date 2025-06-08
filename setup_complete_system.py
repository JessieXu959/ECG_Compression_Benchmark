#!/usr/bin/env python3
"""
ECG Compression Challenge - Complete System Setup
Sets up and starts both frontend and backend components
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import threading

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🏥 ECG COMPRESSION CHALLENGE - COMPLETE SETUP")
    print("=" * 60)
    print("Setting up your local ECG compression challenge environment")
    print()

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_backend_dependencies():
    """Install backend dependencies"""
    print("\n📦 Installing backend dependencies...")
    try:
        os.chdir("mini-backend")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Backend dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install backend dependencies:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    finally:
        os.chdir("..")

def check_node():
    """Check if Node.js is available for frontend server"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Node.js not found - will use Python HTTP server for frontend")
            return False
    except FileNotFoundError:
        print("⚠️  Node.js not found - will use Python HTTP server for frontend")
        return False

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    try:
        os.chdir("mini-backend")
        # Start backend in a separate process
        process = subprocess.Popen([sys.executable, "start_backend.py"])
        print("✅ Backend server starting on http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None
    finally:
        os.chdir("..")

def start_frontend():
    """Start the frontend server"""
    print("\n🌐 Starting frontend server...")
    try:
        # Use Python's built-in HTTP server
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000",
            "--bind", "localhost"
        ])
        print("✅ Frontend server starting on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_servers():
    """Wait for servers to start"""
    print("\n⏳ Waiting for servers to start...")
    time.sleep(3)

    # Check backend health
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is healthy")
        else:
            print("⚠️  Backend server may not be ready")
    except:
        print("⚠️  Could not verify backend health (requests module not available)")

    print("✅ Frontend server should be ready")

def open_browser():
    """Open browser to the application"""
    print("\n🌐 Opening application in browser...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please manually open: http://localhost:3000")

def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Your ECG Compression Challenge is now running:")
    print()
    print("📱 Frontend (Web Interface):")
    print("   URL: http://localhost:3000")
    print("   File: index.html")
    print()
    print("🔧 Backend (API Server):")
    print("   URL: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print()
    print("📁 Project Structure:")
    print("   ├── index.html          # Main web interface")
    print("   ├── scripts.js          # Frontend JavaScript")
    print("   ├── styles.css          # Frontend styles")
    print("   ├── mini-backend/       # Backend API server")
    print("   └── codabench_bundle/   # Original Codabench files")
    print()
    print("🔧 How to use:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Register a new team account")
    print("   3. Submit your ECG compression algorithm")
    print("   4. View results on the leaderboard")
    print()
    print("⚠️  To stop the servers:")
    print("   Press Ctrl+C in this terminal")
    print()
    print("📖 For more information, see:")
    print("   - mini-backend/README.md")
    print("   - API documentation at http://localhost:8000/docs")
    print()

def cleanup_on_exit(backend_process, frontend_process):
    """Cleanup function to stop servers"""
    print("\n🛑 Stopping servers...")
    if backend_process:
        backend_process.terminate()
        print("✅ Backend server stopped")
    if frontend_process:
        frontend_process.terminate()
        print("✅ Frontend server stopped")
    print("👋 Goodbye!")

def main():
    """Main setup function"""
    print_banner()

    # Check requirements
    if not check_python():
        sys.exit(1)

    check_node()

    # Install dependencies
    if not install_backend_dependencies():
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)

    # Start servers
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server")
        sys.exit(1)

    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend server")
        if backend_process:
            backend_process.terminate()
        sys.exit(1)

    # Wait and verify
    wait_for_servers()
    open_browser()
    print_instructions()

    # Keep running until interrupted
    try:
        print("🔄 Servers are running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_on_exit(backend_process, frontend_process)

if __name__ == "__main__":
    main()