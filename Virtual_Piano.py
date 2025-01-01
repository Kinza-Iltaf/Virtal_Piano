import cv2
import mediapipe as mp
import pygame
import numpy as np
import time

# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Define piano key regions and their corresponding sound files
# Updated key regions with uniform height for black and white keys
key_regions = {
    "C": (80, 120, 160, 330, "notes/C.wav"),
    "C#": (160, 120, 220, 330, "notes/C#.wav"),  # Black key, adjusted width
    "D": (220, 120, 320, 330, "notes/D.wav"),
    "D#": (320, 120, 400, 330, "notes/D#.ogg"),  # Black key, adjusted width
    "E": (400, 120, 480, 330, "notes/E.mp3"),
    "F": (480, 120, 560, 330, "notes/F.wav"),
    "F#": (560, 120, 640, 330, "notes/F#.wav"),  # Black key, adjusted width
    "G": (640, 120, 720, 330, "notes/G.wav"),
    "G#": (720, 120, 800, 330, "notes/G#.wav"),  # Black key, adjusted width
    "A": (800, 120, 880, 330, "notes/A.wav"),
    "A#": (880, 120, 960, 330, "notes/A#.wav"),  # Black key, adjusted width
    "B": (960, 120, 1040, 330, "notes/B.wav"),
    "C5": (1040, 120, 1120, 330, "notes/c5.wav"),  # Adjusted for consistency
}


# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Start Webcam Capture
cap = cv2.VideoCapture(0)


# Get screen width and height
screen_width = 1920
screen_height = 1080

# Set window size to cover the entire screen
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)


# Variable to track the currently playing note (to avoid playing the same note repeatedly)
current_note = None
# Create a list to store the trail of fingertip positions
trail_points = []

# Initialize a dictionary for sound effects
sounds = {note: pygame.mixer.Sound(sound_file) for note, (_, _, _, _, sound_file) in key_regions.items()}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for a mirror view
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (Mediapipe requires RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with Mediapipe Hands
    result = hands.process(rgb_frame)

    # Apply gradient background (tweaked to blend better)
    height, width, _ = frame.shape
    for i in range(height):
        color = (255 - int(i * 255 / height), 255, 255)  # Subtle gradient
        frame[i, :] = color

    # Set the background color
    frame[:] = (59, 59, 59)  # Background color in BGR
  
    # Draw a title text at the top of the frame
    cv2.putText(frame, "Virtual Piano", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw a border around all the keys to give the "piano keyboard" feeling
    border_x1, border_y1 = 70, 80
    border_x2, border_y2 = 1190, 350

    # Draw the background of the box first (wooden color)
    cv2.rectangle(frame, (border_x1 + 5, border_y1 + 5), (border_x2 - 5, border_y2 - 5), (0, 0, 0), -1)

    # Draw the black border around the box
    cv2.rectangle(frame, (border_x1, border_y1), (border_x2, border_y2), (0, 0, 0), 2)

    # Draw the individual piano keys
    for note, (x1, y1, x2, y2, _) in key_regions.items():
        if "#" not in note:
            # White keys (with smooth pressed effect)
            if note == current_note:
                cv2.rectangle(frame, (x1, y1 + 10), (x2, y2 + 10), (173, 216, 230), -1)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 3)
                cv2.rectangle(frame, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), (255, 255, 240), -1)
            cv2.putText(frame, note, (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        else:
            # Black keys (with stylish orange pressed effect)
            if note == current_note:
                cv2.rectangle(frame, (x1, y1 + 10), (x2, y2 + 10), (0, 100, 255), -1)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.rectangle(frame, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), (0, 0, 0), -1)
            cv2.putText(frame, note, (x1 + 5, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)


    # Add the "Playing" text box dynamically
    update_box_y = border_y2 + 300
    update_box_width = 900
    update_box_height = 80

    cv2.rectangle(frame, 
                  (border_x1 + (border_x2 - border_x1 - update_box_width) // 2, update_box_y - update_box_height // 2), 
                  (border_x1 + (border_x2 - border_x1 + update_box_width) // 2, update_box_y + update_box_height // 2), 
                  (255, 255, 255), -1)

    text = f"Playing: {current_note if current_note else 'None'}"
    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = (border_x1 + (border_x2 - border_x1 - update_box_width) // 2) + (update_box_width - text_width) // 2
    text_y = update_box_y + update_box_height // 4 + text_height // 2
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Process hand landmarks
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand skeleton with glowing neon effect
            for start_idx, end_idx in mp_hands.HAND_CONNECTIONS:

                start_landmark = hand_landmarks.landmark[start_idx]
                end_landmark = hand_landmarks.landmark[end_idx]

                # Scale and position calculation
                start_x, start_y = int(start_landmark.x * width), int(start_landmark.y * height)
                end_x, end_y = int(end_landmark.x * width), int(end_landmark.y * height)

                # Neon glowing effect with dynamic color based on hand movement
                cv2.line(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 1)  # Neon Yellow
                cv2.line(frame, (start_x + 1, start_y + 1), (end_x + 1, end_y + 1), (255, 255, 255), 2)  # Neon Purple Glow

            # Highlight the fingertips (for all 5 fingers)
            for id, lm in enumerate(hand_landmarks.landmark):
                if id in [4, 8, 12, 16, 20]:  # Fingertip landmarks for thumb, index, middle, ring, little
                    cx, cy = int(lm.x * width), int(lm.y * height)

                    # Glowing pulsing effect on fingertips (dynamic size and color)
                    cv2.circle(frame, (cx, cy), 15, (0,0,0), -1)  # Light wood primary glow inner circle
                    cv2.circle(frame, (cx, cy), 20, (19, 69, 139), 1)   # Soft wood outer glow
                    cv2.circle(frame, (cx, cy), 10, (245, 245, 245), 3)  # Bright white inner pulse

                   


            # Additional hand landmarks if you want (optional) - applying the same glowing effect
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Highlight each finger joint with glowing circles for extra impact
                if id != 8:  # Avoid fingertip glow
                    cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)  # Soft white joint highlights


                     # Check if fingertip is over a key
                    for note, (x1, y1, x2, y2, _) in key_regions.items():
                        if x1 < cx < x2 and y1 < cy < y2:
                            if current_note != note:
                                current_note = note
                                sounds[note].play()

    # Display the frame
    cv2.imshow("Virtual Piano", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
