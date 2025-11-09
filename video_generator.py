"""
AURA Module 1 - Enhanced Video Generator
Robust video creation with multiple fallback methods and proper frame validation
Returns: (success: bool, message: str, frames_written: int)
"""

import subprocess
import os
import sys
import tempfile
import shutil

def _safe_int_fps(fps):
    """Ensure FPS is a valid integer"""
    try:
        iv = int(round(float(fps)))
        return max(1, min(iv, 60))  # Cap at 60fps
    except:
        return 30

def _validate_frame(frame, target_width, target_height):
    """Validate and prepare frame for video encoding"""
    try:
        import cv2
        import numpy as np
        
        if frame is None:
            return None
            
        # Check if frame is valid numpy array
        if not isinstance(frame, np.ndarray):
            return None
            
        # Check dimensions
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return None
            
        h, w = frame.shape[:2]
        
        # Resize if needed
        if (w, h) != (target_width, target_height):
            frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
            
        # Ensure frame is in proper format (BGR for OpenCV)
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            
        return frame
        
    except Exception:
        return None

def create_video_with_ffmpeg(frames_list, output_path, fps, width, height, crf=18, preset="medium"):
    """
    Create MP4 (H.264) using FFmpeg with improved error handling
    """
    if not frames_list or len(frames_list) == 0:
        return False, "No frames provided", 0

    if fps <= 0 or width <= 0 or height <= 0:
        return False, "Invalid video parameters", 0

    try:
        import cv2
    except Exception as e:
        return False, f"OpenCV not available: {e}", 0

    # Create temporary directory for frames
    temp_dir = tempfile.mkdtemp(prefix="aura_frames_")
    frame_pattern = os.path.join(temp_dir, "frame_%06d.png")
    
    written = 0
    try:
        # Write frames as numbered PNGs with validation
        for i, frame in enumerate(frames_list):
            validated_frame = _validate_frame(frame, width, height)
            if validated_frame is not None:
                frame_path = frame_pattern % i
                if cv2.imwrite(frame_path, validated_frame):
                    written += 1
                else:
                    print(f"Warning: Failed to write frame {i}")

        if written == 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, "No valid frames could be written", 0

        # Build FFmpeg command with better compatibility
        safe_fps = _safe_int_fps(fps)
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # overwrite output
            "-framerate", str(safe_fps),
            "-i", frame_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",  # Ensures compatibility
            "-crf", str(crf),
            "-preset", preset,
            "-movflags", "+faststart",  # Optimize for web playback
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            output_path
        ]

        # Run FFmpeg with timeout
        result = subprocess.run(
            ffmpeg_cmd, 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )

        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

        if result.returncode != 0:
            stderr = result.stderr if result.stderr else result.stdout
            return False, f"FFmpeg failed: {stderr.strip()[:200]}", 0

        # Verify output file
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return False, "Output file not created or too small", 0

        file_size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0)
        return True, f"✅ FFmpeg MP4 Created: {written} frames | {file_size_mb:.2f} MB", written

    except subprocess.TimeoutExpired:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False, "FFmpeg timeout - video too long or system overloaded", 0
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False, f"FFmpeg error: {str(e)}", 0

def create_video_with_opencv(frames_list, output_path, fps, width, height):
    """
    Enhanced OpenCV VideoWriter with multiple codec fallbacks
    """
    try:
        import cv2
    except Exception as e:
        return False, f"OpenCV missing: {e}", 0

    # Try multiple codecs in order of preference
    codecs_to_try = [
        ('mp4v', 'MP4V'),  # Most compatible
        ('XVID', 'XVID'),  # Good fallback
        ('MJPG', 'MJPG'),  # Always works
    ]
    
    for fourcc_str, codec_name in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
            writer = cv2.VideoWriter(output_path, fourcc, float(fps), (int(width), int(height)))
            
            if not writer.isOpened():
                continue
                
            written = 0
            for frame in frames_list:
                validated_frame = _validate_frame(frame, width, height)
                if validated_frame is not None:
                    success = writer.write(validated_frame)
                    if success:
                        written += 1

            writer.release()

            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000 and written > 0:
                file_size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0)
                return True, f"✅ OpenCV {codec_name} Created: {written} frames | {file_size_mb:.2f} MB", written
            else:
                # Try next codec
                if os.path.exists(output_path):
                    os.remove(output_path)
                continue
                
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            continue

    return False, "All OpenCV codecs failed", 0

def create_video_from_frames(frames_list, output_path, fps, width, height, crf=18, preset="ultrafast"):
    """
    OPTIMIZED for DEMO SPEED - Enhanced video creation with robust fallback chain
    """
    if not frames_list or len(frames_list) == 0:
        return False, "No frames provided", 0
        
    # Ensure output is MP4
    output_path = os.path.splitext(output_path)[0] + ".mp4"
    
    # Validate parameters
    fps = max(1, min(fps, 60))
    width = max(64, int(width))
    height = max(64, int(height))
    
    # Make dimensions even (required for some codecs)
    width = width + (width % 2)
    height = height + (height % 2)
    
    print(f"Creating video: {len(frames_list)} frames, {fps}fps, {width}x{height}")
    
    # DEMO OPTIMIZATION: Try OpenCV first (faster than FFmpeg for small videos)
    try:
        success, message, written = create_video_with_opencv(
            frames_list, output_path, fps, width, height
        )
        if success:
            return True, f"{message} (Fast OpenCV)", written
        opencv_error = message
    except Exception as e:
        opencv_error = f"OpenCV exception: {str(e)}"
    
    print(f"OpenCV failed: {opencv_error}")
    
    # Method 2: Try FFmpeg with ultrafast preset
    try:
        success, message, written = create_video_with_ffmpeg(
            frames_list, output_path, fps, width, height, crf=23, preset="ultrafast"  # Faster settings
        )
        if success:
            return True, message, written
        ffmpeg_error = message
    except Exception as e:
        ffmpeg_error = f"FFmpeg exception: {str(e)}"
    
    print(f"FFmpeg failed: {ffmpeg_error}")
    
    # Method 3: Create image sequence as fallback
    try:
        import cv2
        frames_dir = os.path.splitext(output_path)[0] + "_frames"
        os.makedirs(frames_dir, exist_ok=True)
        
        written = 0
        for i, frame in enumerate(frames_list):
            validated_frame = _validate_frame(frame, width, height)
            if validated_frame is not None:
                frame_path = os.path.join(frames_dir, f"frame_{i:06d}.jpg")
                if cv2.imwrite(frame_path, validated_frame):
                    written += 1
        
        if written > 0:
            return False, f"Video creation failed, but {written} frames saved to {frames_dir}", written
            
    except Exception as e:
        pass
    
    return False, f"All methods failed - OpenCV: {opencv_error} | FFmpeg: {ffmpeg_error}", 0
