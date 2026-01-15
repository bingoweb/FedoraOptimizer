import re
import sys
import os

VERSION_FILE = os.getenv("VERSION_FILE_PATH", "src/ui/tui_app.py")

def get_current_version(content=None):
    if content is None:
        if not os.path.exists(VERSION_FILE):
             raise FileNotFoundError(f"{VERSION_FILE} not found.")
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

    match = re.search(r'VERSION\s*=\s*"([\d\.]+)"', content)
    if not match:
        raise ValueError("Could not find VERSION variable in src/ui/tui_app.py")
    return match.group(1)

def increment_version(version):
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Version {version} does not follow semver (X.Y.Z)")

    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    # Increment patch
    patch += 1

    # Safety check: Never reach 1.0.0 automatically
    if major >= 1:
        print("Warning: Major version is already 1 or greater. Keeping as is.", file=sys.stderr)
        return version

    return f"{major}.{minor}.{patch}"

def update_version_file(new_version):
    if not os.path.exists(VERSION_FILE):
        raise FileNotFoundError(f"{VERSION_FILE} not found.")

    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(
        r'VERSION\s*=\s*"[\d\.]+"',
        f'VERSION = "{new_version}"',
        content
    )

    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

def get_next_version():
    """Calculates the next version without modifying files"""
    current_ver = get_current_version()
    return increment_version(current_ver)

def main():
    try:
        new_version = get_next_version()
        current_version = get_current_version()

        if current_version == new_version:
             # Print current version to stdout even if unchanged, so scripts don't break
             print(new_version)
             return

        update_version_file(new_version)
        print(new_version)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
