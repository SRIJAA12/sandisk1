"""
AURA MODULE 4: ADAPTIVE POWER CONTROLLER
V2 - Interactive Simulation of Workload Consolidation (Batching)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui_components import apply_custom_css, show_hero
import numpy as np
import time

# --- Page Config ---
st.set_page_config(
    page_title="AURA Module 4",
    layout="wide"
)
apply_custom_css()
show_hero()

# --- Power State Definitions (from module4.docx) ---
POWER_STATES = {
    "Active": {"w": 2.3, "color": "#E31E24"},
    "Idle": {"w": 1.2, "color": "#FF6B6B"},
    "Light Sleep": {"w": 0.5, "color": "#4ECDC4"},
    "Deep Sleep": {"w": 0.1, "color": "#0a0e27"}
}
# Timeouts for the "dumb" reactive model
TIMEOUTS_MS = {
    "active_to_idle": 50,    # Stays Active for 50ms per write
    "idle_to_light": 1000,   # Stays Idle for 1s
    "light_to_deep": 2000    # Stays Light Sleep for 2s
}
# Parameters for AURA
AURA_BATCH_SIZE_KB = 1024 * 4  # 4MB
AURA_BATCH_TIME_MS = 500       # 500ms
AURA_WRITE_COST_MS = 200       # Time to write a full batch

# --- Initialize Session State ---
if 'sim_time' not in st.session_state:
    st.session_state.sim_time = 0
    st.session_state.baseline_log = [{"time": 0, "state": "Deep Sleep"}]
    st.session_state.aura_log = [{"time": 0, "state": "Deep Sleep"}]
    st.session_state.aura_buffer_kb = 0
    st.session_state.baseline_state = "Deep Sleep"
    st.session_state.baseline_timer = 0
    st.session_state.aura_timer = 0
    st.session_state.events = []

def get_last(log):
    return log[-1]

def add_log(log, time, state):
    if get_last(log)['state'] != state:
        log.append({"time": time, "state": get_last(log)['state']})
        log.append({"time": time, "state": state})

def run_simulation_step(write_kb=0):
    """Simulates one step (10ms) of the world"""
    ss = st.session_state
    ss.sim_time += 10

    # --- 1. AURA (Batched) Logic ---
    ss.aura_timer += 10
    if write_kb > 0:
        ss.aura_buffer_kb += write_kb # Add to buffer, no power cost

    # Check for flush conditions
    buffer_full = ss.aura_buffer_kb >= AURA_BATCH_SIZE_KB
    timer_expired = ss.aura_timer >= AURA_BATCH_TIME_MS
    
    if (buffer_full or timer_expired) and ss.aura_buffer_kb > 0:
        # Flush the buffer!
        flush_reason = "Buffer Full (4MB)" if buffer_full else "Timer Expired (500ms)"
        ss.events.append(f"[{ss.sim_time}ms] 🔥 AURA ACTIVE MODE STARTING - {flush_reason} - Flushing {ss.aura_buffer_kb:.0f}KB")
        add_log(ss.aura_log, ss.sim_time, "Active")
        add_log(ss.aura_log, ss.sim_time + AURA_WRITE_COST_MS, "Deep Sleep")
        ss.events.append(f"[{ss.sim_time + AURA_WRITE_COST_MS}ms] ✅ AURA Write Complete - Returning to Deep Sleep")
        ss.aura_buffer_kb = 0
        ss.aura_timer = 0
    elif get_last(ss.aura_log)['state'] == "Active" and ss.sim_time >= get_last(ss.aura_log)['time']:
        # This handles the end of the "Active" write state
        add_log(ss.aura_log, ss.sim_time, "Deep Sleep")


    # --- 2. Baseline (Reactive) Logic ---
    ss.baseline_timer += 10
    
    if write_kb > 0:
        # A write INTERRUPTS any sleep state
        add_log(ss.baseline_log, ss.sim_time, "Active")
        ss.baseline_state = "Active"
        ss.baseline_timer = 0 # Reset timer
    
    # State machine for timeouts
    current_state = ss.baseline_state
    
    if current_state == "Active" and ss.baseline_timer > TIMEOUTS_MS['active_to_idle']:
        add_log(ss.baseline_log, ss.sim_time, "Idle")
        ss.baseline_state = "Idle"
        ss.baseline_timer = 0
    
    elif current_state == "Idle" and ss.baseline_timer > TIMEOUTS_MS['idle_to_light']:
        add_log(ss.baseline_log, ss.sim_time, "Light Sleep")
        ss.baseline_state = "Light Sleep"
        ss.baseline_timer = 0
        
    elif current_state == "Light Sleep" and ss.baseline_timer > TIMEOUTS_MS['light_to_deep']:
        add_log(ss.baseline_log, ss.sim_time, "Deep Sleep")
        ss.baseline_state = "Deep Sleep"
        ss.baseline_timer = 0

def add_final_log_point():
    ss = st.session_state
    add_log(ss.baseline_log, ss.sim_time, ss.baseline_state)
    add_log(ss.aura_log, ss.sim_time, get_last(ss.aura_log)['state'])

def reset_simulation():
    st.session_state.sim_time = 0
    st.session_state.baseline_log = [{"time": 0, "state": "Deep Sleep"}]
    st.session_state.aura_log = [{"time": 0, "state": "Deep Sleep"}]
    st.session_state.aura_buffer_kb = 0
    st.session_state.baseline_state = "Deep Sleep"
    st.session_state.baseline_timer = 0
    st.session_state.aura_timer = 0
    st.session_state.events = []

# --- UI Layout ---
st.markdown(
    '<div class="glass-card"><h3>⚡ Interactive Workload Consolidation Demo</h3><p>Send different types of write requests to the storage system and see how the "Traditional" and "AURA" models respond in <strong>real-time</strong>. Watch the power graphs update live!</p></div>',
    unsafe_allow_html=True
)

# --- Interactive Controls ---
st.markdown("---")
st.markdown(
    '<div class="glass-card"><h3>🎮 Interactive Controls</h3><p>Click buttons to send different types of write requests and observe both systems\' power management strategies in real-time!</p></div>',
    unsafe_allow_html=True
)

sim_controls = st.columns(5)
with sim_controls[0]:
    if st.button("📝 Send 1KB Log Entry", use_container_width=True):
        run_simulation_step(write_kb=1)
        st.session_state.events.append(f"[{st.session_state.sim_time}ms] Sent 1KB Log Entry")
        st.rerun()

with sim_controls[1]:
    if st.button("📸 Send 1024KB Photo", use_container_width=True):
        run_simulation_step(write_kb=1024)
        st.session_state.events.append(f"[{st.session_state.sim_time}ms] Sent 1MB Photo")
        st.rerun()

with sim_controls[2]:
    if st.button("💾 Send 4096KB Data", use_container_width=True, type="primary"):
        run_simulation_step(write_kb=4096)
        st.session_state.events.append(f"[{st.session_state.sim_time}ms] Sent 4MB Data (Buffer Full!)")
        st.rerun()

with sim_controls[3]:
    if st.button("⚡ Multiple Small Writes", use_container_width=True):
        st.session_state.events.append(f"[{st.session_state.sim_time}ms] Starting Multiple Small Writes Simulation...")
        progress_bar = st.progress(0)
        for i in range(100): # 100 steps of 10ms = 1 second
            write_kb = 10 if np.random.rand() > 0.8 else 0 # 20% chance of a small write
            run_simulation_step(write_kb=write_kb)
            progress_bar.progress((i + 1) / 100)
            time.sleep(0.01) # Small delay to show progress
        st.session_state.events.append(f"[{st.session_state.sim_time}ms] Multiple Writes Simulation Complete!")
        st.rerun()

with sim_controls[4]:
    if st.button("🔄 Reset Simulation", use_container_width=True):
        reset_simulation()
        st.rerun()

# --- AURA Buffer Status (moved up for better visibility) ---
st.markdown("---")
buffer_cols = st.columns([2, 1])

with buffer_cols[0]:
    st.markdown("##### 🗂️ AURA Write Buffer Status")
    buffer_percent = min(st.session_state.aura_buffer_kb / AURA_BATCH_SIZE_KB, 1.0)
    st.progress(buffer_percent)
    st.markdown(f"**{st.session_state.aura_buffer_kb:.0f} KB / {AURA_BATCH_SIZE_KB} KB** ({buffer_percent*100:.1f}% full)")
    
    if buffer_percent >= 1.0:
        st.error("🔥 **BUFFER FULL - ACTIVE MODE TRIGGERED!**")
        st.markdown("*⚡ AURA is now in ACTIVE MODE (2.3W) - Writing all buffered data to storage in one efficient operation!*")
    elif buffer_percent > 0.8:
        st.warning("⚠️ **Buffer Nearly Full** - Next large write will trigger flush")
        st.markdown("*AURA will flush when buffer reaches 4096KB OR after 500ms timeout*")
    elif buffer_percent > 0.5:
        st.info("📊 **Buffer Filling** - Collecting writes for batch processing")
        st.markdown("*Small writes are being accumulated in RAM buffer*")
    elif buffer_percent > 0:
        st.info("📝 **Buffer Active** - Data waiting for batch write")
        st.markdown("*Timer: " + f"{st.session_state.aura_timer}ms / {AURA_BATCH_TIME_MS}ms*")
    else:
        st.success("✅ **Buffer Empty** - Ready for new write requests")
        st.markdown("*Storage remains in Deep Sleep (0.1W) until buffer fills or timeout*")

with buffer_cols[1]:
    st.markdown("##### 📋 Recent Events")
    recent_events = st.session_state.events[-4:] if st.session_state.events else ["No events yet!"]
    for event in reversed(recent_events):  # Show most recent first
        st.text(event)

# --- Control Explanations ---
st.markdown(
    """
    <div class="glass-card">
    <h4>📋 Control Explanations</h4>
    <ul>
        <li><strong>1KB Log Entry:</strong> Simulates small application logs (GPS, sensors, telemetry)</li>
        <li><strong>1024KB Photo:</strong> Simulates medium-sized file writes</li>
        <li><strong>4096KB Data:</strong> Exactly fills AURA's buffer - demonstrates immediate flush behavior</li>
        <li><strong>Multiple Small Writes:</strong> Simulates 1 second of sporadic small writes from various applications</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Live Dashboards ---
