"""
AURA MODULE 1 - Main Application
Intelligent Data Manager with Real-Time Classification
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
from ui_components import apply_custom_css, show_hero, show_metrics, get_category_badge
from config import COLORS

# Page config
st.set_page_config(
    page_title="AURA Module 1 - Intelligent Data Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_custom_css()

# Show hero
show_hero()

# Create tabs
tab1, tab2 = st.tabs(["📹 Video Analysis", "🖼️ Image Analysis"])

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    st.markdown("""
    <div class="glass-card">
        <h3>📹 Upload Drone Video</h3>
        <p>Upload your drone footage for intelligent frame-by-frame analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        # Save video
        tmpdir = tempfile.mkdtemp()
        tfile = os.path.join(tmpdir, "video.mp4")
        with open(tfile, 'wb') as f:
            f.write(video_file.read())
        
        # Get video info
        video = cv2.VideoCapture(tfile)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        video.release()
        
        st.success(f"✅ Video loaded: {total_frames} frames @ {fps:.1f} FPS | Duration: {duration:.1f}s")
        
        # Process button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
                
                # Initialize
                frame_num = 0
                processed = 0
                last_frame = None
                counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
                results = []
                
                # UI placeholders
                st.markdown("---")
                st.markdown('<div class="glass-card"><h3>🔄 Processing Frames...</h3></div>', unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_placeholder = st.empty()
                frame_placeholder = st.empty()
                
                # Metrics row
                metrics_placeholders = {}
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                metrics_placeholders['processed'] = col_m1.empty()
                metrics_placeholders['duplicates'] = col_m2.empty()
                metrics_placeholders['saved'] = col_m3.empty()
                metrics_placeholders['reduction'] = col_m4.empty()
                
                # Process video
                video = cv2.VideoCapture(tfile)
                start_time = time.time()
                
                while True:
                    ret, frame = video.read()
                    if not ret or frame_num >= min(300, total_frames):
                        break
                    
                    # Update progress
                    progress = frame_num / total_frames
                    progress_bar.progress(min(progress, 1.0))
                    
                    # Display frame every 5 frames
                    if frame_num % 5 == 0:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_placeholder.image(frame_rgb, caption=f"Frame {frame_num}/{total_frames}")
                    
                    # Classify
                    category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                    
                    # Update counts
                    if category == "Discard" and detected == "duplicate_frame":
                        counts["Duplicates"] += 1
                    counts[category] += 1
                    processed += 1
                    
                    # Status update
                    badge_html = get_category_badge(category)
                    status_placeholder.markdown(f"""
                    <div class="glass-card">
                        <p><strong>Frame {frame_num}</strong> | {badge_html}</p>
                        <p>Object: <strong>{detected}</strong> | Confidence: <strong>{confidence:.1%}</strong> | Latency: <strong>{latency*1000:.1f}ms</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Store result
                    results.append({
                        "Frame": frame_num,
                        "Category": category,
                        "Object": detected,
                        "Confidence": f"{confidence:.1%}",
                        "Latency": f"{latency*1000:.1f}ms"
                    })
                    
                    # Update metrics
                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = (1 - saved / max(processed, 1)) * 100
                    
                    metrics_placeholders['processed'].metric("Processed", processed)
                    metrics_placeholders['duplicates'].metric("Duplicates", counts["Duplicates"])
                    metrics_placeholders['saved'].metric("Saved", saved)
                    metrics_placeholders['reduction'].metric("Reduction %", f"{reduction:.1f}%")
                    
                    last_frame = frame
                    frame_num += 1
                
                video.release()
                elapsed_time = time.time() - start_time
                
                # Results section
                st.markdown("---")
                st.markdown('<div class="glass-card"><h3>✅ Analysis Complete!</h3></div>', unsafe_allow_html=True)
                
                # Calculate final metrics
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = (1 - saved / processed) * 100 if processed > 0 else 0
                lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
                storage_saved_gb = (processed - saved) * 3.5 / 1000
                
                # Show final metrics
                show_metrics(processed, saved, counts["Duplicates"], reduction, lifespan_extension, storage_saved_gb)
                
                # Charts
                st.markdown("---")
                st.subheader("📊 Classification Analysis")
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    fig_pie = px.pie(
                        values=[counts[c] for c in ["Critical", "Important", "Normal", "Discard"]],
                        names=["Critical", "Important", "Normal", "Discard"],
                        color_discrete_map=COLORS,
                        title="Frame Distribution by Priority"
                    )
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_chart2:
                    fig_bar = go.Figure(data=[go.Bar(
                        x=["Critical", "Important", "Normal", "Discard"],
                        y=[counts[c] for c in ["Critical", "Important", "Normal", "Discard"]],
                        marker_color=[COLORS[c] for c in ["Critical", "Important", "Normal", "Discard"]]
                    )])
                    fig_bar.update_layout(
                        title="Frame Count by Category",
                        xaxis_title="Category",
                        yaxis_title="Count",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="white"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Formulas section
                st.markdown("---")
                st.subheader("📐 Mathematical Formulas (Real-Time Calculation)")
                
                formula_col1, formula_col2 = st.columns(2)
                
                with formula_col1:
                    st.markdown(f"""
                    ### Write Reduction Formula
                    ```
                    Reduction% = (Total - Saved) / Total × 100
                    
                    Reduction% = ({processed} - {saved}) / {processed} × 100
                    Reduction% = {reduction:.2f}%
                    ```
                    """)
                
                with formula_col2:
                    st.markdown(f"""
                    ### Lifespan Extension Formula
                    ```
                    Extension = 1 / (1 - Reduction%)
                    
                    Extension = 1 / (1 - {reduction/100:.4f})
                    Extension = {lifespan_extension:.2f}x
                    ```
                    """)
                
                # Storage impact
                st.markdown("---")
                st.subheader("💾 Storage Impact")
                
                col_storage1, col_storage2, col_storage3 = st.columns(3)
                
                with col_storage1:
                    original_size = processed * 3.5 / 1000
                    st.metric("Original Storage", f"{original_size:.2f} GB")
                
                with col_storage2:
                    aura_size = saved * 3.5 / 1000
                    st.metric("AURA Storage", f"{aura_size:.2f} GB")
                
                with col_storage3:
                    st.metric("Storage Saved", f"{storage_saved_gb:.2f} GB")
                
                # Data table
                st.markdown("---")
                st.subheader("📋 Detailed Frame Analysis")
                
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, height=300)
                
                # Download report
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download Report (CSV)",
                    csv,
                    f"aura_module1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

# ============================================================================
# TAB 2: IMAGE ANALYSIS
# ============================================================================

with tab2:
    st.markdown("""
    <div class="glass-card">
        <h3>🖼️ Single Image Analysis</h3>
        <p>Upload a single frame to see Module 1 classification in detail</p>
    </div>
    """, unsafe_allow_html=True)
    
    image_file = st.file_uploader("Select image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if image_file:
        # Load image
        image_array = np.array(bytearray(image_file.read()), dtype=np.uint8)
        image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        if st.button("🔍 ANALYZE IMAGE", type="primary", use_container_width=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image_rgb, caption="Input Frame", use_column_width=True)
            
            with col2:
                # Classify
                category, confidence, detected, metric, latency = classify_frame(image_bgr)
                
                badge_html = get_category_badge(category)
                
                st.markdown(f"""
                <div class="glass-card">
                    <h4>Classification Result</h4>
                    <p>{badge_html}</p>
                    <p><strong>Detected Object:</strong> {detected}</p>
                    <p><strong>Confidence:</strong> {confidence:.1%}</p>
                    <p><strong>Processing Time:</strong> {latency*1000:.1f}ms</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Explanation
                st.markdown("### Analysis Details")
                
                if category == "Discard":
                    if detected == "empty_sky":
                        st.info("🔵 **Empty Sky Detected** - Zero information value, not saved")
                    elif detected == "duplicate_frame":
                        st.info("🔄 **Duplicate Frame** - Identical to previous, not saved")
                    else:
                        st.info("⚪ **Discard** - Low information value, not saved")
                
                elif category == "Critical":
                    st.success("🔴 **CRITICAL** - Person/Animal detected! Saved at full 4K quality")
                
                elif category == "Important":
                    st.warning("🟠 **IMPORTANT** - Vehicle/Infrastructure detected. Standard compression applied")
                
                else:
                    st.info("🟢 **NORMAL** - Other objects detected. Heavy compression applied")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 40px;">
    AURA Module 1 | Intelligent Data Manager | SanDisk Smart Storage ©️ 2025
</div>
""", unsafe_allow_html=True)
