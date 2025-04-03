import cv2
import mediapipe as mp
import math


def calculate_angle(a, b, c):
    ab = [a[0] - b[0], a[1] - b[1]]
    cb = [c[0] - b[0], c[1] - b[1]]
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    mag_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    mag_cb = math.sqrt(cb[0]**2 + cb[1]**2)
    if mag_ab * mag_cb == 0:
        return 0
    return math.degrees(math.acos(dot / (mag_ab * mag_cb)))


def analyze_squat_video(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    results_data = []

    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_index = 0
    rep_index = 0
    current_rep = {"depths": [], "start_frame": None}
    depth_threshold = 100

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[24].x, landmarks[24].y]
            knee = [landmarks[26].x, landmarks[26].y]
            ankle = [landmarks[28].x, landmarks[28].y]
            angle = calculate_angle(hip, knee, ankle)
            if angle < depth_threshold:
                if current_rep["start_frame"] is None:
                    current_rep["start_frame"] = frame_index
                current_rep["depths"].append(angle)
            elif current_rep["start_frame"] is not None:
                end_frame = frame_index
                min_depth = min(current_rep["depths"]
                                ) if current_rep["depths"] else 999
                duration = (
                    end_frame - current_rep["start_frame"]) / frame_rate
                is_valid = min_depth < 90
                results_data.append({
                    "rep": rep_index + 1,
                    "min_depth": round(min_depth, 1),
                    "duration": round(duration, 2),
                    "valid": is_valid
                })
                current_rep = {"depths": [], "start_frame": None}
                rep_index += 1
        frame_index += 1

    cap.release()
    pose.close()

    return results_data
