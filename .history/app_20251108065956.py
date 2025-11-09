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
from ui_components import apply_custom_css, show_hero, get_category_badge
from video_generator import create_video_from_frames
from config import COLORS

# PAGE CONFIG
st.set_page_config(
    page_title="AURA Module 1 - Intelligent Data Manager",
    page_icon="🧠",
    layout="wide"
)

apply_custom_css()
show_hero()

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

        if st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
            st.markdown("---")
            st.markdown("### ⏳ Processing Video Frames...")

            frame_num = 0
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            results, saved_frames = [], []
            last_frame = None
            processed = 0

            progress_bar = st.progress(0, text="Starting...")
            display_col1, display_col2 = st.columns(2)
            frame_display, status_display = display_col1.empty(), display_col2.empty()
            metrics = st.columns(4)
            metric_p, metric_d, metric_s, metric_r = [m.empty() for m in metrics]

            cap = cv2.VideoCapture(input_path)
            start_time = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                progress_bar.progress(frame_num / total_frames, text=f"Processing {frame_num}/{total_frames}")

                if frame_num % 5 == 0:
                    try:
                        frame_display.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_column_width=True)
                    except:
                        pass

                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                counts[category] += 1
                processed += 1

                if category != "Discard":
                    saved_frames.append(frame.copy())
                    cv2.imwrite(os.path.join(frames_dir, f"{frame_num:06d}_{category}.jpg"), frame)

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
                frame_num += 1

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

            if len(saved_frames) == 0:
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
                    success, message, frames_written = create_video_from_frames(
                        saved_frames, output_path, fps, width, height, crf=18, preset="medium"
                    )
                    progress_vid.progress(1.0, text="Done")
                    video_creation_status.success(message if success else f"❌ {message}")
                    video_created = success
                except Exception as e:
                    progress_vid.progress(1.0, text="Failed")
                    video_creation_status.error(f"❌ Exception: {e}")
                    video_created = False

            # ======================= VIDEO DISPLAY (AUTOLOOP) ==================== #
            st.markdown("---")
            st.markdown("### 🎥 Optimized Video Preview")

            if video_created and os.path.exists(output_path):
                try:
                    import base64
                    import streamlit.components.v1 as components
                    with open(output_path, "rb") as f:
                        data = base64.b64encode(f.read()).decode("utf-8")
                    video_html = f"""
                    <video controls autoplay loop muted playsinline
                           style="width:100%;max-height:520px;border-radius:8px;
                           box-shadow:0 6px 20px rgba(0,0,0,0.35);">
                        <source src="data:video/mp4;base64,{data}" type="video/mp4">
                    </video>"""
                    components.html(video_html, height=520)
                except Exception:
                    st.video(output_path)
            else:
                st.error("Optimized video not available.")

            # ======================= COMPARISON & ANALYSIS ====================== #
            st.markdown("---")
            st.markdown("### 📊 Comparison & Storage Analysis")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Original Video")
                st.video(input_path)
            with col2:
                st.markdown("#### Optimized Video (AURA)")
                if video_created:
                    st.video(output_path)

            st.markdown(f"**Storage Saved:** {storage_saved_gb:.2f} GB ({reduction:.1f}%)")

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
                    st.image(img_rgb, caption="Input Frame", use_column_width=True)
                with c2:
                    category, confidence, detected, metric, latency = classify_frame(img_bgr)
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
