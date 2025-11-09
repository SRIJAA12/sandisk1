"""
AURA HOMEPAGE - Module Selection
Navigate between AURA Module 1 (Data Manager) and Module 3 (Security Layer)
"""

import streamlit as st
from ui_components import apply_custom_css

# PAGE CONFIG
st.set_page_config(
    page_title="AURA - AI-Powered Storage Intelligence",
    page_icon="🧠",
    layout="wide"
)

apply_custom_css()

# HERO SECTION
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1>🧠 AURA</h1>
        <h2>AI-Powered Storage Intelligence Platform</h2>
        <p>Revolutionizing data management and security for edge devices</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# MODULE SELECTION
st.markdown("### 🚀 Select AURA Module")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>📹 Module 1</h3>
            <span class="module-badge">DATA MANAGER</span>
        </div>
        <div class="module-content">
            <h4>Intelligent Data Manager</h4>
            <p>AI-powered video frame classification and optimization for drone footage. Reduces storage writes by up to 77% and extends device lifespan by 4.44x.</p>
            <div class="module-features">
                <div class="feature-item">✅ YOLOv8 Object Detection</div>
                <div class="feature-item">✅ SSIM Duplicate Detection</div>
                <div class="feature-item">✅ Mathematical Analysis</div>
                <div class="feature-item">✅ Video Optimization</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎬 Launch Module 1", type="primary", use_container_width=True):
        st.switch_page("pages/01__Module_1.py")

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-header">
            <h3>🔒 Module 3</h3>
            <span class="module-badge security">SECURITY LAYER</span>
        </div>
        <div class="module-content">
            <h4>Distributed Security Layer</h4>
            <p>Military-grade encryption with mathematical sharding. Makes stealing 1-2 devices completely useless by requiring 3 of 5 fragments to access data.</p>
            <div class="module-features">
                <div class="feature-item">🔐 AES-256-GCM Encryption</div>
                <div class="feature-item">🧮 Shamir's Secret Sharing</div>
                <div class="feature-item">🌐 IPFS Distribution</div>
                <div class="feature-item">⛓️ Blockchain Auditing</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔒 Launch Module 3", type="primary", use_container_width=True):
        st.switch_page("pages/02__Module_3.py")

# ADDITIONAL CSS FOR MODULE CARDS
st.markdown("""
<style>
.module-card {
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(78, 205, 196, 0.3);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    transition: all 0.3s ease;
    height: 450px;
    display: flex;
    flex-direction: column;
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
    font-size: 1.8rem;
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
}

.module-badge.security {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
}

.module-content h4 {
    color: #FFD54F;
    font-size: 1.3rem;
    margin-bottom: 15px;
}

.module-content p {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.6;
    margin-bottom: 20px;
}

.module-features {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
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
