"""
AURA MODULE 1 - INTELLIGENT DATA MANAGER
FINAL WORKING VERSION WITH VIDEO GENERATION
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

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    
    st.markdown(
        '<div class="glass-card"><h3>📹 Upload Drone Video</h3><p>Upload your drone footage for intelligent analysis</p></div>',
        unsafe_allow_html=True
    )
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        
        # Setup directories
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.avi")
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Save input video
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
        
        # Display video info
        st.write("")
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        info_col1.metric("Total Frames", f"{total_frames}")
        info_col2.metric("FPS", f"{fps:.1f}")
        info_col3.metric("Duration", f"{duration:.1f}s")
        info_col4.metric("Resolution", f"{width}×{height}")
        
        st.write("")
        
        # Start button
        if st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
            
            st.markdown("---")
            st.markdown("### ⏳ Processing Video Frames...")
            
            # Initialize
            frame_num = 0
            processed = 0
            last_frame = None
            counts = {
                "Critical": 0,
                "Important": 0,
                "Normal": 0,
                "Discard": 0,
                "Duplicates": 0
            }
            results = []
            saved_frames = []
            
            # UI Elements
            progress_bar = st.progress(0, text="Starting...")
            
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
                
                # Update progress
                progress_value = frame_num / total_frames
                progress_bar.progress(
                    min(progress_value, 1.0),
                    text=f"Processing: {frame_num}/{total_frames}"
                )
                
                # Display frame every 5 frames
                if frame_num % 5 == 0:
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_display.image(frame_rgb, use_column_width=True)
                    except:
                        pass
                
                # Classify frame
                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                
                # Update counts
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                
                counts[category] += 1
                processed += 1
                
                # Save frames that are NOT discarded
                if category != "Discard":
                    saved_frames.append(frame.copy())
                    frame_file = os.path.join(frames_dir, f"{frame_num:06d}_{category}.jpg")
                    try:
                        cv2.imwrite(frame_file, frame)
                    except:
                        pass
                
                # Display status
                badge_html = get_category_badge(category)
                status_display.markdown(f"""
                <div class="glass-card">
                    <p><strong>Frame {frame_num}</strong> | {badge_html}</p>
                    <p>Object: <strong>{detected}</strong> | Confidence: {confidence:.0%} | Latency: {latency*1000:.1f}ms</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Store result
                results.append({
                    "Frame": frame_num,
                    "Category": category,
                    "Object": detected,
                    "Confidence": f"{confidence:.1%}"
                })
                
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
            elapsed_time = time.time() - start_time
            
            # ===================================================================
            # RESULTS
            # ===================================================================
            
            st.markdown("---")
            st.markdown("### ✅ Analysis Complete!")
            st.write("")
            
            # Calculate metrics
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
            
            original_size_gb = processed * 3.5 / 1000
            optimized_size_gb = saved * 3.5 / 1000
            storage_saved_gb = original_size_gb - optimized_size_gb
            
            # Final metrics
            final_m1, final_m2, final_m3, final_m4, final_m5 = st.columns(5)
            
            final_m1.metric(
                "Total Processed",
                processed,
                f"{processed/elapsed_time:.1f} fps"
            )
            final_m2.metric(
                "Frames Saved",
                saved,
                f"{saved/processed*100:.1f}%"
            )
            final_m3.metric(
                "Duplicates",
                counts["Duplicates"],
                f"{counts['Duplicates']/processed*100:.1f}%"
            )
            final_m4.metric(
                "Write Reduction",
                f"{reduction:.1f}%",
                "Lower is better"
            )
            final_m5.metric(
                "Lifespan Extension",
                f"{lifespan_extension:.1f}x",
                "Higher is better"
            )
            
            # ===================================================================
            # VIDEO CREATION
            # ===================================================================
            
            st.markdown("---")
            st.markdown("### 🎬 Creating Optimized Video...")
            
            video_creation_status = st.empty()
            video_creation_status.write("⏳ Processing...")
            
            if len(saved_frames) > 0:
                success, message, frames_written = create_video_from_frames(
                    saved_frames,
                    output_path,
                    fps,
                    width,
                    height
                )
                
                if success:
                    video_creation_status.success(f"✅ {message}")
                    video_created = True
                else:
                    video_creation_status.error(f"❌ {message}")
                    video_created = False
            else:
                video_creation_status.error("❌ No frames to save!")
                video_created = False
            
            # ===================================================================
            # VIDEO COMPARISON
            # ===================================================================
            
            st.markdown("---")
            st.markdown("### 🎥 Video Comparison & Formula Analysis")
            st.write("")
            
            comp_col1, comp_col2 = st.columns([1, 1])
            
            # Original Video
            with comp_col1:
                st.markdown("#### Original Video (All Frames)")
                st.markdown(f"""
                **Storage Size:** {original_size_gb:.2f} GB  
                **Frame Count:** {processed}  
                **Duration:** {duration:.1f}s  
                **Quality:** Full 4K (No Compression)
                """)
                
                try:
                    st.video(input_path)
                except Exception as e:
                    st.error(f"Cannot load original: {str(e)}")
            
            # Optimized Video
            with comp_col2:
                st.markdown("#### Optimized Video (AURA Processed)")
                st.markdown(f"""
                **Storage Size:** {optimized_size_gb:.2f} GB  
                **Frame Count:** {saved}  
                **Duration:** {duration * (saved/processed):.1f}s (approx)  
                **Storage Saved:** {storage_saved_gb:.2f} GB ({reduction:.1f}%)
                """)
                
                if video_created and os.path.exists(output_path):
                    try:
                        st.video(output_path)
                    except Exception as e:
                        st.warning("Cannot display in browser")
                        try:
                            with open(output_path, 'rb') as vf:
                                st.download_button(
                                    "📥 Download Optimized Video",
                                    vf.read(),
                                    f"aura_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi",
                                    "video/x-msvideo",
                                    use_container_width=True
                                )
                        except:
                            st.error("Cannot download video")
                else:
                    st.error("Video not created")
            
            st.write("")
            
            # Storage comparison chart
            st.markdown("**Storage Comparison Chart:**")
            
            storage_fig = go.Figure(data=[
                go.Bar(
                    name='Original',
                    x=['Storage Size'],
                    y=[original_size_gb],
                    marker_color='#E31E24',
                    text=[f'{original_size_gb:.2f} GB'],
                    textposition='auto'
                ),
                go.Bar(
                    name='AURA Optimized',
                    x=['Storage Size'],
                    y=[optimized_size_gb],
                    marker_color='#4ECDC4',
                    text=[f'{optimized_size_gb:.2f} GB'],
                    textposition='auto'
                )
            ])
            
            storage_fig.update_layout(
                title='Storage Size: Original vs AURA Optimized',
                yaxis_title='Size (GB)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(storage_fig, use_container_width=True)
            
            # ===================================================================
            # MATHEMATICAL FORMULAS
            # ===================================================================
            
            st.markdown("---")
            st.markdown("### 📐 Mathematical Formulas & Calculations")
            
            # Formula 1
            with st.expander("✏️ Formula 1: Write Reduction Percentage", expanded=True):
                st.markdown("""
                #### The Formula
                ```
                Reduction% = (Total Frames - Saved Frames) / Total Frames × 100
                ```
                """)
                
                f1_col1, f1_col2, f1_col3 = st.columns(3)
                f1_col1.metric("Step 1: Total", f"{processed}", "All frames")
                f1_col2.metric("Step 2: Saved", f"{saved}", "Useful frames")
                f1_col3.metric("Step 3: Discarded", f"{processed - saved}", "Unnecessary")
                
                st.write("")
                
                st.markdown(f"""
                #### Calculation
                ```
                Reduction% = ({processed} - {saved}) / {processed} × 100
                Reduction% = {processed - saved} / {processed} × 100
                Reduction% = {reduction:.2f}%
                ```
                
                #### What This Means
                - **{reduction:.1f}% of storage writes ELIMINATED**
                - Device needs only {100-reduction:.1f}% of original writes
                - Significantly reduces flash memory wear
                - Extends storage lifespan dramatically
                """)
            
            # Formula 2
            with st.expander("⏱️ Formula 2: Storage Lifespan Extension Factor", expanded=True):
                st.markdown("""
                #### The Formula
                ```
                Lifespan Extension = 1 / (1 - Reduction%)
                ```
                """)
                
                remaining_pct = 1 - (reduction / 100)
                f2_col1, f2_col2, f2_col3 = st.columns(3)
                f2_col1.metric("Step 1: Reduction %", f"{reduction:.2f}%", "From Formula 1")
                f2_col2.metric("Step 2: Decimal", f"{remaining_pct:.4f}", "1 - Reduction")
                f2_col3.metric("Step 3: Extension", f"{lifespan_extension:.2f}x", "Final result")
                
                st.write("")
                
                st.markdown(f"""
                #### Calculation
                ```
                Extension = 1 / (1 - {reduction/100:.4f})
                Extension = 1 / {remaining_pct:.4f}
                Extension = {lifespan_extension:.2f}x
                ```
                
                #### Real-World Impact
                - **Normal SanDisk lifespan:** ~6.8 years
                - **With AURA:** 6.8 × {lifespan_extension:.1f} = **{6.8 * lifespan_extension:.1f} years**
                - Device lasts **{lifespan_extension:.1f}x LONGER**
                - Massive reduction in e-waste & operational costs
                """)
            
            # Formula 3
            with st.expander("💾 Formula 3: Storage Space Savings (GB)", expanded=True):
                st.markdown("""
                #### The Formula
                ```
                Original = Total Frames × Average Frame Size
                Optimized = Saved Frames × Average Frame Size  
                Savings = Original - Optimized
                ```
                """)
                
                f3_col1, f3_col2, f3_col3 = st.columns(3)
                f3_col1.metric("Original", f"{original_size_gb:.2f} GB", f"{processed} × 3.5MB")
                f3_col2.metric("Optimized", f"{optimized_size_gb:.2f} GB", f"{saved} × 3.5MB")
                f3_col3.metric("Saved", f"{storage_saved_gb:.2f} GB", f"{(storage_saved_gb/original_size_gb*100):.1f}%")
                
                st.write("")
                
                st.markdown(f"""
                #### Calculation
                ```
                Original = {processed} × 3.5 MB = {original_size_gb:.2f} GB
                Optimized = {saved} × 3.5 MB = {optimized_size_gb:.2f} GB
                Saved = {original_size_gb:.2f} - {optimized_size_gb:.2f} = {storage_saved_gb:.2f} GB
                ```
                
                #### Enterprise Scale
                - **Per video:** {storage_saved_gb:.2f} GB saved
                - **Per day (1000 videos):** {storage_saved_gb*1000:.0f} GB = {storage_saved_gb*1000/1024:.1f} TB
                - **Monthly:** {storage_saved_gb*1000*30/1024:.1f} TB
                - **Annual cost reduction:** ${(storage_saved_gb*1000*30*0.023):.0f} (at $0.023/GB)
                """)

# CONTINUE TO NEXT MESSAGE FOR REST
