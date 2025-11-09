# modules/video_processor.py
"""
Drone Video Processing Module
Extracts metadata and prepares for sharding
"""

import cv2
import os
from datetime import datetime
from typing import Dict
import hashlib


class DroneVideoProcessor:
    """Process drone footage for secure distributed storage"""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.video_info = {}
        self.metadata = {}
    
    def extract_metadata(self) -> Dict:
        """Extract video metadata"""
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")
        
        self.video_info = {
            'filename': os.path.basename(self.video_path),
            'size_bytes': os.path.getsize(self.video_path),
            'size_mb': round(os.path.getsize(self.video_path) / (1024**2), 2),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration_sec': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
            'processed_at': datetime.now().isoformat()
        }
        
        cap.release()
        return self.video_info
    
    def read_video_bytes(self) -> bytes:
        """Read video file as bytes for encryption"""
        with open(self.video_path, 'rb') as f:
            return f.read()
    
    def get_file_hash(self) -> str:
        """Calculate SHA-256 hash of video file"""
        sha256 = hashlib.sha256()
        with open(self.video_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def extract_frame(self, frame_number: int = 0) -> bytes:
        """Extract a specific frame as thumbnail"""
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert to JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None
