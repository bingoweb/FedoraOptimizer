import re
import sys
import os

VERSION_FILE = os.getenv("VERSION_FILE_PATH", "src/ui/tui_app.py")

def get_current_version(content):
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

def main():
    if not os.path.exists(VERSION_FILE):
        print(f"Error: {VERSION_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        current_version = get_current_version(content)
        new_version = increment_version(current_version)

        if current_version == new_version:
             print(f"Version unchanged: {new_version}")
             return

        new_content = re.sub(
            r'VERSION\s*=\s*"[\d\.]+"',
            f'VERSION = "{new_version}"',
            content
        )

        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(new_version)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
