"""
AURA MODULE 1 - FAST DEMO VERSION FOR JUDGES
Ultra-optimized version that processes only 10-20 frames for quick demonstration
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import time
from classifier import classify_frame
from ui_components import apply_custom_css, get_category_badge

# PAGE CONFIG
st.set_page_config(
    page_title="AURA Module 1 - FAST DEMO",
    layout="wide"
)

apply_custom_css()

# HERO SECTION
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <div class="hero-logo">🧠</div>
        <h1 class="hero-title">AURA MODULE 1</h1>
        <h2 class="hero-subtitle">Intelligent Data Manager - FAST DEMO</h2>
        <div class="hero-tags">
            <span class="hero-tag">AI-Powered</span>
            <span class="hero-tag">Real-Time</span>
            <span class="hero-tag">Edge Optimized</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Initialize session state for thresholds
if 'thresholds' not in st.session_state:
    st.session_state.thresholds = {
        'yolo_confidence': 0.5,
        'ssim_threshold': 0.97,
        'sky_threshold': 0.8,
        'edge_threshold': 0.01
    }

# DEMO SECTION
st.markdown("### 🎬 FAST DEMO - Upload Video for Instant Analysis")
st.info("⚡ **DEMO MODE**: Processes only 10-20 frames for quick demonstration to judges")

video_file = st.file_uploader("Select video", type=["mp4", "avi", "mov"], label_visibility="collapsed")

if video_file:
    # Save uploaded video
    tmpdir = tempfile.mkdtemp()
    input_path = os.path.join(tmpdir, "demo_input.mp4")
    
    with open(input_path, "wb") as f:
        f.write(video_file.read())
    
    # Extract video metadata
    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Show video info
    info_cols = st.columns(4)
    info_cols[0].metric("Total Frames", f"{total_frames}")
    info_cols[1].metric("FPS", f"{fps:.1f}")
    info_cols[2].metric("Demo Frames", "10-20")
    info_cols[3].metric("Resolution", f"{width}×{height}")
    
    # FAST DEMO PROCESSING
    if st.button("🚀 START FAST DEMO", type="primary", use_container_width=True):
        st.markdown("### ⚡ Real-Time Analysis in Progress...")
        
        # Create display areas
        display_col1, display_col2 = st.columns(2)
        frame_display = display_col1.empty()
        status_display = display_col2.empty()
        
        # Metrics
        metrics_cols = st.columns(4)
        metric_processed = metrics_cols[0].empty()
        metric_critical = metrics_cols[1].empty()
        metric_saved = metrics_cols[2].empty()
        metric_discarded = metrics_cols[3].empty()
        
        # Progress bar
        progress_bar = st.progress(0)
        
        # Process only 15 frames for demo
        cap = cv2.VideoCapture(input_path)
        demo_frames = 15
        frame_skip = max(1, total_frames // demo_frames)  # Skip frames to get 15 samples
        
        counts = {"Critical": 0, "Important": 0, "Normal": 0, "Discard": 0}
        processed = 0
        frame_num = 0
        
        start_time = time.time()
        
        for i in range(demo_frames):
            # Jump to specific frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_skip)
            ret, frame = cap.read()
            
            if not ret:
                break
                
            frame_num = i * frame_skip
            processed += 1
            
            # Update progress
            progress_bar.progress(processed / demo_frames)
            
            # Show current frame
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_display.image(display_frame, caption=f"Analyzing Frame {frame_num}", use_container_width=True)
            
            # Classify frame
            category, confidence, detected, metric, latency = classify_frame(frame, None, st.session_state.thresholds)
            counts[category] += 1
            
            # Update status
            badge = get_category_badge(category)
            status_display.markdown(
                f"<div class='glass-card'>"
                f"<h4>🎯 Analysis Result</h4>"
                f"<p><strong>Frame {frame_num}</strong> | {badge}</p>"
                f"<p>📊 Object: <strong>{detected}</strong></p>"
                f"<p>🎯 Confidence: <strong>{confidence:.0%}</strong></p>"
                f"<p>⚡ Speed: <strong>{latency*1000:.1f}ms</strong></p>"
                f"</div>",
                unsafe_allow_html=True,
            )
            
            # Update metrics
            saved = counts["Critical"] + counts["Important"] + counts["Normal"]
            metric_processed.metric("Processed", processed)
            metric_critical.metric("Critical", counts["Critical"])
            metric_saved.metric("Saved", saved)
            metric_discarded.metric("Discarded", counts["Discard"])
            
            # Small delay for demo effect
            time.sleep(0.3)
        
        cap.release()
        elapsed_time = time.time() - start_time
        
        # RESULTS
        st.markdown("---")
        st.success("### ✅ FAST DEMO COMPLETE!")
        
        saved = counts["Critical"] + counts["Important"] + counts["Normal"]
        reduction = (counts["Discard"] / processed) * 100 if processed > 0 else 0
        
        # Final metrics
        result_cols = st.columns(4)
        result_cols[0].metric("Demo Frames Processed", processed, f"{processed/elapsed_time:.1f} fps")
        result_cols[1].metric("Frames Saved", saved, f"{(saved/processed)*100:.1f}%")
        result_cols[2].metric("Frames Discarded", counts["Discard"], f"{reduction:.1f}%")
        result_cols[3].metric("Processing Speed", f"{elapsed_time:.1f}s", "Ultra Fast!")
        
        # Show breakdown
        st.markdown("### 📊 Classification Breakdown")
        breakdown_cols = st.columns(4)
        
        categories = ["Critical", "Important", "Normal", "Discard"]
        colors = ["#E31E24", "#FF6B6B", "#4ECDC4", "#95A5A6"]
        
        for i, (cat, color) in enumerate(zip(categories, colors)):
            with breakdown_cols[i]:
                count = counts[cat]
                percentage = (count / processed) * 100 if processed > 0 else 0
                st.markdown(
                    f"<div style='background: {color}; padding: 15px; border-radius: 10px; text-align: center; color: white;'>"
                    f"<h3>{cat}</h3>"
                    f"<h2>{count}</h2>"
                    f"<p>{percentage:.1f}%</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        # Demo explanation
        st.markdown("---")
        st.markdown("### 🎯 What This Demo Shows Judges")
        
        demo_points = st.columns(2)
        
        with demo_points[0]:
            st.markdown("""
            **🧠 AI Intelligence:**
            - Real-time object detection using YOLOv8
            - Smart classification (Critical/Important/Normal/Discard)
            - Duplicate frame detection
            - Empty sky/water detection
            """)
        
        with demo_points[1]:
            st.markdown("""
            **⚡ Performance Benefits:**
            - Reduces storage writes by discarding unnecessary frames
            - Extends SSD lifespan significantly
            - Maintains critical data integrity
            - Edge-optimized processing
            """)
        
        st.success("🎉 **DEMO READY FOR JUDGES!** This shows AURA's intelligent data management in action.")

# BACKUP DEMO SECTION
st.markdown("---")
st.markdown("### 🎯 Alternative: Image Analysis Demo")
st.info("If video upload is slow, use this instant image analysis demo")

uploaded_image = st.file_uploader("Upload a single image for instant analysis", type=["jpg", "jpeg", "png"])

if uploaded_image:
    # Convert uploaded file to opencv format
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(img_rgb, caption="Input Image", use_container_width=True)
    
    with col2:
        # Analyze image
        category, confidence, detected, metric, latency = classify_frame(img_bgr, None, st.session_state.thresholds)
        badge = get_category_badge(category)
        
        st.markdown(
            f"<div class='glass-card'>"
            f"<h4>🎯 Instant Analysis Result</h4>"
            f"<p>{badge}</p>"
            f"<p>📊 Detected: <strong>{detected}</strong></p>"
            f"<p>🎯 Confidence: <strong>{confidence:.0%}</strong></p>"
            f"<p>⚡ Processing Time: <strong>{latency*1000:.1f}ms</strong></p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        
        # Explanation
        if category == "Critical":
            st.error("🚨 **CRITICAL**: Contains important objects (people, animals) - MUST SAVE")
        elif category == "Important":
            st.warning("⚠️ **IMPORTANT**: Contains vehicles/infrastructure - SHOULD SAVE")
        elif category == "Normal":
            st.info("ℹ️ **NORMAL**: General content - SAVE")
        else:
            st.success("✅ **DISCARD**: Empty/duplicate content - SAVE STORAGE")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.6); padding: 20px;">
    <p>🧠 AURA Module 1 - Fast Demo Version for Judges</p>
    <p>Intelligent • Real-Time • Edge-Optimized</p>
</div>
""", unsafe_allow_html=True)