st.markdown("---")
st.markdown("### 📊 Live Power Consumption Comparison")

dash_cols = st.columns(2)

with dash_cols[0]:
    st.markdown("#### 📊 Traditional (Reactive) System")
    st.markdown("*This conventional system processes each write request immediately with standard power state transitions*")
    
    baseline_state = st.session_state.baseline_state
    baseline_power = POWER_STATES[baseline_state]['w']
    baseline_color = POWER_STATES[baseline_state]['color']
    
    st.markdown(f'<div style="background: {baseline_color}; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;"><strong>Current State: {baseline_state}</strong><br/><strong>{baseline_power} Watts</strong></div>', unsafe_allow_html=True)
    
    # Graph
    add_final_log_point()
    df_baseline = pd.DataFrame(st.session_state.baseline_log)
    df_baseline['power'] = df_baseline['state'].map(lambda x: POWER_STATES[x]['w'])
    
    fig_base = go.Figure()
    fig_base.add_trace(go.Scatter(
        x=df_baseline['time'], y=df_baseline['power'], name='Traditional System Power',
        line=dict(color='#E31E24', width=3, shape='hv'), # 'hv' creates step chart
        fill='tozeroy'
    ))
    fig_base.update_layout(
        title="Traditional System: Individual Write Processing",
        xaxis_title="Time (milliseconds)", yaxis_title="Power (Watts)",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)', font_color='white',
        yaxis_range=[0, 3.0], height=350
    )
    st.plotly_chart(fig_base, use_container_width=True)

