#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Flask
Run this script and copy the output to your .env file or Vercel environment variables
"""
import secrets

if __name__ == '__main__':
    secret_key = secrets.token_hex(32)
    print("\n" + "="*60)
    print("Generated SECRET_KEY for Flask:")
    print("="*60)
    print(f"\n{secret_key}\n")
    print("="*60)
    print("\nAdd this to your .env file or Vercel environment variables:")
    print(f"SECRET_KEY={secret_key}")
    print("="*60 + "\n")
