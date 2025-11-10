"""
UI Components for AURA Module 1
Reusable UI elements and styling
"""

import streamlit as st
import os
from config import COLORS

def apply_custom_css():
    """Apply enhanced custom CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .aura-container {
      min-height: 100vh;
      background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
      color: white;
      padding: 20px;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }

    .hero-section {
      background: linear-gradient(135deg, #E31E24 0%, #8B0000 50%, #003366 100%);
      border-radius: 24px;
      padding: 60px 40px;
      text-align: center;
      margin-bottom: 40px;
      box-shadow: 0 20px 60px rgba(227, 30, 36, 0.5);
    }

    .hero-content {
      position: relative;
      z-index: 1;
    }

    .hero-logo {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 80px;
      height: 80px;
      background: rgba(255,255,255,0.2);
      border-radius: 50%;
      margin-bottom: 20px;
    }

    .hero-title {
      font-size: 3rem;
      font-weight: 900;
      margin-bottom: 10px;
    }

    .hero-subtitle {
      font-size: 1.2rem;
      opacity: 0.95;
      margin-bottom: 25px;
    }

    .hero-tags {
      display: flex;
      justify-content: center;
      gap: 15px;
      flex-wrap: wrap;
    }

    .hero-tag {
      background: rgba(255,255,255,0.2);
      padding: 10px 20px;
      border-radius: 50px;
      font-size: 0.9rem;
      font-weight: 600;
    }

    .main-content {
      max-width: 1400px;
      margin: 0 auto;
    }

    .glass-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 35px;
      margin-bottom: 30px;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    }

    .glass-card h3 {
      font-size: 1.6rem;
      font-weight: 700;
      margin-bottom: 20px;
      color: white;
    }

    .upload-card {
      text-align: center;
    }

    .upload-area {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px;
      border: 3px dashed rgba(227, 30, 36, 0.5);
      border-radius: 16px;
      margin: 30px 0;
      cursor: pointer;
      transition: all 0.3s ease;
      background: rgba(227, 30, 36, 0.05);
    }

    .upload-area:hover {
      border-color: #E31E24;
      background: rgba(227, 30, 36, 0.1);
    }

    .upload-area svg {
      color: #E31E24;
      margin-bottom: 15px;
    }

    .upload-area p {
      font-size: 1.2rem;
      margin-bottom: 8px;
    }

    .upload-hint {
      font-size: 0.9rem;
      opacity: 0.6;
    }

    .video-preview {
      margin: 20px 0;
      text-align: center;
    }

    .process-button {
      background: linear-gradient(135deg, #E31E24 0%, #8B0000 100%);
      color: white;
      border: none;
      padding: 15px 40px;
      font-size: 1rem;
      font-weight: 700;
      border-radius: 50px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 10px 25px rgba(227, 30, 36, 0.3);
      transition: all 0.3s ease;
      margin-top: 20px;
    }

    .process-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 15px 35px rgba(227, 30, 36, 0.5);
    }

    .progress-section {
      margin-top: 30px;
    }

    .progress-bar {
      width: 100%;
      height: 16px;
      background: rgba(255,255,255,0.1);
      border-radius: 50px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #E31E24 0%, #FF6B6B 50%, #003366 100%);
      border-radius: 50px;
      transition: width 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 15px;
    }

    .progress-text {
      font-size: 0.75rem;
      font-weight: 700;
    }

    .progress-label {
      margin-top: 15px;
      font-size: 1rem;
      opacity: 0.8;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }

    .metric-card {
      background: rgba(255, 255, 255, 0.05);
      border: 2px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 25px;
      text-align: center;
      transition: all 0.3s ease;
    }

    .metric-card:hover {
      transform: translateY(-5px);
      border-color: rgba(227, 30, 36, 0.5);
    }

    .metric-icon {
      width: 60px;
      height: 60px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 15px;
      color: white;
    }

    .metric-value {
      font-size: 2.5rem;
      font-weight: 900;
      color: #FF6B6B;
      margin-bottom: 8px;
    }

    .metric-label {
      font-size: 0.9rem;
      color: rgba(255, 255, 255, 0.6);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 5px;
    }

    .metric-change {
      font-size: 0.85rem;
      color: #4ECDC4;
      font-weight: 600;
    }

    .categories-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }

    .category-badge {
      background: rgba(255, 255, 255, 0.05);
      border: 2px solid;
      border-radius: 16px;
      padding: 20px;
      transition: all 0.3s ease;
    }

    .category-badge:hover {
      transform: translateY(-5px);
    }

    .badge-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;
    }

    .badge-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .badge-title {
      font-size: 0.9rem;
      font-weight: 700;
      letter-spacing: 1px;
    }

    .badge-stats {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }

    .badge-count {
      font-size: 2rem;
      font-weight: 900;
    }

    .badge-percentage {
      font-size: 1.2rem;
      opacity: 0.7;
    }

    .comparison-container {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      gap: 30px;
      align-items: center;
      margin: 30px 0;
    }

    @media (max-width: 1024px) {
      .comparison-container {
        grid-template-columns: 1fr;
      }
    }

    .video-panel {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 16px;
      padding: 20px;
      border: 2px solid rgba(255, 255, 255, 0.1);
    }

    .video-panel.original {
      border-color: rgba(227, 30, 36, 0.3);
    }

    .video-panel.optimized {
      border-color: rgba(78, 205, 196, 0.3);
    }

    .video-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
    }

    .video-header h4 {
      font-size: 1.2rem;
      font-weight: 700;
    }

    .video-badge {
      padding: 6px 16px;
      border-radius: 50px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .original-badge {
      background: rgba(227, 30, 36, 0.2);
      color: #FF6B6B;
    }

    .optimized-badge {
      background: rgba(78, 205, 196, 0.2);
      color: #4ECDC4;
    }

    .video-player {
      width: 100%;
      border-radius: 12px;
      background: #000;
      display: block;
      margin-bottom: 15px;
    }

    .video-stats {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    .stat-item {
      background: rgba(255, 255, 255, 0.05);
      padding: 12px;
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
    }

    .stat-label {
      font-size: 0.85rem;
      opacity: 0.7;
    }

    .stat-value {
      font-weight: 700;
    }

    .stat-value.red {
      color: #FF6B6B;
    }

    .stat-value.green {
      color: #4ECDC4;
    }

    .comparison-arrow {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }

    .arrow-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #E31E24 0%, #003366 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 10px 30px rgba(227, 30, 36, 0.4);
    }

    .arrow-label {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .optimized-overlay {
      position: absolute;
      top: 10px;
      left: 10px;
      right: 10px;
      z-index: 10;
      pointer-events: none;
    }

    .overlay-badge {
      background: rgba(78, 205, 196, 0.95);
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      display: inline-block;
    }

    .comparison-chart {
      margin-top: 30px;
      padding: 25px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 12px;
    }

    .chart-title {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 20px;
      text-align: center;
    }

    .chart-bars {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }

    .chart-bar-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .chart-bar {
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      padding: 0 20px;
      transition: all 0.3s ease;
    }

    .original-bar {
      background: linear-gradient(135deg, rgba(227, 30, 36, 0.3) 0%, rgba(227, 30, 36, 0.6) 100%);
      border: 2px solid rgba(227, 30, 36, 0.5);
    }

    .optimized-bar {
      background: linear-gradient(135deg, rgba(78, 205, 196, 0.3) 0%, rgba(78, 205, 196, 0.6) 100%);
      border: 2px solid rgba(78, 205, 196, 0.5);
    }

    .bar-label {
      font-weight: 700;
    }

    .bar-title {
      font-size: 0.85rem;
      opacity: 0.7;
    }

    .chart-savings {
      margin-top: 20px;
      text-align: center;
      font-size: 1.1rem;
      font-weight: 700;
      color: #4ECDC4;
    }

    .demo-notice {
      margin-top: 20px;
      padding: 15px;
      background: rgba(255, 193, 7, 0.1);
      border: 2px solid rgba(255, 193, 7, 0.3);
      border-radius: 12px;
      display: flex;
      gap: 15px;
      align-items: flex-start;
      color: #FFC107;
    }

    .demo-notice strong {
      color: #FFD54F;
    }

    .action-buttons {
      display: flex;
      gap: 15px;
      justify-content: center;
      flex-wrap: wrap;
    }

    .action-button {
      padding: 15px 30px;
      border-radius: 50px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.3s ease;
      border: none;
    }

    .action-button.secondary {
      background: rgba(255, 255, 255, 0.1);
      color: white;
      border: 2px solid rgba(255, 255, 255, 0.2);
    }

    .action-button:hover {
      transform: translateY(-2px);
    }

    /* STREAMLIT SPECIFIC OVERRIDES */
    .stButton > button {
        background: linear-gradient(135deg, #E31E24 0%, #8B0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 40px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        box-shadow: 0 10px 25px rgba(227, 30, 36, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 35px rgba(227, 30, 36, 0.5) !important;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #E31E24 0%, #FF6B6B 50%, #003366 100%) !important;
        height: 12px !important;
        border-radius: 50px !important;
    }

    h1, h2, h3, h4, h5, p, span, div {
        color: white;
    }

    .stMarkdown {
        color: white;
    }

    [data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
    }

    /* SIDEBAR STYLING */
    .stSidebar {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
    }

    .stSidebar .stMarkdown {
        color: white !important;
    }

    /* FORMULA STYLING */
    .formula-card {
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(78, 205, 196, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .formula-card:hover {
        transform: translateY(-3px);
        border-color: rgba(78, 205, 196, 0.6);
        box-shadow: 0 10px 25px rgba(78, 205, 196, 0.2);
    }

    .formula-title {
        font-size: 1rem;
        font-weight: 700;
        color: #4ECDC4;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .formula-equation {
        font-size: 0.9rem;
        font-family: 'Courier New', monospace;
        background: rgba(0, 0, 0, 0.4);
        padding: 10px;
        border-radius: 6px;
        margin: 8px 0;
        color: #FFD54F;
        border: 1px solid rgba(255, 213, 79, 0.2);
    }

    .formula-result {
        font-size: 1.1rem;
        font-weight: 900;
        color: #4ECDC4;
        margin-top: 8px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    </style>
    """, unsafe_allow_html=True)


