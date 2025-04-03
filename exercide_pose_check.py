import cv2
import mediapipe as mp
import numpy as np
import time
from collections import defaultdict

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
        np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


class Exercise:
    def __init__(self, name, angle_points, up_threshold, down_threshold, direction='up_down'):
        self.name = name
        self.angle_points = angle_points
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.direction = direction
        self.counter = 0
        self.stage = None
        self.just_completed_rep = False
        self.rep_completed_time = None  # ← NEW

    def update(self, landmarks):
        try:
            a = [landmarks[self.angle_points[0]].x,
                 landmarks[self.angle_points[0]].y]
            b = [landmarks[self.angle_points[1]].x,
                 landmarks[self.angle_points[1]].y]
            c = [landmarks[self.angle_points[2]].x,
                 landmarks[self.angle_points[2]].y]

            angle = calculate_angle(a, b, c)
            self.just_completed_rep = False  # Reset at start

            if self.direction == 'up_down':
                if angle > self.up_threshold:
                    self.stage = "down"
                if angle < self.down_threshold and self.stage == "down":
                    self.stage = "up"
                    self.counter += 1
                    self.just_completed_rep = True
                    self.rep_completed_time = time.time()  # ← ✅ ADD THIS

                    print(f"{self.name} Reps: {self.counter}")
            elif self.direction == 'down_up':
                if angle < self.up_threshold:
                    self.stage = "up"
                if angle > self.down_threshold and self.stage == "up":
                    self.stage = "down"
                    self.counter += 1
                    self.just_completed_rep = True
                    self.rep_completed_time = time.time()  # ← ✅ ADD THIS
                    print(f"{self.name} Reps: {self.counter}")

            return angle
        except IndexError:
            return None


def detect_exercise(angles, prev_exercise, angle_changes, angle_change_threshold=10):
    detected_exercise = None
    exercise_priority = ["Bicep Curl", "Squat", "Push-Up"]
    for exercise in exercise_priority:
        change_key = exercise.lower().replace(" ", "_")
        if abs(angle_changes.get(change_key, 0)) > angle_change_threshold:
            detected_exercise = exercise
            break
    return detected_exercise


def main():
    exercise_config = {
        "Bicep Curl": {
            "angle_points": (
                mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                mp_pose.PoseLandmark.LEFT_ELBOW.value,
                mp_pose.PoseLandmark.LEFT_WRIST.value,
            ),
            "up_threshold": 160,
            "down_threshold": 30,
            "direction": "up_down",
        },
        "Squat": {
            "angle_points": (
                mp_pose.PoseLandmark.LEFT_HIP.value,
                mp_pose.PoseLandmark.LEFT_KNEE.value,
                mp_pose.PoseLandmark.LEFT_ANKLE.value,
            ),
            "up_threshold": 160,
            "down_threshold": 70,
            "direction": "up_down",
        },
        "Push-Up": {
            "angle_points": (
                mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                mp_pose.PoseLandmark.LEFT_ELBOW.value,
                mp_pose.PoseLandmark.LEFT_WRIST.value,
            ),
            "up_threshold": 160,
            "down_threshold": 90,
            "direction": "down_up",
        },
    }

    exercises = {name: Exercise(name, **config)
                 for name, config in exercise_config.items()}

    prev_angles = defaultdict(float)
    current_exercise = None

    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                angles = {}
                for name, exercise in exercises.items():
                    try:
                        a = [landmarks[exercise.angle_points[0]].x,
                             landmarks[exercise.angle_points[0]].y]
                        b = [landmarks[exercise.angle_points[1]].x,
                             landmarks[exercise.angle_points[1]].y]
                        c = [landmarks[exercise.angle_points[2]].x,
                             landmarks[exercise.angle_points[2]].y]
                        angles_key = name.lower().replace(" ", "_")
                        angles[angles_key] = calculate_angle(a, b, c)
                    except IndexError:
                        angles[angles_key] = 0

                angle_changes = {k: angles[k] - prev_angles[k] for k in angles}
                prev_angles = angles.copy()

                detected_exercise = detect_exercise(
                    angles, current_exercise, angle_changes)

                if detected_exercise:
                    current_exercise = detected_exercise

                if current_exercise:
                    exercise = exercises[current_exercise]
                    angle = exercise.update(landmarks)

                    if angle is not None:
                        a = [landmarks[exercise.angle_points[0]].x,
                             landmarks[exercise.angle_points[0]].y]
                        b = [landmarks[exercise.angle_points[1]].x,
                             landmarks[exercise.angle_points[1]].y]
                        c = [landmarks[exercise.angle_points[2]].x,
                             landmarks[exercise.angle_points[2]].y]

                        image_height, image_width, _ = image.shape
                        a_pixel = tuple(np.multiply(
                            a, [image_width, image_height]).astype(int))
                        b_pixel = tuple(np.multiply(
                            b, [image_width, image_height]).astype(int))
                        c_pixel = tuple(np.multiply(
                            c, [image_width, image_height]).astype(int))

                        cv2.putText(
                            image,
                            str(int(angle)),
                            b_pixel,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        cv2.rectangle(image, (0, 0), (300, 150),
                                      (245, 117, 16), -1)

                        cv2.putText(
                            image,
                            "REPS",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 0),
                            2,
                            cv2.LINE_AA,
                        )
                        cv2.putText(
                            image,
                            str(exercise.counter),
                            (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        cv2.putText(
                            image,
                            "STAGE",
                            (150, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 0),
                            2,
                            cv2.LINE_AA,
                        )
                        stage_text = exercise.stage if exercise.stage else ""
                        cv2.putText(
                            image,
                            stage_text,
                            (150, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        cv2.putText(
                            image,
                            f"Exercise: {current_exercise}",
                            (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA,
                        )

                        # 🎉 Show GOOD JOB popup
                if exercise.rep_completed_time and (time.time() - exercise.rep_completed_time < 3):
                    cv2.putText(
                        image,
                        "Good job!",
                        (image_width // 2 - 100, image_height // 2),
                        cv2.FONT_HERSHEY_DUPLEX,
                        1.5,
                        (0, 255, 0),
                        3,
                        cv2.LINE_AA,
                    )
                    exercise.just_completed_rep = False

            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66),
                                       thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                       thickness=2, circle_radius=2),
            )

            cv2.imshow("Personal Trainer", image)

            key = cv2.waitKey(10) & 0xFF
            if key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
