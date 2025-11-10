"""
AURA MODULE 3: DISTRIBUTED SECURITY LAYER
Proof-of-Concept Simulation
"""

import streamlit as st
from ui_components import apply_custom_css, show_hero
from module3_encryption import encrypt_data, decrypt_data
from module3_shamir import split_secret, reconstruct_secret
import math

# --- Page Config ---
st.set_page_config(
    page_title="AURA Module 3 - Security",
    page_icon="🔒",
    layout="wide"
)
apply_custom_css()

# CUSTOM HERO FOR MODULE 3
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1>🔒 AURA Module 3</h1>
        <h2>Distributed Security Layer</h2>
        <p>Military-grade encryption with mathematical sharding</p>
    </div>
</div>
""", unsafe_allow_html=True)

# BACK TO HOMEPAGE BUTTON (use anchor link to avoid switch_page session issues)
st.markdown("""
<div style="margin-bottom: 20px;">
    <a href="/" target="_self" style="text-decoration: none;">
        <button style="
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(78, 205, 196, 0.3);
            color: #4ECDC4;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        ">← Back to Homepage</button>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="glass-card"><h3>🔒 Module 3: Distributed Security Layer</h3><p>This simulation demonstrates how AURA protects data by splitting it into mathematical fragments. Stealing one or two devices is useless.</p></div>',
    unsafe_allow_html=True
)

# SECURITY OVERVIEW
st.markdown("---")
st.markdown("### 🛡️ Security Architecture Overview")

arch_col1, arch_col2, arch_col3, arch_col4 = st.columns(4)

with arch_col1:
    st.markdown("""
    <div class="security-step">
        <div class="step-number">1</div>
        <h4>🔐 AES-256-GCM</h4>
        <p>Military-grade encryption with authentication</p>
    </div>
    """, unsafe_allow_html=True)

with arch_col2:
    st.markdown("""
    <div class="security-step">
        <div class="step-number">2</div>
        <h4>🧮 Shamir's Sharing</h4>
        <p>Mathematical sharding (3 of 5 scheme)</p>
    </div>
    """, unsafe_allow_html=True)

with arch_col3:
    st.markdown("""
    <div class="security-step">
        <div class="step-number">3</div>
        <h4>🌐 IPFS Distribution</h4>
        <p>Decentralized storage across devices</p>
    </div>
    """, unsafe_allow_html=True)

with arch_col4:
    st.markdown("""
    <div class="security-step">
        <div class="step-number">4</div>
        <h4>⛓️ Blockchain Audit</h4>
        <p>Immutable transaction logging</p>
    </div>
    """, unsafe_allow_html=True)

# --- Main Simulation ---
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📝 1. Input Sensitive Data")
    st.write("Enter sensitive data, like a drone's delivery manifest.")
    
    data_input = st.text_area(
        "Sensitive Data (e.g., GPS coordinates, customer info)",
        "GPS: 40.7128° N, 74.0060° W\nCustomer: John Doe\nAddress: 123 Main St, New York\nPayment: **** **** **** 1234\nRoute: Warehouse A → Customer → Return",
        height=150
    )
    
    password = st.text_input("Enter a password to encrypt this data", "SanDisk2025", type="password")
    
    st.markdown("---")
    st.markdown("#### ⚙️ 2. Sharding Configuration")
    st.info("""
    **Shamir's Secret Sharing (3, 5) Scheme:**
    - **Total Shards (N):** 5 fragments
    - **Threshold (K):** 3 fragments needed
    - **Security:** Stealing 1-2 devices = 0% data access
    """)

