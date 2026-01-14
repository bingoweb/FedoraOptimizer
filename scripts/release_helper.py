#!/usr/bin/env python3
"""
Release Helper Script for Fedora Optimizer
Automates version bumping and changelog updates.
"""

import os
import sys
import re
import argparse
from datetime import datetime

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT_DIR, "src", "ui", "tui_app.py")
CHANGELOG_FILE = os.path.join(ROOT_DIR, "CHANGELOG.md")
MEMORY_FILE = os.path.join(ROOT_DIR, "docs", "AI_MEMORY.md")


def get_current_version():
    """Reads the current version from the source code."""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    return None


def update_version_file(new_version):
    """Updates the version in the source code."""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{new_version}"', content)

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {VERSION_FILE} to {new_version}")


def update_changelog(new_version):
    """Updates CHANGELOG.md to move Unreleased to a new version."""
    today = datetime.now().strftime("%Y-%m-%d")
    with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if Unreleased section exists and is not empty
    unreleased_pattern = r"## \[Unreleased\]\s*(.*?)\s*## \["
    match = re.search(unreleased_pattern, content, re.DOTALL)

    if not match:
        print("Warning: Could not find [Unreleased] section or it is empty/malformed.")
        # Try to just find the header
        if "## [Unreleased]" not in content:
            print("Error: CHANGELOG.md missing ## [Unreleased] header.")
            return False

    # Construct new section header
    new_section = f"## [Unreleased]\n\n## [{new_version}] - {today}"

    # Replace the [Unreleased] header with [Unreleased] + [New Version]
    new_content = content.replace("## [Unreleased]", new_section)

    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {CHANGELOG_FILE} with version {new_version}")
    return True


def update_memory_file(new_version):
    """Updates the version in AI_MEMORY.md."""
    if not os.path.exists(MEMORY_FILE):
        return

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update "Current Version: vX.Y.Z"
    new_content = re.sub(
        r'\*\*Current Version:\*\* v[0-9]+\.[0-9]+\.[0-9]+',
        f'**Current Version:** v{new_version}',
        content
    )

    # Update "**Version:** X.Y.Z" (at bottom)
    new_content = re.sub(
        r'\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+',
        f'**Version:** {new_version}',
        new_content
    )

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {MEMORY_FILE} to {new_version}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Release helper for Fedora Optimizer")
    parser.add_argument("version", help="New version number (e.g., 0.5.0)")
    args = parser.parse_args()

    new_version = args.version
    current_version = get_current_version()

    print(f"Current version: {current_version}")
    print(f"New version:     {new_version}")

    if current_version == new_version:
        print("Version is already set to this value.")
        sys.exit(1)

    confirm = input("Proceed with update? (y/N): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    update_version_file(new_version)
    update_changelog(new_version)
    update_memory_file(new_version)

    print("\nDone! Please verify CHANGELOG.md links manually if needed.")


if __name__ == "__main__":
    main()
