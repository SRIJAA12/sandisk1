"""
UI Components for AURA Module 1
Reusable UI elements and styling
"""

import streamlit as st
from config import COLORS

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* HERO SECTION */
    .hero-section {
        background: linear-gradient(135deg, #E31E24 0%, #8B0000 50%, #003366 100%);
        padding: 60px 40px;
        border-radius: 25px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(227, 30, 36, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section h1 {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    }
    
    .hero-section p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin: 10px 0 0 0;
    }
    
    /* GLASS CARD */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 20px; /* Use margin-bottom instead of margin */
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(227, 30, 36, 0.2);
        border-color: rgba(227, 30, 36, 0.3);
    }
    
    .glass-card h3 {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0;
    }
    
    .glass-card p {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
    }
    
    /* BADGES */
    .badge {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px;
        border: 2px solid;
    }
    
    .badge-critical {
        background: rgba(227, 30, 36, 0.2);
        border-color: #E31E24;
        color: #FF6B6B;
    }
    
    .badge-important {
        background: rgba(255, 107, 107, 0.2);
        border-color: #FF6B6B;
        color: #FFB3B3;
    }
    
    .badge-normal {
        background: rgba(78, 205, 196, 0.2);
        border-color: #4ECDC4;
        color: #7FE6DC;
    }
    
    .badge-discard {
        background: rgba(149, 165, 166, 0.2);
        border-color: #95A5A6;
        color: #BDC3C7;
    }
    
    /* BUTTONS */
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
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #E31E24 0%, #FF6B6B 50%, #003366 100%) !important;
        height: 12px !important;
        border-radius: 50px !important;
    }
    
    /* TEXT */
    h1, h2, h3, h4, h5, p, span, div {
        color: white;
    }
    
    .stMarkdown {
        color: white;
    }
    
    /* TABS */
    [data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
    }
    
    </style>
    """, unsafe_allow_html=True)


def show_hero():
    """Display hero section"""
    st.markdown("""
    <div class="hero-section">
        <h1>🧠 AURA MODULE 1</h1>
        <p>Intelligent Data Manager with AI Classification</p>
        <div style="margin-top: 25px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">🤖 AI Powered</div>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">⚡ Real-Time</div>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px;">💾 70% Savings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_category_badge(category):
    """Get HTML badge for category"""
    return f'<span class="badge badge-{category.lower()}">{category}</span>'