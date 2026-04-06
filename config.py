"""
Configuration for the GTA V AI Agent system.
Reads settings from environment variables or a .env file.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Load .env file if present (ignored if not found)
load_dotenv()

# --------------------------------------------------------------------- #
# OpenAI / LLM settings                                                 #
# --------------------------------------------------------------------- #
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# --------------------------------------------------------------------- #
# Agent selection                                                        #
# --------------------------------------------------------------------- #
# Comma-separated list of agent names to enable.
# Leave empty or set to "all" to enable every agent.
ENABLED_AGENTS: list[str] = [
    a.strip()
    for a in os.getenv("ENABLED_AGENTS", "all").split(",")
    if a.strip()
]

# --------------------------------------------------------------------- #
# Report settings                                                        #
# --------------------------------------------------------------------- #
REPORTS_DIR: str = os.getenv("REPORTS_DIR", "reports")
