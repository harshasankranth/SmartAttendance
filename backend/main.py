# backend/main.py
# ─────────────────────────────────────────────────────
# SmartAttendance — FastAPI Backend
# Exposes the face recognition engine as a web API
# Frontend connects via WebSocket for real time recognition
# REST endpoints for attendance data
# ─────────────────────────────────────────────────────

import cv2
import pickle
import numpy as np
import base64
import json
from datetime import datetime
from deepface import DeepFace
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings('ignore')

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ─────────────────────────────────────────────
# INITIALIZE APP
# ─────────────────────────────────────────────
app = FastAPI(
    title="SmartAttendance API",
    description="AI-powered facial recognition attendance system",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────────
# LOAD MODEL ON STARTUP
# ─────────────────────────────────────────────
clf = None
students = []
attendance_log = []  # temporary storage for now (Firebase comes in Phase 8)

@app.on_event("startup")
async def load_model():
    global clf, students
    try:
        clf = pickle.load(open("model/classifier.pkl", "rb"))
        data = pickle.load(open("model/encodings.pkl", "rb"))
        students = data["students"]
        print(f"Model loaded! Recognizing: {students}")
    except Exception as e:
        print(f"ERROR loading model: {e}")

# ─────────────────────────────────────────────
# REST ENDPOINTS
# ─────────────────────────────────────────────

# Health check — is the server running?
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "SmartAttendance API is live!",
        "students": students
    }

# Get today's attendance
@app.get("/attendance")
def get_attendance():
    today = datetime.now().strftime("%d %b %Y")
    todays_records = [r for r in attendance_log if r["date"] == today]
    return {
        "date": today,
        "present": todays_records,
        "total_present": len(todays_records),
        "total_students": len(students)
    }

# Get all students
@app.get("/students")
def get_students():
    return {
        "students": students,
        "total": len(students)
    }

# ─────────────────────────────────────────────
# WEBSOCKET — REAL TIME RECOGNITION
# ─────────────────────────────────────────────
@app.websocket("/ws/recognize")
async def recognize(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected via WebSocket!")

    marked_this_session = set()

    try:
        while True:
            # Receive base64 image from frontend
            data = await websocket.receive_text()
            payload = json.loads(data)
            image_b64 = payload.get("image", "")

            if not image_b64:
                continue

            # Decode base64 → image
            img_bytes = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(80, 80))

            results = []

            for (x, y, w, h) in faces:
                face_crop = frame[y:y+h, x:x+w]

                if face_crop.shape[0] < 50 or face_crop.shape[1] < 50:
                    continue

                try:
                    # Save temp and recognize
                    temp_path = "model/temp_face.jpg"
                    cv2.imwrite(temp_path, face_crop)

                    result = DeepFace.represent(
                        img_path=temp_path,
                        model_name="Facenet",
                        enforce_detection=False,
                        detector_backend="skip"
                    )

                    embedding = np.array(result[0]["embedding"]).reshape(1, -1)
                    name = clf.predict(embedding)[0]
                    confidence = round(clf.predict_proba(embedding).max() * 100, 2)

                    # Mark attendance if confident enough
                    if confidence >= 55 and name not in marked_this_session:
                        marked_this_session.add(name)
                        record = {
                            "name": name,
                            "confidence": confidence,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "date": datetime.now().strftime("%d %b %Y")
                        }
                        attendance_log.append(record)
                        print(f"MARKED: {name} ({confidence}%)")

                    results.append({
                        "name": name,
                        "confidence": confidence,
                        "box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    })

                except Exception as e:
                    results.append({
                        "name": "Unknown",
                        "confidence": 0,
                        "box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    })

            # Send results back to frontend
            await websocket.send_json({
                "faces": results,
                "marked_today": list(marked_this_session),
                "total_present": len(marked_this_session)
            })

    except WebSocketDisconnect:
        print("Frontend disconnected.")

# ─────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)