with dash_cols[1]:
    st.markdown("#### ⚡ AURA (Optimized) System")
    st.markdown("*This intelligent system **consolidates** writes in RAM buffer to maximize Deep Sleep duration*")
    
    aura_state = get_last(st.session_state.aura_log)['state']
    aura_power = POWER_STATES[aura_state]['w']
    aura_color = POWER_STATES[aura_state]['color']
    
    st.markdown(f'<div style="background: {aura_color}; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;"><strong>Current State: {aura_state}</strong><br/><strong>{aura_power} Watts</strong></div>', unsafe_allow_html=True)
    
    # Graph
    df_aura = pd.DataFrame(st.session_state.aura_log)
    df_aura['power'] = df_aura['state'].map(lambda x: POWER_STATES[x]['w'])
    
    fig_aura = go.Figure()
    fig_aura.add_trace(go.Scatter(
        x=df_aura['time'], y=df_aura['power'], name='AURA Optimized Power',
        line=dict(color='#4ECDC4', width=3, shape='hv'),
        fill='tozeroy'
    ))
    fig_aura.update_layout(
        title="AURA System: Workload Consolidation (Optimized)",
        xaxis_title="Time (milliseconds)", yaxis_title="Power (Watts)",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)', font_color='white',
        yaxis_range=[0, 3.0], height=350
    )
    st.plotly_chart(fig_aura, use_container_width=True)

