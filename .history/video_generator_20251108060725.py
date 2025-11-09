"""
Video Generator with Real-Time Progress Display
Fast video creation with visual feedback
"""

import cv2
import os
import numpy as np
import streamlit as st

def create_video_with_progress(frames_list, output_path, fps, width, height):
    """
    Create video with real-time progress display
    Shows which frames are being written
    
    Returns: (success, message, frames_written)
    """
    
    if not frames_list or len(frames_list) == 0:
        return False, "No frames provided", 0
    
    if fps <= 0:
        return False, "Invalid FPS", 0
    
    try:
        total_frames = len(frames_list)
        
        # Progress display
        progress_container = st.empty()
        status_container = st.empty()
        
        # Try codecs
        codecs_to_try = [
            ('MJPG', 'MJPEG'),
            ('mp4v', 'MP4V'),
            ('XVID', 'XVID'),
            ('DIVX', 'DIVX')
        ]
        
        for codec_code, codec_name in codecs_to_try:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec_code)
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                if not writer.isOpened():
                    continue
                
                frames_written = 0
                
                # Write frames with progress
                for i, frame in enumerate(frames_list):
                    try:
                        # Update progress
                        progress_pct = (i + 1) / total_frames
                        progress_container.progress(progress_pct, text=f"Writing frame {i+1}/{total_frames}")
                        
                        # Show current frame being written (every 10th frame)
                        if i % 10 == 0:
                            status_container.markdown(f"""
                            <div style="padding: 10px; background: rgba(78, 205, 196, 0.1); border-radius: 10px; margin: 5px 0;">
                                <p style="color: white; margin: 0;">
                                    ✍️ Writing: Frame {i+1} | Codec: {codec_name} | Progress: {progress_pct*100:.1f}%
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Resize if needed
                        if frame.shape[0] != height or frame.shape[1] != width:
                            frame = cv2.resize(frame, (width, height))
                        
                        # Write frame
                        if writer.write(frame):
                            frames_written += 1
                    
                    except Exception as frame_err:
                        continue
                
                writer.release()
                
                # Verify output
                if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
                    file_size_mb = os.path.getsize(output_path) / (1024*1024)
                    
                    progress_container.empty()
                    status_container.empty()
                    
                    message = f"✅ Success ({codec_name}): {frames_written} frames | {file_size_mb:.2f} MB"
                    return True, message, frames_written
                else:
                    if os.path.exists(output_path):
                        os.remove(output_path)
            
            except Exception as codec_err:
                continue
        
        progress_container.empty()
        status_container.empty()
        return False, "All codecs failed", 0
    
    except Exception as e:
        return False, f"Error: {str(e)}", 0


def create_video_from_frames(frames_list, output_path, fps, width, height):
    """
    Main video creation function
    Wrapper for progress display version
    """
    return create_video_with_progress(frames_list, output_path, fps, width, height)
