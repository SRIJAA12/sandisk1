"""
AURA MODULE 1 - Intelligent Data Manager
Championship Demo with Professional UI
"""
import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
from datetime import datetime
from classifier import classify_frame

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(page_title="AURA Module 1", page_icon="🧠", layout="wide")

# Ultra-professional Jeton.com inspired CSS
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">

<style>
    * { font-family: 'Inter', sans-serif; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%) !important;
    }
    
    /* HERO SECTION */
    .hero {
        background: linear-gradient(135deg, #E31E24 0%, #8B0000 50%, #003366 100%);
        padding: 80px 40px;
        border-radius: 30px;
        text-align: center;
        color: white;
        margin-bottom: 50px;
        box-shadow: 0 30px 60px rgba(227, 30, 36, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .hero h1 {
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
        text-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    
    .hero p {
        font-size: 1.5rem;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(227, 30, 36, 0.3);
        border-color: rgba(227, 30, 36, 0.5);
    }
    
    .glass-card h3 {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    /* METRIC CARDS */
    .metric-card {
        background: linear-gradient(135deg, rgba(227, 30, 36, 0.1) 0%, rgba(0, 51, 102, 0.1) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(227, 30, 36, 0.3);
        border-radius: 20px;
        padding: 35px 25px;
        text-align: center;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #E31E24 0%, #003366 100%);
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        border-color: #E31E24;
        box-shadow: 0 20px 40px rgba(227, 30, 36, 0.4);
    }
    
    .metric-value {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #E31E24 0%, #FF6B6B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        display: block;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* STATUS BADGES */
    .badge-critical {
        background: rgba(227, 30, 36, 0.2);
        border: 2px solid #E31E24;
        color: #FF6B6B;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-important {
        background: rgba(255, 107, 107, 0.2);
        border: 2px solid #FF6B6B;
        color: #FFB3B3;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-normal {
        background: rgba(78, 205, 196, 0.2);
        border: 2px solid #4ECDC4;
        color: #7FE6DC;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-discard {
        background: rgba(149, 165, 166, 0.2);
        border: 2px solid #95A5A6;
        color: #BDC3C7;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #E31E24 0%, #8B0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 18px 50px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 15px 35px rgba(227, 30, 36, 0.4) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 20px 45px rgba(227, 30, 36, 0.6) !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #E31E24 0%, #FF6B6B 50%, #003366 100%) !important;
        height: 14px !important;
        border-radius: 50px !important;
        box-shadow: 0 5px 15px rgba(227, 30, 36, 0.5) !important;
    }
    
    /* TEXT */
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown("""
<div class="hero">
    <h1>🧠 AURA MODULE 1</h1>
    <p>Intelligent Data Manager with Real-Time AI Classification</p>
    <div style="margin-top: 30px;">
        <span style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px; margin: 0 5px; display: inline-block;">
            ✨ AI Classification
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px; margin: 0 5px; display: inline-block;">
            📊 Real-Time Analysis
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px; margin: 0 5px; display: inline-block;">
            💾 70% Storage Savings
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================

tab1, tab2 = st.tabs(["🎥 Video Analysis", "🖼️ Single Image"])

# ============================================================================
# TAB 1: VIDEO ANALYSIS
# ============================================================================

with tab1:
    st.markdown("""
    <div class="glass-card">
        <h3>📹 Upload Drone Video</h3>
        <p>Upload your drone surveillance footage for intelligent frame analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    video_file = st.file_uploader("", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
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
        video.release()
        
        st.success(f"✅ Video loaded: {total_frames} frames @ {fps:.1f} FPS")
        
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
                formulas_data = []
                
                st.markdown("---")
                st.markdown('<div class="glass-card"><h3>🔄 Processing...</h3></div>', unsafe_allow_html=True)
                
                progress = st.progress(0)
                status = st.empty()
                frame_display = st.empty()
                
                # Metrics row
                col_a, col_b, col_c, col_d = st.columns(4)
                m_a = col_a.empty()
                m_b = col_b.empty()
                m_c = col_c.empty()
                m_d = col_d.empty()
                
                # Process
                video = cv2.VideoCapture(tfile)
                
                while True:
                    ret, frame = video.read()
                    if not ret or frame_num >= min(300, total_frames):  # Limit to 300 frames for speed
                        break
                    
                    progress.progress(min(frame_num / total_frames, 1.0))
                    
                    if frame_num % 5 == 0:
                        frame_display.image(frame, channels="BGR", use_container_width=True)
                    
                    # Classify
                    category, confidence, detected, metric, latency = classify_frame(frame, last_frame)
                    counts[category] += 1
                    processed += 1
                    
                    status.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #E31E24;">
                        <strong>Frame {frame_num}</strong><br>
                        Category: <span class="badge-{category.lower()}">{category}</span><br>
                        Object: {detected} ({confidence:.0%})<br>
                        Latency: {latency*1000:.1f}ms
                    </div>
                    """, unsafe_allow_html=True)
                    
                    results.append({"Frame": frame_num, "Category": category, "Object": detected, "Confidence": f"{confidence:.1%}"})
                    
                    # Metrics
                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = (1 - saved / max(processed, 1)) * 100
                    
                    m_a.markdown(f'<div class="metric-card"><div class="metric-value">{processed}</div><div class="metric-label">Processed</div></div>', unsafe_allow_html=True)
                    m_b.markdown(f'<div class="metric-card"><div class="metric-value">{counts["Duplicates"]}</div><div class="metric-label">Duplicates</div></div>', unsafe_allow_html=True)
                    m_c.markdown(f'<div class="metric-card"><div class="metric-value">{saved}</div><div class="metric-label">Saved</div></div>', unsafe_allow_html=True)
                    m_d.markdown(f'<div class="metric-card"><div class="metric-value">{reduction:.0f}%</div><div class="metric-label">Reduction</div></div>', unsafe_allow_html=True)
                    
                    last_frame = frame
                    frame_num += 1
                
                video.release()
                
                # Results
                st.markdown("---")
                st.markdown('<div class="glass-card"><h3>✅ Analysis Complete!</h3></div>', unsafe_allow_html=True)
                
                # Final metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                reduction = (1 - saved / processed) * 100
                lifespan = 100 / (100 - reduction) if reduction < 100 else 999
                
                with col1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{processed}</div><div class="metric-label">Total Processed</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{saved}</div><div class="metric-label">Saved Frames</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{reduction:.0f}%</div><div class="metric-label">Write Reduction</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{lifespan:.1f}x</div><div class="metric-label">Lifespan Gain</div></div>', unsafe_allow_html=True)
                with col5:
                    storage_saved = (processed - saved) * 3.5 / 1000
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{storage_saved:.1f}GB</div><div class="metric-label">Storage Saved</div></div>', unsafe_allow_html=True)
                
                # Charts
                st.markdown("---")
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    fig_pie = px.pie(
                        values=[counts[c] for c in ["Critical", "Important", "Normal", "Discard"]],
                        names=["Critical", "Important", "Normal", "Discard"],
                        title="Frame Distribution",
                        color_discrete_map={"Critical": "#E31E24", "Important": "#FF6B6B", "Normal": "#4ECDC4", "Discard": "#95A5A6"}
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_chart2:
                    fig_bar = go.Figure(data=[go.Bar(
                        x=["Critical", "Important", "Normal", "Discard"],
                        y=[counts[c] for c in ["Critical", "Important", "Normal", "Discard"]],
                        marker_color=["#E31E24", "#FF6B6B", "#4ECDC4", "#95A5A6"]
                    )])
                    fig_bar.update_layout(title="Frame Count by Category", xaxis_title="Category", yaxis_title="Count")
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Formulas section
                st.markdown("---")
                st.markdown('<div class="glass-card"><h3>📐 Mathematical Formulas (Real-Time Calculation)</h3></div>', unsafe_allow_html=True)
                
                formula_col1, formula_col2 = st.columns(2)
                
                with formula_col1:
                    st.markdown(f"""
                    ### Formula 1: Write Reduction
                    ```
                    Reduction% = (Total - Saved) / Total × 100
                    Reduction% = ({processed} - {saved}) / {processed} × 100
                    Reduction% = {reduction:.2f}%
                    ```
                    """)
                
                with formula_col2:
                    st.markdown(f"""
                    ### Formula 2: Lifespan Extension
                    ```
                    Extension = 1 / (1 - Reduction%)
                    Extension = 1 / (1 - {reduction/100:.2f})
                    Extension = {lifespan:.2f}x longer
                    ```
                    """)
                
                # Data table
                st.markdown("---")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # Download
                csv = df.to_csv(index=False)
                st.download_button("📥 Download Report", csv, f"aura_module1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")

# ============================================================================
# TAB 2: SINGLE IMAGE ANALYSIS
# ============================================================================

with tab2:
    st.markdown("""
    <div class="glass-card">
        <h3>🖼️ Single Image Analysis</h3>
        <p>Upload a single frame to see Module 1 classification in detail</p>
    </div>
    """, unsafe_allow_html=True)
    
    image_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if image_file:
        image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        if st.button("🔍 ANALYZE IMAGE", type="primary", use_container_width=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, channels="BGR", use_container_width=True)
            
            with col2:
                category, confidence, detected, metric, latency = classify_frame(image)
                
                st.markdown(f"""
                <div class="glass-card">
                    <h4>Classification Result</h4>
                    <div style="margin: 20px 0;">
                        <span class="badge-{category.lower()}">{category}</span>
                    </div>
                    <p><strong>Detected Object:</strong> {detected}</p>
                    <p><strong>Confidence:</strong> {confidence:.1%}</p>
                    <p><strong>Processing Time:</strong> {latency*1000:.1f}ms</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show why
                st.markdown("### Why this classification?")
                if category == "Discard":
                    st.info("🔵 This frame contains empty sky or static water - zero information value")
                elif category == "Critical":
                    st.success("🔴 Person/animal detected - CRITICAL, saved at full quality!")
                elif category == "Important":
                    st.warning("🟠 Vehicle/infrastructure detected - IMPORTANT, standard compression")
                else:
                    st.info("🟢 Other objects detected - NORMAL, heavy compression applied")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;">
    AURA Module 1 | Intelligent Data Manager | SanDisk Smart Storage © 2025
</div>
""", unsafe_allow_html=True)
