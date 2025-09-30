#!/usr/bin/env python3
"""
Startup script for the STEM Tutor Emotion Recognition Backend
"""

import subprocess
import sys
import os
import time

def check_dependencies():
    """Check if required dependencies are installed."""
    # Map package names to their import names
    package_imports = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'python-multipart': 'multipart',
        'opencv-python': 'cv2',
        'ultralytics': 'ultralytics',
        'torch': 'torch',
        'numpy': 'numpy'
    }
    
    missing_packages = []
    
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} - OK")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - Missing")
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ All required packages are installed")
    return True

def main():
    print("🚀 Starting STEM Tutor Emotion Recognition Backend...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  Some dependencies are missing, but attempting to start anyway...")
        print("   The server may fail if critical packages are not available.")
        print("   Press Ctrl+C to stop and install dependencies, or wait 5 seconds to continue...")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Startup cancelled by user")
            sys.exit(1)
    
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
        sys.exit(1)

if __name__ == "__main__":
    main()