with col2:
    st.markdown("#### 🚀 3. Run Security Simulation")
    st.write("Click below to encrypt, split, and distribute the data.")
    
    if st.button("🔒 Encrypt & Distribute Data", type="primary", use_container_width=True):
        
        if not data_input or not password:
            st.error("Please enter both data and a password.")
        else:
            with st.spinner("Running AURA Module 3 Security Pipeline..."):
                
                # --- STAGE 1: ENCRYPTION ---
                st.markdown("---")
                st.markdown("#### 🔐 Stage 1: AES-256-GCM Encryption")
                try:
                    encrypted_payload = encrypt_data(data_input.encode('utf-8'), password)
                    st.success("✅ Data encrypted successfully using AES-256-GCM.")
                    
                    # Store data in session state
                    st.session_state.encrypted_payload = encrypted_payload
                    
                    ciphertext_hex = encrypted_payload['ciphertext'].hex()
                    st.code(f"Encrypted Ciphertext: {ciphertext_hex[:60]}...{ciphertext_hex[-20:]}", language="text")
                    
                    # Show encryption details
                    st.markdown("""
                    **Encryption Details:**
                    - **Algorithm:** AES-256-GCM (Advanced Encryption Standard)
                    - **Key Size:** 256 bits (2²⁵⁶ possible combinations)
                    - **Mode:** Galois/Counter Mode (provides authentication)
                    - **Security:** Unbreakable by current technology
                    """)

                except Exception as e:
                    st.error(f"Encryption failed: {e}")
                    st.stop()

                # --- STAGE 2: SHARDING ---
                st.markdown("---")
                st.markdown("#### 🧮 Stage 2: Shamir's Secret Sharing (3, 5)")
                try:
                    # We split the *ciphertext*
                    secret_to_split = int.from_bytes(encrypted_payload['ciphertext'], 'big')
                    shares = split_secret(secret_to_split, threshold=3, total_shares=5)
                    st.session_state.shares = shares
                    st.success("✅ Encrypted data split into 5 mathematical shards.")
                    
                    st.markdown("**Mathematical Shards Distribution:**")
                    
                    # Display shards in a nice format
                    shard_cols = st.columns(5)
                    for i, (x, y) in enumerate(shares):
                        with shard_cols[i]:
                            st.markdown(f"""
                            <div class="shard-card">
                                <h5>🚁 Drone {chr(65+i)}</h5>
                                <p><strong>Shard {i+1}</strong></p>
                                <code>x = {x}</code><br>
                                <code>y = {str(y)[:20]}...</code>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    **Mathematical Security:**
                    - Each shard is a point on a secret polynomial: P(x) = S + a₁x + a₂x²
                    - The secret S is the y-intercept P(0)
                    - Any 2 points = infinite possible polynomials (useless)
                    - Any 3 points = unique polynomial (can recover S)
                    """)

                except Exception as e:
                    st.error(f"Sharding failed: {e}")
                    st.stop()

# --- Data Recovery Simulation ---
st.markdown("---")
st.markdown(
    '<div class="glass-card"><h3>🛡️ Theft Simulation & Data Recovery</h3><p>Simulate device theft to test security. You must select at least 3 shards (the threshold) to recover the data.</p></div>',
    unsafe_allow_html=True
)

