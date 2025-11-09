# modules/shamir.py
"""
Shamir's Secret Sharing Implementation
(K, N) threshold scheme with detailed mathematical operations
"""

import random
from typing import List, Tuple
import numpy as np


class ShamirSecretSharing:
    """
    Implement Shamir's (K, N) threshold secret sharing
    """
    
    def __init__(self, threshold: int, total_shares: int, prime: int = None):
        """
        Initialize Shamir's Secret Sharing
        
        Args:
            threshold: K - minimum shares needed to reconstruct
            total_shares: N - total number of shares to create
            prime: Large prime for finite field (default: 2^31 - 1)
        """
        self.threshold = threshold
        self.total_shares = total_shares
        self.prime = prime or (2**31 - 1)  # Mersenne prime
        self.polynomial_coefficients = []
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """
        Evaluate polynomial P(x) = a₀ + a₁x + a₂x² + ... + aₖ₋₁xᵏ⁻¹
        
        Uses Horner's method for efficient computation
        """
        result = 0
        for i, coeff in enumerate(coefficients):
            result = (result + coeff * pow(x, i, self.prime)) % self.prime
        return result
    
    def split_secret(self, secret: int) -> List[Tuple[int, int]]:
        """
        Split secret into N shares using polynomial interpolation
        
        Returns:
            List of (x, y) share tuples
        """
        if secret < 0 or secret >= self.prime:
            raise ValueError(f"Secret must be between 0 and {self.prime-1}")
        
        # Create random polynomial: P(x) = secret + a₁x + a₂x² + ... + aₖ₋₁xᵏ⁻¹
        self.polynomial_coefficients = [secret]  # P(0) = secret
        
        # Random coefficients for degree (K-1) polynomial
        for _ in range(self.threshold - 1):
            self.polynomial_coefficients.append(random.randint(1, self.prime - 1))
        
        # Generate N shares by evaluating P(1), P(2), ..., P(N)
        shares = []
        for x in range(1, self.total_shares + 1):
            y = self._evaluate_polynomial(self.polynomial_coefficients, x)
            shares.append((x, y))
        
        return shares
    
    def _lagrange_interpolation(self, shares: List[Tuple[int, int]]) -> int:
        """
        Reconstruct secret using Lagrange interpolation
        
        Computes P(0) = Σᵢ yᵢ · Lᵢ(0)
        where Lᵢ(0) = Πⱼ≠ᵢ (-xⱼ)/(xᵢ - xⱼ)
        """
        if len(shares) < self.threshold:
            raise ValueError(f"Need at least {self.threshold} shares, got {len(shares)}")
        
        secret = 0
        
        for i, (x_i, y_i) in enumerate(shares):
            # Calculate Lagrange basis polynomial Lᵢ(0)
            numerator = 1
            denominator = 1
            
            for j, (x_j, _) in enumerate(shares):
                if i != j:
                    numerator = (numerator * (-x_j)) % self.prime
                    denominator = (denominator * (x_i - x_j)) % self.prime
            
            # Modular multiplicative inverse
            lagrange_basis = (numerator * pow(denominator, -1, self.prime)) % self.prime
            
            # Add weighted contribution
            secret = (secret + y_i * lagrange_basis) % self.prime
        
        return secret
    
    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> int:
        """
        Reconstruct the original secret from K or more shares
        """
        return self._lagrange_interpolation(shares)
    
    def get_polynomial_formula(self) -> str:
        """Return the polynomial as a human-readable string"""
        if not self.polynomial_coefficients:
            return "No polynomial generated yet"
        
        terms = []
        for i, coeff in enumerate(self.polynomial_coefficients):
            if i == 0:
                terms.append(f"{coeff}")
            elif i == 1:
                terms.append(f"{coeff}x")
            else:
                terms.append(f"{coeff}x^{i}")
        
        return "P(x) = " + " + ".join(terms)
    
    def get_lagrange_formula(self, share_indices: List[int]) -> str:
        """
        Generate Lagrange interpolation formula for given shares
        """
        formula_parts = []
        
        for i in share_indices:
            numerator_parts = []
            denominator_parts = []
            
            for j in share_indices:
                if i != j:
                    numerator_parts.append(f"(-{j})")
                    denominator_parts.append(f"({i} - {j})")
            
            numerator = " × ".join(numerator_parts) if numerator_parts else "1"
            denominator = " × ".join(denominator_parts) if denominator_parts else "1"
            
            formula_parts.append(f"y_{i} × [{numerator}] / [{denominator}]")
        
        return "P(0) = " + " + ".join(formula_parts)


def split_bytes_into_shards(data: bytes, threshold: int, total_shares: int) -> List[bytes]:
    """
    Split byte data into Shamir shards
    
    Processes data in chunks and applies Shamir's algorithm
    """
    sss = ShamirSecretSharing(threshold, total_shares)
    
    chunk_size = 4  # Process 4 bytes at a time
    shard_data = [[] for _ in range(total_shares)]
    
    # Process each chunk
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        
        # Pad if necessary
        if len(chunk) < chunk_size:
            chunk = chunk + b'\x00' * (chunk_size - len(chunk))
        
        # Convert bytes to integer
        secret_int = int.from_bytes(chunk, byteorder='big')
        
        # Split this chunk
        shares = sss.split_secret(secret_int)
        
        # Store in each shard
        for j, (x, y) in enumerate(shares):
            shard_data[j].append((x, y))
    
    # Serialize to bytes
    import pickle
    return [pickle.dumps(shard) for shard in shard_data]


def reconstruct_bytes_from_shards(shards: List[bytes], threshold: int, total_shares: int) -> bytes:
    """
    Reconstruct original bytes from Shamir shards
    """
    import pickle
    
    # Deserialize shards
    shard_lists = [pickle.loads(shard) for shard in shards]
    
    sss = ShamirSecretSharing(threshold, total_shares)
    reconstructed_bytes = bytearray()
    
    # Reconstruct each chunk
    num_chunks = len(shard_lists[0])
    for chunk_idx in range(num_chunks):
        # Collect shares for this chunk
        chunk_shares = [(shard_lists[i][chunk_idx][0], shard_lists[i][chunk_idx][1]) 
                       for i in range(len(shards))]
        
        # Reconstruct integer
        secret_int = sss.reconstruct_secret(chunk_shares)
        
        # Convert back to bytes
        chunk_bytes = secret_int.to_bytes(4, byteorder='big')
        reconstructed_bytes.extend(chunk_bytes)
    
    # Remove padding
    return bytes(reconstructed_bytes).rstrip(b'\x00')
