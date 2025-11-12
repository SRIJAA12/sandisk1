"""
Create a simple test video for AURA Module 1 demo
"""

import cv2
import numpy as np
import os

def create_test_video():
    """Create a simple 5-second test video with different scenes"""
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 5  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_demo_video.mp4', fourcc, fps, (width, height))
    
    print(f"Creating test video: {total_frames} frames at {fps} FPS...")
    
    for frame_num in range(total_frames):
        # Create different scenes
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        if frame_num < 30:  # First second - blue sky
            frame[:, :] = [135, 206, 235]  # Sky blue
            cv2.putText(frame, "Empty Sky Scene", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        elif frame_num < 60:  # Second second - person scene
            frame[:, :] = [34, 139, 34]  # Forest green background
            # Draw a simple person (rectangle + circle)
            cv2.rectangle(frame, (250, 200), (350, 400), (255, 255, 255), -1)  # Body
            cv2.circle(frame, (300, 150), 40, (255, 255, 255), -1)  # Head
            cv2.putText(frame, "Person Detected - CRITICAL", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        elif frame_num < 90:  # Third second - car scene
            frame[:, :] = [128, 128, 128]  # Gray road
            # Draw a simple car
            cv2.rectangle(frame, (200, 250), (400, 350), (0, 0, 255), -1)  # Car body
            cv2.circle(frame, (230, 350), 25, (0, 0, 0), -1)  # Wheel 1
            cv2.circle(frame, (370, 350), 25, (0, 0, 0), -1)  # Wheel 2
            cv2.putText(frame, "Vehicle Detected - IMPORTANT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
            
        elif frame_num < 120:  # Fourth second - normal scene
            frame[:, :] = [50, 150, 50]  # Dark green
            cv2.putText(frame, "Normal Scene - SAVE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            # Add some random shapes
            cv2.rectangle(frame, (100, 100), (200, 200), (100, 100, 255), 2)
            cv2.circle(frame, (400, 300), 50, (255, 100, 100), 2)
            
        else:  # Last second - duplicate frames
            frame[:, :] = [135, 206, 235]  # Same sky blue
            cv2.putText(frame, "Duplicate Sky - DISCARD", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_num}", (width-200, height-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)
        
        if frame_num % 30 == 0:
            print(f"Progress: {frame_num}/{total_frames} frames")
    
    out.release()
    print("✅ Test video created: test_demo_video.mp4")
    print("📊 Video contains:")
    print("  - Empty sky scenes (should be DISCARDED)")
    print("  - Person scene (should be CRITICAL)")
    print("  - Vehicle scene (should be IMPORTANT)")
    print("  - Normal scenes (should be SAVED)")
    print("  - Duplicate frames (should be DISCARDED)")

if __name__ == "__main__":
    create_test_video()
