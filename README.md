#  SmartAttendance — AI Facial Recognition Attendance System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-blue?style=for-the-badge)](https://smart-attendance-puce.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Hugging%20Face-yellow?style=for-the-badge)](https://harshasankranth-smartattendance.hf.space)
[![GitHub](https://img.shields.io/badge/GitHub-SmartAttendance-black?style=for-the-badge)](https://github.com/harshasankranth/SmartAttendance)

> Built from scratch in 3 weeks as my first ever full stack project. Zero prior knowledge of APIs, databases, or deployment.

---

##  Live Demo

** Web App:** https://smart-attendance-puce.vercel.app  
** API:** https://harshasankranth-smartattendance.hf.space  
**Default login:** `harsha` / `lucky123`

---

##  What It Does

Traditional attendance = manual roll calls, proxy attendance, paper registers.

SmartAttendance replaces all of that with **AI facial recognition**:

1. Admin registers students via **live webcam** on the website
2. System extracts facial embeddings using **InsightFace** (state-of-the-art)
3. Students stand in front of camera → **recognized instantly**
4. Attendance marked automatically with timestamp
5. Export to **Excel** anytime

No apps to install. No hardware. Just a browser.

---

##  Features

- 🔐 **Admin Login** — Protected dashboard
- 📸 **Live Student Registration** — Capture 20 photos directly from browser
- 🧠 **Auto Model Training** — Retrains automatically when new student added
- 👁️ **Real-time Recognition** — WebSocket-powered live camera feed
- 📊 **Attendance Dashboard** — Live attendance tracking
- 🗑️ **Delete Students** — Remove students and retrain
- 📥 **Excel Export** — Download attendance as formatted spreadsheet
- ☁️ **Cloud Persistence** — Model and data saved to Supabase Storage

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Face Recognition | InsightFace (buffalo_sc) + Cosine Similarity |
| Backend | FastAPI + WebSockets |
| Frontend | React 18 + Tailwind CSS |
| Database | Supabase PostgreSQL |
| Model Storage | Supabase Storage |
| Backend Hosting | Hugging Face Spaces (Docker) |
| Frontend Hosting | Vercel |
| Containerization | Docker (Python 3.10-slim) |

---

## How Face Recognition Works

```
Student stands in front of camera
        ↓
InsightFace detects face in frame
        ↓
buffalo_sc model extracts 512-dimensional embedding
        ↓
Cosine similarity compared against all known faces
        ↓
If similarity ≥ 35% threshold → identity confirmed
        ↓
Attendance marked with name, enrollment, timestamp
```

**Why InsightFace over DeepFace/FaceNet?**
- Works with just 3-5 photos per person
- ONNX runtime → no TensorFlow → fast on CPU
- Generalizes across different cameras and lighting
- Industry-grade accuracy (used in production systems)

---

## Architecture

```
Browser (React + Tailwind)
    ↕ WebSocket (real-time frames)
FastAPI Backend (Hugging Face Spaces)
    ↕ SQL queries
Supabase PostgreSQL (students + attendance)
    ↕ File storage
Supabase Storage (face encodings model)
```

---

##  Run Locally

```bash
# Clone
git clone https://github.com/harshasankranth/SmartAttendance
cd SmartAttendance

# Backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r backend/requirements.txt

# Add .env file
echo "SUPABASE_URL=your_url" > .env
echo "SUPABASE_KEY=your_key" >> .env

# Start backend
uvicorn backend.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
SmartAttendance/
├── backend/
│   ├── main.py          # FastAPI app + InsightFace recognition
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Login.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Camera.jsx
│       │   ├── Students.jsx
│       │   └── AddStudent.jsx
│       └── App.jsx
├── Dockerfile
├── Procfile
└── README.md
```

---

## Results

- ✅ Recognizes students with high confidence across different cameras
- ✅ Works with phone photos and webcam photos
- ✅ Real-time recognition at ~1 frame/second
- ✅ Model persists across server restarts via Supabase Storage
- ✅ Fully deployed — accessible from any device globally

---

## The Journey

This was my **first ever full stack project**. Here's what I learned the hard way:

- **Distribution shift is real** — training on phone photos and recognizing via webcam fails. Switched from DeepFace+SVM to InsightFace+cosine similarity to fix this
- **Deployment is hard** — TensorFlow version conflicts broke Render multiple times. Switched to Hugging Face Spaces with Docker
- **Stateless servers lose files** — HF Spaces resets on restart. Built Supabase Storage persistence for model files
- **Cache bugs are sneaky** — Double `https://` URLs and Vercel cache issues took hours to debug
- **SVM always picks closest match** — regardless of confidence. Cosine similarity with threshold is better for open-set recognition

---

##  Planned Features

- [ ] Subject-wise attendance tracking
- [ ] Attendance history page (all days)
- [ ] UptimeRobot monitoring
- [ ] Better mobile UI

---

##  Built By

**Harsha Sankranth** — First full stack AI project, built in 3 weeks from zero.

---

*I am glad my project helped you! will keep doing more!*
