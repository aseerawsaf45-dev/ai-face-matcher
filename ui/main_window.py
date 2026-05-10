from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QStackedWidget, QPushButton, QLabel)
from PySide6.QtCore import Qt, QSize
from ui.dashboard import Dashboard
from ui.settings_page import SettingsPage
from ui.logs_page import LogsPage
import qdarktheme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Matcher AI - Professional Edition")
        self.setMinimumSize(1000, 700)
        
        # Apply theme
        self.setStyleSheet(qdarktheme.load_stylesheet())
        
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-right: 1px solid #333333;
            }
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                background-color: transparent;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
            QPushButton:checked {
                background-color: #333333;
                border-left: 4px solid #4a90e2;
            }
            QLabel {
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        title_lbl = QLabel("Face Matcher AI")
        sidebar_layout.addWidget(title_lbl)
        
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        
        self.btn_logs = QPushButton("Logs")
        self.btn_logs.setCheckable(True)
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setCheckable(True)
        
        # Button Group equivalent logic
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.btn_dashboard))
        self.btn_logs.clicked.connect(lambda: self.switch_page(1, self.btn_logs))
        self.btn_settings.clicked.connect(lambda: self.switch_page(2, self.btn_settings))
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_logs)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()
        
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)
        
        # Content Area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #121212;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #333333;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#primaryButton {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton#primaryButton:hover {
                background-color: #357abd;
            }
            QPushButton#primaryButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        
        # Pages
        self.dashboard_page = Dashboard()
        self.logs_page = LogsPage()
        self.settings_page = SettingsPage()
        
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.logs_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.stacked_widget)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def switch_page(self, index, active_btn):
        # Reset all buttons
        self.btn_dashboard.setChecked(False)
        self.btn_logs.setChecked(False)
        self.btn_settings.setChecked(False)
        
        # Set active button
        active_btn.setChecked(True)
        
        # Switch stacked widget
        self.stacked_widget.setCurrentIndex(index)
