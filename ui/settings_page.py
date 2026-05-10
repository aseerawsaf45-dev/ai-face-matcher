from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QSlider, 
                               QLabel, QCheckBox, QSpinBox, QPushButton, QHBoxLayout, QComboBox)
from PySide6.QtCore import Qt
from core.settings_manager import settings_manager
from core.logger import app_logger

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # UI Elements
        self.lbl_threshold = QLabel()
        self.slider_threshold = QSlider(Qt.Horizontal)
        self.slider_threshold.setRange(1, 100) # 1 to 100 for percentage
        
        self.chk_duplicates = QCheckBox("Enable Duplicate Detection")
        
        self.spin_sensitivity = QSpinBox()
        self.spin_sensitivity.setRange(0, 20)
        
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 32)
        
        self.chk_auto_open = QCheckBox("Auto-open Destination Folder on Complete")
        
        # New settings
        self.combo_accuracy = QComboBox()
        self.combo_accuracy.addItems(["Maximum accuracy (slower)", "Balanced", "Fast scanning"])
        
        self.combo_hardware = QComboBox()
        self.combo_hardware.addItems(["Auto (GPU if available)", "CPU Only"])
        
        self.chk_offline = QCheckBox("Offline-only processing (No internet req)")
        self.chk_realtime_logs = QCheckBox("Show real-time verbose logs")
        
        # Build Form
        form.addRow("Accuracy Priority:", self.combo_accuracy)
        form.addRow("Hardware Acceleration:", self.combo_hardware)
        form.addRow("Recognition Tolerance:", self.slider_threshold)
        form.addRow("", self.lbl_threshold)
        form.addRow("Duplicates:", self.chk_duplicates)
        form.addRow("Duplicate Sensitivity (Hamming Dist):", self.spin_sensitivity)
        form.addRow("Max Worker Threads:", self.spin_threads)
        form.addRow("", self.chk_auto_open)
        form.addRow("", self.chk_offline)
        form.addRow("", self.chk_realtime_logs)
        
        layout.addLayout(form)
        
        # Save Button
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Connections
        self.slider_threshold.valueChanged.connect(self.update_threshold_label)
        self.chk_duplicates.toggled.connect(self.spin_sensitivity.setEnabled)
        
        self.load_settings()

    def load_settings(self):
        # Threshold: inverted for UI (higher % = more strict = lower tolerance value)
        tolerance = settings_manager.get("recognition_threshold", 0.6)
        percent = int((1.0 - tolerance) * 100)
        self.slider_threshold.setValue(max(1, min(100, percent)))
        self.update_threshold_label(percent)
        
        detect_dup = settings_manager.get("detect_duplicates", True)
        self.chk_duplicates.setChecked(detect_dup)
        self.spin_sensitivity.setEnabled(detect_dup)
        
        self.spin_sensitivity.setValue(settings_manager.get("duplicate_sensitivity", 5))
        self.spin_threads.setValue(settings_manager.get("max_worker_threads", 4))
        self.chk_auto_open.setChecked(settings_manager.get("auto_open_destination", True))
        
        # Load new settings
        accuracy = settings_manager.get("accuracy_priority", "Balanced")
        if accuracy == "Maximum accuracy": self.combo_accuracy.setCurrentIndex(0)
        elif accuracy == "Balanced": self.combo_accuracy.setCurrentIndex(1)
        elif accuracy == "Fast scanning": self.combo_accuracy.setCurrentIndex(2)
        
        hardware = settings_manager.get("hardware_acceleration", "Auto")
        if hardware == "Auto": self.combo_hardware.setCurrentIndex(0)
        elif hardware == "CPU Only": self.combo_hardware.setCurrentIndex(1)
        
        self.chk_offline.setChecked(settings_manager.get("offline_processing", True))
        self.chk_realtime_logs.setChecked(settings_manager.get("realtime_logs", False))

    def update_threshold_label(self, val):
        self.lbl_threshold.setText(f"Confidence Threshold: {val}%")

    def save_settings(self):
        # Convert percent back to tolerance
        percent = self.slider_threshold.value()
        tolerance = 1.0 - (percent / 100.0)
        
        settings_manager.set("recognition_threshold", tolerance)
        settings_manager.set("detect_duplicates", self.chk_duplicates.isChecked())
        settings_manager.set("duplicate_sensitivity", self.spin_sensitivity.value())
        settings_manager.set("max_worker_threads", self.spin_threads.value())
        settings_manager.set("auto_open_destination", self.chk_auto_open.isChecked())
        
        # Save new settings
        acc_idx = self.combo_accuracy.currentIndex()
        if acc_idx == 0: accuracy = "Maximum accuracy"
        elif acc_idx == 1: accuracy = "Balanced"
        else: accuracy = "Fast scanning"
        
        hw_idx = self.combo_hardware.currentIndex()
        if hw_idx == 0: hardware = "Auto"
        else: hardware = "CPU Only"
        
        settings_manager.set("accuracy_priority", accuracy)
        settings_manager.set("hardware_acceleration", hardware)
        settings_manager.set("offline_processing", self.chk_offline.isChecked())
        settings_manager.set("realtime_logs", self.chk_realtime_logs.isChecked())
        
        app_logger.info("Settings saved successfully.")
