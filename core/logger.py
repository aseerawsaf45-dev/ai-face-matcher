import logging
import os
import sys
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class UILogHandler(logging.Handler):
    """
    Custom logging handler that emits a signal to update the UI.
    """
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)

class LoggerSignals(QObject):
    log_message = Signal(str)

class AppLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.signals = LoggerSignals()
        self.logger = logging.getLogger("FaceMatcherAI")
        self.logger.setLevel(logging.DEBUG)
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # File Handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # UI Handler
        ui_handler = UILogHandler(self.signals.log_message)
        ui_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        ui_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(ui_handler)

    def get_logger(self):
        return self.logger
        
    def get_signals(self):
        return self.signals

# Global instance
app_logger = AppLogger().get_logger()
logger_signals = AppLogger().get_signals()
