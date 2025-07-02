import os
import sys
import cv2
import time
import pygame
import numpy as np
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

from landmarks_function import detect_face_regions_mediapipe, get_face_regions_reactangels_plus_10_pixels, get_enhanced_face_regions
from database import create_database, insert_data_sql

def main():
    pygame.init()
    pygame.font.init()
    
    # Get the display dimensions
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    wait_time = 20  # seconds to wait before closing the window
    eyes_ticks = 0
    nose_ticks = 0
    mouth_ticks = 0
    forehead_ticks = 0
    chin_ticks = 0
    total_ticks = 0
    start_time = True
    font_size = 48
    clock = pygame.time.Clock()
    running = True
    iterator = 0
    prev_x = 0
    prev_y = 0
    # Set up colors
    RED = (255, 0, 100)
    BLUE = (100, 0, 255)
    WHITE = (255, 255, 255)
    
    # Set up the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("EyeGestures v2 example")
    bold_font = pygame.font.Font(None, font_size)
    bold_font.set_bold(True)  # Set the font to bold

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(f'{dir_path}/..')

    gestures = EyeGestures_v3(calibration_radius=200)
    cap = VideoCapture(0)

    x = np.arange(0.15, 0.9, 0.15)
    y = np.arange(0.15, 0.9, 0.15)

    xx, yy = np.meshgrid(x, y)

    calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
    n_points = min(len(calibration_map),25)
    np.random.shuffle(calibration_map)
    gestures.uploadCalibrationMap(calibration_map,context="my_context")
    gestures.setFixation(0.8)
    
    face_frame = cv2.imread("face_1.jpg")
    landmarks = detect_face_regions_mediapipe(face_frame)
    print(f"Detected {len(landmarks)} landmarks in the image.")
    rectangles = get_face_regions_reactangels_plus_10_pixels(landmarks, screen_width, screen_height)
    print(f"Detected {len(rectangles)} face regions.")
    for region_name, rect in rectangles.items():
        print(f"Region {region_name} rectangle: {rect}")

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    running = False


        # Generate new random position for the cursor
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)

        calibrate = (iterator <= n_points) 

        event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")

        if event is None:
            continue

        
        screen.fill((0, 0, 0))
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
                    pygame.draw.circle(screen, RED, event.point, 20)
                if gestures.whichAlgorithm(context="my_context") == "LassoCV":
                    pygame.draw.circle(screen, BLUE, event.point, 50)
                my_font = pygame.font.SysFont('Comic Sans MS', 30)
                """ text_surface = my_font.render(f'{gestures.whichAlgorithm(context="my_context")}', False, (0, 0, 0))
                screen.blit(text_surface, event.point) """
                
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
                end_time = time.time() + wait_time  # Run for x seconds, adjust as needed
            if time.time() > end_time:
                running = False
                
                # for debugging purposes, draw rectangles around the regions
            """  for region_name in rectangles.keys():   
                    rect_width = rectangles[region_name][1][0] - rectangles[region_name][0][0]
                    rect_height = rectangles[region_name][1][1] - rectangles[region_name][0][1]
                    color = (255, 255, 255)
                    
                    if rect_width > 0 and rect_height > 0:
                        # Add some padding to make the rectangles more visible
                        padding = 5
                        pygame.draw.rect(screen, color, 
                                    (rectangles[region_name][0][0] - padding, rectangles[region_name][0][1] - padding, 
                                        rect_width + 2*padding, rect_height + 2*padding), 3)
                        
                        # Draw region name label
                        font = pygame.font.Font(None, 36)
                        text = font.render(region_name, True, color)
                        screen.blit(text, (rectangles[region_name][0][0], max(0, rectangles[region_name][0][1] - 25)))

                        print(f"Drew rectangle for {region_name}") """
            total_ticks += 1
            # if event cordinate inside eyes recrtangel from rectangles[region_name] it should count one tick
            if event.point is not None:
                if rectangles['eyes'][0][0] <= event.point[0] <= rectangles['eyes'][1][0] and \
                   rectangles['eyes'][0][1] <= event.point[1] <= rectangles['eyes'][1][1]:
                    eyes_ticks += 1
                if rectangles['nose'][0][0] <= event.point[0] <= rectangles['nose'][1][0] and \
                   rectangles['nose'][0][1] <= event.point[1] <= rectangles['nose'][1][1]:
                    nose_ticks += 1
                if rectangles['mouth'][0][0] <= event.point[0] <= rectangles['mouth'][1][0] and \
                   rectangles['mouth'][0][1] <= event.point[1] <= rectangles['mouth'][1][1]:
                    mouth_ticks += 1
                if rectangles['forehead'][0][0] <= event.point[0] <= rectangles['forehead'][1][0] and \
                   rectangles['forehead'][0][1] <= event.point[1] <= rectangles['forehead'][1][1]:
                    forehead_ticks += 1
                if rectangles['chin'][0][0] <= event.point[0] <= rectangles['chin'][1][0] and \
                   rectangles['chin'][0][1] <= event.point[1] <= rectangles['chin'][1][1]:
                    chin_ticks += 1
                    
            if gestures.whichAlgorithm(context="my_context") == "Ridge":
                pygame.draw.circle(screen, (255, 0, 0), event.point, 7)    
        pygame.display.flip()
        # Cap the frame rate
        clock.tick(60)
    # make screen black
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # insert every time with region text to pygame screen
    time_calculator = wait_time/total_ticks
    time_eyes = eyes_ticks * time_calculator
    time_nose = nose_ticks * time_calculator
    time_mouth = mouth_ticks * time_calculator
    time_forehead = forehead_ticks * time_calculator
    time_chin = chin_ticks * time_calculator
    
    time_text = bold_font.render("Time spent on each region:", True, WHITE)
    screen.blit(time_text, (50, 50))
    screen.blit(bold_font.render(f"Eyes: {time_eyes:.2f} seconds", True, WHITE), (50, 100))
    screen.blit(bold_font.render(f"Nose: {time_nose:.2f} seconds", True, WHITE), (50, 150))
    screen.blit(bold_font.render(f"Mouth: {time_mouth:.2f} seconds", True, WHITE), (50, 200))
    screen.blit(bold_font.render(f"Forehead: {time_forehead:.2f} seconds", True, WHITE), (50, 250))
    screen.blit(bold_font.render(f"Chin: {time_chin:.2f} seconds", True, WHITE), (50, 300))
    pygame.display.flip()
    pygame.time.delay(10000)  # Show the results for some seconds
    
    create_database()
    insert_data_sql(forehead=time_forehead, eyes=time_eyes, nose=time_nose, mouth=time_mouth, chin=time_chin)
    print("Exiting...")
    # Release the video capture object
    # Close the Pygame window
    pygame.display.quit()
    # Save the calibration data
    # Quit Pygame
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()  