# Setup & Build Instructions for Face Matcher AI

## 1. Prerequisites
- **Python 3.12+**
- **CMake** (required for `dlib` which is a dependency of `face_recognition`)
- **Visual Studio C++ Build Tools** (Select "Desktop development with C++")
  - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

## 2. Installation

1. Open your terminal/command prompt.
2. Navigate to this project directory:
   ```cmd
   cd path\to\Album Creator
   ```
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
5. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   *(Note: Installing `dlib` / `face_recognition` may take a few minutes as it compiles C++ code).*

## 3. Running the Application
To run the application in development mode:
```cmd
python main.py
```

## 4. Building the Windows EXE
We use PyInstaller to package the application into a standalone Windows executable.

1. Ensure your virtual environment is activated.
2. Run the build script:
   ```cmd
   python build_exe.py
   ```
3. Wait for the build process to complete. It will generate a `dist` folder.
4. Inside the `dist\FaceMatcherAI` folder, you will find `FaceMatcherAI.exe` along with its dependencies. You can distribute this entire folder.

## 5. Reducing EXE Size & Advanced Build
If you want to package it into a single file (slower startup time but single file):
```cmd
pyinstaller --noconfirm --onedir --windowed --name "FaceMatcherAI" --icon "assets/icons/app_icon.ico" main.py
```
*(For `onefile` replace `--onedir` with `--onefile`)*

## 6. Architecture & Quality
- **Clean Architecture:** MVC/MVVM inspired structure.
- **SQLite Database:** Stores scan history, settings, and duplicate image data.
- **Face Recognition Engine:** Runs concurrently in thread pools to prevent UI blocking.
- **Modern UI:** Uses PySide6 with QDarkTheme and custom glassmorphism styles.
