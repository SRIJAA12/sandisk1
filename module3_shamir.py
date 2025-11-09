"""
AURA Module 3: Shamir's Secret Sharing Helper
Implements (K, N) threshold splitting using polynomial mathematics
Based on MODULE 3 specifications - (3, 5) scheme
"""

import random
import math

# Use a large prime number for the finite field
# This ensures mathematical operations work correctly
DEFAULT_PRIME = 2**31 - 1  # Mersenne prime: 2,147,483,647

def _eval_polynomial(coeffs, x, prime):
    """
    Evaluates a polynomial at point x in a finite field.
    P(x) = coeffs[0] + coeffs[1]*x + coeffs[2]*x^2 + ...
    """
    result = 0
    for i, coeff in enumerate(coeffs):
        result = (result + coeff * pow(x, i, prime)) % prime
    return result

def _extended_gcd(a, b):
    """
    Extended Euclidean Algorithm for finding modular inverse.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b)
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = _extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def _mod_inverse(a, m):
    """
    Calculates modular inverse of a modulo m.
    Used in Lagrange interpolation for reconstruction.
    """
    gcd, x, _ = _extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError(f"Modular inverse does not exist for {a} mod {m}")
    return (x % m + m) % m

def split_secret(secret: int, threshold: int, total_shares: int, prime=DEFAULT_PRIME) -> list:
    """
    Splits a secret (as an integer) into N shares using Shamir's Secret Sharing.
    Any K shares can reconstruct the secret, but K-1 shares reveal nothing.
    
    Args:
        secret: The secret to split (as integer)
        threshold: K - minimum shares needed to reconstruct (e.g., 3)
        total_shares: N - total shares to create (e.g., 5)
        prime: Prime number for finite field arithmetic
        
    Returns:
        List of (x, y) coordinate pairs representing shares
        
    Mathematical Process:
        1. Create polynomial P(x) = secret + a₁x + a₂x² + ... + aₖ₋₁x^(k-1)
        2. Set P(0) = secret (y-intercept is our secret)
        3. Generate random coefficients a₁, a₂, ..., aₖ₋₁
        4. Evaluate P(x) at x = 1, 2, 3, ..., N to get N shares
    """
    if threshold > total_shares:
        raise ValueError(f"Threshold ({threshold}) cannot be greater than total shares ({total_shares})")
    
    if threshold < 2:
        raise ValueError("Threshold must be at least 2")
    
    if secret >= prime:
        raise ValueError(f"Secret ({secret}) must be smaller than prime ({prime})")

    # Create a random polynomial P(x) of degree (K-1)
    # P(x) = secret + a₁x + a₂x² + ... + aₖ₋₁x^(k-1)
    coefficients = [secret]  # P(0) = secret
    
    # Generate K-1 random coefficients
    for _ in range(threshold - 1):
        coefficients.append(random.randint(1, prime - 1))

    # Generate N shares by evaluating P(x) at x=1, 2, 3, ..., N
    shares = []
    for x in range(1, total_shares + 1):
        y = _eval_polynomial(coefficients, x, prime)
        shares.append((x, y))

    return shares

def reconstruct_secret(shares: list, prime=DEFAULT_PRIME) -> int:
    """
    Reconstructs the secret from K shares using Lagrange Interpolation.
    Finds P(0) which is the original secret.
    
    Args:
        shares: List of (x, y) coordinate pairs
        prime: Prime number for finite field arithmetic
        
    Returns:
        The reconstructed secret (integer)
        
    Mathematical Process:
        1. Use Lagrange Interpolation to find the unique polynomial
        2. Calculate P(0) = Σ(yᵢ * Lᵢ(0)) where Lᵢ(0) is the Lagrange basis
        3. Lᵢ(0) = Π((0-xⱼ)/(xᵢ-xⱼ)) for all j≠i
    """
    if not shares:
        raise ValueError("No shares provided for reconstruction")
    
    if len(shares) < 2:
        raise ValueError("At least 2 shares are required for reconstruction")

    secret = 0
    
    # Use Lagrange Interpolation to find P(0)
    for i, (x_i, y_i) in enumerate(shares):
        # Calculate Lagrange basis polynomial Lᵢ(0)
        numerator = 1
        denominator = 1
        
        for j, (x_j, _) in enumerate(shares):
            if i != j:
                # For P(0): numerator *= (0 - x_j) = -x_j
                numerator = (numerator * (-x_j)) % prime
                # denominator *= (x_i - x_j)
                denominator = (denominator * (x_i - x_j)) % prime
        
        # Calculate Lᵢ(0) = numerator * (denominator^-1) mod prime
        lagrange_basis = (numerator * _mod_inverse(denominator, prime)) % prime
        
        # Add this term to the secret: secret += yᵢ * Lᵢ(0)
        secret = (secret + y_i * lagrange_basis) % prime

    return secret

def get_sharing_info(threshold: int, total_shares: int) -> dict:
    """
    Returns information about the Shamir's Secret Sharing configuration.
    """
    return {
        'scheme': f'({threshold}, {total_shares})',
        'threshold': threshold,
        'total_shares': total_shares,
        'security_level': 'Information-theoretically secure',
        'polynomial_degree': threshold - 1,
        'prime_modulus': DEFAULT_PRIME,
        'attack_resistance': {
            'shares_needed': threshold,
            'shares_useless': threshold - 1,
            'mathematical_guarantee': 'K-1 shares reveal zero information about the secret'
        },
        'use_cases': [
            'Distributed key storage',
            'Backup systems',
            'Multi-party authentication',
            'Secure data distribution'
        ]
    }

def validate_shares(shares: list, expected_threshold: int = None) -> dict:
    """
    Validates a list of shares for consistency and security.
    """
    if not shares:
        return {'valid': False, 'error': 'No shares provided'}
    
    # Check for duplicate x-coordinates
    x_coords = [x for x, y in shares]
    if len(set(x_coords)) != len(x_coords):
        return {'valid': False, 'error': 'Duplicate x-coordinates found'}
    
    # Check if we have enough shares
    if expected_threshold and len(shares) < expected_threshold:
        return {
            'valid': False, 
            'error': f'Insufficient shares: {len(shares)} provided, {expected_threshold} required'
        }
    
    return {
        'valid': True,
        'share_count': len(shares),
        'x_coordinates': x_coords,
        'reconstruction_possible': len(shares) >= 2
    }
