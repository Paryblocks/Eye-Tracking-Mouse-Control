import cv2 as cv
from eye_tracking import EyeTracker
from mouse_control import MouseController
from virtual_keyboard import VirtualKeyboard

# 0 means the default camera, changing it to 1 or so on will select any additional cameras
cap = cv.VideoCapture(0)
tracker = EyeTracker()
keyboard = VirtualKeyboard()
mouse = MouseController(keyboard)

# Points representing the eyes according to Google Face Mesh
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

if not cap.isOpened():
    print("Cannot open the camera.")
    exit()

while True:
    # cap.read() returns a boolean that the frame is read correctly and the frame itself
    confirmation, frame = cap.read()

    # Checking if the frame was read correctly to proceed, otherwise exit program
    if not confirmation:
        break

    # Processes frame using the eye tracker class
    face_points = tracker.process_frame(frame)

    if face_points is not None and len(face_points) >= 478:
        # Gets the EAR for both eyes
        ear_left = tracker.get_ear(face_points, LEFT_EYE)
        ear_right = tracker.get_ear(face_points, RIGHT_EYE)

        gaze_x = None
        gaze_y = None

        # Gets iris value for both eyes
        gaze_left = tracker.get_gaze_position(face_points, LEFT_EYE, list(range(473, 478)))
        gaze_right = tracker.get_gaze_position(face_points, RIGHT_EYE, list(range(468, 473)))

        # Gets average gaze value
        if gaze_left is not None and gaze_right is not None:
            gaze_x = (gaze_left[0] + gaze_right[0]) / 2
            gaze_y = (gaze_left[1] + gaze_right[1]) / 2

        # Processes movements and click
        mouse.process_commands(ear_left, ear_right, gaze_x, gaze_y)
        keyboard.update()

        # Highlights eyes for testing
        for idx in LEFT_EYE + RIGHT_EYE:
            if idx < len(face_points):
                x, y = face_points[idx]
                cv.circle(frame, (x, y), 2, (0, 255, 0), -1)

    # Mirrors the camera for easier visualization (left and right eyes)
    frame = cv.flip(frame, 1)

    # Displaying the frames for testing
    cv.imshow("Camera", frame)

    # Ends capture when pressing *
    if cv.waitKey(1) == ord('*'):
        break

# Closing everything at the end
cap.release()
keyboard.close()
cv.destroyAllWindows()