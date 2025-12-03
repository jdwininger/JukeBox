#!/usr/bin/env python3
"""Test to validate fix command generation based on environment."""
from src.diagnostics import get_fix_commands, run_diagnostics


def test_fix_command_structure():
    res = run_diagnostics()
    cmds = get_fix_commands(res)
    assert "audio" in cmds and isinstance(cmds["audio"], list)
    assert "image" in cmds and isinstance(cmds["image"], list)
    assert "svg" in cmds and isinstance(cmds["svg"], list)
    # Ensure there is at least one suggested command for linux cases
    if "linux" in res["platform"].lower():
        # Ensure suggestion contains at least one common package-manager token
        found = any(
            token in " ".join(cmds["audio"])
            for token in ("apt-get", "dnf", "pacman", "zypper")
        )
        assert (
            found
        ), f"Expected package manager suggestion in audio commands: {cmds['audio']}"


if __name__ == "__main__":
    test_fix_command_structure()
    print("test_fix_commands.py: OK")
