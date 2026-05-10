import face_recognition
import cv2
import numpy as np
import threading
from core.logger import app_logger

class FaceEngine:
    def __init__(self, tolerance=0.6):
        """
        tolerance: Distance threshold. Lower is stricter. Default 0.6.
        """
        self.tolerance = tolerance
        self.target_encodings = []
        self._lock = threading.Lock()
        
        from core.settings_manager import settings_manager
        
        # Accuracy settings
        accuracy = settings_manager.get("accuracy_priority", "Balanced")
        if accuracy == "Maximum accuracy":
            self.upsample = 2
        elif accuracy == "Fast scanning":
            self.upsample = 0
        else: # Balanced
            self.upsample = 1
            
        # Hardware settings
        hardware = settings_manager.get("hardware_acceleration", "Auto")
        self.model = "hog"
        if hardware == "Auto" and accuracy == "Maximum accuracy":
            # Attempt to use CNN only if Auto and Maximum Accuracy (due to performance cost)
            try:
                import dlib
                if dlib.DLIB_USE_CUDA:
                    self.model = "cnn"
            except:
                pass

    def load_reference_images(self, image_paths):
        """
        Load target reference images and compute encodings.
        Returns the number of successful encodings found.
        """
        self.target_encodings = []
        for path in image_paths:
            try:
                img = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    self.target_encodings.append(encodings[0])
                    app_logger.info(f"Loaded reference face from: {path}")
                else:
                    app_logger.warning(f"No face found in reference image: {path}")
            except Exception as e:
                app_logger.error(f"Error loading reference image {path}: {e}")
        
        return len(self.target_encodings)

    def check_match(self, image_path):
        """
        Checks if the image contains any face that matches the target encodings.
        Returns (is_match, best_confidence)
        """
        if not self.target_encodings:
            return False, 0.0

        try:
            # We use OpenCV to read because it's fast, then convert to RGB
            img = cv2.imread(str(image_path))
            if img is None:
                return False, 0.0
                
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Find all face locations and encodings in the current image
            # We use a lock here because the underlying dlib detector is not always thread-safe
            with self._lock:
                face_locations = face_recognition.face_locations(rgb_img, number_of_times_to_upsample=self.upsample, model=self.model)
                if not face_locations:
                    return False, 0.0
                    
                face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            
            best_match_distance = 1.0 # Initialize with worst case (1.0 distance)
            
            for face_encoding in face_encodings:
                # Compare current face with all reference encodings
                matches = face_recognition.compare_faces(self.target_encodings, face_encoding, tolerance=self.tolerance)
                face_distances = face_recognition.face_distance(self.target_encodings, face_encoding)
                
                if True in matches:
                    # Find the best distance for this match
                    min_distance = np.min(face_distances)
                    if min_distance < best_match_distance:
                        best_match_distance = min_distance
            
            if best_match_distance < 1.0:
                # Convert distance to a confidence percentage
                # Distance of 0.0 is 100%, distance of self.tolerance is threshold
                confidence = max(0.0, 1.0 - best_match_distance) * 100
                return True, confidence
                
            return False, 0.0

        except Exception as e:
            app_logger.debug(f"Error processing {image_path}: {e}")
            return False, 0.0
