import cv2
import os
import time

def collect_faces():
    name = input("/n Enter Student name: ").strip()
    if not name:
        print("X Name Cant be empty!")
        return
save_path = f"dataset/{name}"
os.makedirs(save_path, exist= True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascades_frontalface_default.xml" )

cap = cv2.VideoCapture(0)
if not cap.isOpened():
     print("Cant open camera.")
     return
 
