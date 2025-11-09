"""
Test script for AURA Module 1 video generation
Creates test frames and verifies video creation works
"""

import cv2
import numpy as np
import os
import tempfile
from video_generator import create_video_from_frames

def create_test_frames(num_frames=30, width=640, height=480):
    """Create test frames with different colors and patterns"""
    frames = []
    
    for i in range(num_frames):
        # Create a frame with changing colors
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create gradient background
        color_intensity = int((i / num_frames) * 255)
        frame[:, :, 0] = color_intensity  # Blue channel
        frame[:, :, 1] = 255 - color_intensity  # Green channel
        frame[:, :, 2] = (color_intensity + 128) % 255  # Red channel
        
        # Add some text
        text = f"Frame {i+1}/{num_frames}"
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add a moving circle
        center_x = int((i / num_frames) * width)
        center_y = height // 2
        cv2.circle(frame, (center_x, center_y), 30, (255, 255, 255), -1)
        
        frames.append(frame)
    
    return frames

def test_video_generation():
    """Test the video generation functionality"""
    print("🧪 Testing AURA Module 1 Video Generation...")
    
    # Create test frames
    print("📝 Creating test frames...")
    frames = create_test_frames(30, 640, 480)
    print(f"✅ Created {len(frames)} test frames")
    
    # Create temporary output path
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "test_video.mp4")
    
    # Test video creation
    print("🎬 Testing video creation...")
    success, message, frames_written = create_video_from_frames(
        frames, output_path, fps=30, width=640, height=480, crf=18, preset="medium"
    )
    
    print(f"📊 Result: {message}")
    
    if success:
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"✅ Video created successfully!")
        print(f"📁 File: {output_path}")
        print(f"📏 Size: {file_size:.2f} MB")
        print(f"🎞️ Frames written: {frames_written}")
        
        # Test if video can be read back
        cap = cv2.VideoCapture(output_path)
        if cap.isOpened():
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            print(f"🔍 Video verification:")
            print(f"   - Frames: {frame_count}")
            print(f"   - FPS: {fps}")
            print(f"   - Resolution: {width}x{height}")
            
            if frame_count > 0:
                print("✅ Video is readable and contains frames!")
                return True
            else:
                print("❌ Video is empty!")
                return False
        else:
            print("❌ Video cannot be opened!")
            return False
    else:
        print(f"❌ Video creation failed: {message}")
        return False

if __name__ == "__main__":
    success = test_video_generation()
    if success:
        print("\n🎉 All tests passed! Video generation is working correctly.")
    else:
        print("\n💥 Tests failed! Check the error messages above.")
