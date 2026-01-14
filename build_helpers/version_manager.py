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

    # Handle standard SemVer (0.4.1) -> Convert to extended (0.4.1.01)
    if len(parts) == 3:
        major, minor, patch = map(int, parts)
        # Start the build number
        return f"{major}.{minor}.{patch}.01"

    # Handle extended version (0.4.1.01)
    elif len(parts) == 4:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
        build = int(parts[3])

        # Increment build number
        build += 1

        # Format with leading zero if less than 10
        build_str = f"{build:02d}"

        return f"{major}.{minor}.{patch}.{build_str}"

    else:
        raise ValueError(f"Version {version} format not recognized")

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
