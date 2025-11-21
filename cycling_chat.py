#!/usr/bin/env python3
"""
Cycling Assistant - Conversational AI for cycling enthusiasts

Usage:
    python cycling_chat.py

Or set a different model provider:
    MODEL_PROVIDER=anthropic python cycling_chat.py
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agents.conversational_agent import main

if __name__ == "__main__":
    main()
