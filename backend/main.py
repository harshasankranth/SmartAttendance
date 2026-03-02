# backend/main.py
# ─────────────────────────────────────────────────────
# SmartAttendance — Full Backend
# Endpoints:
#   GET  /                    → health check
#   POST /auth/login          → admin login
#   GET  /students/all        → get all students
#   POST /students/add        → add new student + save photos
#   POST /students/train      → retrain model
#   GET  /attendance          → get today's attendance
#   GET  /attendance/export   → download Excel
#   WS   /ws/recognize        → live recognition
# ─────────────────────────────────────────────────────

import os
import cv2
import pickle
import numpy as np
import base64
import json
import shutil
from datetime import datetime
from deepface import DeepFace
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
# INITIALIZE APP
# ─────────────────────────────────────────────
app = FastAPI(title="SmartAttendance API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class StudentRequest(BaseModel):
    name: str
    enrollment: str
    images: List[str]  # list of base64 images

# ─────────────────────────────────────────────
# IN MEMORY STORAGE
# ─────────────────────────────────────────────
clf = None
students_db = {}     # { enrollment: { name, enrollment, added_on } }
attendance_log = []  # [ { name, enrollment, time, date } ]

STUDENTS_FILE = "model/students.json"
ATTENDANCE_FILE = "model/attendance.json"

# ─────────────────────────────────────────────
# LOAD DATA ON STARTUP
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global clf, students_db, attendance_log
    
    # Load model
    try:
        clf = pickle.load(open("model/classifier.pkl", "rb"))
        print("Model loaded!")
    except:
        print("No model found. Add students to train.")
    
    # Load students
    if os.path.exists(STUDENTS_FILE):
        students_db = json.load(open(STUDENTS_FILE))
        print(f"Loaded {len(students_db)} students")
    
    # Load attendance
    if os.path.exists(ATTENDANCE_FILE):
        attendance_log = json.load(open(ATTENDANCE_FILE))
        print(f"Loaded {len(attendance_log)} attendance records")

def save_students():
    os.makedirs("model", exist_ok=True)
    json.dump(students_db, open(STUDENTS_FILE, "w"), indent=2)

def save_attendance():
    os.makedirs("model", exist_ok=True)
    json.dump(attendance_log, open(ATTENDANCE_FILE, "w"), indent=2)

def save_student_to_supabase(student):
    try:
        supabase.table("students").insert({
            "name": student["name"],
            "enrollment": student["enrollment"],
            "folder": student["folder"],
            "photos": student["photos"],
            "added_on": student["added_on"]
        }).execute()
        print(f"Student saved to Supabase: {student['name']}")
    except Exception as e:
        print(f"Supabase student save error: {e}")

def save_attendance_to_supabase(record):
    try:
        supabase.table("attendance").insert({
            "name": record["name"],
            "enrollment": record["enrollment"],
            "confidence": record["confidence"],
            "time": record["time"],
            "date": record["date"]
        }).execute()
        print(f"Attendance saved to Supabase: {record['name']}")
    except Exception as e:
        print(f"Supabase attendance save error: {e}")
# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
ADMIN_USERNAME = "harsha"
ADMIN_PASSWORD = "lucky123"

@app.post("/auth/login")
def login(req: LoginRequest):
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ─────────────────────────────────────────────
# STUDENTS
# ─────────────────────────────────────────────
@app.get("/students/all")
def get_students():
    return {
        "students": list(students_db.values()),
        "total": len(students_db)
    }

@app.post("/students/add")
async def add_student(req: StudentRequest):
    global students_db

    name = req.name.strip().replace(" ", "_")
    enrollment = req.enrollment.strip()

    if enrollment in students_db:
        raise HTTPException(status_code=400, detail="Enrollment number already exists")

    # Save photos to dataset
    student_folder = f"dataset/{enrollment}_{name}"
    os.makedirs(student_folder, exist_ok=True)

    saved = 0
    for i, img_b64 in enumerate(req.images):
        try:
            img_bytes = base64.b64decode(img_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imwrite(f"{student_folder}/img_{i:03d}.jpg", frame)
                saved += 1
        except:
            continue

    if saved < 5:
        shutil.rmtree(student_folder)
        raise HTTPException(status_code=400, detail="Not enough valid photos captured")

    # Save student to DB
    students_db[enrollment] = {
        "name": req.name,
        "enrollment": enrollment,
        "folder": student_folder,
        "photos": saved,
        "added_on": datetime.now().strftime("%d %b %Y %H:%M")
    }
    save_students()
    save_student_to_supabase(students_db[enrollment])

    # Retrain model
    success = retrain_model()

    return {
        "success": True,
        "message": f"Student {req.name} added with {saved} photos",
        "trained": success
    }

# ─────────────────────────────────────────────
# TRAIN MODEL
# ─────────────────────────────────────────────
def retrain_model():
    global clf
    try:
        from sklearn.svm import SVC

        embeddings = []
        labels = []

        for folder in os.listdir("dataset"):
            folder_path = f"dataset/{folder}"
            if not os.path.isdir(folder_path):
                continue

            for img_file in os.listdir(folder_path):
                img_path = f"{folder_path}/{img_file}"
                try:
                    result = DeepFace.represent(
                        img_path=img_path,
                        model_name="Facenet",
                        enforce_detection=False
                    )
                    embeddings.append(result[0]["embedding"])
                    labels.append(folder)
                except:
                    continue

        if len(set(labels)) < 2:
            print("Need at least 2 students to train")
            return False

        clf_new = SVC(kernel="linear", probability=True, C=1.0)
        clf_new.fit(embeddings, labels)

        os.makedirs("model", exist_ok=True)
        pickle.dump(clf_new, open("model/classifier.pkl", "wb"))
        pickle.dump({
            "embeddings": embeddings,
            "labels": labels,
            "students": list(set(labels))
        }, open("model/encodings.pkl", "wb"))

        clf = clf_new
        print(f"Model retrained! Students: {list(set(labels))}")
        return True

    except Exception as e:
        print(f"Training error: {e}")
        return False

@app.post("/students/train")
def train_endpoint():
    success = retrain_model()
    if success:
        return {"success": True, "message": "Model retrained successfully"}
    raise HTTPException(status_code=500, detail="Training failed")

# ─────────────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────────────
@app.get("/attendance")
def get_attendance():
    today = datetime.now().strftime("%d %b %Y")
    todays = [r for r in attendance_log if r["date"] == today]
    return {
        "date": today,
        "records": todays,
        "total_present": len(todays),
        "total_students": len(students_db)
    }

@app.get("/attendance/export")
def export_attendance():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance"

        # Header styling
        header_fill = PatternFill("solid", fgColor="1E40AF")
        header_font = Font(bold=True, color="FFFFFF")

        headers = ["#", "Name", "Enrollment", "Date", "Time", "Confidence"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # Data rows
        today = datetime.now().strftime("%d %b %Y")
        todays = [r for r in attendance_log if r["date"] == today]

        for row, record in enumerate(todays, 2):
            ws.cell(row=row, column=1, value=row-1)
            ws.cell(row=row, column=2, value=record.get("name", ""))
            ws.cell(row=row, column=3, value=record.get("enrollment", ""))
            ws.cell(row=row, column=4, value=record.get("date", ""))
            ws.cell(row=row, column=5, value=record.get("time", ""))
            ws.cell(row=row, column=6, value=record.get("confidence", ""))

        # Column widths
        ws.column_dimensions["A"].width = 5
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 20
        ws.column_dimensions["D"].width = 15
        ws.column_dimensions["E"].width = 15
        ws.column_dimensions["F"].width = 15

        export_path = "model/attendance_export.xlsx"
        wb.save(export_path)
        return FileResponse(
            export_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"attendance_{today}.xlsx"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# WEBSOCKET — LIVE RECOGNITION
# ─────────────────────────────────────────────
@app.websocket("/ws/recognize")
async def recognize(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected!")

    marked_this_session = set()
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            image_b64 = payload.get("image", "")

            if not image_b64 or clf is None:
                await websocket.send_json({"faces": [], "marked_today": [], "total_present": 0})
                continue

            img_bytes = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(80, 80))

            results = []

            for (x, y, w, h) in faces:
                face_crop = frame[y:y+h, x:x+w]
                if face_crop.shape[0] < 50 or face_crop.shape[1] < 50:
                    continue

                try:
                    temp_path = "model/temp_face.jpg"
                    cv2.imwrite(temp_path, face_crop)

                    result = DeepFace.represent(
                        img_path=temp_path,
                        model_name="Facenet",
                        enforce_detection=False,
                        detector_backend="skip"
                    )

                    embedding = np.array(result[0]["embedding"]).reshape(1, -1)
                    
                    # Get folder name and find enrollment
                    folder_name = clf.predict(embedding)[0]
                    confidence = round(clf.predict_proba(embedding).max() * 100, 2)

                    # Find student by folder name
                    student_info = None
                    for enr, info in students_db.items():
                        if f"{enr}_{info['name'].replace(' ', '_')}" == folder_name:
                            student_info = info
                            break

                    display_name = student_info["name"] if student_info else folder_name
                    enrollment = student_info["enrollment"] if student_info else "N/A"

                    if confidence >= 55 and folder_name not in marked_this_session:
                        marked_this_session.add(folder_name)
                        record = {
                            "name": display_name,
                            "enrollment": enrollment,
                            "confidence": confidence,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "date": datetime.now().strftime("%d %b %Y")
                        }
                        attendance_log.append(record)
                        save_attendance()
                        save_attendance_to_supabase(record)
                        print(f"MARKED: {display_name} ({enrollment}) {confidence}%")

                    results.append({
                        "name": display_name,
                        "enrollment": enrollment,
                        "confidence": confidence,
                        "box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    })

                except Exception as e:
                    results.append({
                        "name": "Unknown",
                        "enrollment": "",
                        "confidence": 0,
                        "box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    })

            await websocket.send_json({
                "faces": results,
                "marked_today": list(marked_this_session),
                "total_present": len(marked_this_session)
            })

    except WebSocketDisconnect:
        print("Frontend disconnected.")

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "status": "running",
        "students": len(students_db),
        "model_loaded": clf is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)