import os
import sys
import cv2
import time
import pygame
import numpy as np
import mediapipe as mp


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

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v2 example")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)  # Set the font to bold

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

gestures = EyeGestures_v3()
cap = VideoCapture(0)

x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)

xx, yy = np.meshgrid(x, y)

calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map,context="my_context")
#gestures.setClassicalImpact(2)
gestures.setFixation(1.0)
# Initialize Pygame
# Set up colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
BLANK = (0,0,0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

# Main game loop
running = True
iterator = 0
prev_x = 0
prev_y = 0

infos = pygame.display.Info()

face_frame = cv2.imread("face_1.jpg")
 
resized_image = cv2.resize(face_frame, (infos.current_w, infos.current_h))
        # Draw the cursor at the new position
landmarks = detect_face_regions_mediapipe(face_frame)
print(f"Detected {len(landmarks)} landmarks in the image.")

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

start_time = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False


    # Generate new random position for the cursor
    calibrate = (iterator <= 25) # calibrate 25 point
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")

    if event is None:
        continue

    
    screen.fill((0, 0, 0))
    frame = np.rot90(frame)
    if calibrate:
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.scale(frame, (400, 400))

    if event is not None or calibration is not None:
        # Display frame on Pygame screen
        if calibrate:
            screen.blit(frame, (0, 0))
            my_font = pygame.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render(f'{event.fixation}', False, (0, 0, 0))
            screen.blit(text_surface, (0,0))
            if calibrate:
                if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                    iterator += 1
                    prev_x = calibration.point[0]
                    prev_y = calibration.point[1]
                # pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
                pygame.draw.circle(screen, BLUE, calibration.point, calibration.acceptance_radius)
                text_surface = bold_font.render(f"{iterator}/{25}", True, WHITE)
                text_square = text_surface.get_rect(center=calibration.point)
                screen.blit(text_surface, text_square)
            else:
                pass
            if gestures.whichAlgorithm(context="my_context") == "Ridge":
                pygame.draw.circle(screen, RED, event.point, 50)
            if gestures.whichAlgorithm(context="my_context") == "LassoCV":
                pygame.draw.circle(screen, BLUE, event.point, 50)
            my_font = pygame.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render(f'{gestures.whichAlgorithm(context="my_context")}', False, (0, 0, 0))
            screen.blit(text_surface, event.point)
            
    if not calibrate:
        frame = pygame.image.load("face_1.jpg")
        # Get original dimensions
        original_width, original_height = frame.get_size()
        
        # Calculate scaling factor to fill screen while maintaining aspect ratio
        scale_x = screen_width / original_width
        scale_y = screen_height / original_height
        scale = max(scale_x, scale_y)  # Use larger scale to fill entirely
        
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        frame = pygame.transform.scale(frame, (new_width, new_height))
        
        # Center the image (may crop edges)
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        screen.blit(frame, (x_offset, y_offset))
        
        

        if start_time:
            start_time = False
            end_time = time.time() + 20  # Run for 10 seconds
        if time.time() > end_time:
            running = False
            break
        
        if landmarks:
            # Extract and normalize landmarks (same as before)
            landmark_points = landmarks
            
            original_width = 642
            original_height = 389
            
            normalized_landmarks = []
            for point in landmarks:
                if len(point) >= 2:
                    x_norm = point[0] / original_width
                    y_norm = point[1] / original_height
                    normalized_landmarks.append((x_norm, y_norm))
            
            print(f"Number of normalized landmarks: {len(normalized_landmarks)}")
            
            # Define the correct facial landmark indices for each region
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
            
            # Define colors for each region
            region_colors = {
                'eyes': (0, 255, 0),      # Green
                'nose': (255, 165, 0),    # Orange
                'mouth': (255, 0, 255),   # Magenta
                'forehead': (0, 0, 255),  # Blue
                'chin': (255, 255, 0)     # Yellow
            }
            
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
                    
                    # Draw rectangle
                    rect_width = max_x - min_x
                    rect_height = max_y - min_y
                    color = region_colors.get(region_name, (255, 255, 255))
                    
                    if rect_width > 0 and rect_height > 0:
                        # Add some padding to make the rectangles more visible
                        padding = 5
                        pygame.draw.rect(screen, color, 
                                    (min_x - padding, min_y - padding, 
                                        rect_width + 2*padding, rect_height + 2*padding), 3)
                        
                        # Draw region name label
                        font = pygame.font.Font(None, 36)
                        text = font.render(region_name, True, color)
                        screen.blit(text, (min_x, max(0, min_y - 25)))
                        
                        print(f"Drew rectangle for {region_name}")

            # Draw the gaze point
            if gestures.whichAlgorithm(context="my_context") == "Ridge":
                pygame.draw.circle(screen, (255, 0, 0), event.point, 7)
                
    pygame.display.flip()
    # Cap the frame rate
    clock.tick(10)

print("Exiting...")
# Release the video capture object
# Close the Pygame window
pygame.display.quit()
# Save the calibration data
# Quit Pygame
pygame.quit()
sys.exit(0)
