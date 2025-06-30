import mediapipe as mp
import cv2


mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def detect_face_regions_mediapipe(image):
    """Fallback face detection using MediaPipe"""
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            # Convert normalized coordinates to pixel coordinates
            coords = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                coords.append((x, y))
            print(f"Detected {len(coords)} landmarks using MediaPipe")
            return coords
    return None
        



def get_face_regions_reactangels_plus_10_pixels(landmarks, screen_width, screen_height):
    pass

def get_enhanced_face_regions(landmarks):
    pass
