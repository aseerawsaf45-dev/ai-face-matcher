from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QFont
from core.logger import logger_signals

class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.text_edit.clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Connect to logger signals
        logger_signals.log_message.connect(self.append_log)

    def append_log(self, msg):
        self.text_edit.append(msg)
        # Scroll to bottom
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
