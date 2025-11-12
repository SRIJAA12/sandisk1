"""
AURA HOMEPAGE - Module Selection
Navigate between AURA Module 1 (Data Manager) and Module 3 (Security Layer)
"""

import streamlit as st
from ui_components import apply_custom_css
from global_status import show_compact_status, get_processing_summary

# PAGE CONFIG
st.set_page_config(
    page_title="AURA - Adaptive Unified Resource Architecture For Edge Storage",
    layout="wide"
)

apply_custom_css()

# HERO SECTION
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1>AURA</h1>
        <h2>Adaptive Unified Resource Architecture For Edge Storage</h2>
        <p>Revolutionizing data management and security for edge devices</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# BACKGROUND PROCESSING STATUS
show_compact_status()

# MODULE SELECTION
st.markdown("### Select AURA Module")

# First row: Module 1 and Module 2
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>Module 1</h3>
            <span class="module-badge">DATA MANAGER</span>
        </div>
        <div class="module-content">
            <h4>Intelligent Data Manager</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show processing status for Module 1
    if 'processing_active' in st.session_state and st.session_state.processing_active:
        st.info("🔄 Processing in background...")
    
    # Navigation link
    if st.button("Launch Module 1", key="launch_m1", use_container_width=True):
        st.switch_page("pages/01__Module_1.py")

with row1_col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>Module 2</h3>
            <span class="module-badge health">HEALTH ENGINE</span>
        </div>
        <div class="module-content">
            <h4>Predictive Health Engine</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Module 2", key="launch_m2", use_container_width=True):
        st.switch_page("pages/02__Module_2.py")

# Second row: Module 3 and Module 4
st.markdown("\n")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>Module 3</h3>
            <span class="module-badge security">SECURITY LAYER</span>
        </div>
        <div class="module-content">
            <h4>Distributed Security Layer</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Module 3", key="launch_m3", use_container_width=True):
        st.switch_page("pages/03__Module_3.py")

with row2_col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>Module 4</h3>
            <span class="module-badge power">POWER CONTROLLER</span>
        </div>
        <div class="module-content">
            <h4>Adaptive Power Controller</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Module 4", key="launch_m4", use_container_width=True):
        st.switch_page("pages/04__Module_4.py")

# ADDITIONAL CSS FOR MODULE CARDS
st.markdown("""
<style>
.module-badge.health {
    background: rgba(255, 107, 107, 0.2);
    color: #FF6B6B;
}

.module-badge.security {
    background: rgba(255, 193, 7, 0.2);
    color: #FFC107;
}

.module-badge.power {
    background: rgba(78, 205, 196, 0.2);
    color: #4ECDC4;
}

.module-card {
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(78, 205, 196, 0.3);
    border-radius: 20px;
    padding: 20px; /* reduced padding to avoid overflow */
    margin: 20px 0;
    transition: all 0.3s ease;
    min-height: 260px; /* allow flexible height instead of fixed */
    display: flex;
    flex-direction: column;
    overflow: hidden; /* prevent children from overflowing and overlapping */
}

.module-card:hover {
    transform: translateY(-5px);
    border-color: rgba(78, 205, 196, 0.6);
    box-shadow: 0 15px 35px rgba(78, 205, 196, 0.2);
}

.module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.module-header h3 {
    color: #4ECDC4;
    font-size: 1.6rem;
    margin: 0;
}

.module-badge {
    background: linear-gradient(135deg, #4ECDC4, #44A08D);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: inline-block;
    position: relative;
    white-space: nowrap; /* prevent badge text breaking */
}

.module-badge.security {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
}

.module-content h4 {
    color: #FFD54F;
    font-size: 1.1rem;
    margin-bottom: 15px;
}

.module-content p {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.8;
    margin-bottom: 20px;
    font-size: 0.95rem;
}

.module-features {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

/* Responsive rules to avoid overlap on narrow screens */
@media (max-width: 1100px) {
    .module-card {
        min-height: 1 auto;
        padding: 16px;
    }
    .module-header h3 {
        font-size: 1.3rem;
    }
    .module-content h4 {
        font-size: 1rem;
    }
}

@media (max-width: 700px) {
    /* When columns compress, ensure text wraps and cards can stack */
    .module-card {
        min-height: auto;
        padding: 12px;
    }
    .module-header {
        flex-direction: row;
        gap: 10px;
    }
    .module-header h3, .module-badge {
        font-size: 1rem;
    }
    .module-content h4 {
        font-size: 0.95rem;
    }
}

.feature-item {
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-item:last-child {
    border-bottom: none;
}
</style>
""", unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.6); padding: 20px;">
    <p>🧠 AURA - Revolutionizing Storage Intelligence for Edge Devices</p>
    <p>Powered by AI • Secured by Mathematics • Built for the Future</p>
</div>
""", unsafe_allow_html=True)
