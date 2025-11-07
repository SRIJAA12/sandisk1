"""
Configuration for AURA Module 1
"""

# Classification categories
CATEGORIES = ["Critical", "Important", "Normal", "Discard"]

# Colors for UI
COLORS = {
    "Critical": "#E31E24",
    "Important": "#FF6B6B",
    "Normal": "#4ECDC4",
    "Discard": "#95A5A6"
}

# YOLO classes mapping
CRITICAL_CLASSES = ['person', 'dog', 'cat', 'horse', 'cow', 'elephant', 'bear', 'zebra']
IMPORTANT_CLASSES = ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'boat', 'train', 'airplane']

# Thresholds
SSIM_THRESHOLD = 0.93
BLUE_RATIO_THRESHOLD = 0.6
EDGE_RATIO_THRESHOLD = 0.02
