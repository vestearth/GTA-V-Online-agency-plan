"""
Base agent class for all GTA V character agents.
All agents share a common interface for analyzing weekly activity data.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE


class BaseAgent(ABC):
    """Abstract base agent – sub-classed by every GTA character agent."""

    # --------------------------------------------------------------------- #
    # Identity – override in each sub-class                                  #
    # --------------------------------------------------------------------- #
    name: str = "Base Agent"
    character_type: str = "unknown"   # "offline" | "online"
    role: str = "Generic analyst"
    personality: str = "Neutral and analytical"

    # --------------------------------------------------------------------- #
    # Public interface                                                        #
    # --------------------------------------------------------------------- #

    def build_system_prompt(self) -> str:
        """Return the system prompt that shapes this agent's personality."""
        return (
            f"You are {self.name}, a character from GTA V ({self.character_type}).\n"
            f"Role: {self.role}\n"
            f"Personality: {self.personality}\n"
            "Respond in Thai (ภาษาไทย) unless the user writes in another language.\n"
            "Keep answers concise, insightful, and true to your character."
        )

    def build_user_prompt(self, weekly_data: dict[str, Any]) -> str:
        """Convert raw weekly-activity data into a user prompt."""
        data_str = json.dumps(weekly_data, ensure_ascii=False, indent=2)
        return (
            f"ข้อมูลกิจกรรมประจำสัปดาห์:\n{data_str}\n\n"
            f"{self.get_analysis_instruction()}"
        )

    @abstractmethod
    def get_analysis_instruction(self) -> str:
        """Return the specific analysis task this agent should perform."""

    def analyze(self, weekly_data: dict[str, Any]) -> str:
        """
        Run the agent against `weekly_data` and return the analysis text.

        Uses the OpenAI Chat Completions API when an API key is configured;
        otherwise returns a formatted offline placeholder so the system can be
        tested without credentials.
        """
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(weekly_data)

        if OPENAI_API_KEY:
            return self._call_openai(system_prompt, user_prompt)
        return self._offline_response(system_prompt, user_prompt)

    # --------------------------------------------------------------------- #
    # Internal helpers                                                        #
    # --------------------------------------------------------------------- #

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call the OpenAI API and return the assistant's message content."""
        try:
            from openai import OpenAI  # lazy import – optional dependency

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except ImportError:
            return (
                "[ERROR] openai package not installed. "
                "Run: pip install openai"
            )
        except Exception as exc:  # noqa: BLE001
            return f"[ERROR] OpenAI API call failed: {exc}"

    def _offline_response(self, system_prompt: str, user_prompt: str) -> str:
        """Return a placeholder when no API key is set (for testing/demo)."""
        return (
            f"[OFFLINE MODE – {self.name}]\n"
            f"System: {system_prompt}\n\n"
            f"User: {user_prompt}\n\n"
            "(Set OPENAI_API_KEY in your environment or .env file to get real responses.)"
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} type={self.character_type!r}>"
