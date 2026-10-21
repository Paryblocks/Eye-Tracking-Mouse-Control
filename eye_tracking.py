import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

# Creating a class for better modularization
class EyeTracker:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def process_frame(self, frame):
        # Convert the BGR frame from OpenCV into a RGB for MediaPipe
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect(mp_image)

        height, width, _ = frame.shape
        eye_data = None

        if result.face_landmarks:
            face_landmarks = result.face_landmarks[0]
            # Multiply the mesh value for the decimal value of height/width to get the pixel value
            points = np.array([(int(pt.x * width), int(pt.y * height)) for pt in face_landmarks])
            eye_data = points
        return eye_data

    # EAR = Eye Aspect Ratio, Distance between the eyelids divided by eye width
    # Used to verify if eyes are closed or open
    def get_ear(self, points, eye_values):
        try:
            p1 = points[eye_values[0]]  # Eye corner
            p2 = points[eye_values[1]]  # Upper lid 1
            p3 = points[eye_values[2]]  # Upper lid 2
            p4 = points[eye_values[3]]  # Other corner
            p5 = points[eye_values[4]]  # Bottom lid 1
            p6 = points[eye_values[5]]  # Bottom lid 2

            # Calculating the L2 distance
            vertical1 = np.linalg.norm(p2 - p5)
            vertical2 = np.linalg.norm(p3 - p6)
            horizontal = np.linalg.norm(p1 - p4)

            # EAR formula
            ear = (vertical1 + vertical2) / (2.0 * horizontal)
            return ear
        except:
            return 0.0

    # Calculates the center of the iris for controlling the cursor
    def get_gaze_position(self, points, eye_values, iris_indices):
        # Center of the iris
        iris_center = np.mean(points[iris_indices], axis=0)

        # Eye corners
        p1 = points[eye_values[0]]
        p4 = points[eye_values[3]]

        # Upper and lower eyelids
        upper = np.mean([
            points[eye_values[1]],
            points[eye_values[2]]
        ], axis=0)

        lower = np.mean([
            points[eye_values[4]],
            points[eye_values[5]]
        ], axis=0)

        # Horizontal position relative to eye corners
        left_corner_x = min(p1[0], p4[0])
        eye_width = abs(p4[0] - p1[0])

        if eye_width < 1:
            return None

        x_ratio = (iris_center[0] - left_corner_x) / eye_width

        # Vertical position relative to eyelids
        eye_height = lower[1] - upper[1]

        if abs(eye_height) < 1:
            return None

        y_ratio = (iris_center[1] - upper[1]) / eye_height

        return x_ratio, y_ratio