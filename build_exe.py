import PyInstaller.__main__
import os

def build():
    print("Starting build process for FaceMatcher AI...")
    
    # Ensure assets directory exists for PyInstaller
    if not os.path.exists("assets"):
        os.makedirs("assets/icons", exist_ok=True)
        os.makedirs("assets/styles", exist_ok=True)
        os.makedirs("assets/fonts", exist_ok=True)

    # Basic PyInstaller arguments
    args = [
        'main.py',
        '--name=FaceMatcherAI',
        '--onefile', # Single file bundle for easier distribution
        '--windowed', # No console window
        '--noconfirm',
        '--clean',
        '--add-data=assets;assets',
        '--hidden-import=pkg_resources',
        '--hidden-import=setuptools',
        '--collect-data=face_recognition_models',
        '--log-level=INFO',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    print("Build complete! Check the 'dist' folder.")

if __name__ == "__main__":
    build()
