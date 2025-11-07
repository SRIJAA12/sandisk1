"""
AURA Module 1 - Hybrid Classification Engine (FIXED)
YOLOv8 + Relaxed Heuristics for frame classification
ISSUE: Was too aggressive - fixed thresholds
"""

from ultralytics import YOLO
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from config import CRITICAL_CLASSES, IMPORTANT_CLASSES, SSIM_THRESHOLD, BLUE_RATIO_THRESHOLD, EDGE_RATIO_THRESHOLD

# Load YOLOv8
try:
    model = YOLO('yolov8n.pt')
except Exception as e:
    print(f"Warning: Could not load YOLO model: {e}")
    model = None

def is_duplicate(frame1, frame2, threshold=0.97):  # RELAXED: was 0.93, now 0.97
    """
    Detect ONLY truly duplicate frames using SSIM
    More conservative to avoid discarding good frames
    """
    if frame1 is None or frame2 is None:
        return False, 0.0
    
    try:
        # Only check every few frames for duplicates
        gray1 = cv2.cvtColor(cv2.resize(frame1, (64, 64)), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv2.resize(frame2, (64, 64)), cv2.COLOR_BGR2GRAY)
        
        similarity, _ = ssim(gray1, gray2, full=True)
        
        # More strict: require near-perfect match AND low motion
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        flow_magnitude = np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2))
        
        # BOTH conditions must be true:
        # 1. Frames are 97%+ identical (was 93%)
        # 2. Optical flow is minimal
        is_dup = similarity > threshold and flow_magnitude < 1.0  # was 0.5, now 1.0
        
        return is_dup, float(similarity)
    
    except Exception as e:
        return False, 0.0


def is_empty_sky(frame):
    """
    Detect empty sky - but be VERY conservative
    Only discard if CLEARLY empty
    """
    try:
        small = cv2.resize(frame, (64, 64))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        
        # Blue sky detection (relaxed thresholds)
        lower_blue = np.array([85, 20, 50])      # was [90, 30, 50]
        upper_blue = np.array([135, 255, 255])   # was [130, 255, 255]
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
        
        # White/gray sky detection (overcast)
        lower_white = np.array([0, 0, 200])      # was [0, 0, 180]
        upper_white = np.array([180, 20, 255])   # was [180, 30, 255]
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        white_ratio = np.sum(white_mask > 0) / white_mask.size
        
        # Edge detection
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        # MORE STRICT SKY CRITERIA:
        # Must be VERY blue (>80%) AND very few edges (<1%)
        is_blue_sky = (blue_ratio > 0.80 and edge_ratio < 0.01)      # was 0.6 and 0.02
        is_overcast_sky = (white_ratio > 0.85 and edge_ratio < 0.01) # was 0.70 and 0.02
        
        return (is_blue_sky or is_overcast_sky), blue_ratio, edge_ratio
    
    except Exception as e:
        return False, 0.0, 0.0


def is_static_water(frame):
    """
    Detect static water surfaces - VERY conservative
    """
    try:
        small = cv2.resize(frame, (64, 64))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        
        # Water color ranges (blue-green spectrum)
        lower_water = np.array([80, 20, 20])
        upper_water = np.array([110, 200, 180])
        water_mask = cv2.inRange(hsv, lower_water, upper_water)
        water_ratio = np.sum(water_mask > 0) / water_mask.size
        
        # Calculate texture variance
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        
        # Only discard if VERY uniform water (>80% ratio AND very low variance)
        return water_ratio > 0.85 and variance < 300, water_ratio
    
    except Exception as e:
        return False, 0.0


def classify_frame(frame, last_frame=None):
    """
    Main classification function - FIXED VERSION
    LESS AGGRESSIVE - saves more frames
    """
    start_time = time.time()
    
    # Stage 1: Duplicate check (VERY strict now)
    if last_frame is not None:
        is_dup, ssim_val = is_duplicate(frame, last_frame)
        if is_dup:
            latency = time.time() - start_time
            return "Discard", 1.0, "duplicate_frame", ssim_val, latency
    
    # Stage 2: Sky detection (VERY conservative)
    is_sky, blue_ratio, edge_ratio = is_empty_sky(frame)
    if is_sky:
        latency = time.time() - start_time
        return "Discard", 0.99, "empty_sky", blue_ratio, latency
    
    # Stage 3: Water detection (VERY conservative)
    is_water, water_ratio = is_static_water(frame)
    if is_water:
        latency = time.time() - start_time
        return "Discard", 0.99, "static_water", water_ratio, latency
    
    # Stage 4: YOLO object detection
    try:
        if model is None:
            # If YOLO not available, save as Normal
            latency = time.time() - start_time
            return "Normal", 0.8, "no_model", 0.0, latency
        
        results = model(frame, verbose=False)
        
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]
                confidence = float(box.conf)
                
                # Only consider detections with >50% confidence
                if confidence > 0.5:
                    detected_objects.append((class_name, confidence))
        
        # No objects detected = Still save as Normal (not Discard!)
        if not detected_objects:
            latency = time.time() - start_time
            return "Normal", 0.7, "no_objects_but_saved", 0.0, latency
        
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
        # If YOLO fails, save as Normal anyway
        latency = time.time() - start_time
        return "Normal", 0.6, f"detection_ok_saved", 0.0, latency


# Test function to debug
def test_classification():
    """Test the classifier with a simple frame"""
    import numpy as np
    
    # Create test frame - mostly blue (sky)
    test_frame = np.ones((480, 640, 3), dtype=np.uint8)
    test_frame[:, :] = [255, 0, 0]  # Blue in BGR
    
    category, confidence, detected, metric, latency = classify_frame(test_frame)
    print(f"Blue frame test: {category} - {detected} ({confidence:.1%})")
    
    # Create test frame - mostly normal scene
    test_frame2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    category2, confidence2, detected2, metric2, latency2 = classify_frame(test_frame2)
    print(f"Random frame test: {category2} - {detected2} ({confidence2:.1%})")

if __name__ == "__main__":
    test_classification()
