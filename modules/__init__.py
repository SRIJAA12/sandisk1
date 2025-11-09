# modules/__init__.py
"""
AURA Module 3: Distributed Security Layer
Package initialization for all modules
"""

from .encryption import AESEncryption
from .shamir import (
    ShamirSecretSharing,
    split_bytes_into_shards,
    reconstruct_bytes_from_shards
)
from .video_processor import DroneVideoProcessor
from .visualizer import plot_polynomial, create_shard_distribution_chart

__all__ = [
    'AESEncryption',
    'ShamirSecretSharing',
    'split_bytes_into_shards',
    'reconstruct_bytes_from_shards',
    'DroneVideoProcessor',
    'plot_polynomial',
    'create_shard_distribution_chart'
]

__version__ = '1.0.0'
__author__ = 'Team AURA'
__description__ = 'Distributed Security Layer using Shamir Secret Sharing & AES-256'
