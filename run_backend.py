#!/usr/bin/env python3
"""
Simple backend runner without dependency checking
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting STEM Tutor Backend (Simple Mode)...")
    print("=" * 50)
    
    # Check if model file exists
    model_path = os.path.join("Models", "ALL_models", "YoloFace recognition", "best.pt")
    if not os.path.exists(model_path):
        print(f"⚠️  Warning: Model file not found at {model_path}")
        print("   Emotion recognition will be disabled until model is available")
    
    # Start the backend server
    try:
        print("\n🌐 Starting FastAPI server on http://localhost:8000")
        print("📖 API documentation available at http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Try installing missing dependencies:")
        print("   pip install fastapi uvicorn python-multipart opencv-python ultralytics torch numpy")
        sys.exit(1)

if __name__ == "__main__":
    main()