if 'shares' in st.session_state:
    st.markdown("#### 🎯 1. Device Availability Simulation")
    st.write("**Scenario:** Select which drones are available (not stolen/offline). Red = Stolen/Offline, Green = Available")
    
    cols = st.columns(5)
    selected_shares_indices = []
    for i in range(5):
        with cols[i]:
            available = st.checkbox(f"🚁 Drone {chr(65+i)}", value=True, key=f"check_{i}")
            if available:
                selected_shares_indices.append(i)
                st.success(f"✅ Shard {i+1} Available")
            else:
                st.error(f"❌ Shard {i+1} Stolen/Offline")
    
    num_selected = len(selected_shares_indices)
    
    # Security Analysis
    st.markdown("#### 🔍 Security Analysis")
    if num_selected < 3:
        st.error(f"""
        **🚨 DATA COMPLETELY SECURE! 🚨**
        - **Available Shards:** {num_selected}/5
        - **Required Threshold:** 3/5
        - **Attacker Access:** 0% (Mathematically impossible to decrypt)
        - **Status:** Data is completely safe even with {5-num_selected} devices stolen!
        """)
    else:
        st.warning(f"""
        **⚠️ DATA CAN BE RECOVERED**
        - **Available Shards:** {num_selected}/5  
        - **Required Threshold:** 3/5 ✅
        - **Status:** Authorized recovery possible with correct password
        """)

    st.markdown("#### 🔓 2. Authorized Data Recovery")
    recovery_password = st.text_input("Enter decryption password", "SanDisk2025", type="password", key="recovery_pass")

    if st.button("🔧 Reconstruct & Decrypt Data", use_container_width=True):
        if num_selected < 3:
            st.error("❌ **RECONSTRUCTION IMPOSSIBLE!** Not enough shards available. The mathematical threshold prevents any data access.")
        elif not recovery_password:
            st.error("Please enter the password to decrypt.")
        else:
            with st.spinner("Reconstructing from available shards..."):
                try:
                    # --- STAGE 3: RECONSTRUCTION ---
                    st.markdown("**🧮 Shamir's Reconstruction Process:**")
                    available_shares = [st.session_state.shares[i] for i in selected_shares_indices]
                    # We only need 3, even if more are available
                    shares_to_use = available_shares[:3] 
                    
                    st.info(f"Using {len(shares_to_use)} shards for Lagrange Interpolation...")
                    
                    reconstructed_secret_int = reconstruct_secret(shares_to_use)
                    
                    # Convert int back to bytes
                    reconstructed_ciphertext = reconstructed_secret_int.to_bytes(
                        math.ceil(reconstructed_secret_int.bit_length() / 8), 'big'
                    )
                    
                    # Check if it matches
                    original_ciphertext = st.session_state.encrypted_payload['ciphertext']
                    
                    if reconstructed_ciphertext != original_ciphertext:
                        st.error("❌ Shard reconstruction failed! Data integrity check failed.")
                    else:
                        st.success("✅ **Shamir's Reconstruction Successful!** Encrypted data perfectly reassembled.")
                        
                        # --- STAGE 4: DECRYPTION ---
                        st.markdown("**🔐 AES-256-GCM Decryption Process:**")
                        payload_to_decrypt = st.session_state.encrypted_payload.copy()
                        payload_to_decrypt['ciphertext'] = reconstructed_ciphertext
                        
                        decrypted_data = decrypt_data(payload_to_decrypt, recovery_password)
                        
                        st.success("✅ **AES-256-GCM Decryption Successful!**")
                        st.markdown("#### 📄 Recovered Original Data:")
                        st.code(decrypted_data.decode('utf-8'), language="text")
                        
                        st.balloons()

                except Exception as e:
                    st.error(f"❌ **Decryption Failed:** {e}")
                    st.error("This likely means you used the wrong password or the data was tampered with.")
else:
    st.info("👆 Run the encryption simulation above to generate data shards for testing.")

# MATHEMATICAL FORMULAS SECTION
st.markdown("---")
st.markdown("### 📊 Mathematical Security Analysis")

math_col1, math_col2, math_col3 = st.columns(3)

with math_col1:
    st.markdown("#### 🔢 Shamir's Polynomial")
    st.latex(r'''
        P(x) = S + a_1x + a_2x^2
    ''')
    st.markdown("**Where:**")
    st.markdown("- S = Secret (y-intercept)")
    st.markdown("- a₁, a₂ = Random coefficients")
    st.markdown("- Degree = K-1 = 2")

with math_col2:
    st.markdown("#### 🎯 Security Threshold")
    st.latex(r'''
        \text{Security} = \frac{\text{Available Shards}}{\text{Required Threshold}}
    ''')
    st.markdown("**Security Levels:**")
    st.markdown("- < 3 shards = 0% access")
    st.markdown("- ≥ 3 shards = Full recovery")

with math_col3:
    st.markdown("#### 🛡️ Attack Resistance")
    st.latex(r'''
        \text{Combinations} = 2^{256} \times \binom{5}{3}
    ''')
    st.markdown("**Attack Requirements:**")
    st.markdown("- Steal ≥3 devices AND")
    st.markdown("- Break AES-256 encryption")
    st.markdown("- = Practically impossible")

# ADDITIONAL CSS FOR MODULE 3
st.markdown("""
<style>
.security-step {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 107, 107, 0.3);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.step-number {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px auto;
    font-weight: bold;
}

.security-step h4 {
    color: #FF6B6B;
    margin: 10px 0 5px 0;
    font-size: 1rem;
}

.security-step p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.85rem;
    margin: 0;
}

.shard-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(78, 205, 196, 0.3);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    margin: 5px 0;
}

.shard-card h5 {
    color: #4ECDC4;
    margin: 0 0 10px 0;
}

.shard-card p {
    color: #FFD54F;
    margin: 5px 0;
    font-weight: bold;
}

.shard-card code {
    background: rgba(0, 0, 0, 0.3);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)
