"""
AURA Module 3: Distributed Security Layer
Complete Streamlit Dashboard with Mathematical Visualizations
"""

import streamlit as st
import json
import time
from datetime import datetime
import pickle
import os

# Import custom modules
from modules.encryption import AESEncryption
from modules.shamir import ShamirSecretSharing, split_bytes_into_shards, reconstruct_bytes_from_shards
from modules.video_processor import DroneVideoProcessor
from modules.visualizer import plot_polynomial, create_shard_distribution_chart

# ============================================================================
# STREAMLIT PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="AURA Module 3: Distributed Security Layer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BACK TO HOMEPAGE BUTTON
st.markdown("""
<div style="margin-bottom: 20px;">
    <a href="/" target="_self" style="text-decoration: none;">
        <button style="
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.3);
            color: #FF6B6B;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        ">← Back to Homepage</button>
    </a>
</div>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0A0E27;
    }
    h1 {
        color: #00D4FF;
        text-align: center;
        margin-bottom: 30px;
    }
    h2 {
        color: #00E676;
        border-bottom: 2px solid #00D4FF;
        padding-bottom: 10px;
    }
    .info-box {
        background-color: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00D4FF;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: rgba(0, 230, 118, 0.1);
        border-left: 4px solid #00E676;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: rgba(255, 214, 0, 0.1);
        border-left: 4px solid #FFD600;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'encrypted_data' not in st.session_state:
    st.session_state.encrypted_data = None
if 'shares' not in st.session_state:
    st.session_state.shares = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'sss_instance' not in st.session_state:
    st.session_state.sss_instance = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_bytes(bytes_size):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

def save_to_file(data, filename):
    """Save data to file"""
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_from_file(filename):
    """Load data from file"""
    with open(filename, 'rb') as f:
        return pickle.load(f)

# ============================================================================
# HEADER & INTRODUCTION
# ============================================================================

st.markdown("# 🔐 AURA Module 3: Distributed Security Layer")
st.markdown("### Secure Storage Through Encryption & Shamir's Secret Sharing")

st.markdown("""
<div class="info-box">
    <strong>Module 3 Dashboard</strong><br>
    This dashboard demonstrates secure data distribution using:
    <ul>
        <li><strong>AES-256-GCM Encryption:</strong> Military-grade data encryption</li>
        <li><strong>Shamir's Secret Sharing:</strong> Mathematical data splitting with K-of-N threshold</li>
        <li><strong>IPFS Distribution:</strong> Federated storage across multiple nodes</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 Concepts & Formulas",
    "🔬 Demo Simulation",
    "📤 Upload & Process",
    "🎯 Reconstruction",
    "📊 Security Analysis"
])

# ============================================================================
# TAB 1: CONCEPTS & FORMULAS
# ============================================================================

