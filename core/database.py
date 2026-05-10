import sqlite3
import os
from pathlib import Path
from core.logger import app_logger

class DatabaseManager:
    def __init__(self):
        self.db_dir = Path("database")
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "app.db"
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Scan History
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scan_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        person_name TEXT,
                        source_folder TEXT,
                        dest_folder TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_scanned INTEGER DEFAULT 0,
                        matches_found INTEGER DEFAULT 0,
                        duplicates_skipped INTEGER DEFAULT 0
                    )
                ''')
                # Processed Files (to avoid re-processing if needed later, or just for logs)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processed_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_id INTEGER,
                        original_path TEXT,
                        copied_path TEXT,
                        confidence REAL,
                        FOREIGN KEY(scan_id) REFERENCES scan_history(id)
                    )
                ''')
                conn.commit()
        except Exception as e:
            app_logger.error(f"Database initialization failed: {e}")

    def create_scan_record(self, person_name, source_folder, dest_folder):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scan_history (person_name, source_folder, dest_folder)
                    VALUES (?, ?, ?)
                ''', (person_name, source_folder, dest_folder))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            app_logger.error(f"Failed to create scan record: {e}")
            return -1

    def update_scan_record(self, scan_id, total_scanned, matches_found, duplicates_skipped):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE scan_history 
                    SET total_scanned = ?, matches_found = ?, duplicates_skipped = ?
                    WHERE id = ?
                ''', (total_scanned, matches_found, duplicates_skipped, scan_id))
                conn.commit()
        except Exception as e:
            app_logger.error(f"Failed to update scan record: {e}")

    def add_processed_file(self, scan_id, original_path, copied_path, confidence):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO processed_files (scan_id, original_path, copied_path, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (scan_id, str(original_path), str(copied_path), confidence))
                conn.commit()
        except Exception as e:
            app_logger.error(f"Failed to add processed file: {e}")

db_manager = DatabaseManager()
