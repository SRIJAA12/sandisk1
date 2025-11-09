"""
Video Generator using FFmpeg (forced MP4 H.264, CRF 18) with OpenCV fallback
Returns: (success: bool, message: str, frames_written: int)
"""

import subprocess
import os
import sys
import tempfile

def _safe_int_fps(fps):
    try:
        iv = int(round(float(fps)))
        return max(1, iv)
    except:
        return 30

def create_video_with_ffmpeg(frames_list, output_path, fps, width, height, crf=18, preset="medium"):
    """
    Create MP4 (H.264) using ffmpeg from a list of numpy frames.
    - frames_list: list of numpy arrays (BGR or RGB) — cv2.imwrite will handle them.
    - output_path: full path to final .mp4
    - fps: frames per second (float)
    - width,height: target resolution (int)
    - crf: ffmpeg CRF value (lower = better quality). default 18.
    - preset: ffmpeg preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, etc.)
    Returns: (success, message, frames_written)
    """

    if not frames_list or len(frames_list) == 0:
        return False, "No frames provided", 0

    if fps <= 0 or width <= 0 or height <= 0:
        return False, "Invalid video parameters", 0

    # Prepare temp directory for frames
    tmp_dir = os.path.dirname(os.path.abspath(output_path))
    frame_pattern = os.path.join(tmp_dir, "aura_frame_%06d.png")

    written = 0
    try:
        import cv2
    except Exception as e:
        return False, f"OpenCV not available: {e}", 0

    try:
        # Write frames as numbered PNGs
        for i, frame in enumerate(frames_list):
            try:
                if frame is None:
                    continue
                # Ensure correct dimensions
                h, w = frame.shape[:2]
                if (w, h) != (width, height):
                    frame = cv2.resize(frame, (width, height))
                # cv2.imwrite expects BGR; if frame has 3 channels it's fine.
                cv2.imwrite(frame_pattern % i, frame)
                written += 1
            except Exception:
                # skip frames that fail
                continue

        if written == 0:
            return False, "No frames could be written to disk", 0

        # Build ffmpeg command
        # -framerate <fps> -i frame_%06d.png -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p output.mp4
        safe_fps = _safe_int_fps(fps)
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-framerate", str(safe_fps),
            "-i", os.path.join(tmp_dir, "aura_frame_%06d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", str(crf),
            "-preset", preset,
            "-movflags", "+faststart",
            output_path
        ]

        # Run ffmpeg
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0 or not os.path.exists(output_path):
            stderr = result.stderr if result.stderr else result.stdout
            # Cleanup temp frames
            idx = 0
            while os.path.exists(frame_pattern % idx):
                try:
                    os.remove(frame_pattern % idx)
                except:
                    pass
                idx += 1
            return False, f"FFmpeg failed: {stderr.strip()[:200]}", 0

        # success -> compute file size, cleanup frames
        file_size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0)

        idx = 0
        while os.path.exists(frame_pattern % idx):
            try:
                os.remove(frame_pattern % idx)
            except:
                pass
            idx += 1

        return True, f"✅ MP4 Created (H.264): {written} frames | {file_size_mb:.2f} MB", written

    except Exception as e:
        # attempt to cleanup
        idx = 0
        try:
            while os.path.exists(frame_pattern % idx):
                os.remove(frame_pattern % idx)
                idx += 1
        except:
            pass
        return False, f"FFmpeg-stage error: {str(e)}", 0


def create_video_with_opencv(frames_list, output_path, fps, width, height):
    """
    Fallback: use OpenCV VideoWriter to make an MP4.
    Returns (success, message, frames_written)
    """
    try:
        import cv2
    except Exception as e:
        return False, f"OpenCV missing: {e}", 0

    try:
        # Use mp4v codec and .mp4 extension
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, float(fps), (int(width), int(height)))
        written = 0

        for frame in frames_list:
            if frame is None:
                continue
            h, w = frame.shape[:2]
            if (w, h) != (width, height):
                try:
                    frame = cv2.resize(frame, (int(width), int(height)))
                except:
                    continue
            writer.write(frame)
            written += 1

        writer.release()

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            file_size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0)
            return True, f"✅ OpenCV MP4 Created: {written} frames | {file_size_mb:.2f} MB", written
        else:
            return False, "OpenCV output too small or missing", written

    except Exception as e:
        return False, f"OpenCV error: {e}", 0


def create_video_from_frames(frames_list, output_path, fps, width, height, crf=18, preset="medium"):
    """
    Primary wrapper — try ffmpeg first (mp4/h.264 CRF), fallback to OpenCV.
    Returns (success, message, frames_written)
    """
    # Force mp4 extension
    out_ext = os.path.splitext(output_path)[1].lower()
    if out_ext != ".mp4":
        output_path = os.path.splitext(output_path)[0] + ".mp4"

    # Try ffmpeg
    try:
        success, message, written = create_video_with_ffmpeg(frames_list, output_path, fps, width, height, crf=crf, preset=preset)
        if success:
            return True, message, written
        # else fallthrough to try OpenCV while preserving message for debug
        ffmpeg_error = message
    except Exception as e:
        ffmpeg_error = f"FFmpeg attempt exception: {e}"

    # Fallback to OpenCV
    try:
        success2, message2, written2 = create_video_with_opencv(frames_list, output_path, fps, width, height)
        if success2:
            return True, message2, written2
        else:
            # Return combined error
            return False, f"FFmpeg failed -> {ffmpeg_error} | OpenCV failed -> {message2}", written2
    except Exception as e2:
        return False, f"Both methods failed: FFmpeg: {ffmpeg_error} | OpenCV exception: {e2}", 0
