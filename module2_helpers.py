"""
AURA Module 2: Predictive Health Helper
Generates synthetic S.M.A.R.T. data for the simulation
"""

import pandas as pd
import numpy as np

def get_healthy_drive_data(days=14):
    """Generates a 14-day timeseries for a HEALTHY drive."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # 1. ECC Rate (Corrected Errors) - Stays low and flat
    ecc_rate = np.random.randint(1, 5, size=days)
    
    # 2. Bad Block Count - Stays at 0
    bad_blocks = np.zeros(days, dtype=int)
    
    # 3. Read Latency - Stays low and stable
    latency = np.random.normal(loc=2.5, scale=0.2, size=days)
    
    # 4. Program/Erase Cycles - Gradual increase but within normal range
    pe_cycles = np.random.randint(1000, 1200, size=days)
    
    # 5. Temperature - Stable operating temperature
    temperature = np.random.normal(loc=45, scale=3, size=days)
    
    # 6. Voltage Fluctuations - Minimal variations
    voltage_var = np.random.normal(loc=0.02, scale=0.005, size=days)
    
    df = pd.DataFrame({
        'ds': dates,
        'ECC_Rate': ecc_rate,
        'Bad_Block_Count': bad_blocks,
        'Read_Latency_ms': latency,
        'PE_Cycles': pe_cycles,
        'Temperature_C': temperature,
        'Voltage_Variation': voltage_var
    })
    return df

def get_failing_drive_data(days=14):
    """Generates a 14-day timeseries for a FAILING drive."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # 1. ECC Rate (Corrected Errors) - Spikes at the end
    ecc_base = np.random.randint(1, 10, size=days)
    ecc_spike = (np.linspace(0, 1, days) ** 4) * 100 # Exponential spike
    ecc_rate = ecc_base + ecc_spike.astype(int)
    
    # 2. Bad Block Count - Ticks up from 0 to 2
    bad_blocks = np.linspace(0, 2, days).astype(int)
    
    # 3. Read Latency - Gets worse (higher) and more erratic
    latency_base = np.random.normal(loc=2.5, scale=0.2, size=days)
    latency_spike = (np.linspace(0, 1, days) ** 2) * 5
    latency = latency_base + latency_spike
    
    # 4. Program/Erase Cycles - Accelerating wear
    pe_base = np.random.randint(1000, 1200, size=days)
    pe_acceleration = (np.linspace(0, 1, days) ** 3) * 500
    pe_cycles = pe_base + pe_acceleration.astype(int)
    
    # 5. Temperature - Rising due to stress
    temp_base = np.random.normal(loc=45, scale=3, size=days)
    temp_rise = np.linspace(0, 15, days)
    temperature = temp_base + temp_rise
    
    # 6. Voltage Fluctuations - Increasing instability
    voltage_base = np.random.normal(loc=0.02, scale=0.005, size=days)
    voltage_instability = (np.linspace(0, 1, days) ** 2) * 0.08
    voltage_var = voltage_base + voltage_instability
    
    df = pd.DataFrame({
        'ds': dates,
        'ECC_Rate': ecc_rate,
        'Bad_Block_Count': bad_blocks,
        'Read_Latency_ms': latency,
        'PE_Cycles': pe_cycles,
        'Temperature_C': temperature,
        'Voltage_Variation': voltage_var
    })
    return df

def run_simulated_prediction(df_metrics):
    """
    This is our "fake" LSTM model.
    It analyzes the trend and patterns to make a prediction.
    Mimics the 89.3% accuracy mentioned in the script.
    """
    last_day = df_metrics.iloc[-1]
    
    risk_score = 0
    
    # Check ECC Rate - Critical indicator
    if last_day['ECC_Rate'] > 50:
        risk_score += 0.4
    elif last_day['ECC_Rate'] > 20:
        risk_score += 0.25
    elif last_day['ECC_Rate'] > 10:
        risk_score += 0.1
        
    # Check Bad Blocks - Any bad blocks are concerning
    if last_day['Bad_Block_Count'] > 1:
        risk_score += 0.3
    elif last_day['Bad_Block_Count'] > 0:
        risk_score += 0.15
        
    # Check Latency - Performance degradation
    if last_day['Read_Latency_ms'] > 6.0:
        risk_score += 0.2
    elif last_day['Read_Latency_ms'] > 4.0:
        risk_score += 0.1
    
    # Check Temperature - Thermal stress
    if last_day['Temperature_C'] > 55:
        risk_score += 0.15
    elif last_day['Temperature_C'] > 50:
        risk_score += 0.05
    
    # Check Voltage Variations - Power instability
    if last_day['Voltage_Variation'] > 0.05:
        risk_score += 0.1
    
    # Analyze trends (slope of last 7 days)
    recent_data = df_metrics.tail(7)
    
    # ECC Rate trend
    ecc_trend = np.polyfit(range(7), recent_data['ECC_Rate'], 1)[0]
    if ecc_trend > 5:  # Rapidly increasing
        risk_score += 0.2
    
    # Latency trend
    latency_trend = np.polyfit(range(7), recent_data['Read_Latency_ms'], 1)[0]
    if latency_trend > 0.3:  # Increasing latency
        risk_score += 0.15
    
    # Add some realistic noise
    risk_score += np.random.uniform(0.01, 0.05)
    
    # Ensure we match the script's "89.3% accuracy" for failing drives
    if risk_score > 0.6:
        # Make it realistic but high for failing drives
        risk_score = np.random.uniform(0.85, 0.95)
    elif risk_score < 0.2:
        # Keep healthy drives low
        risk_score = np.random.uniform(0.02, 0.15)
        
    risk_score = min(risk_score, 0.99) # Cap at 99%
    
    return risk_score

def get_smart_metrics_info():
    """Returns information about all 12 SMART metrics mentioned in the script."""
    return {
        "Program/Erase Cycles": "Shows wear accumulation per memory block",
        "Bad Block Count": "Reveals physical degradation of memory cells",
        "ECC Rate": "Error correction code rates - indicates system overwhelm",
        "Read/Write Latency": "Performance degradation trends over time",
        "Temperature History": "Thermal stress accelerates memory wear",
        "Voltage Fluctuations": "Power instability damages memory cells",
        "Wear Leveling Count": "Shows uneven usage patterns across blocks",
        "Unexpected Power-Off": "Indicates corruption and data loss risks",
        "Endurance Remaining": "Manufacturer-rated lifespan percentage left",
        "Data Retention Time": "How long unpowered data stays reliable",
        "Controller Retry Freq": "Desperate attempts to read failing blocks",
        "Garbage Collection": "Increasing cleanup overhead indicates stress"
    }
