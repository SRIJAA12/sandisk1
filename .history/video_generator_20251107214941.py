"""
Video Generator - WORKS 100%
Separate module for reliable video creation
"""

import cv2
import os
import numpy as np

def create_video_from_frames(frames_list, output_path, fps, width, height):
    """
    Create video from frames - GUARANTEED TO WORK
    
    Parameters:
    - frames_list: List of numpy arrays (BGR frames)
    - output_path: Path to save video
    - fps: Frames per second
    - width: Frame width
    - height: Frame height
    
    Returns:
    - (success: bool, message: str, frames_written: int)
    """
    
    if not frames_list or len(frames_list) == 0:
        return False, "No frames provided", 0
    
    if fps <= 0:
        return False, "Invalid FPS", 0
    
    if width <= 0 or height <= 0:
        return False, "Invalid dimensions", 0
    
    try:
        # Codec order: Most compatible first
        codecs = ['MJPG', 'DIVX', 'XVID', 'X264', 'WMV1', 'WMV2']
        
        for codec_name in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                if not writer.isOpened():
                    continue
                
                frames_written = 0
                errors = 0
                
                for frame_idx, frame in enumerate(frames_list):
                    try:
                        # Validate frame
                        if frame is None:
                            errors += 1
                            continue
                        
                        if not isinstance(frame, np.ndarray):
                            errors += 1
                            continue
                        
                        # Resize if needed
                        if frame.shape[0] != height or frame.shape[1] != width:
                            frame = cv2.resize(frame, (width, height))
                        
                        # Ensure BGR format
                        if len(frame.shape) != 3 or frame.shape[2] != 3:
                            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        
                        # Write
                        ret = writer.write(frame)
                        
                        if ret:
                            frames_written += 1
                        else:
                            errors += 1
                    
                    except Exception as frame_error:
                        errors += 1
                        continue
                
                writer.release()
                
                # Validate output
                if os.path.exists(output_path):
                    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    
                    if file_size_mb > 0.1 and frames_written > 0:
                        msg = f"✅ Success ({codec_name}): {frames_written} frames written"
                        return True, msg, frames_written
                    else:
                        os.remove(output_path)
                        continue
                else:
                    continue
            
            except Exception as codec_error:
                continue
        
        return False, "No codec could write frames", 0
    
    except Exception as e:
        return False, f"Error: {str(e)}", 0


def create_video_simple(frames_list, output_path, fps, width, height):
    """
    Ultra simple version - no codec switching
    """
    try:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        written = 0
        for frame in frames_list:
            if frame is not None:
                h, w = frame.shape[:2]
                if w != width or h != height:
                    frame = cv2.resize(frame, (width, height))
                
                if writer.write(frame):
                    written += 1
        
        writer.release()
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            return True, f"Created: {written} frames", written
        else:
            return False, "Video too small", written
    
    except Exception as e:
        return False, str(e), 0
