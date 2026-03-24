

import cv2
import pickle
import numpy as np
from deepface import DeepFace
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def load_model():
    try:
        data = pickle.load(open("model/encodings.pkl", "rb"))

        known_encodings = np.array(data["embeddings"])
        known_names = data["labels"]

        print("Embeddings loaded!")
        return known_encodings, known_names

    except FileNotFoundError:
        print("ERROR: Model not found.")
        return None, None

def recognize_face(known_encodings, known_names, face_img, threshold=0.6):
    try:
        temp_path = "model/temp_face.jpg"
        cv2.imwrite(temp_path, face_img)

        result = DeepFace.represent(
            img_path=temp_path,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="opencv"
        )

        if not result:
            return "Unknown", 0

        embedding = np.array(result[0]["embedding"])

        # Distance calculation
        distances = np.linalg.norm(known_encodings - embedding, axis=1)

        min_idx = np.argmin(distances)
        min_distance = distances[min_idx]

        print("Distance:", min_distance)

        if min_distance < threshold:
            return known_names[min_idx], round((1 - min_distance) * 100, 2)
        else:
            return "Unknown", 0

    except:
        return "Unknown", 0

def run_recognition():
    print("\n" + "="*50)
    print("   SmartAttendance - Recognition Engine")
    print("="*50)

    clf, students = load_model()
    if clf is None:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam!")
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
                         
    marked_today = set()
    frame_count = 0
    current_name = "Detecting..."
    current_confidence = 0
    color = (0, 255, 0)

    print("Webcam opened! Looking for faces...")
    print("Press Q to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Lost webcam connection")
            break

        frame_count += 1
        display = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(80, 80))

        for (x, y, w, h) in faces:

            # Only recognize every 15 frames for performance
            if frame_count % 15 == 0:
                face_crop = frame[y:y+h, x:x+w]

                # Make sure face crop is big enough
                if face_crop.shape[0] > 50 and face_crop.shape[1] > 50:
                    current_name, current_confidence = recognize_face(
                        known_encodings, known_names, face_crop
                    )

                    # Mark attendance
                    if current_confidence >= 82 and current_name != "Unknown":
                        if current_name not in marked_today:
                            marked_today.add(current_name)
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"MARKED: {current_name} at {timestamp} ({current_confidence}%)")

            # Set color
            color = (0, 255, 0) if current_name not in ["Unknown", "Detecting..."] else (0, 0, 255)

            # Draw face box
            cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)

            # Name background
            cv2.rectangle(display, (x, y-45), (x+w, y), color, -1)

            # Name text
            cv2.putText(display, current_name, (x+5, y-25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            # Confidence
            cv2.putText(display, f"Confidence: {current_confidence}%", (x+5, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # Top bar
        now = datetime.now().strftime("%d %b %Y  %H:%M:%S")
        cv2.rectangle(display, (0, 0), (display.shape[1], 45), (20, 20, 20), -1)
        cv2.putText(display, f"SmartAttendance  |  {now}  |  Present: {len(marked_today)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Bottom bar
        if marked_today:
            names = ", ".join(marked_today)
            cv2.rectangle(display, (0, display.shape[0]-40),
                         (display.shape[1], display.shape[0]), (20, 20, 20), -1)
            cv2.putText(display, f"Present: {names}",
                       (10, display.shape[0]-12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 1)

        cv2.imshow("SmartAttendance", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Final summary
    print("\n" + "="*50)
    print("ATTENDANCE SUMMARY")
    print("="*50)
    print(f"Date: {datetime.now().strftime('%d %b %Y')}")
    print(f"Present ({len(marked_today)}): {', '.join(marked_today) if marked_today else 'None'}")
    absent = set(students) - marked_today
    print(f"Absent ({len(absent)}): {', '.join(absent) if absent else 'None'}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_recognition()