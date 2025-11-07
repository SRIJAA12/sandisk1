"""
AURA MODULE 1 - EMERGENCY VERSION
Simple, working, no complications
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

st.set_page_config(page_title="AURA Module 1", layout="wide")
apply_custom_css()
show_hero()

tab1, tab2 = st.tabs(["📹 VIDEO ANALYSIS", "🖼️ IMAGE ANALYSIS"])

with tab1:
    st.markdown('<div class="glass-card"><h3> Upload Video</h3><p>Process drone footage</p></div>', unsafe_allow_html=True)
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.avi")
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        with open(input_path, 'wb') as f:
            f.write(video_file.read())
        
        cap = cv2.VideoCapture(input_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        st.write("")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Frames", f"{total_frames}")
        col2.metric("FPS", f"{fps:.1f}")
        col3.metric("Duration", f"{duration:.1f}s")
        col4.metric("Resolution", f"{width}×{height}")
        
        st.write("")
        
        if st.button("🚀 ANALYZE", type="primary", use_container_width=True):
            
            st.markdown("---")
            st.markdown("### ⏳ Processing...")
            
            frame_num = 0
            processed = 0
            last_frame = None
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            results = []
            saved_frames = []
            
            progress_bar = st.progress(0)
            
            display_col1, display_col2 = st.columns(2)
            with display_col1:
                st.write("**Frame**")
                frame_display = st.empty()
            with display_col2:
                st.write("**Info**")
                status_display = st.empty()
            
            st.write("")
            metric_row = st.columns(4)
            metric_p = metric_row[0].empty()
            metric_d = metric_row[1].empty()
            metric_s = metric_row[2].empty()
            metric_r = metric_row[3].empty()
            
            cap = cv2.VideoCapture(input_path)
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                progress_bar.progress(min(frame_num / total_frames, 1.0))
                
                if frame_num % 5 == 0:
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_display.image(frame_rgb, use_column_width=True)
                    except:
                        pass
                
                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                
                counts[category] += 1
                processed += 1
                
                if category != "Discard":
                    saved_frames.append(frame.copy())
                    frame_file = os.path.join(frames_dir, f"{frame_num:06d}_{category}.jpg")
                    cv2.imwrite(frame_file, frame)
                
                badge = get_category_badge(category)
                status_display.markdown(f'<div class="glass-card"><p><strong>Frame {frame_num}</strong> | {badge}</p><p>{detected} ({confidence:.0%})</p></div>', unsafe_allow_html=True)
                
                results.append({"Frame": frame_num, "Category": category, "Object": detected, "Confidence": f"{confidence:.1%}"})
                
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
            
            st.markdown("---")
            st.markdown("### ✅ Complete!")
            st.write("")
            
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
            
            st.markdown("---")
            st.markdown("### 🎬 Creating Video...")
            
            if len(saved_frames) > 0:
                try:
                    # SIMPLE VIDEO CREATION - NO COMPLICATIONS
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                    
                    written = 0
                    for frame in saved_frames:
                        try:
                            if frame.shape[1] != width or frame.shape[0] != height:
                                frame = cv2.resize(frame, (width, height))
                            if out.write(frame):
                                written += 1
                        except:
                            pass
                    
                    out.release()
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        file_mb = os.path.getsize(output_path) / (1024*1024)
                        st.success(f"✅ Video: {written} frames | {file_mb:.2f} MB")
                        
                        st.markdown("---")
                        st.markdown("### 🎥 Video Comparison")
                        
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.markdown(f"**Original**\nSize: {original_size:.2f} GB\nFrames: {processed}")
                            try:
                                st.video(input_path)
                            except:
                                st.error("Cannot display")
                        
                        with comp_col2:
                            st.markdown(f"**AURA Optimized**\nSize: {optimized_size:.2f} GB\nFrames: {saved}\nSaved: {saved_storage:.2f} GB ({reduction:.1f}%)")
                            try:
                                st.video(output_path)
                            except:
                                try:
                                    with open(output_path, 'rb') as vf:
                                        st.download_button("📥 Download", vf.read(), "video.avi")
                                except:
                                    st.error("Cannot display")
                    else:
                        st.error("Video file empty")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("No frames saved")
            
            st.markdown("---")
            st.markdown("### 📐 Formulas")
            
            with st.expander("Formula 1: Reduction %", expanded=True):
                st.markdown(f"``````")
            
            with st.expander("Formula 2: Lifespan Extension", expanded=True):
                st.markdown(f"``````")
            
            with st.expander("Formula 3: Storage Saved", expanded=True):
                st.markdown(f"``````")
            
            st.markdown("---")
            st.markdown("### 📊 Charts")
            
            c1, c2 = st.columns(2)
            
            with c1:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=["Critical", "Important", "Normal", "Discard"],
                    values=[counts[x] for x in ["Critical", "Important", "Normal", "Discard"]],
                    marker=dict(colors=[COLORS.get(x) for x in ["Critical", "Important", "Normal", "Discard"]])
                )])
                fig_pie.update_layout(title="Distribution", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with c2:
                fig_bar = go.Figure(data=[go.Bar(
                    x=["Critical", "Important", "Normal", "Discard"],
                    y=[counts[x] for x in ["Critical", "Important", "Normal", "Discard"]],
                    marker=dict(color=[COLORS.get(x) for x in ["Critical", "Important", "Normal", "Discard"]])
                )])
                fig_bar.update_layout(title="Count", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 💾 Breakdown")
            
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("🔴 Critical", f"{counts['Critical']}\n{counts['Critical']*3.5/1000:.2f}GB")
            b2.metric("🟠 Important", f"{counts['Important']}\n{counts['Important']*1.5/1000:.2f}GB")
            b3.metric("🟢 Normal", f"{counts['Normal']}\n{counts['Normal']*0.3/1000:.2f}GB")
            b4.metric("⚪ Discard", f"{counts['Discard']}\n0GB")
            
            st.markdown("---")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            csv = pd.DataFrame(results).to_csv(index=False)
            st.download_button("📥 Report", csv, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

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
st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.5);"><p>AURA Module 1 © 2025</p></div>', unsafe_allow_html=True)
