#!/usr/bin/env python3
"""
Compiles all Git-tracked text files from the project root
into a single compilation.txt (with summary + full directory tree)
Automatically moves up one directory to find root.
"""

from pathlib import Path
from datetime import datetime
import subprocess

OUTPUT_FILE = "compilation.txt"


def is_likely_text_file(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return b'\0' not in f.read(1024)
    except:
        return False


def get_directory_tree(root: Path) -> str:
    """Generate a clean, full directory tree (folders + files)"""
    lines = [f"Project Root: {root.resolve()}\n"]

    def walk(path: Path, prefix: str = ""):
        contents = sorted(p for p in path.iterdir() if not p.name.startswith('.'))

        # Skip junk directories
        contents = [p for p in contents if p.name not in {
            '.git', '.venv', '__pycache__', 'results', 'log',
            '.pytest_cache', '.ipynb_checkpoints', '.mypy_cache'
        }]

        pointers = ['├── '] * (len(contents) - 1) + ['└── '] if contents else []

        for pointer, child in zip(pointers, contents):
            if child.is_dir():
                lines.append(f"{prefix}{pointer}{child.name}/")
                walk(child, prefix + ("    " if pointer == "└── " else "│   "))
            else:
                lines.append(f"{prefix}{pointer}{child.name}")

    walk(root)
    return "\n".join(lines)


def main():
    # Move up one directory to reach project root
    root = Path(__file__).parent.parent.resolve()
    print(f"Project root detected → {root}\n")

    # Get all files tracked by git
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True
        )
        tracked_files = [root / f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    except Exception as e:
        print("Error running git ls-files:", e)
        return

    # Filter to text files only
    text_files = [p for p in tracked_files if p.is_file() and is_likely_text_file(p)]

    # Summary stats
    total_files = len(text_files)
    total_size_kb = sum(p.stat().st_size for p in text_files) // 1024

    with open(OUTPUT_FILE, "w", encoding="utf-8", errors="ignore") as out:
        out.write("=" * 90 + "\n")
        out.write(f"PROJECT COMPILATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Root: {root}\n")
        out.write("=" * 90 + "\n\n")

        # Summary Table
        out.write("SUMMARY\n")
        out.write("-" * 50 + "\n")
        out.write(f"Total files included : {total_files}\n")
        out.write(f"Total size           : {total_size_kb} KB\n")
        out.write(f"Generated on         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write("-" * 50 + "\n\n")

        # Directory Tree
        out.write("DIRECTORY TREE\n")
        out.write("-" * 50 + "\n")
        out.write(get_directory_tree(root))
        out.write("\n" + "=" * 90 + "\n\n")

        # File contents
        text_files.sort()
        for file_path in text_files:
            try:
                rel_path = file_path.relative_to(root)
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                out.write(f"FILE: {rel_path}\n")
                out.write("-" * 80 + "\n")
                out.write(content.strip())
                out.write("\n\n" + "=" * 90 + "\n\n")
                print(f"✓ Added: {rel_path} ({len(content):,} chars)")
            except Exception as e:
                print(f"✗ Skipped {file_path}: {e}")

    print(f"\nDone! → {OUTPUT_FILE} created ({total_files} files, {total_size_kb} KB)")


if __name__ == "__main__":
    main()