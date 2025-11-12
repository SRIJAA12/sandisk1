"""
AURA MODULE 1 - INTELLIGENT DATA MANAGER
FINAL CLEANED VERSION WITH MP4 VIDEO GENERATION (CRF18, AUTO-LOOP PREVIEW)
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import tempfile
import os
import time
from datetime import datetime
from classifier import classify_frame
from ui_components import apply_custom_css, show_hero, get_category_badge, show_enhanced_video_comparison
from video_generator import create_video_from_frames, create_video_from_frame_files
from config import COLORS
from background_processor import (
    init_background_state, get_background_status, start_background_processing,
    stop_background_processing, update_background_state
)

# PAGE CONFIG
st.set_page_config(
    page_title="AURA Module 1",
    layout="wide"
)

apply_custom_css()

# BACK TO HOMEPAGE BUTTON
st.markdown("""
<div style="margin-bottom: 20px;">
    <a href="/" target="_self" style="text-decoration: none;">
        <button style="
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(78, 205, 196, 0.3);
            color: #4ECDC4;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        ">← Back to Homepage</button>
    </a>
</div>
""", unsafe_allow_html=True)

show_hero()

# ============================================================================ #
# SIDEBAR - THRESHOLD CONTROLS
# ============================================================================ #
st.sidebar.markdown("## 🎛️ AURA Configuration")
st.sidebar.markdown("### Classification Thresholds")

# YOLO Confidence Threshold
yolo_threshold = st.sidebar.slider(
    "🎯 YOLO Confidence Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.5,
    step=0.05,
    help="Minimum confidence for object detection"
)

# SSIM Threshold for Duplicates
ssim_threshold = st.sidebar.slider(
    "🔍 Duplicate Detection (SSIM)",
    min_value=0.85,
    max_value=0.99,
    value=0.97,
    step=0.01,
    help="Similarity threshold for duplicate frames"
)

# Sky Detection Threshold
sky_threshold = st.sidebar.slider(
    "🌌 Empty Sky Threshold",
    min_value=0.6,
    max_value=0.9,
    value=0.8,
    step=0.05,
    help="Blue ratio threshold for sky detection"
)

# Edge Detection Threshold
edge_threshold = st.sidebar.slider(
    "📐 Edge Detection Threshold",
    min_value=0.005,
    max_value=0.05,
    value=0.01,
    step=0.005,
    help="Edge ratio threshold for content detection"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Current Settings")
st.sidebar.info(f"""
**YOLO Confidence:** {yolo_threshold:.2f}
**SSIM Threshold:** {ssim_threshold:.2f}
**Sky Threshold:** {sky_threshold:.2f}
**Edge Threshold:** {edge_threshold:.3f}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Category Mapping")
st.sidebar.markdown("""
- **🔴 Critical:** People, Animals
- **🟡 Important:** Vehicles, Infrastructure  
- **🟢 Normal:** Landscape, Objects
- **⚫ Discard:** Duplicates, Empty Sky
""")

# Store thresholds in session state for use in classification
if 'thresholds' not in st.session_state:
    st.session_state.thresholds = {}

# Initialize background processing state
init_background_state()

# Auto-refresh every 2 seconds if processing is active
if st.session_state.get('bg_processor_active', False):
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
    st.rerun()

st.session_state.thresholds = {
    'yolo_confidence': yolo_threshold,
    'ssim_threshold': ssim_threshold,
    'sky_threshold': sky_threshold,
    'edge_threshold': edge_threshold
}

tab1, tab2 = st.tabs(["📹 VIDEO ANALYSIS", "🖼️ IMAGE ANALYSIS"])

