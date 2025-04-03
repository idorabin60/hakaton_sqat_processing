import cv2
import mediapipe as mp
import math
from .models import SquatAnalysis


def calculate_angle(a, b, c):
    """
    Given three points a, b, and c, calculates the angle at b formed by a->b->c
    """
    ab = [a[0] - b[0], a[1] - b[1]]
    cb = [c[0] - b[0], c[1] - b[1]]
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    mag_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    mag_cb = math.sqrt(cb[0]**2 + cb[1]**2)
    if mag_ab * mag_cb == 0:
        return 0
    return math.degrees(math.acos(dot / (mag_ab * mag_cb)))


def analyze_squat_video(video_path):
    """
    Analyzes a squat video, returning a list of dictionaries with rep information:
      - Rep number
      - Minimum knee angle (MinDepth)
      - Duration (seconds)
      - Validity of the rep (based on angle threshold)
      - Whether knees were over the toes
      - Whether the back was kept straight
    """

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    results_data = []

    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)

    frame_index = 0
    rep_index = 0

    # Thresholds and counters
    depth_threshold = 125
    recovery_threshold = 120
    valid_depth_threshold = 105
    min_frames_per_rep = 5

    # Track state for the current squat rep
    current_rep = {
        "depths": [],
        "start_frame": None,
        "knee_over_toe_frames": 0,
        "back_straight_frames": 0,
        "rep_frames": 0
    }
    in_squat = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            # Landmark indices from MediaPipe Pose
            # 24: Right hip; 26: Right knee; 28: Right ankle
            # 12: Right shoulder; 8: Right ear; 32: Right foot index (toe)
            # (Or left side if you prefer, just remain consistent.)
            hip = [lm[24].x, lm[24].y]
            knee = [lm[26].x, lm[26].y]
            ankle = [lm[28].x, lm[28].y]
            shoulder = [lm[12].x, lm[12].y]
            ear = [lm[8].x,  lm[8].y]
            toe = [lm[32].x, lm[32].y]

            # Calculate knee angle
            angle = calculate_angle(hip, knee, ankle)

            # Check if knee is over toe (rough: compare x-coords)
            knee_over_toe = (knee[0] < toe[0])

            # Calculate back angle
            back_angle = calculate_angle(shoulder, hip, knee)
            back_straight = back_angle > 160

            # If angle < threshold, we are "in a squat"
            if angle < depth_threshold:
                if not in_squat:
                    # Start a new squat
                    in_squat = True
                    current_rep["start_frame"] = frame_index
                    current_rep["depths"] = [angle]
                    current_rep["knee_over_toe_frames"] = 1 if knee_over_toe else 0
                    current_rep["back_straight_frames"] = 1 if back_straight else 0
                    current_rep["rep_frames"] = 1
                else:
                    current_rep["depths"].append(angle)
                    current_rep["knee_over_toe_frames"] += (
                        1 if knee_over_toe else 0)
                    current_rep["back_straight_frames"] += (
                        1 if back_straight else 0)
                    current_rep["rep_frames"] += 1

            # If we were squatting and have recovered
            elif in_squat and angle > recovery_threshold:
                end_frame = frame_index
                num_frames = end_frame - current_rep["start_frame"]

                # Check if the rep lasted enough frames to be valid
                if num_frames >= min_frames_per_rep:
                    min_depth = min(
                        current_rep["depths"]) if current_rep["depths"] else 999
                    duration = num_frames / frame_rate
                    is_valid = (min_depth < valid_depth_threshold)

                    # Calculate average adherence
                    knee_over_toe_ratio = current_rep["knee_over_toe_frames"] / max(
                        current_rep["rep_frames"], 1)
                    back_straight_ratio = current_rep["back_straight_frames"] / max(
                        current_rep["rep_frames"], 1)

                    results_data.append({
                        "rep": rep_index + 1,
                        "min_depth": round(min_depth, 1),
                        "duration_sec": round(duration, 2),
                        "valid_depth": is_valid,
                        "knees_over_toes": "Yes" if knee_over_toe_ratio > 0.6 else "No",
                        "back_straight":   "Yes" if back_straight_ratio > 0.6 else "No"
                    })
                    SquatAnalysis.objects.create(
                        rep=rep_index + 1,
                        min_depth=round(min_depth, 1),
                        duration_sec=round(duration, 2),
                        valid_depth=is_valid,
                        knees_over_toes="Yes" if knee_over_toe_ratio > 0.6 else "No",
                        back_straight="Yes" if back_straight_ratio > 0.6 else "No"
                    )
                    rep_index += 1

                # Reset rep tracking
                current_rep = {
                    "depths": [],
                    "start_frame": None,
                    "knee_over_toe_frames": 0,
                    "back_straight_frames": 0,
                    "rep_frames": 0
                }
                in_squat = False

        frame_index += 1

    cap.release()
    pose.close()

    return results_data
