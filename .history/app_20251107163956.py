"""
AURA MODULE 1 - FINAL WORKING VERSION
Complete rewrite with proper sections and video comparison
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
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="AURA Module 1",
    page_icon="🧠",
    layout="wide"
)

apply_custom_css()
show_hero()

tab1, tab2 = st.tabs(["📹 Video Analysis", "🖼️ Image Analysis"])

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    st.markdown('<div class="glass-card"><h3>📹 Upload Drone Video</h3><p>Upload drone footage for analysis</p></div>', unsafe_allow_html=True)
    
    video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if video_file:
        # Save and get info
        tmpdir = tempfile.mkdtemp()
        tfile = os.path.join(tmpdir, "input.mp4")
        with open(tfile, 'wb') as f:
            f.write(video_file.read())
        
        video_cap = cv2.VideoCapture(tfile)
        total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        video_cap.release()
        
        # Info display
        st.write("")
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        info_col1.metric("Frames", f"{total_frames}")
        info_col2.metric("FPS", f"{fps:.1f}")
        info_col3.metric("Duration", f"{duration:.1f}s")
        info_col4.metric("Resolution", f"{width}×{height}")
        
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            start_btn = st.button("🚀 START ANALYSIS", type="primary", use_container_width=True, key="start")
        
        if start_btn:
            # PROCESSING SECTION
            st.markdown("---")
            st.subheader("🔄 Processing Video...")
            
            frame_num = 0
            processed = 0
            last_frame = None
            counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0, "Duplicates": 0}
            results = []
            saved_frames = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            frame_img = st.empty()
            
            # Metrics placeholders
            st.write("")
            metric_row = st.columns(4)
            metric_p = metric_row[0].empty()
            metric_d = metric_row[1].empty()
            metric_s = metric_row[2].empty()
            metric_r = metric_row[3].empty()
            
            # Process
            video_cap = cv2.VideoCapture(tfile)
            start_time = time.time()
            max_frames = min(300, total_frames)
            
            while True:
                ret, frame = video_cap.read()
                if not ret or frame_num >= max_frames:
                    break
                
                progress_bar.progress(frame_num / total_frames)
                
                if frame_num % 5 == 0:
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_img.image(frame_rgb, caption=f"Frame {frame_num}/{total_frames}", use_column_width=True)
                    except:
                        pass
                
                category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                
                if category == "Discard" and detected == "duplicate_frame":
                    counts["Duplicates"] += 1
                counts[category] += 1
                processed += 1
                
                if category != "Discard":
                    saved_frames.append(frame)
                
                badge = get_category_badge(category)
                status_text.markdown(f'<div class="glass-card"><p><strong>Frame {frame_num}</strong> | {badge}</p><p>{detected} ({confidence:.0%}) | {latency*1000:.1f}ms</p></div>', unsafe_allow_html=True)
                
                results.append({"Frame": frame_num, "Category": category, "Object": detected, "Confidence": f"{confidence:.1%}"})
                
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = (1 - saved / max(processed, 1)) * 100
                
                metric_p.metric("Processed", processed)
                metric_d.metric("Duplicates", counts["Duplicates"])
                metric_s.metric("Saved", saved)
                metric_r.metric("Reduction %", f"{reduction:.1f}%")
                
                last_frame = frame.copy()
                frame_num += 1
            
            video_cap.release()
            elapsed = time.time() - start_time
            
            # RESULTS
            st.markdown("---")
            st.subheader("✅ Analysis Complete!")
            
            st.write("")
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            reduction = (1 - saved / processed) * 100 if processed > 0 else 0
            lifespan = 100 / (100 - reduction) if reduction < 100 else 999
            storage_saved = (processed - saved) * 3.5 / 1000
            
            # Final metrics
            final_col1, final_col2, final_col3, final_col4, final_col5 = st.columns(5)
            final_col1.metric("Total", processed)
            final_col2.metric("Saved", saved)
            final_col3.metric("Duplicates", counts["Duplicates"])
            final_col4.metric("Reduction", f"{reduction:.1f}%")
            final_col5.metric("Lifespan", f"{lifespan:.1f}x")
            
            # CREATE VIDEO
            st.markdown("---")
            st.subheader("🎬 Creating Optimized Video...")
            
            output_video = os.path.join(tmpdir, "optimized.mp4")
            if len(saved_frames) > 0:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
                for f in saved_frames:
                    writer.write(f)
                writer.release()
                st.success(f"✅ Video created: {len(saved_frames)} frames saved")
            
            # VIDEO COMPARISON
            st.markdown("---")
            st.subheader("🎥 Video Comparison: Original vs Optimized")
            
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.markdown("### Original Video")
                original_size = processed * 3.5 / 1000
                st.write(f"**Size:** {original_size:.2f} GB")
                st.write(f"**Frames:** {processed}")
                try:
                    st.video(open(tfile, 'rb'))
                except:
                    st.error("Could not load original video")
            
            with comp_col2:
                st.markdown("### Optimized Video (AURA)")
                optimized_size = saved * 3.5 / 1000
                st.write(f"**Size:** {optimized_size:.2f} GB")
                st.write(f"**Frames:** {saved}")
                try:
                    if os.path.exists(output_video):
                        st.video(open(output_video, 'rb'))
                    else:
                        st.error("Output video not created")
                except:
                    st.error("Could not load optimized video")
            
            # FORMULAS - CLEAN SECTION
            st.markdown("---")
            st.subheader("📐 Mathematical Formulas & Calculations")
            
            # Formula 1
            with st.expander("✏️ Formula 1: Write Reduction %", expanded=True):
                st.markdown(f"""
                ### The Formula
                ```
                Reduction% = (Total Frames - Saved Frames) / Total Frames × 100
                ```
                
                ### Step-by-Step Calculation
                """)
                
                calc1_col1, calc1_col2, calc1_col3 = st.columns(3)
                calc1_col1.metric("Step 1: Total", f"{processed} frames")
                calc1_col2.metric("Step 2: Saved", f"{saved} frames")
                calc1_col3.metric("Step 3: Discarded", f"{processed - saved} frames")
                
                st.markdown(f"""
                ### Final Result
                ```
                Reduction% = ({processed} - {saved}) / {processed} × 100
                Reduction% = {processed - saved} / {processed} × 100
                Reduction% = {reduction:.2f}%
                ```
                
                **What this means:**
                - {reduction:.1f}% of writes were ELIMINATED
                - Only {reduction:.1f}% fewer storage operations needed
                - Reduces wear on flash memory significantly
                """)
            
            # Formula 2
            with st.expander("⏱️ Formula 2: Storage Lifespan Extension", expanded=True):
                st.markdown(f"""
                ### The Formula
                ```
                Extension = 1 / (1 - Reduction%)
                ```
                
                ### Step-by-Step Calculation
                """)
                
                calc2_col1, calc2_col2, calc2_col3 = st.columns(3)
                calc2_col1.metric("Step 1: Reduction %", f"{reduction:.2f}%")
                remaining_pct = 100 - reduction
                calc2_col2.metric("Step 2: Remaining %", f"{remaining_pct:.2f}%")
                calc2_col3.metric("Step 3: Extension", f"{lifespan:.2f}x")
                
                st.markdown(f"""
                ### Final Result
                ```
                Extension = 1 / (1 - {reduction/100:.4f})
                Extension = 1 / {1 - reduction/100:.4f}
                Extension = {lifespan:.2f}x
                ```
                
                **What this means:**
                - Device lasts **{lifespan:.1f} times longer**
                - 6.8 years → {6.8 * lifespan:.1f} years
                - Massive lifespan improvement
                """)
            
            # Formula 3
            with st.expander("💾 Formula 3: Storage Space Savings", expanded=True):
                st.markdown(f"""
                ### The Formula
                ```
                Original = Total Frames × Average Frame Size
                Optimized = Saved Frames × Average Frame Size
                Savings = Original - Optimized
                ```
                
                ### Calculation
                """)
                
                calc3_col1, calc3_col2, calc3_col3 = st.columns(3)
                calc3_col1.metric("Original Size", f"{original_size:.2f} GB")
                calc3_col2.metric("Optimized Size", f"{optimized_size:.2f} GB")
                calc3_col3.metric("Storage Saved", f"{storage_saved:.2f} GB")
                
                st.markdown(f"""
                ### Result
                ```
                Original = {processed} × 3.5 MB = {original_size:.2f} GB
                Optimized = {saved} × 3.5 MB = {optimized_size:.2f} GB
                Saved = {original_size:.2f} - {optimized_size:.2f} = {storage_saved:.2f} GB
                ```
                
                **Impact:**
                - Save {storage_saved:.2f} GB per video
                - Multiply by 1000s of drones/cameras
                - Massive cost savings for enterprises
                """)
            
            # CHARTS
            st.markdown("---")
            st.subheader("📊 Classification Visualizations")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                pie_vals = [counts[c] for c in ["Critical", "Important", "Normal", "Discard"]]
                pie_labs = ["Critical", "Important", "Normal", "Discard"]
                pie_cols = [COLORS.get(l, "#999") for l in pie_labs]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=pie_labs,
                    values=pie_vals,
                    marker=dict(colors=pie_cols),
                    textinfo='label+percent'
                )])
                fig_pie.update_layout(title="Frame Distribution", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with chart_col2:
                bar_cats = ["Critical", "Important", "Normal", "Discard"]
                bar_vals = [counts[c] for c in bar_cats]
                bar_cols = [COLORS.get(c, "#999") for c in bar_cats]
                
                fig_bar = go.Figure(data=[go.Bar(x=bar_cats, y=bar_vals, marker=dict(color=bar_cols), text=bar_vals, textposition='auto')])
                fig_bar.update_layout(title="Frame Counts", xaxis_title="Category", yaxis_title="Count", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # BREAKDOWN
            st.markdown("---")
            st.subheader("📊 Storage by Category")
            
            break_col1, break_col2, break_col3, break_col4 = st.columns(4)
            break_col1.metric("🔴 Critical", f"{counts['Critical']} frames\n{counts['Critical']*3.5/1000:.2f}GB\nFull 4K")
            break_col2.metric("🟠 Important", f"{counts['Important']} frames\n{counts['Important']*1.5/1000:.2f}GB\n70% quality")
            break_col3.metric("🟢 Normal", f"{counts['Normal']} frames\n{counts['Normal']*0.3/1000:.2f}GB\n50% quality")
            break_col4.metric("⚪ Discard", f"{counts['Discard']} frames\n0.00GB\nNot saved")
            
            # DATA TABLE
            st.markdown("---")
            st.subheader("📋 Frame-by-Frame Details")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, height=300)
            
            # DOWNLOAD
            st.markdown("---")
            st.subheader("📥 Download Reports")
            csv = df.to_csv(index=False)
            st.download_button("📊 Download CSV", csv, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

# ============================================================================
# TAB 2: IMAGE ANALYSIS
# ============================================================================

with tab2:
    st.markdown('<div class="glass-card"><h3>🖼️ Single Image Analysis</h3></div>', unsafe_allow_html=True)
    
    img_file = st.file_uploader("Select image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if img_file:
        img_arr = np.array(bytearray(img_file.read()), dtype=np.uint8)
        img_bgr = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if img_bgr is not None:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            if st.button("🔍 ANALYZE", type="primary", use_container_width=True, key="img_btn"):
                img_col1, img_col2 = st.columns([1, 1])
                
                with img_col1:
                    st.image(img_rgb, caption="Input", use_column_width=True)
                
                with img_col2:
                    category, confidence, detected, metric, latency = classify_frame(img_bgr)
                    badge = get_category_badge(category)
                    st.markdown(f'<div class="glass-card"><h4>Result</h4><p>{badge}</p><p><strong>{detected}</strong></p><p>Confidence: {confidence:.1%}</p></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.85rem;"><p>AURA Module 1 | © 2025</p></div>', unsafe_allow_html=True)