# ============================================================================ #
# TAB 1: VIDEO ANALYSIS
# ============================================================================ #
with tab1:
    st.markdown(
        '<div class="glass-card"><h3>📹 Upload Drone Video</h3><p>Upload your drone footage for intelligent analysis</p></div>',
        unsafe_allow_html=True
    )

    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")

    if video_file:
        # Temporary directories
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "aura_optimized.mp4")
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        # Save uploaded video
        with open(input_path, "wb") as f:
            f.write(video_file.read())

        # Extract video metadata
        cap = cv2.VideoCapture(input_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()

        info_cols = st.columns(4)
        info_cols[0].metric("Total Frames", f"{total_frames}")
        info_cols[1].metric("FPS", f"{fps:.1f}")
        info_cols[2].metric("Duration", f"{duration:.1f}s")
        info_cols[3].metric("Resolution", f"{width}×{height}")

        # Background processing status and controls
        bg_status = get_background_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if not bg_status['active']:
                process_btn = st.button("🎬 START BACKGROUND PROCESSING", type="primary", use_container_width=True)
            else:
                process_btn = False
                st.button("🔄 Processing...", disabled=True, use_container_width=True)
        
        with col2:
            if bg_status['active']:
                if st.button("⏹️ STOP PROCESSING", type="secondary", use_container_width=True):
                    stop_background_processing()
                    st.rerun()
            else:
                st.button("⏹️ Stop", disabled=True, use_container_width=True)
        
        with col3:
            if bg_status['active']:
                st.success("✅ Processing in background...")
            elif bg_status['result']:
                st.info("✅ Processing completed!")
            else:
                st.info("⏸️ Ready to process")
        
        # Start background processing
        if process_btn:
            success, message = start_background_processing(
                input_path, st.session_state.thresholds, fps, width, height, total_frames
            )
            if success:
                st.success("🚀 Background processing started! You can now navigate to other modules.")
                st.rerun()
            else:
                st.error(f"Failed to start processing: {message}")
        
        # Show current processing status
        if bg_status['active'] or bg_status['progress']:
            st.markdown("---")
            st.markdown("### 🔄 Processing Status")
            
            if bg_status['progress']:
                progress = bg_status['progress']
                
                # Progress bar
                progress_pct = progress['processed'] / max(progress['total_estimated'], 1)
                st.progress(progress_pct, text=f"Processed {progress['processed']}/{progress['total_estimated']} frames")
                
                # Current frame info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class='glass-card'>
                        <h4>📊 Current Frame</h4>
                        <p><strong>Frame:</strong> {progress['frame_num']}/{progress['total_frames']}</p>
                        <p><strong>Category:</strong> {get_category_badge(progress['current_category'])}</p>
                        <p><strong>Detected:</strong> {progress['current_detected']}</p>
                        <p><strong>Confidence:</strong> {progress['current_confidence']:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    counts = progress['counts']
                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = (1 - saved / max(progress['processed'], 1)) * 100
                    
                    st.markdown(f"""
                    <div class='glass-card'>
                        <h4>📈 Live Metrics</h4>
                        <p><strong>Processed:</strong> {progress['processed']}</p>
                        <p><strong>Saved:</strong> {saved}</p>
                        <p><strong>Duplicates:</strong> {counts['Duplicates']}</p>
                        <p><strong>Reduction:</strong> {reduction:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show results if processing is complete
        if bg_status['result']:
            result = bg_status['result']
            
            if result.get('completed', False):
                st.markdown("---")
                st.markdown("### ✅ Processing Complete!")
                
                counts = result['counts']
                processed = result['processed']
                elapsed_time = result['elapsed_time']
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = result['reduction']
                lifespan_extension = result['lifespan_extension']
                
                # Results metrics
                fm = st.columns(5)
                fm[0].metric("Total Processed", processed, f"{processed/elapsed_time:.1f} fps")
                fm[1].metric("Frames Saved", saved, f"{saved/processed*100:.1f}%")
                fm[2].metric("Duplicates", counts["Duplicates"], f"{counts['Duplicates']/processed*100:.1f}%")
                fm[3].metric("Write Reduction", f"{reduction:.1f}%", "Lower is better")
                fm[4].metric("Lifespan Extension", f"{lifespan_extension:.1f}x", "Higher is better")
                
                # Video results
                if result['video_created']:
                    st.markdown("---")
                    st.markdown("### 🎬 Video Results")
                    st.success(result['video_message'])
                    
                    # Enhanced video comparison
                    try:
                        original_size_mb = os.path.getsize(result['original_path']) / (1024.0 * 1024.0)
                        optimized_size_mb = os.path.getsize(result['output_path']) / (1024.0 * 1024.0)
                        
                        show_enhanced_video_comparison(
                            result['original_path'], result['output_path'],
                            original_size_mb, optimized_size_mb,
                            total_frames, saved
                        )
                    except Exception as e:
                        # Fallback simple comparison
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### 📹 Original Video")
                            st.video(result['original_path'])
                        with col2:
                            st.markdown("### 🧠 AURA Optimized")
                            if os.path.exists(result['output_path']):
                                st.video(result['output_path'])
                            else:
                                st.error("❌ Optimized video not available")
                
                # Detailed analysis
                st.markdown("---")
                st.markdown("### 📊 Performance Analysis")
                
                analysis_cols = st.columns(3)
                
                with analysis_cols[0]:
                    st.markdown("""
                    <div class='glass-card'>
                        <h4>🎯 Frame Analysis</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Total Processed", processed, f"{processed/elapsed_time:.1f} fps")
                    st.metric("Frames Saved", saved, f"{(saved/processed)*100:.1f}%")
                    st.metric("Duplicates Removed", counts["Duplicates"], f"{(counts['Duplicates']/processed)*100:.1f}%")
                
                with analysis_cols[1]:
                    st.markdown("""
                    <div class='glass-card'>
                        <h4>💾 Storage Impact</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Write Reduction", f"{reduction:.1f}%", "Target: 60-70%")
                    st.metric("Lifespan Extension", f"{lifespan_extension:.1f}x", "Target: 3-3.5x")
                    storage_saved_gb = (processed - saved) * 3.5 / 1000
                    st.metric("Storage Saved", f"{storage_saved_gb:.2f} GB")
                
                with analysis_cols[2]:
                    st.markdown("""
                    <div class='glass-card'>
                        <h4>🏷️ Classification</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Critical Frames", counts["Critical"], "🔴 Full quality")
                    st.metric("Important Frames", counts["Important"], "🟡 70% quality") 
                    st.metric("Normal Frames", counts["Normal"], "🟢 50% quality")
                    
                # Clear results button
                if st.button("🗑️ Clear Results", type="secondary"):
                    st.session_state.bg_processor_result = None
                    st.rerun()
            
            elif 'error' in result:
                st.error(f"❌ Processing failed: {result['error']}")
                if st.button("🗑️ Clear Error", type="secondary"):
                    st.session_state.bg_processor_result = None
                    st.rerun()

# ============================================================================ #
# TAB 2: IMAGE ANALYSIS
# ============================================================================ #
with tab2:
    st.markdown(
        '<div class="glass-card"><h3>🖼️ Single Image Analysis</h3><p>Upload a single frame for detailed classification</p></div>',
        unsafe_allow_html=True
    )

    image_file = st.file_uploader("Select image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if image_file:
        arr = np.frombuffer(image_file.read(), np.uint8)
        img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            st.error("❌ Could not load image")
        else:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            if st.button("🔍 ANALYZE IMAGE", type="primary", use_container_width=True, key="analyze_image"):
                c1, c2 = st.columns(2)
                with c1:
                    st.image(img_rgb, caption="Input Frame", use_container_width=True)
                with c2:
                    category, confidence, detected, metric, latency = classify_frame(img_bgr, None, st.session_state.thresholds)
                    badge = get_category_badge(category)
                    st.markdown(
                        f"<div class='glass-card'><h4>Result</h4><p>{badge}</p>"
                        f"<p>Object: {detected}</p><p>Confidence: {confidence:.1%}</p>"
                        f"<p>Latency: {latency*1000:.1f}ms</p></div>",
                        unsafe_allow_html=True,
                    )

# ============================================================================ #
# FOOTER
# ============================================================================ #
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.5);font-size:0.85rem;margin-top:40px;">
<p><b>🧠 AURA Module 1 | Intelligent Data Manager</b></p>
<p>Advanced Storage Optimization for Edge Devices</p>
<p>© 2025 Team AURA | PSG Institute of Technology | Cerebrum 2025 Finals</p>
<p>Partner: SanDisk</p>
<p style="font-size:0.75rem;font-style:italic;">"Storage that Learns, Adapts, and Extends"</p>
</div>
""", unsafe_allow_html=True)
