import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.logger import app_logger

def main():
    try:
        # Prevent PyInstaller issues with multiprocessing
        if sys.platform.startswith('win'):
            import multiprocessing
            multiprocessing.freeze_support()
        
        # Set High DPI scaling
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        app = QApplication(sys.argv)
        app.setApplicationName("Face Matcher AI")
        app.setApplicationVersion("1.0.0")
        
        app_logger.info("Application starting...")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        app_logger.critical(f"Application crashed: {e}")
        raise

if __name__ == "__main__":
    main()