def show_hero():
    """Display hero section"""
    st.markdown("""
    <div class="hero-section">
        <h1>AURA MODULE 1</h1>
        <p>Intelligent Data Manager with Classification Engine</p>
        <div style="margin-top: 25px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">Machine Learning Powered</div>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">Real-Time Processing</div>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">Storage Optimization</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_metrics(processed, saved, duplicates, reduction, lifespan, storage_saved):
    """Display metric cards"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{processed}</div>
            <div class="metric-label">Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{saved}</div>
            <div class="metric-label">Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{duplicates}</div>
            <div class="metric-label">Duplicates</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{reduction:.0f}%</div>
            <div class="metric-label">Reduction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{lifespan:.1f}x</div>
            <div class="metric-label">Lifespan</div>
        </div>
        """, unsafe_allow_html=True)


def get_category_badge(category):
    """Get HTML badge for category"""
    return f'<span class="badge badge-{category.lower()}">{category}</span>'


def show_mathematical_formulas(processed, saved, original_size_mb, optimized_size_mb):
    """Display mathematical formulas with calculations"""
    reduction = ((processed - saved) / processed) * 100 if processed > 0 else 0
    lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
    storage_saved_gb = (original_size_mb - optimized_size_mb) / 1024
    
    st.markdown("---")
    st.markdown("### 📊 Mathematical Analysis & Formulas")
    
    # Formula 1: Write Reduction
    st.markdown(f"""
    <div class="formula-card">
        <div class="formula-title">Formula 1: Write Reduction Percentage</div>
        <div class="formula-equation">
            Write Reduction % = (Total Frames - Saved Frames) / Total Frames × 100
        </div>
        <div class="formula-equation">
            Write Reduction % = ({processed} - {saved}) / {processed} × 100
        </div>
        <div class="formula-result">
            = {reduction:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formula 2: Lifespan Extension
    st.markdown(f"""
    <div class="formula-card">
        <div class="formula-title">Formula 2: Device Lifespan Extension</div>
        <div class="formula-equation">
            Lifespan Extension = 1 / (1 - Reduction% / 100)
        </div>
        <div class="formula-equation">
            Lifespan Extension = 1 / (1 - {reduction:.1f} / 100)
        </div>
        <div class="formula-result">
            = {lifespan_extension:.2f}x longer lifespan
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formula 3: Storage Savings
    st.markdown(f"""
    <div class="formula-card">
        <div class="formula-title">Formula 3: Storage Space Saved</div>
        <div class="formula-equation">
            Storage Saved = Original Size - Optimized Size
        </div>
        <div class="formula-equation">
            Storage Saved = {original_size_mb:.1f} MB - {optimized_size_mb:.1f} MB
        </div>
        <div class="formula-result">
            = {original_size_mb - optimized_size_mb:.1f} MB ({storage_saved_gb:.3f} GB)
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_enhanced_video_comparison(input_path, output_path, original_size_mb, optimized_size_mb, total_frames, saved_frames):
    """Enhanced video comparison with detailed statistics and mathematical analysis"""
    st.markdown("---")
    st.markdown("### Video Comparison & Mathematical Analysis")
    
    # Calculate metrics for mathematical analysis
    processed = total_frames
    # saved_frames may be a list of frames, a list of file paths, or an integer count
    if isinstance(saved_frames, int):
        saved = saved_frames
    else:
        try:
            saved = len(saved_frames)
        except Exception:
            # Fallback: try to coerce to int
            try:
                saved = int(saved_frames)
            except Exception:
                saved = 0

    reduction = ((processed - saved) / processed) * 100 if processed > 0 else 0
    lifespan_extension = 100 / (100 - reduction) if reduction < 100 else 999
    storage_saved_gb = (original_size_mb - optimized_size_mb) / 1024
    
    # Video comparison container
    col1, col2, col3 = st.columns([1, 0.2, 1])
    
    with col1:
        st.markdown("""
        <div class="video-panel original">
            <div class="video-header">
                <h4>Original Video</h4>
                <span class="video-badge original-badge">ORIGINAL</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.video(input_path)
        
        st.markdown(f"""
            <div class="video-stats">
                <div class="stat-item">
                    <span class="stat-label">Size</span>
                    <span class="stat-value red">{original_size_mb:.1f} MB</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Frames</span>
                    <span class="stat-value red">{total_frames}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Quality</span>
                    <span class="stat-value">100%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Writes</span>
                    <span class="stat-value red">High Impact</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="comparison-arrow">
            <div class="arrow-circle">
                <span style="font-size: 2rem;">→</span>
            </div>
            <div class="arrow-label">AURA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="video-panel optimized">
            <div class="video-header">
                <h4>AURA Optimized</h4>
                <span class="video-badge optimized-badge">OPTIMIZED</span>
            </div>
        """, unsafe_allow_html=True)
        
        if output_path and os.path.exists(output_path):
            st.video(output_path)
            
            st.markdown(f"""
                <div class="video-stats">
                    <div class="stat-item">
                        <span class="stat-label">Size</span>
                        <span class="stat-value green">{optimized_size_mb:.1f} MB</span>
                    </div>
          <div class="stat-item">
            <span class="stat-label">Frames</span>
            <span class="stat-value green">{saved}</span>
          </div>
                    <div class="stat-item">
                        <span class="stat-label">Quality</span>
                        <span class="stat-value">Preserved</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Writes</span>
                        <span class="stat-value green">{reduction:.1f}% Reduced</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="video-stats">
                    <div class="stat-item">
                        <span class="stat-label">Status</span>
                        <span class="stat-value red">Processing...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Mathematical Analysis Section with LaTeX Formulas
    st.markdown("---")
    st.markdown("### Mathematical Analysis & Formulas")
    
    # Create three columns for formulas
    form_col1, form_col2, form_col3 = st.columns(3)
    
    with form_col1:
        st.markdown("#### Formula 1: Write Reduction %")
        st.markdown("**General Formula:**")
        st.latex(r'''
            \text{Reduction\%} = \frac{\text{Total Frames} - \text{Saved Frames}}{\text{Total Frames}} \times 100
        ''')
        st.markdown("**Calculation:**")
        st.latex(f'''
            \\text{{Reduction\\%}} = \\frac{{{processed} - {saved}}}{{{processed}}} \\times 100
        ''')
        st.latex(f'''
            = {reduction:.1f}\\%
        ''')
    
    with form_col2:
        st.markdown("#### Formula 2: Lifespan Extension")
        st.markdown("**General Formula:**")
        st.latex(r'''
            \text{Extension} = \frac{100}{100 - \text{Reduction\%}}
        ''')
        st.markdown("**Calculation:**")
        st.latex(f'''
            \\text{{Extension}} = \\frac{{100}}{{100 - {reduction:.1f}}}
        ''')
        st.latex(f'''
            = {lifespan_extension:.2f}\\text{{x longer}}
        ''')
    
    with form_col3:
        st.markdown("#### Formula 3: Storage Saved")
        st.markdown("**General Formula:**")
        st.latex(r'''
            \text{Storage Saved} = \text{Original Size} - \text{Optimized Size}
        ''')
        st.markdown("**Calculation:**")
        st.latex(f'''
            \\text{{Saved}} = {original_size_mb:.1f} - {optimized_size_mb:.1f}
        ''')
        st.latex(f'''
            = {original_size_mb - optimized_size_mb:.1f}\\text{{ MB}}
        ''')
    
    # Storage size comparison chart
    st.markdown("---")
    st.markdown("### Visual Storage Comparison")
    
    size_reduction_percent = ((original_size_mb - optimized_size_mb) / original_size_mb) * 100 if original_size_mb > 0 else 0
    
    st.markdown(f"""
    <div class="comparison-chart">
        <div class="chart-title">File Size Impact Analysis</div>
        <div class="chart-bars">
            <div class="chart-bar-group">
                <div class="bar-title">Original Video Storage</div>
                <div class="chart-bar original-bar" style="width: 100%;">
                    <span class="bar-label">{original_size_mb:.1f} MB (100% storage usage)</span>
                </div>
            </div>
            <div class="chart-bar-group">
                <div class="bar-title">AURA Optimized Storage</div>
                <div class="chart-bar optimized-bar" style="width: {(optimized_size_mb/original_size_mb)*100 if original_size_mb > 0 else 0:.1f}%;">
                    <span class="bar-label">{optimized_size_mb:.1f} MB ({(optimized_size_mb/original_size_mb)*100 if original_size_mb > 0 else 0:.1f}% usage)</span>
                </div>
            </div>
        </div>
        <div class="chart-savings">
            Total Savings: {original_size_mb - optimized_size_mb:.1f} MB ({size_reduction_percent:.1f}% reduction) | {lifespan_extension:.2f}x Device Lifespan Extension
        </div>
    </div>
    """, unsafe_allow_html=True)
