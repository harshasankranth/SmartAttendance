
import cv2
import os
import time

def collect_faces():
    print("\n" + "="*50)
    print("   SmartAttendance — Face Collector")
    print("="*50)
    
    name = input("\n Enter student name (e.g. Harsha_Sankranth): ").strip()
    
    if not name:
        print("❌ Name cannot be empty!")
        return
    
    save_path = f"dataset/{name}"
    os.makedirs(save_path, exist_ok=True)
    
    print(f"\n📁 Saving photos to: {save_path}")
    print("📸 Get ready! Capturing 20 photos...")
    print("👉 Press Q to quit early\n")
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam. Check if it's connected.")
        return
    
    count = 0
    total = 20
    last_capture = time.time()
    
    while count < total:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from webcam.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Draw green box around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Capture every 0.5 seconds so photos aren't identical
            if time.time() - last_capture >= 0.5:
                img_path = f"{save_path}/img_{count:03d}.jpg"
                cv2.imwrite(img_path, frame[y:y+h, x:x+w])
                count += 1
                last_capture = time.time()
                print(f"  ✅ Captured {count}/{total}")
        
        # Show progress on screen
        cv2.putText(frame, f"Student: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Captured: {count}/{total}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        if len(faces) == 0:
            cv2.putText(frame, "No face detected - move closer", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow("SmartAttendance - Face Collector", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n⚠️  Stopped early by user.")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n{'='*50}")
    print(f"✅ Done! {count} photos saved for {name}")
    print(f"📁 Location: {save_path}/")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    collect_faces()