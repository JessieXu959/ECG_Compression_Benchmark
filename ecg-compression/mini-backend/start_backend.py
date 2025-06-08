#!/usr/bin/env python3
"""
Backend startup script for ECG Compression Challenge
"""

import os
import sys
import subprocess
import uvicorn

def main():
    """Start the FastAPI backend server"""
    print("🚀 Starting ECG Compression Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")

if __name__ == "__main__":
    main()