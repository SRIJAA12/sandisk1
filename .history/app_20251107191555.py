"""
AURA MODULE 1 - INTELLIGENT DATA MANAGER
Championship-Grade Application
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
from config import COLORS

# PAGE CONFIG
st.set_page_config(page_title="AURA Module 1", page_icon="🧠", layout="wide")

# STYLING
apply_custom_css()
show_hero()

# TABS
tab1, tab2 = st.tabs(["📹 VIDEO ANALYSIS", "🖼️ IMAGE ANALYSIS"])

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    st.markdown('<div class="glass-card"><h3>📹 Upload Video</h3><p>Process drone footage</p></div>', unsafe_allow_html=True)
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        # Save video
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.mp4")
        
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
        
        # Info row
        st.write("")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Frames", total_frames)
        col2.metric("FPS", f"{fps:.1f}")
        col3.metric("Duration", f"{duration:.1f}s")
        col4.metric("Resolution", f"{width}×{height}")
        
        st.write("")
        
        # Button
        if st.button("🚀 ANALYZE", type="primary", use_container_width=True):
            
            st.markdown("---")
            st.markdown("### ⏳ Processing...")
            
            # Initialize
            frame_num = 0
            processed = 0
            last_frame = None
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            results = []
            saved_frames = []
            
            # Progress
            progress = st.progress(0)
            status = st.empty()
            
            # Process
            cap = cv2.VideoCapture(input_path)
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                progress.progress(min(frame_num / total_frames, 1.0))
                
                # Classify
                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                
                # Count
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                counts[category] += 1
                processed += 1
                
                # Save if not discarded
                if category != "Discard":
                    saved_frames.append(frame)
                
                # Status
                badge = get_category_badge(category)
                status.markdown(f'<div class="glass-card"><p>Frame {frame_num} | {badge} | {detected} ({confidence:.0%})</p></div>', unsafe_allow_html=True)
                
                results.append({"Frame": frame_num, "Category": category, "Object": detected, "Confidence": f"{confidence:.1%}"})
                
                last_frame = frame.copy()
                frame_num += 1
            
            cap.release()
            elapsed = time.time() - start_time
            
            # RESULTS
            st.markdown("---")
            st.markdown("### ✅ Analysis Complete!")
            
            st.write("")
            
            # Calculate metrics
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan = 100 / (100 - reduction) if reduction < 100 else 999
            storage_original = processed * 3.5 / 1000
            storage_optimized = saved * 3.5 / 1000
            storage_saved = storage_original - storage_optimized
            
            # Metrics
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Processed", processed)
            m2.metric("Saved", saved)
            m3.metric("Duplicates", counts["Duplicates"])
            m4.metric("Reduction", f"{reduction:.1f}%")
            m5.metric("Lifespan", f"{lifespan:.1f}x")
            
            # CREATE VIDEO
            st.markdown("---")
            st.markdown("### 🎬 Creating Video...")
            
            video_created = False
            
            if len(saved_frames) > 0:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                    
                    for frame in saved_frames:
                        writer.write(frame)
                    
                    writer.release()
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success(f"✅ Video created: {len(saved_frames)} frames")
                        video_created = True
                except:
                    st.warning("⚠️ MP4 codec unavailable, trying AVI...")
                    try:
                        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                        
                        for frame in saved_frames:
                            writer.write(frame)
                        
                        writer.release()
                        video_created = True
                    except:
                        st.error("❌ Could not create video")
            
            # VIDEO COMPARISON
            st.markdown("---")
            st.markdown("### 🎥 Video Comparison")
            
            col_vid1, col_vid2 = st.columns(2)
            
            with col_vid1:
                st.markdown("**Original Video**")
                st.write(f"Size: {storage_original:.2f} GB")
                st.write(f"Frames: {processed}")
                try:
                    st.video(input_path)
                except:
                    st.error("Cannot load original")
            
            with col_vid2:
                st.markdown("**Optimized Video (AURA)**")
                st.write(f"Size: {storage_optimized:.2f} GB")
                st.write(f"Frames: {saved}")
                st.write(f"Saved: {storage_saved:.2f} GB ({reduction:.1f}%)")
                
                if video_created:
                    try:
                        st.video(output_path)
                    except:
                        st.warning("Video created but cannot display")
                        if os.path.exists(output_path):
                            with open(output_path, 'rb') as vf:
                                st.download_button("Download Video", vf.read(), "video.mp4")
                else:
                    st.error("Video not created")
            
            # FORMULAS
            st.markdown("---")
            st.markdown("### 📐 Formulas & Calculations")
            
            with st.expander("Formula 1: Write Reduction %", expanded=True):
                st.markdown(f"""
                ```
                Reduction% = (Total - Saved) / Total × 100
                Reduction% = ({processed} - {saved}) / {processed} × 100
                Reduction% = {reduction:.2f}%
                ```
                
                **Meaning:** {reduction:.1f}% fewer writes to storage = Longer device lifespan
                """)
            
            with st.expander("Formula 2: Lifespan Extension", expanded=True):
                st.markdown(f"""
                ```
                Extension = 1 / (1 - Reduction%)
                Extension = 1 / (1 - {reduction/100:.4f})
                Extension = {lifespan:.2f}x
                ```
                
                **Meaning:** Device lasts {lifespan:.1f}× longer (6.8 years → {6.8*lifespan:.1f} years)
                """)
            
            with st.expander("Formula 3: Storage Savings", expanded=True):
                st.markdown(f"""
                ```
                Original = {processed} frames × 3.5 MB = {storage_original:.2f} GB
                Optimized = {saved} frames × 3.5 MB = {storage_optimized:.2f} GB
                Saved = {storage_original:.2f} - {storage_optimized:.2f} = {storage_saved:.2f} GB
                ```
                
                **Impact:** Save {storage_saved:.2f} GB per video
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
                bar_fig.update_layout(title="Frame Counts", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350, showlegend=False)
                st.plotly_chart(bar_fig, use_container_width=True)
            
            # BREAKDOWN
            st.markdown("---")
            st.markdown("### 📊 Storage Breakdown")
            
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("🔴 Critical", f"{counts['Critical']}\n{counts['Critical']*3.5/1000:.2f}GB")
            b2.metric("🟠 Important", f"{counts['Important']}\n{counts['Important']*1.5/1000:.2f}GB")
            b3.metric("🟢 Normal", f"{counts['Normal']}\n{counts['Normal']*0.3/1000:.2f}GB")
            b4.metric("⚪ Discard", f"{counts['Discard']}\n0GB")
            
            # TABLE
            st.markdown("---")
            st.markdown("### 📋 Details")
            st.dataframe(pd.DataFrame(results), use_container_width=True, height=300)
            
            # DOWNLOAD
            st.markdown("---")
            csv = pd.DataFrame(results).to_csv(index=False)
            st.download_button("📥 Download Report (CSV)", csv, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

# ============================================================================
# TAB 2: IMAGE ANALYSIS
# ============================================================================

with tab2:
    st.markdown('<div class="glass-card"><h3>🖼️ Image Analysis</h3><p>Single frame classification</p></div>', unsafe_allow_html=True)
    
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
                    
                    st.markdown(f"""
                    <div class="glass-card">
                    <h4>Result</h4>
                    <p>{badge}</p>
                    <p><strong>{detected}</strong></p>
                    <p>Confidence: {confidence:.1%}</p>
                    <p>Latency: {latency*1000:.1f}ms</p>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.85rem;"><p>AURA Module 1 © 2025</p></div>', unsafe_allow_html=True)
