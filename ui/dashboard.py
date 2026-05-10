import os
import subprocess
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QFileDialog, QProgressBar, 
                               QGroupBox, QFormLayout, QListWidget, QMessageBox)
from PySide6.QtCore import Qt
from core.scanner import ScannerWorker
from core.settings_manager import settings_manager
from core.logger import app_logger
from services.export_service import ExportService

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.reference_images = []
        self.matches_list = []
        self.stats = {}
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 1. Input Section
        input_group = QGroupBox("Scan Setup")
        input_layout = QFormLayout()
        
        # Person Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("E.g. John Doe")
        input_layout.addRow("Person Name:", self.name_input)
        
        # Reference Images
        ref_layout = QHBoxLayout()
        self.ref_btn = QPushButton("Select Reference Images")
        self.ref_btn.clicked.connect(self.select_reference_images)
        self.ref_lbl = QLabel("0 images selected")
        ref_layout.addWidget(self.ref_btn)
        ref_layout.addWidget(self.ref_lbl)
        input_layout.addRow("Reference Faces:", ref_layout)
        
        # Source Folder
        src_layout = QHBoxLayout()
        self.src_btn = QPushButton("Select Source Folder")
        self.src_btn.clicked.connect(self.select_source_folder)
        self.src_lbl = QLabel("None")
        src_layout.addWidget(self.src_btn)
        src_layout.addWidget(self.src_lbl)
        input_layout.addRow("Source Folder:", src_layout)
        
        # Destination Folder
        dest_layout = QHBoxLayout()
        self.dest_btn = QPushButton("Select Destination Folder")
        self.dest_btn.clicked.connect(self.select_dest_folder)
        self.dest_lbl = QLabel("None")
        dest_layout.addWidget(self.dest_btn)
        dest_layout.addWidget(self.dest_lbl)
        input_layout.addRow("Output Folder:", dest_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 2. Control Section
        control_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start Scan")
        self.btn_start.setObjectName("primaryButton")
        self.btn_start.clicked.connect(self.start_scan)
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_scan)
        self.btn_pause.setEnabled(False)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel_scan)
        self.btn_cancel.setEnabled(False)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_cancel)
        layout.addLayout(control_layout)
        
        # 3. Progress Section
        progress_group = QGroupBox("Progress")
        prog_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v Scanned")
        prog_layout.addWidget(self.progress_bar)
        
        stats_layout = QHBoxLayout()
        self.lbl_scanned = QLabel("Scanned: 0")
        self.lbl_matches = QLabel("Matches: 0")
        self.lbl_dups = QLabel("Duplicates Skipped: 0")
        self.lbl_errors = QLabel("Errors: 0")
        
        stats_layout.addWidget(self.lbl_scanned)
        stats_layout.addWidget(self.lbl_matches)
        stats_layout.addWidget(self.lbl_dups)
        stats_layout.addWidget(self.lbl_errors)
        prog_layout.addLayout(stats_layout)
        
        progress_group.setLayout(prog_layout)
        layout.addWidget(progress_group)
        
        # 4. Results List
        results_group = QGroupBox("Recent Matches")
        res_layout = QVBoxLayout()
        self.matches_widget = QListWidget()
        res_layout.addWidget(self.matches_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_csv.setEnabled(False)
        export_layout.addStretch()
        export_layout.addWidget(self.btn_export_csv)
        res_layout.addLayout(export_layout)
        
        results_group.setLayout(res_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)

    def select_reference_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Reference Images", "", "Images (*.jpg *.jpeg *.png *.webp)")
        if files:
            self.reference_images = files
            self.ref_lbl.setText(f"{len(files)} images selected")

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.src_lbl.setText(folder)
            self.src_folder = folder

    def select_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.dest_lbl.setText(folder)
            self.dest_folder = folder

    def start_scan(self):
        if not self.reference_images:
            QMessageBox.warning(self, "Validation Error", "Please select at least one reference image.")
            return
        if not hasattr(self, 'src_folder') or not hasattr(self, 'dest_folder'):
            QMessageBox.warning(self, "Validation Error", "Please select source and destination folders.")
            return
            
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0) # Indeterminate until count is known or just leave as is
        self.lbl_scanned.setText("Scanned: 0")
        self.lbl_matches.setText("Matches: 0")
        self.lbl_dups.setText("Duplicates Skipped: 0")
        self.lbl_errors.setText("Errors: 0")
        self.matches_widget.clear()
        self.matches_list = []
        self.btn_export_csv.setEnabled(False)
        
        # Create a new folder inside dest_folder using reference image name
        ref_name = os.path.splitext(os.path.basename(self.reference_images[0]))[0]
        final_dest_folder = os.path.join(self.dest_folder, ref_name)
        os.makedirs(final_dest_folder, exist_ok=True)

        self.worker = ScannerWorker(
            self.src_folder, 
            final_dest_folder, 
            self.reference_images, 
            self.name_input.text()
        )
        
        self.worker.signals.progress_updated.connect(self.update_progress)
        self.worker.signals.match_found.connect(self.add_match)
        self.worker.signals.log_message.connect(self.add_log_message)
        self.worker.signals.scan_completed.connect(self.scan_finished)
        self.worker.signals.scan_cancelled.connect(self.scan_cancelled)
        self.worker.signals.error_occurred.connect(self.scan_error)
        
        self.worker.start()

    def pause_scan(self):
        if self.worker:
            if self.worker._is_paused:
                self.worker.resume()
                self.btn_pause.setText("Pause")
            else:
                self.worker.pause()
                self.btn_pause.setText("Resume")

    def cancel_scan(self):
        if self.worker:
            self.worker.cancel()
            self.btn_pause.setEnabled(False)

    def update_progress(self, scanned, matches, dups, errors):
        self.progress_bar.setValue(scanned)
        self.progress_bar.setMaximum(max(scanned, self.progress_bar.maximum())) # Just grow it for now
        self.lbl_scanned.setText(f"Scanned: {scanned}")
        self.lbl_matches.setText(f"Matches: {matches}")
        self.lbl_dups.setText(f"Duplicates Skipped: {dups}")
        self.lbl_errors.setText(f"Errors: {errors}")

    def add_match(self, orig, copied, confidence):
        name = os.path.basename(copied)
        self.matches_widget.insertItem(0, f"Match ({confidence:.1f}%): {name}")
        self.matches_list.append({
            'original': orig,
            'copied': copied,
            'confidence': confidence
        })

    def add_log_message(self, msg):
        self.matches_widget.insertItem(0, f"[LOG] {msg}")

    def reset_buttons(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_pause.setText("Pause")
        self.btn_export_csv.setEnabled(len(self.matches_list) > 0)

    def scan_finished(self, total, matches, dups):
        self.reset_buttons()
        self.stats = {'total': total, 'matches': matches, 'duplicates': dups}
        QMessageBox.information(self, "Scan Complete", f"Scan completed!\nMatches found: {matches}\nDuplicates skipped: {dups}")
        
        if settings_manager.get("auto_open_destination", True):
            # Windows specific
            os.startfile(self.dest_folder)

    def scan_cancelled(self):
        self.reset_buttons()
        QMessageBox.information(self, "Scan Cancelled", "The scan was cancelled by the user.")

    def scan_error(self, err_msg):
        self.reset_buttons()
        QMessageBox.critical(self, "Scan Error", f"An error occurred: {err_msg}")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if path:
            if ExportService.export_csv(path, self.stats, self.matches_list):
                QMessageBox.information(self, "Success", "Export successful.")
            else:
                QMessageBox.critical(self, "Error", "Failed to export report.")
