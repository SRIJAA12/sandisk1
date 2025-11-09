# modules/visualizer.py
"""
Mathematical Visualization for Shamir's Algorithm
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Tuple


def plot_polynomial(coefficients: List[int], shares: List[Tuple[int, int]], 
                   threshold: int, prime: int) -> go.Figure:
    """
    Visualize the secret-sharing polynomial and shares
    """
    # Generate x values for plotting
    x_vals = np.linspace(0, len(shares) + 1, 1000)
    
    # Evaluate polynomial (mod prime for visualization)
    def eval_poly(x):
        result = 0
        for i, coeff in enumerate(coefficients):
            result += coeff * (x ** i)
        return result % prime
    
    y_vals = [eval_poly(x) for x in x_vals]
    
    # Create figure
    fig = go.Figure()
    
    # Plot polynomial curve
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name='Polynomial P(x)',
        line=dict(color='#00D4FF', width=3)
    ))
    
    # Plot shares
    share_x = [s[0] for s in shares]
    share_y = [s[1] for s in shares]
    
    fig.add_trace(go.Scatter(
        x=share_x,
        y=share_y,
        mode='markers',
        name='Shares',
        marker=dict(size=12, color='#FF4081', symbol='diamond')
    ))
    
    # Plot secret point at P(0)
    fig.add_trace(go.Scatter(
        x=[0],
        y=[coefficients[0]],
        mode='markers',
        name='Secret (P(0))',
        marker=dict(size=15, color='#00E676', symbol='star')
    ))
    
    fig.update_layout(
        title=f'Shamir\'s Secret Sharing Polynomial (Threshold={threshold})',
        xaxis_title='x',
        yaxis_title='P(x) mod {}'.format(prime),
        template='plotly_dark',
        height=500
    )
    
    return fig


def create_shard_distribution_chart(nodes: List[str], shard_sizes: List[int]) -> go.Figure:
    """Create visual representation of shard distribution"""
    fig = go.Figure(data=[
        go.Bar(
            x=nodes,
            y=shard_sizes,
            marker_color=['#00D4FF', '#FF4081', '#00E676', '#FFD600', '#9C27B0'],
            text=shard_sizes,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Shard Distribution Across Nodes',
        xaxis_title='Node',
        yaxis_title='Shard Size (bytes)',
        template='plotly_dark',
        height=400
    )
    
    return fig
