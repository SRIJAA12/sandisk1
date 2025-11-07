"""
AURA Module 1 - Hybrid Classification Engine
"""
from ultralytics import YOLO
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time

model = YOLO('yolov8n.pt')

CRITICAL_CLASSES = ['person', 'dog', 'cat', 'horse', 'cow', 'elephant', 'bear']
IMPORTANT_CLASSES = ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'boat', 'train']

def is_duplicate(frame1, frame2, threshold=0.93):
    if frame1 is None or frame2 is None:
        return False, 0.0
    
    gray1 = cv2.cvtColor(cv2.resize(frame1, (64,64)), cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(cv2.resize(frame2, (64,64)), cv2.COLOR_BGR2GRAY)
    
    similarity, _ = ssim(gray1, gray2, full=True)
    
    return similarity > threshold, float(similarity)

def is_empty_sky(frame):
    hsv = cv2.cvtColor(cv2.resize(frame, (64,64)), cv2.COLOR_BGR2HSV)
    
    lower_blue = np.array([90, 30, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = np.sum(edges > 0) / edges.size
    
    return blue_ratio > 0.6 and edge_ratio < 0.02, blue_ratio, edge_ratio

def classify_frame(frame, last_frame=None):
    start = time.time()
    
    # Duplicate check
    if last_frame is not None:
        is_dup, ssim_val = is_duplicate(frame, last_frame)
        if is_dup:
            return "Discard", 1.0, "duplicate", ssim_val, time.time()-start
    
    # Sky check
    is_sky, blue_ratio, edge_ratio = is_empty_sky(frame)
    if is_sky:
        return "Discard", 0.99, "empty_sky", blue_ratio, time.time()-start
    
    # YOLO detection
    results = model(frame, verbose=False)
    
    detected_objects = []
    for result in results:
        for box in result.boxes:
            class_name = result.names[int(box.cls)]
            confidence = float(box.conf)
            detected_objects.append((class_name, confidence))
    
    if not detected_objects:
        return "Discard", 0.0, "no_objects", 0.0, time.time()-start
    
    for obj, conf in detected_objects:
        if obj in CRITICAL_CLASSES:
            return "Critical", conf, obj, 0.0, time.time()-start
    
    for obj, conf in detected_objects:
        if obj in IMPORTANT_CLASSES:
            return "Important", conf, obj, 0.0, time.time()-start
    
    return "Normal", detected_objects[0][1], detected_objects[0][0], 0.0, time.time()-start
