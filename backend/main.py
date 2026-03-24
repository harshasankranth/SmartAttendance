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
app = FastAPI(title="SmartAttendance API", version="3.0.0")

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
    images: List[str]

# ─────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────
students_db = {}
attendance_log = []

known_encodings = None
known_names = None

STUDENTS_FILE = "model/students.json"
ATTENDANCE_FILE = "model/attendance.json"

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global students_db, attendance_log, known_encodings, known_names

    if os.path.exists(STUDENTS_FILE):
        students_db = json.load(open(STUDENTS_FILE))

    if os.path.exists(ATTENDANCE_FILE):
        attendance_log = json.load(open(ATTENDANCE_FILE))

    # Load encodings
    try:
        if not os.path.exists("model/encodings.pkl"):
            print("Downloading encodings from Supabase...")
            #res = supabase.storage.from_("models").download("encodings.pkl")
            os.makedirs("model", exist_ok=True)
            #with open("model/encodings.pkl", "wb") as f:
               # f.write(res)

        data = pickle.load(open("model/encodings.pkl", "rb"))
        known_encodings = np.array(data["embeddings"])
        known_names = data["labels"]

        print("Encodings loaded:", len(known_names))

    except Exception as e:
        print("No encodings found:", e)

# ─────────────────────────────────────────────
# SAVE HELPERS
# ─────────────────────────────────────────────
def save_students():
    os.makedirs("model", exist_ok=True)
    json.dump(students_db, open(STUDENTS_FILE, "w"), indent=2)

def save_attendance():
    os.makedirs("model", exist_ok=True)
    json.dump(attendance_log, open(ATTENDANCE_FILE, "w"), indent=2)

# ─────────────────────────────────────────────
# TRAIN MODEL (NO SVM)
# ─────────────────────────────────────────────
def retrain_model():
    global known_encodings, known_names

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

    if len(embeddings) == 0:
        return False

    os.makedirs("model", exist_ok=True)

    pickle.dump({
        "embeddings": embeddings,
        "labels": labels
    }, open("model/encodings.pkl", "wb"))

    known_encodings = np.array(embeddings)
    known_names = labels

    # Upload to Supabase
    try:
        with open("model/encodings.pkl", "rb") as f:
            supabase.storage.from_("models").upload(
                "encodings.pkl",
                f.read(),
                {"upsert": "true"}
            )
        print("Encodings uploaded!")
    except Exception as e:
        print("Upload error:", e)

    return True

# ─────────────────────────────────────────────
# FACE MATCH FUNCTION
# ─────────────────────────────────────────────
def match_face(embedding, threshold=0.6):
    if known_encodings is None:
        return "Unknown", 0

    distances = np.linalg.norm(known_encodings - embedding, axis=1)

    min_idx = np.argmin(distances)
    min_distance = distances[min_idx]

    if min_distance < threshold:
        name = known_names[min_idx]
        confidence = round((1 - min_distance) * 100, 2)
        return name, confidence

    return "Unknown", 0

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
@app.post("/auth/login")
def login(req: LoginRequest):
    if req.username == "harsha" and req.password == "lucky123":
        return {"success": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ─────────────────────────────────────────────
# ADD STUDENT
# ─────────────────────────────────────────────
@app.post("/students/add")
async def add_student(req: StudentRequest):
    name = req.name.strip().replace(" ", "_")
    enrollment = req.enrollment.strip()

    folder = f"dataset/{enrollment}_{name}"
    os.makedirs(folder, exist_ok=True)

    count = 0

    for i, img in enumerate(req.images):
        try:
            img_bytes = base64.b64decode(img)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imwrite(f"{folder}/{i}.jpg", frame)
                count += 1
        except:
            continue

    if count < 5:
        shutil.rmtree(folder)
        raise HTTPException(status_code=400, detail="Need at least 5 images")

    students_db[enrollment] = {
        "name": req.name,
        "enrollment": enrollment,
        "folder": folder
    }

    save_students()
    retrain_model()

    return {"success": True}

# ─────────────────────────────────────────────
# WEBSOCKET
# ─────────────────────────────────────────────
@app.websocket("/ws/recognize")
async def recognize(websocket: WebSocket):
    await websocket.accept()

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    marked = set()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            img_bytes = base64.b64decode(payload["image"])
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            results = []

            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]

                try:
                    cv2.imwrite("temp.jpg", face)

                    rep = DeepFace.represent(
                        img_path="temp.jpg",
                        model_name="Facenet",
                        enforce_detection=False
                    )

                    embedding = np.array(rep[0]["embedding"])

                    name, confidence = match_face(embedding)

                    if name != "Unknown" and name not in marked:
                        marked.add(name)

                        record = {
                            "name": name,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "date": datetime.now().strftime("%d %b %Y"),
                            "confidence": confidence
                        }

                        attendance_log.append(record)
                        save_attendance()

                    results.append({
                        "name": name,
                        "confidence": confidence,
                        "box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    })

                except:
                    continue

            await websocket.send_json({
                "faces": results,
                "present": list(marked)
            })

    except WebSocketDisconnect:
        print("Disconnected")

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "status": "running",
        "students": len(students_db),
        "model_loaded": known_encodings is not None
    }