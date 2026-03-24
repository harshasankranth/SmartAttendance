# backend/trainer.py
# ─────────────────────────────────────────────────────
# SmartAttendance — Model Trainer
# Reads all student photos from /dataset
# Converts faces into embeddings using DeepFace
# Trains an SVM classifier to recognize each student
# Saves trained model to /model/classifier.pkl
# ─────────────────────────────────────────────────────

import os
import pickle
import numpy as np
from deepface import DeepFace
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def train_model():
    print("\n" + "="*50)
    print("   SmartAttendance - Model Trainer")
    print("="*50)

    embeddings = []
    labels = []
    dataset_path = "dataset"

    students = [d for d in os.listdir(dataset_path) 
                if os.path.isdir(f"{dataset_path}/{d}")]

    if len(students) == 0:
        print("ERROR: No students found in dataset/")
        return

    print(f"\nFound {len(students)} students. Starting training...\n")

    # ─────────────────────────────────────────────
    # STEP 1 — Convert every face photo into numbers
    # ─────────────────────────────────────────────
    for student in students:
        student_path = f"{dataset_path}/{student}"
        images = os.listdir(student_path)
        success_count = 0

        print(f"Processing {student} ({len(images)} photos)...")

        for img_file in images:
            img_path = f"{student_path}/{img_file}"

            try:
                result = DeepFace.represent(
                    img_path=img_path,
                    model_name="Facenet",
                    enforce_detection=True,    # ← changed
                    detector_backend="opencv"  # ← added
                )
                embedding = result[0]["embedding"]
                embeddings.append(embedding)
                labels.append(student)
                success_count += 1

            except Exception as e:
                print(f"  Skipping {img_file} - {str(e)}")

        print(f"  Done - {success_count}/{len(images)} photos processed")

    print(f"\nTotal embeddings collected: {len(embeddings)}")

    if len(embeddings) == 0:
        print("ERROR: No faces found. Check your photos.")
        return

    # ─────────────────────────────────────────────
    # STEP 2 — Convert to numpy arrays for training
    # ─────────────────────────────────────────────
    X = np.array(embeddings)
    y = np.array(labels)

    # ─────────────────────────────────────────────
    # STEP 3 — Train the SVM classifier
    # ─────────────────────────────────────────────
    print("\nTraining SVM classifier...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = SVC(kernel="linear", probability=True, C=1.0)
    clf.fit(X_train, y_train)

    # ─────────────────────────────────────────────
    # STEP 4 — Test accuracy
    # ─────────────────────────────────────────────
    accuracy = clf.score(X_test, y_test)
    print(f"Model accuracy: {round(accuracy * 100, 2)}%")

    # ─────────────────────────────────────────────
    # STEP 5 — Save the trained model
    # ─────────────────────────────────────────────
    os.makedirs("model", exist_ok=True)

    pickle.dump(clf, open("model/classifier.pkl", "wb"))
    pickle.dump({
        "embeddings": embeddings,
        "labels": labels,
        "students": students
    }, open("model/encodings.pkl", "wb"))

    print("\n" + "="*50)
    print("Training complete!")
    print(f"Students trained: {sorted(set(labels))}")
    print(f"Accuracy: {round(accuracy * 100, 2)}%")
    print("Model saved to model/classifier.pkl")
    print("="*50 + "\n")

if __name__ == "__main__":
    train_model()