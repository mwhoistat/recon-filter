#!/usr/bin/env python3
"""
Development Entrypoint Proxy.
In production (v1.0.0), the CLI natively invokes `recon_filter.main:app` via pyproject.toml scripts.
This script remains purely for local `python main.py` testing routing bounds seamlessly.
"""
from recon_filter.main import app

if __name__ == "__main__":
    app()
