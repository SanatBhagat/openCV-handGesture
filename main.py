import cv2
import mediapipe as mp
import math
import time
import random
from collections import deque

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=1, 
    min_detection_confidence=0.7, min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
tip_ids = [4, 8, 12, 16, 20]

# --- NEW: Animation Variables ---
# Deque stores the last 20 positions of the index finger for a flowing trail
index_trail = deque(maxlen=20) 
color_palette = [(0, 255, 255), (255, 0, 255), (0, 255, 0)] # Yellow, Purple, Green
cv2.namedWindow('Dynamic Flowing Effects', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Dynamic Flowing Effects', 1280, 720)

while cap.isOpened():
    success, frame = cap.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
            
            if len(lm_list) != 0:
                fingers = []
                # Check Thumb
                if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                
                # Check 4 Fingers
                for id in range(1, 5):
                    if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                        
                # ----------------------------------------------------
                # ADVANCED FLOWING EFFECTS LOGIC
                # ----------------------------------------------------
                
                # Extract key coordinates for easy use
                thumb_x, thumb_y = lm_list[4][1], lm_list[4][2]
                index_x, index_y = lm_list[8][1], lm_list[8][2]
                pinky_x, pinky_y = lm_list[20][1], lm_list[20][2]

                # 1. FLOWING RIBBON TRAIL (Only Index Finger Up)
                if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    # Add current position to memory
                    index_trail.append((index_x, index_y))
                    
                    # Draw the trail by connecting the stored points
                    for i in range(1, len(index_trail)):
                        # Make the tail thinner at the end and thicker near the finger
                        thickness = int(math.sqrt(i) * 2)
                        cv2.line(frame, index_trail[i-1], index_trail[i], (0, 255, 255), thickness)
                        
                    cv2.putText(frame, 'FLOWING RIBBON', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
                else:
                    # Clear the trail memory if the gesture stops
                    index_trail.clear()

                # 2. DYNAMIC LIGHTNING ARCS (Rock On / Spider-Man Pose: Index + Pinky)
                if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0 and fingers[3] == 0:
                    cv2.putText(frame, 'LIGHTNING ARCS', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
                    
                    # Draw 3 chaotic, jittery lines between the index and pinky
                    for _ in range(3):
                        # Add random pixel offsets to create a jagged "lightning" effect
                        jitter_x1 = index_x + random.randint(-20, 20)
                        jitter_y1 = index_y + random.randint(-20, 20)
                        jitter_x2 = pinky_x + random.randint(-20, 20)
                        jitter_y2 = pinky_y + random.randint(-20, 20)
                        
                        cv2.line(frame, (index_x, index_y), (jitter_x1, jitter_y1), (255, 255, 0), 2)
                        cv2.line(frame, (jitter_x1, jitter_y1), (jitter_x2, jitter_y2), (255, 255, 255), 2)
                        cv2.line(frame, (jitter_x2, jitter_y2), (pinky_x, pinky_y), (255, 255, 0), 2)

                # 3. PULSING ENERGY ORB (Pinch Gesture: Thumb & Index close together)
                # Calculate the physical distance between thumb and index tips
                pinch_distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
                
                if pinch_distance < 40 and fingers[2] == 0 and fingers[3] == 0:
                    # Find the midpoint between the two fingers
                    mid_x, mid_y = (index_x + thumb_x) // 2, (index_y + thumb_y) // 2
                    
                    # Use math.sin and time to create a radius that grows and shrinks smoothly
                    pulse = math.sin(time.time() * 8) # Speed of pulse
                    radius = int(25 + (10 * pulse))   # Base size 25, fluctuates by +/- 10
                    
                    # Draw a glowing orb (a filled circle inside a larger hollow circle)
                    cv2.circle(frame, (mid_x, mid_y), radius, (0, 150, 255), cv2.FILLED)
                    cv2.circle(frame, (mid_x, mid_y), radius + 10, (0, 100, 255), 2)
                    
                    cv2.putText(frame, 'PULSING ORB', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 150, 255), 3)

    cv2.imshow('Dynamic Flowing Effects', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()