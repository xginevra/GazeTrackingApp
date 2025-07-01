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
    original_width = 642
    original_height = 389
    
    normalized_landmarks = []
    for point in landmarks:
        if len(point) >= 2:
            x_norm = point[0] / original_width
            y_norm = point[1] / original_height
            normalized_landmarks.append((x_norm, y_norm))
            
    region_indices = {
        'eyes': [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7, 463, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382, 362],
        'nose': [193, 168, 417, 122, 351, 196, 419, 3, 248, 236, 456, 198, 420, 131, 360, 49, 279, 48, 278, 219, 439, 59, 289, 218, 438, 237, 457, 44, 19, 274],
        'mouth': [0, 267, 269, 270, 409, 306, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61, 185, 40, 39, 37],
        'forehead': [10, 151, 9, 107, 55, 65, 52, 336, 296, 334, 293],
        'chin': [152, 175, 377, 172, 136, 150, 149, 176, 148, 400, 378, 379, 365, 397, 288]
    }
            
    # Create regions based on available landmarks
    regions = {}
    max_landmarks = len(normalized_landmarks)
    
    for region_name, indices in region_indices.items():
        # Only use indices that exist in our landmark data
        valid_indices = [i for i in indices if i < max_landmarks]
        if valid_indices:
            regions[region_name] = [normalized_landmarks[i] for i in valid_indices]
            print(f"Region {region_name}: using {len(valid_indices)} out of {len(indices)} landmarks")
        else:
            print(f"Region {region_name}: no valid landmarks found")
    
    print(f"Number of regions: {len(regions)}")
    
    region_rect= {}
    
    for region_name, points in regions.items():
        print(f"Region: {region_name}, Points: {len(points) if points else 0}")
        
        if points and len(points) > 0:
            # Convert normalized coordinates to current screen coordinates
            screen_points = [(int(x * screen_width), int(y * screen_height)) for x, y in points]
            
            # Get bounding rectangle from all points in the region
            min_x = min(point[0] for point in screen_points)
            max_x = max(point[0] for point in screen_points)
            min_y = min(point[1] for point in screen_points)
            max_y = max(point[1] for point in screen_points)
            
            print(f"Bounding box for {region_name}: ({min_x}, {min_y}) to ({max_x}, {max_y})")
            trehshold = 25  # 10 pixels threshold
            # Draw rectangle
            region_rect[region_name] = [(min_x-trehshold, min_y-trehshold), (max_x+trehshold, max_y+trehshold)]
            print(f"Region {region_name} rectangle: {region_rect[region_name]}")
    return region_rect


def get_enhanced_face_regions(landmarks):
    regions = {}
    
    if len(landmarks) >= 468:  # MediaPipe landmarks
        left_eye_indices = [463, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382, 362]
        right_eye_indices = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        regions['eyes'] = [landmarks[i] for i in left_eye_indices + right_eye_indices if i < len(landmarks)]
        
        nose_indices = [193, 168, 417, 122, 351, 196, 419, 3, 248, 236, 456, 198, 420, 131, 360, 49, 279, 48, 278, 219, 439, 59, 289, 218, 438, 237, 457, 44, 19, 274]
        regions['nose'] = [landmarks[i] for i in nose_indices if i < len(landmarks)]
        
        mouth_indices = [0, 267, 269, 270, 409, 306, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61, 185, 40, 39, 37]
        regions['mouth'] = [landmarks[i] for i in mouth_indices if i < len(landmarks)]
        
        forehead_indices = [10, 151, 9, 107, 55, 65, 52, 336, 296, 334, 293]
        regions['forehead'] = [landmarks[i] for i in forehead_indices if i < len(landmarks)]
        
        if regions['forehead']:
            expanded_forehead = []
            for x, y in regions['forehead']:
                expanded_forehead.append((x, max(0, y - 0.05)))  # Adjust for normalized coords
                expanded_forehead.append((x, y))
            regions['forehead'] = expanded_forehead
        
        chin_indices = [152, 175, 377, 172, 136, 150, 149, 176, 148, 400, 378, 379, 365, 397, 288]
        chin_points = [landmarks[i] for i in chin_indices if i < len(landmarks)]
        
        expanded_chin = []
        for x, y in chin_points:
            expanded_chin.append((x, y))
            expanded_chin.append((x, y + 0.05))  # Adjust for normalized coords
        regions['chin'] = expanded_chin
        
    elif len(landmarks) >= 68:
        regions['eyes'] = landmarks[36:48]
        regions['nose'] = landmarks[27:36]
        regions['mouth'] = landmarks[48:68]
        
        brow_points = landmarks[17:27]
        forehead_points = []
        for x, y in brow_points:
            forehead_points.append((x, max(0, y - 0.05)))
            forehead_points.append((x, max(0, y - 0.025)))
        regions['forehead'] = forehead_points
        
        chin_points = landmarks[6:11]
        expanded_chin = []
        for x, y in chin_points:
            expanded_chin.append((x, y + 0.025))
            expanded_chin.append((x, y + 0.05))
        regions['chin'] = expanded_chin
    
    return regions