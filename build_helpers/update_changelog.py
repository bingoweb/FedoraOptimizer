import os
import sys
import re
from datetime import datetime

CHANGELOG_FILE = os.getenv("CHANGELOG_FILE_PATH", "CHANGELOG.md")

def format_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_changes_list(changes_text):
    if not changes_text:
        return []

    # Handle escaped newlines
    changes_text = changes_text.replace('\\n', '\n')

    lines = [line.strip() for line in changes_text.split('\n') if line.strip()]
    cleaned = []
    for line in lines:
        if line.startswith("- "):
            line = line[2:]
        elif line.startswith("* "):
            line = line[2:]

        # Clean git hashes
        line = re.sub(r'\s*\([a-f0-9]{7,}\)$', '', line)
        cleaned.append(line)

    return cleaned

def update_changelog(version, changes_text):
    if not os.path.exists(CHANGELOG_FILE):
        print(f"Error: {CHANGELOG_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    date_str = format_date()
    changes = get_changes_list(changes_text)

    new_entry = f"\n## [{version}] - {date_str}\n\n"
    new_entry += "### Automated Changes\n"
    for change in changes:
        new_entry += f"- {change}\n"

    # Insert logic:
    # Look for the first version header (## [X.Y.Z]...) or ## [Unreleased]
    # We want to insert *after* [Unreleased] if it exists, or at the top of the versions.

    # Common Keep-a-Changelog pattern:
    # ## [Unreleased]
    # ...
    # ## [0.4.0] ...

    if "## [Unreleased]" in content:
        # Split after Unreleased section?
        # Easier: Find the *second* h2 header (which would be the previous version) and insert before it?
        # Or just find "## [Unreleased]" line and search for the NEXT "## [" line.

        # Let's try to find where the first *released* version starts.
        # Regex for version header: ## [\d
        match = re.search(r'## \[\d', content)
        if match:
            start_idx = match.start()
            updated_content = content[:start_idx] + new_entry + "\n" + content[start_idx:]
        else:
            # No version headers found? Append to end or after header?
            # Append after header if exists
            if "# Changelog" in content:
                # Find end of header section?
                # Just insert at top of releases (after Unreleased)
                unreleased_idx = content.find("## [Unreleased]")
                # Find next ## after unreleased
                next_header_idx = content.find("## [", unreleased_idx + 1)
                if next_header_idx != -1:
                     updated_content = content[:next_header_idx] + new_entry + "\n" + content[next_header_idx:]
                else:
                    updated_content = content + "\n" + new_entry
            else:
                 updated_content = new_entry + "\n" + content
    else:
        # No Unreleased section. Just find the first version header.
        match = re.search(r'## \[\d', content)
        if match:
            start_idx = match.start()
            updated_content = content[:start_idx] + new_entry + "\n" + content[start_idx:]
        else:
            # Just append?
             updated_content = content + "\n" + new_entry

    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Successfully updated {CHANGELOG_FILE} with v{version}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_changelog.py <version> <changes_text>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    changes_text = sys.argv[2]

    update_changelog(version, changes_text)

if __name__ == "__main__":
    main()
