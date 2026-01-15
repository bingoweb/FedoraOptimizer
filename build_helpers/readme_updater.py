#!/usr/bin/env python3
import sys
import os
import re

README_FILE = "README.md"

def update_readme(new_version, changes_summary):
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.")
        sys.exit(1)

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strategy:
    # 1. Locate "## 📰 Recent Updates"
    # 2. Extract the current "latest" update (everything until <details>)
    # 3. Create a new "latest" block
    # 4. Move the old "latest" block into the top of <details>...<summary>View Older Updates</summary> content

    # Regex to find Recent Updates section
    # Matches: ## 📰 Recent Updates ... (content) ... <details>

    # Let's find the start of Recent Updates
    header_pattern = r"(## 📰 Recent Updates)"
    header_match = re.search(header_pattern, content)

    if not header_match:
        print("Could not find 'Recent Updates' section in README.")
        return

    start_index = header_match.end()

    # Find the start of <details>
    details_pattern = r"(<details>)"
    details_match = re.search(details_pattern, content[start_index:])

    if not details_match:
        print("Could not find '<details>' block in Recent Updates.")
        return

    details_start_abs = start_index + details_match.start()

    # The content between header and <details> is the current "Recent Update"
    old_recent_content = content[start_index:details_start_abs].strip()

    # Find where to insert inside details
    # We look for the summary line, then insert after it
    summary_pattern = r"(<summary>.*?</summary>)"
    summary_match = re.search(summary_pattern, content[details_start_abs:])

    if not summary_match:
        print("Could not find summary in details block.")
        return

    insert_point_inside_details = details_start_abs + summary_match.end()

    # Construct the NEW recent update block
    # We need a nice summary. The changelog generator produces full markdown.
    # We probably want a condensed version or just the top items.

    import datetime
    date_str = datetime.date.today().strftime("%B %d, %Y")

    new_recent_block = f"\n\n### v{new_version} ({date_str}) 🌟\n"

    # Convert bullet points to a cleaner summary if possible, or just use them
    # changes_summary is expected to be a list of strings or a text block
    if isinstance(changes_summary, str):
        # Filter out empty lines and headers
        lines = [l for l in changes_summary.split('\n') if l.strip().startswith('-')]
        # Take top 5 items
        for line in lines[:5]:
             new_recent_block += f"{line}\n"
        if len(lines) > 5:
            new_recent_block += f"- ... and {len(lines)-5} more changes.\n"

    new_recent_block += "\n"

    # Now construct the moved block (old recent) to go into details
    # We need to make sure headers in old_recent_content are downgraded or kept as is?
    # Usually they are ### vX.Y.Z.
    # Let's just wrap it.

    # Note: old_recent_content might be empty if this is first run, but unlikely given the file.

    moved_block = "\n\n" + old_recent_content + "\n"

    # Reassemble file
    # Part 1: Start to 'Recent Updates' header + new recent block
    # Part 2: <details> + <summary>...<summary> + moved block + rest of details

    part1 = content[:start_index] + new_recent_block

    # We need to preserve the text BEFORE <details> but AFTER the new block?
    # No, we replaced the space between Header and Details with New Block.

    part2_start = content[:details_start_abs] # This is just for reference, we don't use it directly

    part3 = content[insert_point_inside_details:]

    # The middle part is the <details> tag and summary tag
    part_middle = content[details_start_abs:insert_point_inside_details]

    final_content = part1 + part_middle + moved_block + part3

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"README.md updated with v{new_version}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python readme_updater.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]

    # We need to get the changes summary.
    # We can reuse changelog_generator logic or just read it from stdin?
    # Let's import changelog_generator to get the data

    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import changelog_generator

        last_tag = changelog_generator.get_last_tag()
        commits = changelog_generator.get_commits(last_tag)
        categories = changelog_generator.categorize_commits(commits)

        # Create a simple list of changes for the readme
        summary_text = ""
        for cat, items in categories.items():
            for item in items:
                summary_text += f"- {item}\n"

        if not summary_text:
            summary_text = "- Maintenance and stability improvements."

        update_readme(new_version, summary_text)

    except ImportError:
        print("Could not import changelog_generator.")
        sys.exit(1)

if __name__ == "__main__":
    main()
