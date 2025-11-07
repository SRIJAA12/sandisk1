"""
AURA Module 1 - Hybrid Classification Engine
YOLOv8 + Heuristics for frame classification
"""

from ultralytics import YOLO
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from config import CRITICAL_CLASSES, IMPORTANT_CLASSES, SSIM_THRESHOLD, BLUE_RATIO_THRESHOLD, EDGE_RATIO_THRESHOLD

# Load YOLOv8
model = YOLO('yolov8n.pt')

def is_duplicate(frame1, frame2, threshold=SSIM_THRESHOLD):
    """
    Detect duplicate frames using SSIM
    Returns: (is_duplicate: bool, ssim_value: float)
    """
    if frame1 is None or frame2 is None:
        return False, 0.0
    
    try:
        # Resize and convert to grayscale
        gray1 = cv2.cvtColor(cv2.resize(frame1, (64, 64)), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv2.resize(frame2, (64, 64)), cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        similarity, _ = ssim(gray1, gray2, full=True)
        
        # Check optical flow for motion
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        flow_magnitude = np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2))
        
        # Duplicate if both SSIM high and flow low
        is_dup = similarity > threshold and flow_magnitude < 0.5
        
        return is_dup, float(similarity)
    
    except Exception as e:
        return False, 0.0


def is_empty_sky(frame):
    """
    Detect empty sky using color and edge analysis
    Returns: (is_sky: bool, blue_ratio: float, edge_ratio: float)
    """
    try:
        small = cv2.resize(frame, (64, 64))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        
        # Blue sky detection
        lower_blue = np.array([90, 30, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
        
        # Edge detection
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        # Sky criteria
        is_sky = blue_ratio > BLUE_RATIO_THRESHOLD and edge_ratio < EDGE_RATIO_THRESHOLD
        
        return is_sky, blue_ratio, edge_ratio
    
    except Exception as e:
        return False, 0.0, 0.0


def classify_frame(frame, last_frame=None):
    """
    Main classification function - Hybrid approach
    Returns: (category, confidence, detected_object, metric_value, latency_seconds)
    """
    start_time = time.time()
    
    # Stage 1: Duplicate check (fast)
    if last_frame is not None:
        is_dup, ssim_val = is_duplicate(frame, last_frame)
        if is_dup:
            latency = time.time() - start_time
            return "Discard", 1.0, "duplicate_frame", ssim_val, latency
    
    # Stage 2: Sky detection (fast)
    is_sky, blue_ratio, edge_ratio = is_empty_sky(frame)
    if is_sky:
        latency = time.time() - start_time
        return "Discard", 0.99, "empty_sky", blue_ratio, latency
    
    # Stage 3: YOLO object detection (slow but accurate)
    try:
        results = model(frame, verbose=False)
        
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]
                confidence = float(box.conf)
                detected_objects.append((class_name, confidence))
        
        # No objects detected
        if not detected_objects:
            latency = time.time() - start_time
            return "Discard", 0.0, "no_objects", 0.0, latency
        
        # Check for critical objects
        for obj, conf in detected_objects:
            if obj in CRITICAL_CLASSES:
                latency = time.time() - start_time
                return "Critical", conf, obj, conf, latency
        
        # Check for important objects
        for obj, conf in detected_objects:
            if obj in IMPORTANT_CLASSES:
                latency = time.time() - start_time
                return "Important", conf, obj, conf, latency
        
        # Default to normal for other detected objects
        latency = time.time() - start_time
        return "Normal", detected_objects[0][1], detected_objects[0][0], 0.0, latency
    
    except Exception as e:
        latency = time.time() - start_time
        return "Normal", 0.5, f"detection_error", 0.0, latency