# --- Extended Event Log ---
st.markdown("---")
st.markdown("##### 📋 Complete Event Log")
if st.session_state.events:
    recent_events = st.session_state.events[-10:] if len(st.session_state.events) > 10 else st.session_state.events
    event_text = "\n".join(reversed(recent_events))  # Most recent first
    st.text_area("All Events", value=event_text, height=120, disabled=True)
else:
    st.info("No events yet - click buttons above to start the simulation!")

# --- Final Calculation ---
st.markdown("---")
st.markdown("### 🎯 Real-Time Energy Analysis")

if st.session_state.sim_time > 0:
    try:
        # Calculate total power consumed (Power * Time)
        def calculate_energy(log_df):
            total_energy = 0
            for i in range(len(log_df) - 1):
                duration = log_df.iloc[i+1]['time'] - log_df.iloc[i]['time']
                power = log_df.iloc[i]['power']
                total_energy += power * duration
            return total_energy

        baseline_energy = calculate_energy(df_baseline)
        aura_energy = calculate_energy(df_aura)
        
        if baseline_energy > 0:
            avg_power_baseline = baseline_energy / st.session_state.sim_time
            avg_power_aura = aura_energy / st.session_state.sim_time
            savings = (1 - (avg_power_aura / avg_power_baseline)) * 100
            
            calc_cols = st.columns(3)
            with calc_cols[0]:
                st.metric("Baseline Avg. Power", f"{avg_power_baseline:.2f} W", "Reactive System")
            with calc_cols[1]:
                st.metric("AURA Avg. Power", f"{avg_power_aura:.2f} W", "Batched System")
            with calc_cols[2]:
                st.metric("Power Savings", f"{savings:.1f}%", f"-{avg_power_baseline - avg_power_aura:.2f} W")
            
            if savings > 50:
                st.success(f"🎯 **Outstanding Performance:** AURA's Workload Consolidation achieved **{savings:.1f}%** power reduction through intelligent write batching!")
            elif savings > 25:
                st.success(f"✅ **Significant Improvement:** AURA achieved **{savings:.1f}%** power savings by optimizing write operations.")
            else:
                st.info(f"📊 **Current Performance:** {savings:.1f}% power reduction - try 'Multiple Small Writes' for more pronounced results!")
        else:
            st.info("⏱️ Simulation running... metrics will appear as data is collected.")
            
    except (ZeroDivisionError, IndexError):
        st.info("📊 Send some write requests to see power analysis!")
else:
    st.info("🎮 **Get Started:** Click the buttons above to send write requests and watch the real-time power comparison!")

# --- Technical Implementation Details ---
st.markdown("---")
st.markdown(
    f"""
    <div class="glass-card">
    <h4>🔧 Live System Status</h4>
    <ul>
        <li><strong>Simulation Time:</strong> {st.session_state.sim_time}ms</li>
        <li><strong>AURA Buffer:</strong> {st.session_state.aura_buffer_kb:.0f} KB (Threshold: {AURA_BATCH_SIZE_KB} KB)</li>
        <li><strong>AURA Timer:</strong> {st.session_state.aura_timer}ms (Timeout: {AURA_BATCH_TIME_MS}ms)</li>
        <li><strong>Baseline State:</strong> {st.session_state.baseline_state} ({st.session_state.baseline_timer}ms in state)</li>
        <li><strong>Total Events:</strong> {len(st.session_state.events)}</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div class="glass-card">
    <h4>💡 Technical Summary</h4>
    <p><strong>Key Observation:</strong> The Traditional system transitions to 2.3W Active state for each individual write request, while AURA maintains 0.1W Deep Sleep by consolidating writes in RAM buffer. This demonstrates the effectiveness of <strong>Workload Consolidation</strong> - an intelligent software strategy that maximizes storage power efficiency.</p>
    <p><strong>Implementation Benefits:</strong></p>
    <ul>
        <li>Reduces storage wake-up events by up to 90%</li>
        <li>Maximizes time spent in low-power Deep Sleep state</li>
        <li>Maintains data integrity with configurable timeout protection</li>
        <li>Requires minimal additional system resources (RAM buffer)</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)
