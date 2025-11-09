"""
Create a demo video for AURA Module 1 - Super fast demo generation
This creates a sample optimized video that can be used for instant demos
"""

import cv2
import numpy as np
import os
from video_generator import create_video_from_frames

def create_demo_optimized_video():
    """Create a demo optimized video quickly"""
    print("🎬 Creating demo optimized video...")
    
    # Create demo frames that look like processed drone footage
    frames = []
    width, height = 640, 480
    
    # Create 60 frames (2 seconds at 30fps)
    for i in range(60):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create a landscape-like background
        # Sky gradient
        for y in range(height//3):
            intensity = int(200 - (y * 50 / (height//3)))
            frame[y, :] = [intensity, intensity-20, 255]  # Blue sky
        
        # Ground
        for y in range(height//3, height):
            intensity = int(80 + (y-height//3) * 40 / (height*2//3))
            frame[y, :] = [intensity//3, intensity, intensity//2]  # Green ground
        
        # Add some "objects" that would be detected
        if i % 15 == 0:  # Every 15 frames, add a "vehicle"
            cv2.rectangle(frame, (100 + i*5, height//2), (150 + i*5, height//2 + 30), (0, 0, 255), -1)
            cv2.putText(frame, "VEHICLE", (100 + i*5, height//2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if i % 20 == 0:  # Every 20 frames, add a "person"
            cv2.circle(frame, (200 + i*3, height//2 + 20), 15, (255, 0, 0), -1)
            cv2.putText(frame, "PERSON", (180 + i*3, height//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Add frame number
        cv2.putText(frame, f"AURA Frame {i+1}/60", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "AI Optimized", (10, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        frames.append(frame)
    
    # Create the demo video
    output_path = "demo_optimized.mp4"
    success, message, written = create_video_from_frames(
        frames, output_path, fps=30, width=width, height=height, crf=18, preset="ultrafast"
    )
    
    if success:
        print(f"✅ Demo video created: {output_path}")
        print(f"📊 {message}")
        return output_path
    else:
        print(f"❌ Failed to create demo video: {message}")
        return None

if __name__ == "__main__":
    demo_path = create_demo_optimized_video()
    if demo_path:
        print(f"🎉 Demo video ready at: {demo_path}")
        print("This can be used for instant demo presentations!")
    else:
        print("💥 Demo video creation failed!")
