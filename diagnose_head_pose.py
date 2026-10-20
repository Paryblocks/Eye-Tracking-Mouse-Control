import cv2 as cv
import numpy as np
from eye_tracking import EyeTracker

# Modelo 3D aproximado do rosto, em unidades arbitrárias.
# A ordem precisa corresponder à dos landmarks 2D abaixo.
MODEL_POINTS = np.array([
    (0.0,   0.0,    0.0),    # Nariz: 1
    (0.0, -330.0, -65.0),    # Queixo: 152
    (-225.0, 170.0, -135.0), # Canto do olho: 33
    (225.0, 170.0, -135.0),  # Canto do olho: 263
    (-150.0, -150.0, -125.0),# Boca: 61
    (150.0, -150.0, -125.0), # Boca: 291
], dtype=np.float64)

LANDMARK_IDS = [1, 152, 33, 263, 61, 291]


def estimate_head_pose(points, frame_shape):
    if points is None or len(points) <= max(LANDMARK_IDS):
        return None

    image_points = np.array(
        [points[i] for i in LANDMARK_IDS],
        dtype=np.float64
    )

    height, width = frame_shape[:2]

    # Aproximação inicial da câmera; não é uma calibração real.
    focal_length = width
    camera_matrix = np.array([
        [focal_length, 0, width / 2],
        [0, focal_length, height / 2],
        [0, 0, 1]
    ], dtype=np.float64)

    distortion = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vector, translation_vector = cv.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        distortion,
        flags=cv.SOLVEPNP_ITERATIVE
    )

    if not success:
        return None

    rotation_matrix, _ = cv.Rodrigues(rotation_vector)
    angles, *_ = cv.RQDecomp3x3(rotation_matrix)

    # Ângulos aproximados em graus.
    # Os sinais e eixos devem ser conferidos na webcam real.
    pitch, yaw, roll = angles
    return float(yaw), float(pitch), float(roll)


def main():
    tracker = EyeTracker()
    camera = cv.VideoCapture(0)

    try:
        if not camera.isOpened():
            raise RuntimeError("Não foi possível abrir a webcam.")

        while True:
            ok, frame = camera.read()
            if not ok:
                break

            points = tracker.process_frame(frame)
            pose = estimate_head_pose(points, frame.shape)

            if pose is not None:
                yaw, pitch, roll = pose
                cv.putText(
                    frame,
                    f"Yaw: {yaw:7.2f} deg",
                    (20, 35),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2
                )
                cv.putText(
                    frame,
                    f"Pitch: {pitch:7.2f} deg",
                    (20, 65),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2
                )
                cv.putText(
                    frame,
                    f"Roll: {roll:7.2f} deg",
                    (20, 95),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2
                )

            cv.imshow("Diagnostico da cabeca", frame)

            if cv.waitKey(1) & 0xFF == 27:
                break

    finally:
        camera.release()
        cv.destroyAllWindows()
        tracker.detector.close()


if __name__ == "__main__":
    main()
