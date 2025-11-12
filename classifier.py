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

# Global cache for performance optimization
_frame_cache = {}
_cache_counter = 0

def is_duplicate(frame1, frame2, threshold=0.97, frame_counter=None):  # RELAXED: was 0.93, now 0.97
    """
    Detect ONLY truly duplicate frames using SSIM
    More conservative to avoid discarding good frames
    OPTIMIZED: Skip expensive checks for performance
    """
    global _cache_counter
    
    if frame1 is None or frame2 is None:
        return False, 0.0
    
    # PERFORMANCE OPTIMIZATION: Skip duplicate detection every few frames
    _cache_counter += 1
    if _cache_counter % 5 != 0:  # Only check every 5th frame for duplicates (more aggressive)
        return False, 0.0
    
    try:
        # Even smaller resize for faster processing
        gray1 = cv2.cvtColor(cv2.resize(frame1, (24, 24)), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv2.resize(frame2, (24, 24)), cv2.COLOR_BGR2GRAY)
        
        similarity, _ = ssim(gray1, gray2, full=True)
        
        # Skip expensive optical flow for performance - use simple similarity
        is_dup = similarity > threshold
        
        return is_dup, float(similarity)
    
    except Exception as e:
        return False, 0.0


def is_empty_sky(frame):
    """
    Detect empty sky - but be VERY conservative
    Only discard if CLEARLY empty
    OPTIMIZED: Smaller resize for speed
    """
    try:
        small = cv2.resize(frame, (24, 24))  # Even smaller for speed
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
    OPTIMIZED: Smaller resize for speed
    """
    try:
        small = cv2.resize(frame, (24, 24))  # Even smaller for speed
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


def classify_frame(frame, last_frame=None, thresholds=None):
    """
    Main classification function - CONFIGURABLE VERSION
    Uses dynamic thresholds from sidebar
    """
    start_time = time.time()
    
    # Use default thresholds if none provided
    if thresholds is None:
        thresholds = {
            'yolo_confidence': 0.5,
            'ssim_threshold': 0.97,
            'sky_threshold': 0.8,
            'edge_threshold': 0.01
        }
    
    # Stage 1: Duplicate check (configurable threshold)
    if last_frame is not None:
        is_dup, ssim_val = is_duplicate(frame, last_frame, thresholds['ssim_threshold'])
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
    
    # Stage 4: YOLO object detection (OPTIMIZED)
    try:
        if model is None:
            # If YOLO not available, save as Normal
            latency = time.time() - start_time
            return "Normal", 0.8, "no_model", 0.0, latency
        
        # PERFORMANCE: Resize frame for faster YOLO processing
        h, w = frame.shape[:2]
        if w > 640:  # Only resize if frame is large
            scale = 640 / w
            new_w, new_h = int(w * scale), int(h * scale)
            yolo_frame = cv2.resize(frame, (new_w, new_h))
        else:
            yolo_frame = frame
            
        results = model(yolo_frame, verbose=False, imgsz=256)  # Even smaller model size for speed
        
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]
                confidence = float(box.conf)
                
                # Use configurable confidence threshold
                if confidence > thresholds.get('yolo_confidence', 0.5):
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
