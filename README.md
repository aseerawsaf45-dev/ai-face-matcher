# AI Face Matcher & Album Creator

A professional desktop application designed to scan large folders of images, identify specific people using facial recognition, and organize them into specialized albums. Built with Python, PySide6, and the `face_recognition` library.

## 🚀 Key Features

- **High-Accuracy Facial Recognition**: Uses state-of-the-art dlib models to find and match faces.
- **Dynamic Organization**: Automatically creates output folders named after your reference images.
- **Duplicate Detection**: Built-in perceptual hashing (pHash) to skip near-identical images and keep your albums clean.
- **Performance Profiles**:
  - **Maximum Accuracy**: Uses CNN models and high upsampling for detecting small or distant faces.
  - **Balanced**: A perfect middle ground for everyday scanning.
  - **Fast Scanning**: Optimized for speed on clear, high-quality photos.
- **Hardware Acceleration**: Optional GPU (CUDA) support for lightning-fast processing on NVIDIA hardware.
- **Privacy Focused**: 100% offline processing. Your photos never leave your machine.
- **Real-time Monitoring**: Live progress bars and verbose logs to track the scanning process.
- **Export Reports**: Generate CSV summaries of your matches and scan statistics.

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- C++ Build Tools (Required for `dlib`)
- (Optional) CUDA and cuDNN for GPU acceleration

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/aseerawsaf45-dev/ai-face-matcher.git
   cd ai-face-matcher
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

1. **Start the App**: Run `python main.py`.
2. **Select Reference Images**: Choose one or more photos of the person you want to find.
3. **Select Folders**: Choose a source folder (your messy photos) and a destination folder (where the album will be created).
4. **Configure Settings**: Head to the Settings tab to adjust accuracy, enable GPU support, or toggle duplicate detection.
5. **Scan**: Hit "Start Scan" and watch the app build your album!

## 📦 Building Executable

To build a standalone Windows executable:
```bash
python build_exe.py
```
The output will be in the `dist/` directory.



---
Built by [aseerawsaf45-dev](https://github.com/aseerawsaf45-dev)
