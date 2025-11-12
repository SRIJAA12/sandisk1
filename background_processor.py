"""
AURA Module 1 - Background Video Processing System
Handles video processing in separate threads to allow navigation between modules
"""

import threading
import time
import os
import tempfile
import cv2
from datetime import datetime
from classifier import classify_frame
from video_generator import create_video_from_frame_files
import streamlit as st
import queue
import json

class BackgroundVideoProcessor:
    def __init__(self):
        self.processing_thread = None
        self.is_processing = False
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.stop_event = threading.Event()
        
    def start_processing(self, video_path, thresholds, fps, width, height, total_frames):
        """Start background video processing"""
        if self.is_processing:
            return False, "Processing already in progress"
            
        # Reset queues and events
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.stop_event.clear()
        
        # Create processing thread
        self.processing_thread = threading.Thread(
            target=self._process_video_background,
            args=(video_path, thresholds, fps, width, height, total_frames),
            daemon=True
        )
        
        self.is_processing = True
        self.processing_thread.start()
        
        return True, "Background processing started"
    
    def _process_video_background(self, video_path, thresholds, fps, width, height, total_frames):
        """Background video processing worker"""
        try:
            # Create temporary directories
            tmpdir = tempfile.mkdtemp(prefix="aura_bg_")
            frames_dir = os.path.join(tmpdir, "frames")
            output_path = os.path.join(tmpdir, "aura_optimized.mp4")
            os.makedirs(frames_dir, exist_ok=True)
            
            # Initialize counters
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            saved_frame_paths = []
            last_frame = None
            processed = 0
            start_time = time.time()
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            frame_num = 0
            
            # AGGRESSIVE OPTIMIZATION: Process even fewer frames for background
            skip_frames = max(1, total_frames // 300)  # Process max 300 frames for speed
            
            while not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_num += 1
                
                # Skip frames for speed
                if frame_num % skip_frames != 0:
                    continue
                
                # Classify frame
                category, confidence, detected, metric, latency = classify_frame(
                    frame, last_frame, thresholds
                )
                
                # Update counts
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                counts[category] += 1
                processed += 1
                
                # Save important frames
                if category != "Discard":
                    try:
                        frame_id = len(saved_frame_paths)
                        frame_path = os.path.join(frames_dir, f"frame_{frame_id:06d}.png")
                        cv2.imwrite(frame_path, frame)
                        saved_frame_paths.append(frame_path)
                    except Exception:
                        pass
                
                # Send progress update every 10 frames
                if processed % 10 == 0:
                    progress_data = {
                        'processed': processed,
                        'total_estimated': total_frames // skip_frames,
                        'frame_num': frame_num,
                        'total_frames': total_frames,
                        'counts': counts.copy(),
                        'current_category': category,
                        'current_detected': detected,
                        'current_confidence': confidence
                    }
                    self.progress_queue.put(progress_data)
                
                last_frame = frame.copy()
            
            cap.release()
            elapsed_time = time.time() - start_time
            
            # Create optimized video if we have frames
            video_created = False
            video_message = ""
            
            if len(saved_frame_paths) > 0 and not self.stop_event.is_set():
                try:
                    success, message, frames_written = create_video_from_frame_files(
                        frames_dir, output_path, fps, width, height, crf=23, preset="ultrafast"
                    )
                    video_created = success
                    video_message = message
                except Exception as e:
                    video_message = f"Video creation failed: {str(e)}"
            
            # Calculate final metrics
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
            
            # Send final results
            final_result = {
                'completed': True,
                'counts': counts,
                'processed': processed,
                'elapsed_time': elapsed_time,
                'saved_frames': len(saved_frame_paths),
                'reduction': reduction,
                'lifespan_extension': lifespan_extension,
                'video_created': video_created,
                'video_message': video_message,
                'output_path': output_path if video_created else None,
                'original_path': video_path,
                'tmpdir': tmpdir
            }
            
            self.result_queue.put(final_result)
            
        except Exception as e:
            error_result = {
                'completed': False,
                'error': str(e),
                'processed': processed if 'processed' in locals() else 0
            }
            self.result_queue.put(error_result)
        
        finally:
            self.is_processing = False
    
    def get_progress(self):
        """Get current progress without blocking"""
        progress_updates = []
        try:
            while True:
                progress = self.progress_queue.get_nowait()
                progress_updates.append(progress)
        except queue.Empty:
            pass
        
        return progress_updates
    
    def get_result(self):
        """Get final result if available"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_processing(self):
        """Stop background processing"""
        if self.is_processing:
            self.stop_event.set()
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=5)
        self.is_processing = False
    
    def is_active(self):
        """Check if processing is active"""
        return self.is_processing and (self.processing_thread and self.processing_thread.is_alive())

# Global processor instance
_global_processor = None

def get_processor():
    """Get global processor instance"""
    global _global_processor
    if _global_processor is None:
        _global_processor = BackgroundVideoProcessor()
    return _global_processor

def cleanup_processor():
    """Cleanup global processor"""
    global _global_processor
    if _global_processor:
        _global_processor.stop_processing()
        _global_processor = None

# Session state helpers
def init_background_state():
    """Initialize background processing session state"""
    if 'bg_processor_active' not in st.session_state:
        st.session_state.bg_processor_active = False
    if 'bg_processor_progress' not in st.session_state:
        st.session_state.bg_processor_progress = {}
    if 'bg_processor_result' not in st.session_state:
        st.session_state.bg_processor_result = None
    if 'bg_start_time' not in st.session_state:
        st.session_state.bg_start_time = None

def update_background_state():
    """Update session state with background processor status"""
    processor = get_processor()
    
    # Update active status
    st.session_state.bg_processor_active = processor.is_active()
    
    # Get progress updates
    progress_updates = processor.get_progress()
    if progress_updates:
        st.session_state.bg_processor_progress = progress_updates[-1]  # Keep latest
    
    # Check for completion
    result = processor.get_result()
    if result:
        st.session_state.bg_processor_result = result
        st.session_state.bg_processor_active = False

def start_background_processing(video_path, thresholds, fps, width, height, total_frames):
    """Start background processing and update session state"""
    processor = get_processor()
    success, message = processor.start_processing(video_path, thresholds, fps, width, height, total_frames)
    
    if success:
        st.session_state.bg_processor_active = True
        st.session_state.bg_start_time = datetime.now()
        st.session_state.bg_processor_progress = {}
        st.session_state.bg_processor_result = None
    
    return success, message

def get_background_status():
    """Get current background processing status"""
    update_background_state()
    
    return {
        'active': st.session_state.bg_processor_active,
        'progress': st.session_state.bg_processor_progress,
        'result': st.session_state.bg_processor_result,
        'start_time': st.session_state.bg_start_time
    }

def stop_background_processing():
    """Stop background processing"""
    processor = get_processor()
    processor.stop_processing()
    st.session_state.bg_processor_active = False