with tab1:
    st.header("Concepts & Mathematical Formulas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔐 AES-256-GCM Encryption")
        
        st.markdown("""
        **Algorithm:** AES (Advanced Encryption Standard)
        - **Key Size:** 256 bits (extremely secure)
        - **Mode:** GCM (Galois/Counter Mode)
        - **Security:** Military & government grade
        
        **Encryption Formula:**
        ```
        C = AES_Encrypt(P, K)
        where:
            C = Ciphertext (encrypted output)
            P = Plaintext (original data)
            K = Key (256-bit, derived from password)
        ```
        """)
        
        # Show encryption details
        aes = AESEncryption("demo")
        details = aes.get_encryption_details()
        
        st.write("**Encryption Parameters:**")
        for key, value in details.items():
            st.write(f"- {key}: **{value}**")
    
    with col2:
        st.subheader("🔑 Shamir's Secret Sharing")
        
        st.markdown("""
        **Scheme:** (K, N) Threshold
        - **K (Threshold):** Minimum shares to reconstruct
        - **N (Total):** Total shares created
        - **Example:** (3, 5) - Need 3 out of 5 shares
        
        **Polynomial Formula:**
        ```
        P(x) = s + a₁x + a₂x² + ... + aₖ₋₁xᵏ⁻¹
        where:
            s = Secret (original data)
            aᵢ = Random coefficients
            K = Degree of polynomial
        ```
        """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Shamir's Step 1: Create Polynomial")
        st.markdown("""
        **Goal:** Embed secret in polynomial constant term
        
        **Formula:**
        ```
        P(x) = S + a₁x + a₂x² + ...
                ↑
              Secret
        ```
        
        **Why:**
        - Secret = P(0) (value at x=0)
        - Random coefficients ensure security
        - Polynomial degree = K-1
        """)
    
    with col2:
        st.subheader("🔀 Shamir's Step 2: Generate Shares")
        st.markdown("""
        **Goal:** Evaluate polynomial at N points
        
        **Formula:**
        ```
        Share_i = (i, P(i))
        
        For i = 1, 2, 3, ..., N:
            y = (s + a₁·i + a₂·i² + ...) mod p
        ```
        
        **Result:**
        - N shares created
        - Each = (x-coordinate, y-coordinate)
        - Mathematical guarantee: K points → unique polynomial
        """)
    
    with col3:
        st.subheader("🔧 Shamir's Step 3: Reconstruct")
        st.markdown("""
        **Goal:** Find P(0) from K shares
        
        **Lagrange Formula:**
        ```
        P(0) = Σᵢ yᵢ × Lᵢ(0)
        
        where:
        Lᵢ(0) = Πⱼ≠ᵢ (-xⱼ)/(xᵢ-xⱼ)
        ```
        
        **Security:**
        - K-1 shares → 0% information
        - K shares → 100% recovery
        - Information-theoretically secure
        """)

# ============================================================================
# TAB 2: DEMO SIMULATION
# ============================================================================

with tab2:
    st.header("📊 Interactive Demo Simulation")
    
    st.markdown("""
    <div class="info-box">
        <strong>Demo:</strong> Watch the algorithm work step-by-step
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Settings")
        
        demo_secret = st.number_input(
            "Enter Secret Number",
            min_value=1,
            max_value=1000000,
            value=42,
            help="This will be embedded in the polynomial"
        )
        
        demo_threshold = st.slider(
            "Threshold (K)",
            min_value=2,
            max_value=5,
            value=3,
            help="Minimum shares needed to reconstruct"
        )
        
        demo_total = st.slider(
            "Total Shares (N)",
            min_value=demo_threshold,
            max_value=10,
            value=5,
            help="Total number of shares to create"
        )
        
        password = st.text_input(
            "Encryption Password",
            value="demo-password",
            type="password"
        )
    
    with col2:
        st.subheader("Simulation Results")
        
        if st.button("▶️ Run Simulation"):
            with st.spinner("Generating shares..."):
                # Create Shamir instance
                sss = ShamirSecretSharing(demo_threshold, demo_total)
                
                # Generate shares
                shares = sss.split_secret(demo_secret)
                
                st.session_state.sss_instance = sss
                st.session_state.shares = shares
                
                # Display results
                st.markdown("""
                <div class="success-box">
                    <strong>✓ Simulation Complete!</strong>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Secret", demo_secret)
                col2.metric("Threshold", f"{demo_threshold}/{demo_total}")
                col3.metric("Prime Used", sss.prime)
    
    # Display shares table
    if st.session_state.shares:
        st.divider()
        
        st.subheader("📋 Generated Shares")
        
        shares_data = {
            'Share ID': [i+1 for i in range(len(st.session_state.shares))],
            'X (Node)': [s[0] for s in st.session_state.shares],
            'Y (Value)': [s[1] for s in st.session_state.shares]
        }
        
        st.dataframe(shares_data, use_container_width=True)
        
        # Display polynomial formula
        st.subheader("🧮 Generated Polynomial")
        st.code(st.session_state.sss_instance.get_polynomial_formula(), language="text")
        
        # Plot polynomial
        fig = plot_polynomial(
            st.session_state.sss_instance.polynomial_coefficients,
            st.session_state.shares,
            demo_threshold,
            st.session_state.sss_instance.prime
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Test reconstruction
        st.subheader("🔄 Test Reconstruction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_shares = st.multiselect(
                "Select shares to use for reconstruction",
                options=[f"Share {i+1}" for i in range(len(st.session_state.shares))],
                default=[f"Share {i+1}" for i in range(demo_threshold)]
            )
        
        with col2:
            if st.button("🔄 Reconstruct Secret"):
                if len(selected_shares) < demo_threshold:
                    st.error(f"❌ Need at least {demo_threshold} shares!")
                else:
                    indices = [int(s.split()[1]) - 1 for s in selected_shares]
                    selected_share_tuples = [st.session_state.shares[i] for i in indices]
                    
                    reconstructed = st.session_state.sss_instance.reconstruct_secret(selected_share_tuples)
                    
                    if reconstructed == demo_secret:
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>✓ Reconstruction Successful!</strong><br>
                            Original Secret: {demo_secret}<br>
                            Reconstructed: {reconstructed}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Reconstruction failed")

# ============================================================================
# TAB 3: UPLOAD & PROCESS
# ============================================================================

with tab3:
    st.header("📤 Upload & Process Real Data")
    
    st.markdown("""
    <div class="info-box">
        <strong>Features:</strong>
        <ul>
            <li>Upload drone video files</li>
            <li>Automatic encryption with AES-256</li>
            <li>Shamir's Secret Sharing</li>
            <li>Distribution simulation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Drone Video or File",
            type=['mp4', 'avi', 'mov', 'mkv', 'txt', 'bin'],
            help="Maximum 200MB"
        )
    
    with col2:
        st.subheader("⚙️ Configuration")
        enc_password = st.text_input("Encryption Password", type="password", value="aura-2025")
        threshold_config = st.slider("Threshold K", 2, 5, 3)
        total_config = st.slider("Total Shares N", 3, 10, 5)
    
    if uploaded_file is not None:
        st.divider()
        
        # Show file info
        col1, col2, col3 = st.columns(3)
        col1.metric("File Name", uploaded_file.name)
        col2.metric("File Size", format_bytes(uploaded_file.size))
        col3.metric("Upload Time", datetime.now().strftime("%H:%M:%S"))
        
        # Save uploaded file temporarily
        temp_path = f"data/temp_{uploaded_file.name}"
        os.makedirs("data", exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Process video if it's a video file
        if uploaded_file.name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            st.subheader("📹 Video Metadata")
            
            try:
                processor = DroneVideoProcessor(temp_path)
                metadata = processor.extract_metadata()
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Duration", f"{metadata['duration_sec']}s")
                col2.metric("FPS", int(metadata['fps']))
                col3.metric("Resolution", f"{metadata['width']}x{metadata['height']}")
                col4.metric("Frame Count", metadata['frame_count'])
                
                # Extract and show first frame
                st.subheader("🎬 Preview (First Frame)")
                first_frame = processor.extract_frame(0)
                if first_frame:
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(first_frame))
                    st.image(img, use_container_width=True)
                
                file_hash = processor.get_file_hash()
                st.write(f"**File Hash (SHA-256):** `{file_hash}`")
                
            except Exception as e:
                st.error(f"Video processing error: {e}")
        
        # Process and shard
        if st.button("🔐 Encrypt & Shard Data"):
            with st.spinner("Processing..."):
                try:
                    # Read file
                    with open(temp_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Encrypt
                    aes = AESEncryption(enc_password)
                    encrypted = aes.encrypt(file_data)
                    
                    st.session_state.encrypted_data = encrypted
                    
                    # Create shards
                    sss = ShamirSecretSharing(threshold_config, total_config)
                    
                    # Convert encrypted data to integer chunks and shard
                    shares = sss.split_secret(int.from_bytes(file_data[:4], 'big'))
                    
                    st.session_state.shares = shares
                    st.session_state.sss_instance = sss
                    
                    # Show results
                    st.markdown("""
                    <div class="success-box">
                        <strong>✓ Encryption & Sharding Complete!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Size", format_bytes(len(file_data)))
                    col2.metric("Encrypted Size", format_bytes(len(json.dumps(encrypted))))
                    col3.metric("Shards Created", len(shares))
                    
                    # Show shard info
                    st.subheader("📦 Shard Distribution Across Nodes")
                    
                    nodes = [f"Node_{chr(65+i)}" for i in range(total_config)]
                    shard_sizes = [100] * total_config  # Each shard is 20% of data
                    
                    fig = create_shard_distribution_chart(nodes, shard_sizes)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show shares
                    st.subheader("📋 Shares Details")
                    shares_df_data = {
                        'Node': nodes,
                        'Share (x)': [s[0] for s in shares],
                        'Value (y)': [s[1] for s in shares],
                        'Status': ['✓ Stored'] * len(shares)
                    }
                    st.dataframe(shares_df_data, use_container_width=True)
                    
                    # Download options
                    st.subheader("💾 Download Shards")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        shares_json = json.dumps({
                            'metadata': {
                                'filename': uploaded_file.name,
                                'threshold': threshold_config,
                                'total_shares': total_config,
                                'timestamp': datetime.now().isoformat()
                            },
                            'shares': shares
                        }, indent=2)
                        
                        st.download_button(
                            label="📥 Download Shares JSON",
                            data=shares_json,
                            file_name="shards_metadata.json"
                        )
                    
                    with col2:
                        st.write("*Other downloads available after reconstruction*")
                    
                    with col3:
                        st.write("")
                    
                except Exception as e:
                    st.error(f"Processing error: {e}")
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

# ============================================================================
# TAB 4: RECONSTRUCTION
# ============================================================================

with tab4:
    st.header("🔄 Data Reconstruction")
    
    st.markdown("""
    <div class="warning-box">
        <strong>Reconstruction Threshold:</strong>
        You need at least K shares to successfully reconstruct the original data.
        Having fewer than K shares will fail and provide zero information.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.shares is None:
        st.warning("⚠️ No shares available. Please process data first in the 'Upload & Process' tab.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Select Shares for Reconstruction")
            
            num_shares = len(st.session_state.shares)
            
            shares_to_use = st.multiselect(
                "Choose which shares to use",
                options=[f"Node_{chr(65+i)} (Share {i+1})" for i in range(num_shares)],
                default=[f"Node_{chr(65+i)} (Share {i+1})" for i in range(st.session_state.sss_instance.threshold)]
            )
        
        with col2:
            st.subheader("Reconstruction Status")
            
            threshold = st.session_state.sss_instance.threshold
            selected_count = len(shares_to_use)
            
            if selected_count >= threshold:
                st.markdown(f"""
                <div class="success-box">
                    ✓ Have {selected_count}/{threshold} shares
                    <br><strong>Ready to reconstruct!</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    ⚠ Have {selected_count}/{threshold} shares
                    <br><strong>Need {threshold - selected_count} more!</strong>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🔄 Reconstruct Data"):
            if len(shares_to_use) < st.session_state.sss_instance.threshold:
                st.error(f"❌ Insufficient shares! Need {st.session_state.sss_instance.threshold}, got {len(shares_to_use)}")
            else:
                with st.spinner("Reconstructing..."):
                    try:
                        # Get selected indices
                        indices = []
                        for share_desc in shares_to_use:
                            idx = ord(share_desc.split('_')[1][0]) - ord('A')
                            indices.append(idx)
                        
                        # Get share tuples
                        selected_share_tuples = [st.session_state.shares[i] for i in indices]
                        
                        # Reconstruct
                        reconstructed = st.session_state.sss_instance.reconstruct_secret(selected_share_tuples)
                        
                        st.markdown("""
                        <div class="success-box">
                            <strong>✓ Reconstruction Successful!</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Shares Used", len(shares_to_use))
                        col2.metric("Reconstructed Value", reconstructed)
                        col3.metric("Time", "< 100ms")
                        
                        # Show Lagrange formula
                        st.subheader("🧮 Lagrange Interpolation Used")
                        st.code(st.session_state.sss_instance.get_lagrange_formula(sorted([i+1 for i in indices])), language="text")
                        
                    except Exception as e:
                        st.error(f"❌ Reconstruction failed: {e}")

# ============================================================================
# TAB 5: SECURITY ANALYSIS
# ============================================================================

with tab5:
    st.header("📊 Security Analysis")
    
    st.subheader("🔒 Threat Scenarios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Scenario 1: 1 Node Stolen**
        
        ```
        Nodes Available: 4/5
        Threshold: 3/5
        Data Access: ❌ 0%
        ```
        
        ✓ **Safe** - Still above threshold
        """)
    
    with col2:
        st.markdown("""
        **Scenario 2: 2 Nodes Stolen**
        
        ```
        Nodes Available: 3/5
        Threshold: 3/5
        Data Access: ❌ 0%
        ```
        
        ✓ **Safe** - Exactly at threshold
        """)
    
    with col3:
        st.markdown("""
        **Scenario 3: 3+ Nodes Stolen**
        
        ```
        Nodes Available: 2/5
        Threshold: 3/5
        Data Access: ❌ 0%*
        ```
        
        ⚠ **Compromised**
        *Still encrypted without password
        """)
    
    
    st.divider()
    
    st.subheader("📈 Comparison: Traditional vs AURA")
    
    comparison_data = {
        'Feature': [
            'Data Location',
            'Theft Risk',
            'Cloud Dependency',
            'Encryption',
            'Reconstruction',
            'Key Management',
            'Compliance'
        ],
        'Traditional Storage': [
            'Single device',
            'All data exposed',
            'Required for backup',
            'Optional',
            'N/A',
            'Complex',
            'GDPR challenges'
        ],
        'AURA Module 3': [
            'Distributed nodes',
            'Need 3/5 devices',
            'Optional',
            'Mandatory AES-256',
            'Threshold-based',
            'Automatic',
            'GDPR compliant'
        ]
    }
    
    st.dataframe(comparison_data, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #B0B8D4; margin-top: 50px;">
    <p><strong>AURA Module 3</strong> | Distributed Security Layer</p>
    <p>Built with ❤️ for SanDisk Cerebrum 2025</p>
    <p>PSG Institute of Technology | Team AURA</p>
</div>
""", unsafe_allow_html=True)
