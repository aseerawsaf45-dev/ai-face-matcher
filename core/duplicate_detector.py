import imagehash
from PIL import Image
from core.logger import app_logger

class DuplicateDetector:
    def __init__(self, sensitivity=5):
        """
        sensitivity: Hamming distance threshold.
        0 means exact match required.
        Higher value means more tolerant to differences (near-duplicates).
        """
        self.sensitivity = sensitivity
        self.seen_hashes = []

    def get_hash(self, image_path):
        try:
            with Image.open(image_path) as img:
                return imagehash.phash(img)
        except Exception as e:
            app_logger.warning(f"Could not hash image {image_path}: {e}")
            return None

    def is_duplicate(self, image_path):
        """
        Check if the image is a duplicate based on previously seen hashes.
        If not duplicate, adds to seen_hashes.
        """
        img_hash = self.get_hash(image_path)
        if img_hash is None:
            return False # Assume not duplicate if we can't hash it

        for seen in self.seen_hashes:
            if img_hash - seen <= self.sensitivity:
                return True
                
        self.seen_hashes.append(img_hash)
        return False

    def clear(self):
        self.seen_hashes.clear()
