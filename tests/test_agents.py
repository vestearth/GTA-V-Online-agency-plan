"""
Tests for the GTA V AI Agent system.
Runs in offline mode (no OpenAI key required).
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# --------------------------------------------------------------------- #
# Fixtures                                                               #
# --------------------------------------------------------------------- #

SAMPLE_WEEKLY_DATA: dict = {
    "week": "2024-W01",
    "player": "TestPlayer",
    "playtime_hours": 5,
    "financials": {
        "earnings_total": 1000000,
        "expenses_total": 200000,
        "net_profit": 800000,
        "currency": "GTA$",
    },
    "missions_completed": [
        {
            "name": "Test Mission",
            "type": "heist",
            "earnings": 500000,
            "duration_minutes": 30,
            "success": True,
            "difficulty": "normal",
            "players": 2,
            "notes": "test",
        }
    ],
    "highlights": ["Test highlight"],
}


# --------------------------------------------------------------------- #
# Base agent tests                                                       #
# --------------------------------------------------------------------- #

class TestBaseAgent:
    """Tests for the BaseAgent interface."""

    def test_offline_agents_importable(self):
        from agents.offline.michael import MichaelAgent
        from agents.offline.trevor import TrevorAgent
        from agents.offline.franklin import FranklinAgent
        assert MichaelAgent
        assert TrevorAgent
        assert FranklinAgent

    def test_online_agents_importable(self):
        from agents.online.lester import LesterAgent
        from agents.online.ron import RonAgent
        from agents.online.lamar import LamarAgent
        from agents.online.english_dave import EnglishDaveAgent
        from agents.online.agent14 import Agent14Agent
        assert LesterAgent
        assert RonAgent
        assert LamarAgent
        assert EnglishDaveAgent
        assert Agent14Agent

    def test_agents_package_exports(self):
        from agents import (
            MichaelAgent, TrevorAgent, FranklinAgent,
            LesterAgent, RonAgent, LamarAgent,
            EnglishDaveAgent, Agent14Agent,
        )
        assert all([
            MichaelAgent, TrevorAgent, FranklinAgent,
            LesterAgent, RonAgent, LamarAgent,
            EnglishDaveAgent, Agent14Agent,
        ])


# --------------------------------------------------------------------- #
# Agent identity tests                                                   #
# --------------------------------------------------------------------- #

class TestAgentIdentity:
    """Each agent has correct name, type, role, and personality."""

    @pytest.mark.parametrize("agent_class,expected_name,expected_type", [
        ("agents.offline.michael.MichaelAgent", "Michael De Santa", "offline"),
        ("agents.offline.trevor.TrevorAgent", "Trevor Philips", "offline"),
        ("agents.offline.franklin.FranklinAgent", "Franklin Clinton", "offline"),
        ("agents.online.lester.LesterAgent", "Lester Crest", "online"),
        ("agents.online.ron.RonAgent", "Ron Jakowski", "online"),
        ("agents.online.lamar.LamarAgent", "Lamar Davis", "online"),
        ("agents.online.english_dave.EnglishDaveAgent", "English Dave", "online"),
        ("agents.online.agent14.Agent14Agent", "Agent 14", "online"),
    ])
    def test_agent_identity(self, agent_class, expected_name, expected_type):
        module_path, class_name = agent_class.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        agent = cls()
        assert agent.name == expected_name
        assert agent.character_type == expected_type
        assert agent.role
        assert agent.personality


# --------------------------------------------------------------------- #
# System prompt tests                                                    #
# --------------------------------------------------------------------- #

class TestSystemPrompts:
    """Agents produce valid system prompts."""

    def _all_agents(self):
        from agents import (
            MichaelAgent, TrevorAgent, FranklinAgent,
            LesterAgent, RonAgent, LamarAgent,
            EnglishDaveAgent, Agent14Agent,
        )
        return [
            MichaelAgent(), TrevorAgent(), FranklinAgent(),
            LesterAgent(), RonAgent(), LamarAgent(),
            EnglishDaveAgent(), Agent14Agent(),
        ]

    def test_system_prompts_contain_name(self):
        for agent in self._all_agents():
            prompt = agent.build_system_prompt()
            assert agent.name in prompt, f"{agent.name} missing from its own system prompt"

    def test_system_prompts_contain_role(self):
        for agent in self._all_agents():
            prompt = agent.build_system_prompt()
            assert prompt.strip(), f"{agent.name} system prompt is empty"

    def test_analysis_instructions_non_empty(self):
        for agent in self._all_agents():
            instruction = agent.get_analysis_instruction()
            assert instruction.strip(), f"{agent.name} analysis instruction is empty"


# --------------------------------------------------------------------- #
# Offline-mode analysis tests                                            #
# --------------------------------------------------------------------- #

class TestOfflineModeAnalysis:
    """Agents return a response in offline mode (no API key)."""

    def _all_agents(self):
        from agents import (
            MichaelAgent, TrevorAgent, FranklinAgent,
            LesterAgent, RonAgent, LamarAgent,
            EnglishDaveAgent, Agent14Agent,
        )
        return [
            MichaelAgent(), TrevorAgent(), FranklinAgent(),
            LesterAgent(), RonAgent(), LamarAgent(),
            EnglishDaveAgent(), Agent14Agent(),
        ]

    def test_analyze_returns_string(self):
        os.environ.pop("OPENAI_API_KEY", None)
        import config
        original_key = config.OPENAI_API_KEY
        config.OPENAI_API_KEY = ""
        try:
            for agent in self._all_agents():
                result = agent.analyze(SAMPLE_WEEKLY_DATA)
                assert isinstance(result, str), f"{agent.name} analyze() did not return str"
                assert result.strip(), f"{agent.name} analyze() returned empty string"
        finally:
            config.OPENAI_API_KEY = original_key

    def test_offline_response_contains_agent_name(self):
        import config
        original_key = config.OPENAI_API_KEY
        config.OPENAI_API_KEY = ""
        try:
            for agent in self._all_agents():
                result = agent.analyze(SAMPLE_WEEKLY_DATA)
                assert agent.name in result, (
                    f"{agent.name} not found in offline response"
                )
        finally:
            config.OPENAI_API_KEY = original_key


# --------------------------------------------------------------------- #
# User prompt tests                                                      #
# --------------------------------------------------------------------- #

class TestUserPromptBuilding:
    """build_user_prompt embeds the weekly data."""

    def test_user_prompt_contains_week(self):
        from agents.online.lester import LesterAgent
        agent = LesterAgent()
        prompt = agent.build_user_prompt(SAMPLE_WEEKLY_DATA)
        assert "2024-W01" in prompt

    def test_user_prompt_contains_earnings(self):
        from agents.offline.michael import MichaelAgent
        agent = MichaelAgent()
        prompt = agent.build_user_prompt(SAMPLE_WEEKLY_DATA)
        assert "1000000" in prompt


# --------------------------------------------------------------------- #
# Main orchestrator tests                                                #
# --------------------------------------------------------------------- #

class TestMainOrchestrator:
    """Tests for main.py logic."""

    def test_load_weekly_data(self, tmp_path):
        from main import load_weekly_data
        data_file = tmp_path / "week.json"
        data_file.write_text(json.dumps(SAMPLE_WEEKLY_DATA), encoding="utf-8")
        loaded = load_weekly_data(str(data_file))
        assert loaded["week"] == "2024-W01"

    def test_resolve_agents_all(self):
        from main import resolve_agents, AGENT_REGISTRY
        agents = resolve_agents(["all"])
        assert len(agents) == len(AGENT_REGISTRY)

    def test_resolve_agents_specific(self):
        from main import resolve_agents
        agents = resolve_agents(["michael", "lester"])
        names = [a.name for a in agents]
        assert "Michael De Santa" in names
        assert "Lester Crest" in names
        assert len(agents) == 2

    def test_resolve_agents_unknown_skipped(self, capsys):
        from main import resolve_agents
        agents = resolve_agents(["michael", "nonexistent_agent"])
        assert len(agents) == 1
        captured = capsys.readouterr()
        assert "nonexistent_agent" in captured.err

    def test_format_report_contains_week(self):
        from main import format_report
        results = {"Test Agent": "Some analysis"}
        report = format_report(SAMPLE_WEEKLY_DATA, results)
        assert "2024-W01" in report
        assert "Test Agent" in report
        assert "Some analysis" in report

    def test_save_report(self, tmp_path):
        from main import save_report
        content = "# Test Report\nSome content"
        filepath = save_report(content, str(tmp_path), "2024-W01")
        assert os.path.exists(filepath)
        assert Path(filepath).read_text(encoding="utf-8") == content

    def test_main_no_save_mode(self, tmp_path, capsys):
        import config
        original_key = config.OPENAI_API_KEY
        config.OPENAI_API_KEY = ""
        data_file = tmp_path / "week.json"
        data_file.write_text(json.dumps(SAMPLE_WEEKLY_DATA), encoding="utf-8")
        try:
            from main import main
            exit_code = main([
                "--data", str(data_file),
                "--agents", "michael",
                "--no-save",
            ])
            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Michael De Santa" in captured.out
        finally:
            config.OPENAI_API_KEY = original_key

    def test_main_missing_data_file(self, capsys):
        from main import main
        exit_code = main(["--data", "/nonexistent/path/week.json"])
        assert exit_code == 1

    def test_main_saves_report(self, tmp_path):
        import config
        original_key = config.OPENAI_API_KEY
        config.OPENAI_API_KEY = ""
        data_file = tmp_path / "week.json"
        data_file.write_text(json.dumps(SAMPLE_WEEKLY_DATA), encoding="utf-8")
        output_dir = tmp_path / "reports"
        try:
            from main import main
            exit_code = main([
                "--data", str(data_file),
                "--agents", "lester",
                "--output", str(output_dir),
            ])
            assert exit_code == 0
            reports = list(output_dir.glob("*.md"))
            assert len(reports) == 1
        finally:
            config.OPENAI_API_KEY = original_key
