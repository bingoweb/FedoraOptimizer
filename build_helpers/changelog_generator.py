#!/usr/bin/env python3
import sys
import os
import subprocess
import datetime
import re

# Add the current directory to path so we can import version_manager if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

CHANGELOG_FILE = "CHANGELOG.md"

def get_last_tag():
    try:
        # Get the latest tag reachable from HEAD
        return subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        # If no tags exist, return None, meaning we fetch all history
        return None

def get_commits(last_tag=None):
    if last_tag:
        cmd = ["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%s"]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        return output.split('\n')
    except subprocess.CalledProcessError:
        return []

def categorize_commits(commits):
    categories = {
        "New Features 🚀": [],
        "Improvements 🔧": [],
        "Fixes 🐛": [],
        "Other Changes": []
    }

    for commit in commits:
        if not commit.strip(): continue
        # Skip CI skips and merge commits if any slip through
        if "[skip ci]" in commit or commit.startswith("Merge"): continue

        lower_commit = commit.lower()

        # Strip prefix for cleaner display
        clean_msg = commit
        if ':' in commit:
            parts = commit.split(':', 1)
            clean_msg = parts[1].strip()
            # capitalize first letter
            if clean_msg:
                clean_msg = clean_msg[0].upper() + clean_msg[1:]

        if lower_commit.startswith("feat") or lower_commit.startswith("add"):
            categories["New Features 🚀"].append(clean_msg)
        elif lower_commit.startswith("fix") or lower_commit.startswith("bug"):
            categories["Fixes 🐛"].append(clean_msg)
        elif lower_commit.startswith("chore") or lower_commit.startswith("docs") or lower_commit.startswith("refactor") or lower_commit.startswith("style") or lower_commit.startswith("perf"):
            categories["Improvements 🔧"].append(clean_msg)
        else:
            categories["Other Changes"].append(clean_msg)

    return categories

def generate_markdown(version, categories):
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    md = f"## [{version}] - {date_str}\n\n"

    has_changes = False
    for title, items in categories.items():
        if items:
            has_changes = True
            md += f"### {title}\n"
            for item in items:
                md += f"- {item}\n"
            md += "\n"

    if not has_changes:
        md += "- Maintenance updates and minor fixes.\n\n"

    return md

def update_changelog_file(new_block):
    if not os.path.exists(CHANGELOG_FILE):
        print("CHANGELOG.md not found! Creating new one.")
        with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# Changelog\n\nAll notable changes to Fedora Optimizer will be documented in this file.\n\n")
            f.write("## [Unreleased]\n\n")
            f.write(new_block)
        return

    with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find ## [Unreleased] and insert after it
    # We assume ## [Unreleased] is at the top.
    # If [Unreleased] section has content, we might want to keep it or move it?
    # Standard auto-release: The commits ARE the release. So we effectively move them to the versioned block.
    # So we insert the new version block immediately after "## [Unreleased]" line.

    pattern = r"(## \[Unreleased\])"
    match = re.search(pattern, content)

    if match:
        # Check if there is extra whitespace or content after [Unreleased]
        # We prefer to insert after the line "## [Unreleased]"
        insertion_index = match.end()

        # Add newlines for spacing
        new_content = content[:insertion_index] + "\n\n" + new_block + content[insertion_index:]

        # Clean up potential double newlines if [Unreleased] was followed by empty lines
        # But simple insertion is usually safer.
    else:
        # No [Unreleased] header found, try to insert after header
        print("Warning: ## [Unreleased] section not found. Appending to top.")
        lines = content.splitlines()
        # Find where to insert (after title)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("# Changelog"):
                insert_pos = i + 1
            if line.startswith("## ["):
                # Found first version, insert before it
                insert_pos = i
                break

        new_content = "\n".join(lines[:insert_pos]) + "\n\n" + new_block + "\n" + "\n".join(lines[insert_pos:])

    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python changelog_generator.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    last_tag = get_last_tag()

    print(f"Generating changelog for {new_version} (changes since {last_tag})...")

    commits = get_commits(last_tag)
    categories = categorize_commits(commits)
    new_block = generate_markdown(new_version, categories)

    update_changelog_file(new_block)

    # Also write to a temporary file for GitHub Release body
    with open("release_body.md", "w", encoding="utf-8") as f:
        f.write(new_block)

    print("CHANGELOG.md updated and release_body.md created.")

if __name__ == "__main__":
    main()
