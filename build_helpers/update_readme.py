import os
import sys
import re
from datetime import datetime

README_FILE = os.getenv("README_FILE_PATH", "README.md")

def format_date():
    return datetime.now().strftime("%B %d, %Y")

def get_changes_list(changes_text):
    if not changes_text:
        return []

    # Handle escaped newlines if they come from GitHub Actions string
    changes_text = changes_text.replace('\\n', '\n')

    # Split by lines, clean up
    lines = [line.strip() for line in changes_text.split('\n') if line.strip()]
    # Remove git hash if present in parentheses at end (e.g. "Fix bug (a1b2c3d)")
    cleaned = []
    for line in lines:
        # Remove leading "- " if present
        if line.startswith("- "):
            line = line[2:]
        elif line.startswith("* "):
            line = line[2:]

        # Optional: Clean git hashes like (abc1234)
        line = re.sub(r'\s*\([a-f0-9]{7,}\)$', '', line)
        cleaned.append(line)

    return cleaned[:5] # Return max 5 items

def update_readme(version, changes_text):
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the marker where we want to insert
    marker = "## 📰 Recent Updates"
    if marker not in content:
        print(f"Error: Marker '{marker}' not found in README.", file=sys.stderr)
        sys.exit(1)

    date_str = format_date()
    changes = get_changes_list(changes_text)

    new_section = f"\n\n### v{version} ({date_str})\n"
    for change in changes:
        new_section += f"- {change}\n"

    if len(changes) >= 5:
        new_section += f"- [See full changelog](CHANGELOG.md)\n"

    # Insert after the marker
    parts = content.split(marker)

    # We want to keep the marker, then add our new section, then the rest
    # But we might want to check if there is an existing version header immediately after

    updated_content = parts[0] + marker + new_section + parts[1]

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Successfully updated {README_FILE} with v{version}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_readme.py <version> <changes_text>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    changes_text = sys.argv[2]

    update_readme(version, changes_text)

if __name__ == "__main__":
    main()
