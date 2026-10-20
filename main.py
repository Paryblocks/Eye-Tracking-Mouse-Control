import cv2 as cv
from eye_tracking import EyeTracker
from mouse_control import MouseController

# 0 means the default camera, changing it to 1 or so on will select any aditional cameras
cap = cv.VideoCapture(0)
tracker = EyeTracker()
mouse = MouseController()

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

    height, width, _ = frame.shape

    # Processes frame using the eye tracker class
    face_points = tracker.process_frame(frame)

    features = tracker.get_gaze_features(face_points)

    if features is not None:
        print(
            f"Olho 1: x={features[0]:.3f}, y={features[1]:.3f} | "
            f"Olho 2: x={features[2]:.3f}, y={features[3]:.3f}"
        )

    if face_points is not None and len(face_points) > 468:
        # Gets the EAR for both eyes
        ear_left = tracker.get_ear(face_points, LEFT_EYE)
        ear_right = tracker.get_ear(face_points, RIGHT_EYE)

        # Processes movements and click
        #mouse.process_commands(ear_left, ear_right, face_points)

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
cv.destroyAllWindows()