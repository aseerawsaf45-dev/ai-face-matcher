import os
import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal, QThread
from core.logger import app_logger
from core.face_engine import FaceEngine
from core.duplicate_detector import DuplicateDetector
from core.settings_manager import settings_manager
from core.database import db_manager

class ScannerSignals(QObject):
    progress_updated = Signal(int, int, int, int) # scanned, matches, duplicates, errors
    scan_completed = Signal(int, int, int) # total, matches, duplicates
    scan_cancelled = Signal()
    match_found = Signal(str, str, float) # original_path, copied_path, confidence
    error_occurred = Signal(str)
    log_message = Signal(str)

class ScannerWorker(QThread):
    def __init__(self, source_folder, dest_folder, reference_images, person_name=""):
        super().__init__()
        self.source_folder = Path(source_folder)
        self.dest_folder = Path(dest_folder)
        self.reference_images = reference_images
        self.person_name = person_name
        
        self.signals = ScannerSignals()
        
        self._is_paused = False
        self._is_cancelled = False
        
        # Load settings
        self.tolerance = settings_manager.get("recognition_threshold", 0.6)
        self.detect_duplicates = settings_manager.get("detect_duplicates", True)
        self.dup_sensitivity = settings_manager.get("duplicate_sensitivity", 5)
        self.max_workers = settings_manager.get("max_worker_threads", 4)
        
        # Initialize engines
        self.face_engine = FaceEngine(tolerance=self.tolerance)
        self.duplicate_detector = DuplicateDetector(sensitivity=self.dup_sensitivity) if self.detect_duplicates else None
        
        self.show_realtime_logs = settings_manager.get("realtime_logs", False)
        
        # Stats
        self.total_scanned = 0
        self.matches_found = 0
        self.duplicates_skipped = 0
        self.errors = 0
        
        # Supported extensions
        self.supported_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def cancel(self):
        self._is_cancelled = True

    def _process_image(self, img_path):
        """Worker function for threading"""
        if self._is_cancelled:
            return None
            
        while self._is_paused:
            time.sleep(0.5)
            if self._is_cancelled:
                return None

        result = {
            'path': img_path,
            'is_match': False,
            'confidence': 0.0,
            'is_duplicate': False,
            'error': None
        }

        try:
            # 1. Face Match
            is_match, confidence = self.face_engine.check_match(img_path)
            result['is_match'] = is_match
            result['confidence'] = confidence

            # 2. Duplicate Detection (only if it's a match and duplicates enabled)
            if is_match and self.duplicate_detector:
                if self.duplicate_detector.is_duplicate(img_path):
                    result['is_duplicate'] = True
            
            return result
        except Exception as e:
            result['error'] = str(e)
            return result

    def run(self):
        try:
            app_logger.info(f"Starting scan in {self.source_folder}")
            
            # Load faces
            loaded = self.face_engine.load_reference_images(self.reference_images)
            if loaded == 0:
                self.signals.error_occurred.emit("Could not load any reference faces. Scan aborted.")
                return

            # Create Database Record
            scan_id = db_manager.create_scan_record(self.person_name, str(self.source_folder), str(self.dest_folder))

            # Ensure destination exists
            self.dest_folder.mkdir(parents=True, exist_ok=True)

            # Gather files
            image_files = []
            for root, _, files in os.walk(self.source_folder):
                for file in files:
                    if Path(file).suffix.lower() in self.supported_exts:
                        image_files.append(Path(root) / file)
            
            total_files = len(image_files)
            app_logger.info(f"Found {total_files} images to scan.")

            # Process with ThreadPool
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._process_image, path): path for path in image_files}
                
                for future in as_completed(futures):
                    if self._is_cancelled:
                        app_logger.info("Scan cancelled.")
                        self.signals.scan_cancelled.emit()
                        break
                        
                    res = future.result()
                    if not res:
                        continue
                    
                    self.total_scanned += 1
                    
                    if self.show_realtime_logs:
                        self.signals.log_message.emit(f"Scanned: {res['path'].name}")
                    
                    if res['error']:
                        self.errors += 1
                        app_logger.debug(f"Error processing {res['path']}: {res['error']}")
                        if self.show_realtime_logs:
                            self.signals.log_message.emit(f"Error: {res['error']}")
                    elif res['is_match']:
                        if res['is_duplicate']:
                            self.duplicates_skipped += 1
                            app_logger.info(f"Duplicate skipped: {res['path'].name}")
                            if self.show_realtime_logs:
                                self.signals.log_message.emit(f"Skipped duplicate: {res['path'].name}")
                        else:
                            self.matches_found += 1
                            # Copy file
                            dest_path = self.dest_folder / res['path'].name
                            # Handle name collision
                            counter = 1
                            while dest_path.exists():
                                dest_path = self.dest_folder / f"{res['path'].stem}_{counter}{res['path'].suffix}"
                                counter += 1
                            
                            try:
                                shutil.copy2(res['path'], dest_path)
                                # Log to DB
                                db_manager.add_processed_file(scan_id, str(res['path']), str(dest_path), res['confidence'])
                                self.signals.match_found.emit(str(res['path']), str(dest_path), res['confidence'])
                                app_logger.info(f"Match found ({res['confidence']:.1f}%): {res['path'].name}")
                            except Exception as e:
                                self.errors += 1
                                app_logger.error(f"Failed to copy file {res['path']}: {e}")

                    # Update UI progress
                    self.signals.progress_updated.emit(
                        self.total_scanned, 
                        self.matches_found, 
                        self.duplicates_skipped, 
                        self.errors
                    )
            
            if not self._is_cancelled:
                # Update DB Stats
                db_manager.update_scan_record(scan_id, self.total_scanned, self.matches_found, self.duplicates_skipped)
                self.signals.scan_completed.emit(self.total_scanned, self.matches_found, self.duplicates_skipped)
                app_logger.info("Scan completed successfully.")

        except Exception as e:
            app_logger.error(f"Scan failed: {e}")
            self.signals.error_occurred.emit(str(e))
