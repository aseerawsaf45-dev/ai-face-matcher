import csv
import json
from pathlib import Path
from core.logger import app_logger

class ExportService:
    @staticmethod
    def export_csv(filepath, stats, matches_list):
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Face Matcher AI - Scan Report"])
                writer.writerow([])
                writer.writerow(["Total Scanned", stats.get('total', 0)])
                writer.writerow(["Matches Found", stats.get('matches', 0)])
                writer.writerow(["Duplicates Skipped", stats.get('duplicates', 0)])
                writer.writerow([])
                writer.writerow(["Original Path", "Copied Path", "Confidence (%)"])
                for m in matches_list:
                    writer.writerow([m['original'], m['copied'], f"{m['confidence']:.2f}"])
            app_logger.info(f"Exported CSV report to {filepath}")
            return True
        except Exception as e:
            app_logger.error(f"Failed to export CSV: {e}")
            return False

    @staticmethod
    def export_json(filepath, stats, matches_list):
        try:
            data = {
                "summary": stats,
                "matches": matches_list
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            app_logger.info(f"Exported JSON report to {filepath}")
            return True
        except Exception as e:
            app_logger.error(f"Failed to export JSON: {e}")
            return False
