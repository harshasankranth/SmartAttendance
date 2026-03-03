# Smart Attendance — Journal

## Day1 [24 Feb 2025]

### What I built
- Created GitHub repo and cloned it locally
- Set up full folder structure in VS Code
- Learned Git add, commit, push workflow
- Fixed PowerShell issues by switching to Git Bash

### What I learned
- Git tracks files not folders, so empty folders need .gitkeep
- PowerShell and Git Bash are different terminals with different commands
- Moving a folder doesn't break Git, it moves with it
- git add . → commit → push is the core workflow every developer uses

### What I still don't understand
- How do i train my FaceNet and integrate it
- how websockets work

### Errors I hit and fixed
- mkdir failed in PowerShell → ran folders one by one
- type nul failed → switched to Git Bash, used touch instead.

## You are here now:
```
PHASE 1 — Setup & Git          ✅ DONE
PHASE 2 — Python Environment   ✅ DONE← just finished!
PHASE 3 — Dataset Collection   ⏳ NEXT
PHASE 4 — Train the Model      ⏳ 
PHASE 5 — Face Recognition     ⏳ 
PHASE 6 — Backend API          ⏳
PHASE 7 — Frontend UI          ⏳
PHASE 8 — Firebase Database    ⏳
PHASE 9 — Deployment           ⏳










## Day 2 — [2nd march 2026.]

### What I built
- Wrote the model trainer script
- Trained SVM classifier on 6 students
- Got 93.75% accuracy on first run

### What I learned
- DeepFace converts faces into 128 numbers called embeddings
- SVM learns the difference between those number patterns
- train_test_split tests the model on photos it never saw
- Higher accuracy = model generalizes better to new photos

### What I still don't understand
- How exactly FaceNet generates the 128 numbers
- What kernel="linear" means in SVM

### What I built
- Built face_engine.py — real time recognition engine
- System successfully recognized 5/6 students live
- Attendance summary printed with present/absent list

### What I learned
- DeepFace works better reading from file than raw array
- detector_backend="skip" avoids double face detection
- Confidence threshold of 55% filters out wrong matches
- Every 15 frames = smooth video + fast enough recognition

### Moments that hit different
- Seeing my own name appear on screen for the first time
- Watching the attendance summary print automatically
``

### What I built
- Connected Supabase PostgreSQL database
- Students and attendance now save to cloud permanently
- Admin login protecting the whole system
- Add student live from website with auto training
- Export attendance as Excel
- Full stack complete end to end

### What I learned
- Environment variables keep secrets safe
- Supabase is PostgreSQL in the cloud
- Real databases persist data unlike JSON files
- Full stack means frontend + backend + database working together

### How I felt
- Overwhelmed at times but pushed through
- Every error I fixed made me more confident
- Cant believe I built this in one week
---

## You are here now:
```
PHASE 1 — Setup & Git          ✅ DONE
PHASE 2 — Python Environment   ✅ DONE
PHASE 3 — Dataset Collection   ✅ DONE
PHASE 4 — Train the Model      ✅ DONE
PHASE 5 — Face Recognition     ✅ DONE 🎉
PHASE 6 — Backend API          ⏳ 
PHASE 7 — Frontend UI          ⏳
PHASE 8 — Firebase Database    ⏳
PHASE 9 — Deployment           ⏳

## DEPLOYMENT STATUS — 03 Mar 2026

### What's working perfectly:
- Full stack working locally ✅
- Face recognition working ✅
- Frontend UI complete ✅
- Supabase database connected ✅
- Admin login working ✅
- Add student from website ✅
- Export Excel working ✅

### Deployment status:
- Frontend → NOT deployed yet (next: Vercel)
- Backend → Render failing due to DeepFace/TensorFlow conflict
- Fix in progress: requirements.txt with tensorflow==2.12.0 keras==2.12.0

### Exact error on Render:
ImportError: cannot import name 'LocallyConnected2D'
from tensorflow.keras.layers

### Next steps:
1. Wait for current Render build to finish
2. If still fails → try Hugging Face Spaces
3. Deploy frontend to Vercel
4. Update Camera.jsx WebSocket URL to deployed backend URL

