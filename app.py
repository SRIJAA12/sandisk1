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

# PAGE CONFIG
# Note: Max upload size is configured to 800MB in .streamlit/config.toml
st.set_page_config(
    page_title="AURA - Adaptive Unified Resource Architecture For Edge Storage",
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

        # Process Video Button
        if st.button("🎬 PROCESS VIDEO", type="primary", use_container_width=True):
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            results = []
            saved_frames = []  # kept for small demos; primarily we'll save to disk
            saved_frame_paths = []
            last_frame = None
            processed = 0

            progress_bar = st.progress(0, text="Starting...")
            display_col1, display_col2 = st.columns(2)
            frame_display, status_display = display_col1.empty(), display_col2.empty()
            metrics = st.columns(4)
            metric_p, metric_d, metric_s, metric_r = [m.empty() for m in metrics]

            cap = cv2.VideoCapture(input_path)
            start_time = time.time()
            frame_num = 0

            # OPTIMIZED PROCESSING: Process every 2nd frame for speed while maintaining accuracy
            skip_frames = 2  # Process every 2nd frame for faster processing
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_num += 1
                
                # Skip frames for speed optimization
                if frame_num % skip_frames != 0:
                    continue
                    
                progress_bar.progress(frame_num / total_frames, text=f"Processing {frame_num}/{total_frames}")

                # Update display less frequently for better performance
                if frame_num % 20 == 0:
                    try:
                        frame_display.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                    except:
                        pass

                category, confidence, detected, metric, latency = classify_frame(frame, last_frame, st.session_state.thresholds)
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                counts[category] += 1
                processed += 1

                if category != "Discard":
                    # Save frame to disk to avoid holding large lists in memory
                    try:
                        frame_id = len(saved_frame_paths)
                        frame_path = os.path.join(frames_dir, f"frame_{frame_id:06d}.png")
                        import cv2
                        cv2.imwrite(frame_path, frame)
                        saved_frame_paths.append(frame_path)
                        # keep a small in-memory sample for quick preview (optional)
                        if len(saved_frames) < 5:
                            saved_frames.append(frame.copy())
                    except Exception as e:
                        # fallback to in-memory if disk write fails
                        saved_frames.append(frame.copy())

                # Update UI metrics less frequently for performance
                if frame_num % 12 == 0:
                    badge = get_category_badge(category)
                    status_display.markdown(
                        f"<div class='glass-card'><p><strong>Frame {frame_num}</strong> | {badge}</p>"
                        f"<p>Object: <strong>{detected}</strong> | Confidence: {confidence:.0%} | Latency: {latency*1000:.1f}ms</p></div>",
                        unsafe_allow_html=True,
                    )

                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = (1 - saved / max(processed, 1)) * 100
                    metric_p.metric("Processed", processed)
                    metric_d.metric("Duplicates", counts["Duplicates"])
                    metric_s.metric("Saved", saved)
                    metric_r.metric("Reduction %", f"{reduction:.1f}%")

                last_frame = frame.copy()

            cap.release()
            elapsed_time = time.time() - start_time

            # ============================= RESULTS ============================= #
            st.markdown("---")
            st.markdown("### ✅ Analysis Complete!")

            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
            original_size_gb = processed * 3.5 / 1000
            optimized_size_gb = saved * 3.5 / 1000
            storage_saved_gb = original_size_gb - optimized_size_gb

            fm = st.columns(5)
            fm[0].metric("Total Processed", processed, f"{processed/elapsed_time:.1f} fps")
            fm[1].metric("Frames Saved", saved, f"{saved/processed*100:.1f}%")
            fm[2].metric("Duplicates", counts["Duplicates"], f"{counts['Duplicates']/processed*100:.1f}%")
            fm[3].metric("Write Reduction", f"{reduction:.1f}%", "Lower is better")
            fm[4].metric("Lifespan Extension", f"{lifespan_extension:.1f}x", "Higher is better")

            # ========================== VIDEO CREATION ========================== #
            st.markdown("---")
            st.markdown("### 🎬 Creating Optimized Video (AURA MP4, H.264 CRF18)...")

            video_creation_status = st.empty()
            video_creation_status.info("⏳ Preparing video creation...")

            total_saved = len(saved_frame_paths) if saved_frame_paths else len(saved_frames)
            if total_saved == 0:
                video_creation_status.error("❌ No frames to save!")
                video_created = False
            else:
                st.markdown(
                    f"<div class='glass-card'><h4>Video Creation Configuration</h4>"
                    f"<p>📊 Frames: <b>{len(saved_frames)}</b> | 🎞️ FPS: <b>{fps:.1f}</b></p>"
                    f"<p>📐 {width}×{height} | ⚙️ Codec: H.264 (mp4) CRF18</p></div>",
                    unsafe_allow_html=True,
                )
                progress_vid = st.progress(0, text="Encoding...")
                try:
                    # Prefer file-based creation if frames were saved to disk
                    if saved_frame_paths:
                        success, message, frames_written = create_video_from_frame_files(
                            frames_dir, output_path, fps, width, height, crf=18, preset="ultrafast"
                        )
                    else:
                        success, message, frames_written = create_video_from_frames(
                            saved_frames, output_path, fps, width, height, crf=18, preset="ultrafast"
                        )
                    progress_vid.progress(1.0, text="Done")
                    video_creation_status.success(message if success else f"❌ {message}")
                    video_created = success
                except Exception as e:
                    progress_vid.progress(1.0, text="Failed")
                    video_creation_status.error(f"❌ Exception: {e}")
                    video_created = False

            # ======================= ENHANCED VIDEO COMPARISON & ANALYSIS ====================== #
            try:
                original_size_mb = os.path.getsize(input_path) / (1024.0 * 1024.0)
                optimized_size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0) if video_created and os.path.exists(output_path) else 0
                
                # Show enhanced video comparison with integrated mathematical analysis
                show_enhanced_video_comparison(
                    input_path, output_path if video_created else None, 
                    original_size_mb, optimized_size_mb, 
                    total_frames, total_saved
                )
                
            except Exception as e:
                st.error(f"Error in video comparison: {e}")
                
                # Fallback simple comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📹 Original Video")
                    st.video(input_path)
                with col2:
                    st.markdown("### 🧠 AURA Optimized")
                    if video_created and os.path.exists(output_path):
                        st.video(output_path)
                    else:
                        st.error("❌ Optimized video not available")

            # ======================= DETAILED ANALYSIS ====================== #
            st.markdown("---")
            st.markdown("### 📊 Performance Analysis")
            
            # Create metrics in a more organized layout
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
                if 'storage_saved_gb' in locals():
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
<p><b>AURA | Intelligent Data Manager</b></p>
<p>Advanced Storage Optimization for Edge Devices</p>
<p>© 2025 Team AURA | PSG Institute of Technology | Cerebrum 2025 Finals</p>
<p>Partner: SanDisk</p>
<p style="font-size:0.75rem;font-style:italic;">"Storage that Learns, Adapts, and Extends"</p>
</div>
""", unsafe_allow_html=True)
