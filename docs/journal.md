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
```

---

## You are here now:
```
PHASE 1 — Setup & Git          ✅ DONE
PHASE 2 — Python Environment   ✅ DONE
PHASE 3 — Dataset Collection   ✅ DONE
PHASE 4 — Train the Model      ✅ DONE
PHASE 5 — Face Recognition     ✅ DONE 🎉
PHASE 6 — Backend API          ⏳ NEXT
PHASE 7 — Frontend UI          ⏳
PHASE 8 — Firebase Database    ⏳
PHASE 9 — Deployment           ⏳


