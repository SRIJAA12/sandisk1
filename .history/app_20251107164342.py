"""
AURA MODULE 1 - INTELLIGENT DATA MANAGER
Complete Production-Ready Application
Real-Time Video Processing with AI Classification
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

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AURA Module 1 - Intelligent Data Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Display hero section
show_hero()

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2 = st.tabs(["📹 Video Analysis", "🖼️ Image Analysis"])

# ============================================================================
# ============================================================================
# TAB 1: VIDEO ANALYSIS - MAIN FEATURE
# ============================================================================
# ============================================================================

with tab1:
    # Header section
    st.markdown(
        '<div class="glass-card"><h3>📹 Upload Drone Video</h3><p>Upload your drone footage for intelligent frame-by-frame analysis and optimization</p></div>',
        unsafe_allow_html=True
    )
    
    # File uploader
    video_file = st.file_uploader(
        "Select video file",
        type=["mp4", "avi", "mov"],
        label_visibility="collapsed"
    )
    
    if video_file:
        # Save uploaded video to temporary location
        tmpdir = tempfile.mkdtemp()
        tfile = os.path.join(tmpdir, "input_video.mp4")
        with open(tfile, 'wb') as f:
            f.write(video_file.read())
        
        # Extract video information
        video_capture = cv2.VideoCapture(tfile)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        video_capture.release()
        
        # Display video information in metrics
        st.write("")  # Spacing
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        
        info_col1.metric(
            label="Total Frames",
            value=f"{total_frames}"
        )
        info_col2.metric(
            label="FPS",
            value=f"{fps:.1f}"
        )
        info_col3.metric(
            label="Duration",
            value=f"{duration:.1f}s"
        )
        info_col4.metric(
            label="Resolution",
            value=f"{width}×{height}"
        )
        
        # Add spacing
        st.write("")
        
        # Start analysis button
        button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
        with button_col2:
            start_analysis_button = st.button(
                "🚀 START ANALYSIS",
                type="primary",
                use_container_width=True,
                key="start_analysis_btn"
            )
        
        # MAIN PROCESSING LOGIC
        if start_analysis_button:
            
            # Initialize variables
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
            
            # Create processing UI section
            st.markdown("---")
            st.subheader("🔄 Processing Video Frames...")
            
            # Progress bar
            progress_bar = st.progress(0, text="Initializing...")
            
            # Status display
            status_text = st.empty()
            
            # Frame display
            st.write("")
            frame_display_container = st.empty()
            
            # Metrics display - SEPARATED TO AVOID OVERLAP
            st.write("")
            metrics_header = st.markdown("### Processing Metrics")
            
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            metric_processed = metrics_col1.empty()
            metric_duplicates = metrics_col2.empty()
            metric_saved = metrics_col3.empty()
            metric_reduction = metrics_col4.empty()
            
            # Open video file for processing
            video_capture = cv2.VideoCapture(tfile)
            processing_start_time = time.time()
            
            # Set maximum frames to process for performance
            max_frames_to_process = min(300, total_frames)
            
            # Frame processing loop
            while True:
                ret, frame = video_capture.read()
                
                # Exit loop if video ended or max frames reached
                if not ret or frame_num >= max_frames_to_process:
                    break
                
                # Update progress bar
                progress_value = frame_num / total_frames
                progress_bar.progress(
                    min(progress_value, 1.0),
                    text=f"Processing: {frame_num}/{total_frames} frames"
                )
                
                # Display frame preview every 5 frames
                if frame_num % 5 == 0:
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_display_container.image(
                            frame_rgb,
                            caption=f"Current Frame: {frame_num}/{total_frames}",
                            use_column_width=True
                        )
                    except Exception as e:
                        pass
                
                # Classify the current frame
                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                
                # Update counters
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                
                counts[category] += 1
                processed += 1
                
                # Store frames that will be saved (for video reconstruction)
                if category != "Discard":
                    saved_frames.append(frame)
                
                # Create badge for category
                badge_html = get_category_badge(category)
                
                # Update status display
                status_text.markdown(
                    f"""
                    <div class="glass-card">
                        <p><strong>Frame {frame_num}</strong> | {badge_html}</p>
                        <p>Detected: <strong>{detected}</strong> | Confidence: <strong>{confidence:.0%}</strong> | Latency: <strong>{latency*1000:.1f}ms</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Store results for report
                results.append({
                    "Frame": frame_num,
                    "Category": category,
                    "Object": detected,
                    "Confidence": f"{confidence:.1%}",
                    "Latency (ms)": f"{latency*1000:.1f}"
                })
                
                # Calculate current metrics
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = (1 - saved / max(processed, 1)) * 100
                
                # Update metric displays with clean format
                metric_processed.metric(
                    "Processed",
                    processed,
                    f"{int(processed/elapsed_time) if elapsed_time > 0 else 0} fps"
                ) if 'elapsed_time' in locals() else metric_processed.metric("Processed", processed)
                
                metric_duplicates.metric(
                    "Duplicates",
                    counts["Duplicates"]
                )
                
                metric_saved.metric(
                    "Saved",
                    saved
                )
                
                metric_reduction.metric(
                    "Reduction %",
                    f"{reduction:.1f}%"
                )
                
                # Update last frame for duplicate detection
                last_frame = frame.copy()
                frame_num += 1
            
            # Release video capture
            video_capture.release()
            elapsed_time = time.time() - processing_start_time
            
            # ===================================================================
            # RESULTS SECTION - COMPLETE
            # ===================================================================
            
            st.markdown("---")
            st.subheader("✅ Analysis Complete!")
            
            st.write("")
            
            # Calculate final metrics
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
            storage_saved_gb = (processed - saved) * 3.5 / 1000
            original_size_gb = processed * 3.5 / 1000
            optimized_size_gb = saved * 3.5 / 1000
            
            # Final metrics display - CLEAN LAYOUT
            st.subheader("📊 Final Metrics")
            final_metric_col1, final_metric_col2, final_metric_col3, final_metric_col4, final_metric_col5 = st.columns(5)
            
            final_metric_col1.metric(
                "Total Processed",
                processed,
                f"{processed/elapsed_time:.1f} fps"
            )
            final_metric_col2.metric(
                "Frames Saved",
                saved,
                f"{saved/processed*100:.1f}%"
            )
            final_metric_col3.metric(
                "Duplicates",
                counts["Duplicates"],
                f"{counts['Duplicates']/processed*100:.1f}%"
            )
            final_metric_col4.metric(
                "Write Reduction",
                f"{reduction:.1f}%",
                "Lower is better"
            )
            final_metric_col5.metric(
                "Lifespan Extension",
                f"{lifespan_extension:.1f}x",
                "Higher is better"
            )
            
            # ===================================================================
            # VIDEO CREATION AND COMPARISON
            # ===================================================================
            
            st.markdown("---")
            st.subheader("🎬 Video Reconstruction and Comparison")
            
            st.write("Creating optimized video from processed frames...")
            
            # Create output video
            output_video_path = os.path.join(tmpdir, "optimized_video.mp4")
            
            if len(saved_frames) > 0:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out_writer = cv2.VideoWriter(
                        output_video_path,
                        fourcc,
                        fps,
                        (width, height)
                    )
                    
                    for frame in saved_frames:
                        out_writer.write(frame)
                    
                    out_writer.release()
                    
                    st.success(f"✅ Optimized video created successfully with {len(saved_frames)} frames!")
                
                except Exception as e:
                    st.error(f"❌ Error creating video: {str(e)}")
            else:
                st.warning("⚠️ No frames to save")
            
            st.write("")
            
            # VIDEO COMPARISON - SIDE BY SIDE
            st.subheader("🎥 Before vs After Video Comparison")
            
            comparison_col1, comparison_col2 = st.columns(2)
            
            with comparison_col1:
                st.markdown("### Original Video (All Frames)")
                st.markdown(f"**Storage Size:** {original_size_gb:.2f} GB")
                st.markdown(f"**Frame Count:** {processed}")
                st.markdown(f"**Duration:** {duration:.1f}s")
                
                try:
                    with open(tfile, 'rb') as video_file_read:
                        st.video(video_file_read.read())
                except Exception as e:
                    st.error(f"Could not load original video: {str(e)}")
            
            with comparison_col2:
                st.markdown("### Optimized Video (AURA Processed)")
                st.markdown(f"**Storage Size:** {optimized_size_gb:.2f} GB")
                st.markdown(f"**Frame Count:** {saved}")
                st.markdown(f"**Storage Saved:** {storage_saved_gb:.2f} GB ({reduction:.1f}%)")
                
                try:
                    if os.path.exists(output_video_path):
                        with open(output_video_path, 'rb') as video_file_read:
                            st.video(video_file_read.read())
                    else:
                        st.error("Output video file not found")
                except Exception as e:
                    st.error(f"Could not load optimized video: {str(e)}")
            
            st.write("")
            
            # Impact visualization
            st.markdown("---")
            st.subheader("💾 Storage Comparison Chart")
            
            storage_fig = go.Figure(data=[
                go.Bar(name='Original', x=['Storage Size'], y=[original_size_gb], marker_color='#E31E24'),
                go.Bar(name='AURA Optimized', x=['Storage Size'], y=[optimized_size_gb], marker_color='#4ECDC4')
            ])
            
            storage_fig.update_layout(
                barmode='group',
                title='Storage Size: Original vs AURA Optimized',
                yaxis_title='Size (GB)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(storage_fig, use_container_width=True)
            
            # ===================================================================
            # MATHEMATICAL FORMULAS SECTION
            # ===================================================================
            
            st.markdown("---")
            st.subheader("📐 Mathematical Formulas & Real-Time Calculations")
            
            # Formula 1: Write Reduction
            with st.expander("✏️ Formula 1: Write Reduction Percentage", expanded=True):
                
                st.markdown("""
                ### The Formula
                ```
                Reduction% = (Total Frames - Saved Frames) / Total Frames × 100
                ```
                
                ### What Each Component Means
                - **Total Frames:** All frames in the original video
                - **Saved Frames:** Frames with useful information (Critical + Important + Normal)
                - **Reduction %:** Percentage of unnecessary storage writes eliminated
                """)
                
                # Step by step calculation
                st.markdown("### Step-by-Step Calculation")
                
                formula1_step_col1, formula1_step_col2, formula1_step_col3 = st.columns(3)
                
                formula1_step_col1.metric(
                    "Step 1: Total Frames",
                    f"{processed}",
                    "All frames in video"
                )
                formula1_step_col2.metric(
                    "Step 2: Saved Frames",
                    f"{saved}",
                    "Only useful frames"
                )
                formula1_step_col3.metric(
                    "Step 3: Discarded",
                    f"{processed - saved}",
                    "Duplicates + Empty"
                )
                
                st.write("")
                
                st.markdown(f"""
                ### Final Calculation
                ```
                Reduction% = ({processed} - {saved}) / {processed} × 100
                Reduction% = {processed - saved} / {processed} × 100
                Reduction% = {reduction:.2f}%
                ```
                
                ### Interpretation
                - **{reduction:.1f}% of writes were ELIMINATED**
                - Storage controller receives **{100-reduction:.1f}% of original write operations**
                - Dramatically reduces wear on NAND flash memory
                - Extends device lifespan significantly
                """)
            
            # Formula 2: Lifespan Extension
            with st.expander("⏱️ Formula 2: Storage Lifespan Extension Factor", expanded=True):
                
                st.markdown("""
                ### The Formula
                ```
                Lifespan Extension = 1 / (1 - Reduction%)
                ```
                
                ### What Each Component Means
                - **Reduction %:** Percentage of writes eliminated (as decimal: e.g., 0.70 for 70%)
                - **(1 - Reduction%):** Fraction of original writes still performed
                - **1 / Result:** How many times longer the device lasts
                """)
                
                # Step by step calculation
                st.markdown("### Step-by-Step Calculation")
                
                formula2_step_col1, formula2_step_col2, formula2_step_col3 = st.columns(3)
                
                formula2_step_col1.metric(
                    "Step 1: Reduction %",
                    f"{reduction:.2f}%",
                    "From Formula 1"
                )
                
                remaining_decimal = 1 - (reduction / 100)
                formula2_step_col2.metric(
                    "Step 2: Remaining (1 - R%)",
                    f"{remaining_decimal:.4f}",
                    "Decimal form"
                )
                
                formula2_step_col3.metric(
                    "Step 3: Extension Factor",
                    f"{lifespan_extension:.2f}x",
                    "Final result"
                )
                
                st.write("")
                
                st.markdown(f"""
                ### Final Calculation
                ```
                Extension = 1 / (1 - {reduction/100:.4f})
                Extension = 1 / {remaining_decimal:.4f}
                Extension = {lifespan_extension:.2f}x
                ```
                
                ### Real-World Impact
                - **Standard SanDisk Storage Lifespan:** ~6.8 years
                - **With AURA:** 6.8 × {lifespan_extension:.1f} = **{6.8 * lifespan_extension:.1f} years**
                - Storage device lasts **{lifespan_extension:.1f} TIMES LONGER**
                - Reduces e-waste and operational costs
                """)

