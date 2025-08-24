#!/usr/bin/env python3
"""
Generate a secure secret key for Flask application
"""

import secrets
import string
import os

def generate_secure_secret_key(length=32):
    """Generate a secure random secret key"""
    # Use secrets module for cryptographically strong random numbers
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_hex_secret_key(length=32):
    """Generate a secure random hex secret key"""
    return secrets.token_hex(length)

if __name__ == "__main__":
    print("🔐 Flask Secret Key Generator")
    print("=" * 40)
    
    # Generate different types of secret keys
    print("\n1. Alphanumeric Secret Key (32 chars):")
    secret_key = generate_secure_secret_key(32)
    print(f"   {secret_key}")
    
    print("\n2. Hex Secret Key (32 bytes = 64 chars):")
    hex_key = generate_hex_secret_key(32)
    print(f"   {hex_key}")
    
    print("\n3. Long Secret Key (64 chars):")
    long_key = generate_secure_secret_key(64)
    print(f"   {long_key}")
    
    print("\n📋 How to use in production:")
    print("=" * 40)
    print("1. Choose one of the keys above")
    print("2. Set it as an environment variable:")
    print("   export FLASK_SECRET_KEY='your-chosen-key'")
    print("3. Or add it to your .env file:")
    print("   FLASK_SECRET_KEY=your-chosen-key")
    print("4. Never commit the actual key to version control!")
    
    print("\n⚠️  Security Notes:")
    print("- Keep your secret key confidential")
    print("- Use different keys for different environments")
    print("- Rotate keys periodically")
    print("- Use at least 32 characters for production")
