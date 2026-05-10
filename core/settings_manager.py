import json
import os
from pathlib import Path
from core.logger import app_logger

class SettingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.settings_file = Path("settings.json")
        self.default_settings = {
            "recognition_threshold": 0.6,
            "duplicate_sensitivity": 5, # hamming distance threshold
            "max_worker_threads": max(1, os.cpu_count() - 1) if os.cpu_count() else 4,
            "auto_open_destination": True,
            "theme": "dark",
            "detect_duplicates": True
        }
        self.settings = self.default_settings.copy()
        self.load_settings()

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                app_logger.error(f"Failed to load settings: {e}. Using defaults.")
        else:
            self.save_settings()

    def save_settings(self, new_settings=None):
        if new_settings:
            self.settings.update(new_settings)
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            app_logger.error(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

# Global instance
settings_manager = SettingsManager()
