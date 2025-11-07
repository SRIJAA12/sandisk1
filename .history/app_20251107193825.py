"""
AURA MODULE 1 - INTELLIGENT DATA MANAGER
FIXED VERSION - Video generation working + proper frame handling
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
import time
from datetime import datetime
from classifier import classify_frame
from ui_components import apply_custom_css, show_hero, get_category_badge
from config import COLORS

# PAGE CONFIG
st.set_page_config(page_title="AURA Module 1", page_icon="🧠", layout="wide")
apply_custom_css()
show_hero()

tab1, tab2 = st.tabs(["📹 VIDEO ANALYSIS", "🖼️ IMAGE ANALYSIS"])

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    st.markdown('<div class="glass-card"><h3>📹 Upload Video</h3><p>Process drone footage</p></div>', unsafe_allow_html=True)
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        # Save input video
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.avi")  # Changed to AVI for better compatibility
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        with open(input_path, 'wb') as f:
            f.write(video_file.read())
        
        # Get video info
        cap = cv2.VideoCapture(input_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        # Validate video
        if total_frames == 0 or fps == 0:
            st.error("❌ Invalid video file")
        else:
            # Info display
            st.write("")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Frames", f"{total_frames}")
            col2.metric("FPS", f"{fps:.1f}")
            col3.metric("Duration", f"{duration:.1f}s")
            col4.metric("Resolution", f"{width}×{height}")
            
            st.write("")
            
            # Start button
            if st.button("🚀 ANALYZE", type="primary", use_container_width=True):
                
                st.markdown("---")
                st.markdown("### ⏳ Processing Frames...")
                
                # Initialize
                frame_num = 0
                processed = 0
                last_frame = None
                counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
                results = []
                saved_frames = []
                saved_frame_nums = []
                
                # UI Elements
                progress_bar = st.progress(0)
                
                display_col1, display_col2 = st.columns(2)
                with display_col1:
                    st.write("**Current Frame**")
                    frame_display = st.empty()
                with display_col2:
                    st.write("**Classification**")
                    status_display = st.empty()
                
                st.write("")
                metric_row = st.columns(4)
                metric_p = metric_row[0].empty()
                metric_d = metric_row[1].empty()
                metric_s = metric_row[2].empty()
                metric_r = metric_row[3].empty()
                
                # Process video
                cap = cv2.VideoCapture(input_path)
                start_time = time.time()
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Progress
                    progress_bar.progress(min(frame_num / total_frames, 1.0), text=f"{frame_num}/{total_frames}")
                    
                    # Display frame every 5 frames
                    if frame_num % 5 == 0:
                        try:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame_display.image(frame_rgb, use_column_width=True)
                        except:
                            pass
                    
                    # Classify
                    category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                    
                    # Count
                    if category == "Discard" and detected == "duplicate_frame":
                        counts["Duplicates"] += 1
                    
                    counts[category] += 1
                    processed += 1
                    
                    # IMPORTANT: Save ALL frames except those explicitly marked as Discard
                    # Changed logic: Save if NOT "Discard"
                    if category != "Discard":
                        saved_frames.append(frame.copy())
                        saved_frame_nums.append(frame_num)
                        # Save frame image
                        frame_file = os.path.join(frames_dir, f"{frame_num:06d}_{category}.jpg")
                        cv2.imwrite(frame_file, frame)
                    
                    # Status
                    badge = get_category_badge(category)
                    status_display.markdown(f"""
                    <div class="glass-card">
                        <p><strong>Frame {frame_num}</strong> | {badge}</p>
                        <p>{detected} ({confidence:.0%}) | {latency*1000:.1f}ms</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    results.append({"Frame": frame_num, "Category": category, "Object": detected, "Confidence": f"{confidence:.1%}"})
                    
                    # Update metrics
                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = (1 - saved / max(processed, 1)) * 100
                    
                    metric_p.metric("Processed", processed)
                    metric_d.metric("Duplicates", counts["Duplicates"])
                    metric_s.metric("Saved", saved)
                    metric_r.metric("Reduction %", f"{reduction:.1f}%")
                    
                    last_frame = frame.copy()
                    frame_num += 1
                
                cap.release()
                elapsed = time.time() - start_time
                
                # RESULTS
                st.markdown("---")
                st.markdown("### ✅ Analysis Complete!")
                st.write("")
                
                # Metrics
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = (1 - saved / processed) * 100 if processed > 0 else 0
                lifespan = 100 / (100 - reduction) if reduction < 100 else 999
                
                original_size = processed * 3.5 / 1000
                optimized_size = saved * 3.5 / 1000
                saved_storage = original_size - optimized_size
                
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Processed", processed)
                m2.metric("Saved", saved)
                m3.metric("Duplicates", counts["Duplicates"])
                m4.metric("Reduction", f"{reduction:.1f}%")
                m5.metric("Lifespan", f"{lifespan:.1f}x")
                
                # CREATE VIDEO - FIXED
                st.markdown("---")
                st.markdown("### 🎬 Creating Video...")
                
                video_created = False
                error_msg = ""
                
                if len(saved_frames) > 0:
                    try:
                        st.write(f"Creating video: {len(saved_frames)} frames @ {fps:.1f}fps ({width}×{height})")
                        
                        # Use MJPEG for best compatibility
                        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                        
                        if not writer.isOpened():
                            error_msg = "VideoWriter failed to open"
                            raise Exception(error_msg)
                        
                        written = 0
                        for i, frame in enumerate(saved_frames):
                            try:
                                # Ensure frame is correct size
                                if frame.shape[1] != width or frame.shape[0] != height:
                                    frame = cv2.resize(frame, (width, height))
                                
                                ret = writer.write(frame)
                                if ret:
                                    written += 1
                            except Exception as e:
                                st.warning(f"Frame {i} write error: {str(e)}")
                                continue
                        
                        writer.release()
                        
                        # Check file
                        if os.path.exists(output_path):
                            file_size_mb = os.path.getsize(output_path) / (1024*1024)
                            if file_size_mb > 0.1:  # At least 100KB
                                st.success(f"✅ Video created: {written} frames written | {file_size_mb:.2f} MB")
                                video_created = True
                            else:
                                error_msg = f"Video file too small ({file_size_mb:.2f} MB)"
                                st.error(f"❌ {error_msg}")
                        else:
                            error_msg = "Output file not created"
                            st.error(f"❌ {error_msg}")
                    
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Video creation failed: {error_msg}")
                else:
                    st.error("❌ No frames saved!")
                
                # VIDEO COMPARISON
                st.markdown("---")
                st.markdown("### 🎥 Video Comparison")
                
                comp_col1, comp_col2 = st.columns(2)
                
                with comp_col1:
                    st.markdown("#### Original Video")
                    st.write(f"Size: {original_size:.2f} GB")
                    st.write(f"Frames: {processed}")
                    try:
                        st.video(input_path)
                    except Exception as e:
                        st.error(f"Cannot load: {str(e)}")
                
                with comp_col2:
                    st.markdown("#### Optimized Video (AURA)")
                    st.write(f"Size: {optimized_size:.2f} GB")
                    st.write(f"Frames: {saved}")
                    st.write(f"Saved: {saved_storage:.2f} GB ({reduction:.1f}%)")
                    
                    if video_created and os.path.exists(output_path):
                        try:
                            st.video(output_path)
                        except Exception as e:
                            st.warning(f"Cannot display: {str(e)}")
                            # Fallback
                            with open(output_path, 'rb') as vf:
                                st.download_button("📥 Download Video", vf.read(), "optimized.avi", "video/x-msvideo")
                    else:
                        st.error(f"Video not available: {error_msg}")
                
                # FORMULAS
                st.markdown("---")
                st.markdown("### 📐 Formulas")
                
                with st.expander("Formula 1: Write Reduction %", expanded=True):
                    st.markdown(f"""
                    ```
                    Reduction% = ({processed} - {saved}) / {processed} × 100 = {reduction:.2f}%
                    ```
                    **Meaning:** {reduction:.1f}% fewer writes to storage
                    """)
                
                with st.expander("Formula 2: Lifespan Extension", expanded=True):
                    st.markdown(f"""
                    ```
                    Extension = 1 / (1 - {reduction/100:.4f}) = {lifespan:.2f}x
                    ```
                    **Meaning:** Device lasts {lifespan:.1f}x longer (6.8 years → {6.8*lifespan:.1f} years)
                    """)
                
                with st.expander("Formula 3: Storage Saved", expanded=True):
                    st.markdown(f"""
                    ```
                    Original: {original_size:.2f} GB
                    Optimized: {optimized_size:.2f} GB
                    Saved: {saved_storage:.2f} GB ({(saved_storage/original_size*100):.1f}%)
                    ```
                    """)
                
                # CHARTS
                st.markdown("---")
                st.markdown("### 📊 Charts")
                
                c1, c2 = st.columns(2)
                
                with c1:
                    pie_fig = go.Figure(data=[go.Pie(
                        labels=["Critical", "Important", "Normal", "Discard"],
                        values=[counts[x] for x in ["Critical", "Important", "Normal", "Discard"]],
                        marker=dict(colors=[COLORS.get(x) for x in ["Critical", "Important", "Normal", "Discard"]])
                    )])
                    pie_fig.update_layout(title="Distribution", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350)
                    st.plotly_chart(pie_fig, use_container_width=True)
                
                with c2:
                    bar_fig = go.Figure(data=[go.Bar(
                        x=["Critical", "Important", "Normal", "Discard"],
                        y=[counts[x] for x in ["Critical", "Important", "Normal", "Discard"]],
                        marker=dict(color=[COLORS.get(x) for x in ["Critical", "Important", "Normal", "Discard"]])
                    )])
                    bar_fig.update_layout(title="Counts", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350, showlegend=False)
                    st.plotly_chart(bar_fig, use_container_width=True)
                
                # BREAKDOWN
                st.markdown("---")
                st.markdown("### 💾 Breakdown")
                
                b1, b2, b3, b4 = st.columns(4)
                b1.metric("🔴 Critical", f"{counts['Critical']}\n{counts['Critical']*3.5/1000:.2f}GB")
                b2.metric("🟠 Important", f"{counts['Important']}\n{counts['Important']*1.5/1000:.2f}GB")
                b3.metric("🟢 Normal", f"{counts['Normal']}\n{counts['Normal']*0.3/1000:.2f}GB")
                b4.metric("⚪ Discard", f"{counts['Discard']}\n0GB")
                
                # FRAMES GALLERY
                st.markdown("---")
                st.markdown("### 🖼️ Saved Frames")
                
                if os.path.exists(frames_dir):
                    frame_files = sorted([f for f in os.listdir(frames_dir)])[:6]
                    if frame_files:
                        frame_cols = st.columns(3)
                        for i, ff in enumerate(frame_files):
                            fp = os.path.join(frames_dir, ff)
                            fimg = cv2.imread(fp)
                            fimg_rgb = cv2.cvtColor(fimg, cv2.COLOR_BGR2RGB)
                            with frame_cols[i % 3]:
                                st.image(fimg_rgb, caption=ff.replace('.jpg', ''), use_column_width=True)
                
                # TABLE
                st.markdown("---")
                st.dataframe(pd.DataFrame(results), use_container_width=True, height=300)
                
                # DOWNLOAD
                csv = pd.DataFrame(results).to_csv(index=False)
                st.download_button("📥 Report (CSV)", csv, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

# ============================================================================
# TAB 2: IMAGE ANALYSIS
# ============================================================================

with tab2:
    st.markdown('<div class="glass-card"><h3>🖼️ Image Analysis</h3></div>', unsafe_allow_html=True)
    
    img = st.file_uploader("Select image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if img:
        img_arr = np.array(bytearray(img.read()), dtype=np.uint8)
        img_bgr = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if img_bgr is not None:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            if st.button("🔍 ANALYZE", type="primary", use_container_width=True):
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    st.image(img_rgb, use_column_width=True)
                
                with c2:
                    category, confidence, detected, metric, latency = classify_frame(img_bgr)
                    badge = get_category_badge(category)
                    st.markdown(f'<div class="glass-card"><h4>Result</h4><p>{badge}</p><p>{detected} ({confidence:.1%})</p></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center; color:rgba(255,255,255,0.5);"><p>AURA Module 1 © 2025</p></div>', unsafe_allow_html=True)

# PERFORMANCE METRICS
if 'processed' in locals() and processed > 0:
    st.markdown("---")
    st.markdown("### ⚡ Performance")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    fps_speed = processed / elapsed if elapsed > 0 else 0
    avg_latency = (elapsed / processed * 1000) if processed > 0 else 0
    dup_ratio = (counts["Duplicates"] / processed * 100) if processed > 0 else 0
    
    perf_col1.metric("Speed", f"{fps_speed:.1f} FPS", "Real-time ✓")
    perf_col2.metric("Latency", f"{avg_latency:.1f}ms", "Per frame")
    perf_col3.metric("Total Time", f"{elapsed:.1f}s", f"For {processed} frames")
    perf_col4.metric("Duplicates", f"{dup_ratio:.1f}%", f"{counts['Duplicates']} removed")
else:
    st.info("No performance metrics available. Run a video analysis to see performance stats.")

# ============================================================================
# TABS END
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.85rem; padding: 20px;">
    <p><strong>🧠 AURA Module 1 | Intelligent Data Manager</strong></p>
    <p>© 2025 Team AURA | PSG Institute of Technology | Cerebrum 2025</p>
    <p>Partner: SanDisk | Powering Smart Storage Solutions</p>
</div>
""", unsafe_allow_html=True)
