#!/usr/bin/env python3
"""
Compiles all text files (respecting .gitignore) into compilation.txt
→ Directory tree, summary, and included files are now perfectly consistent.
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


def is_ignored_by_git(path: Path) -> bool:
    """True if git would ignore this path"""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=path.parent,
            capture_output=True
        )
        return result.returncode == 0
    except:
        return False


def get_directory_tree(root: Path) -> str:
    """Clean, full directory tree (folders + files)"""
    lines = [f"Project Root: {root.resolve()}\n"]

    def walk(path: Path, prefix: str = ""):
        contents = sorted(p for p in path.iterdir() if not p.name.startswith('.'))

        # Skip junk
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
                if is_likely_text_file(child) and not is_ignored_by_git(child):
                    lines.append(f"{prefix}{pointer}{child.name}")

    walk(root)
    return "\n".join(lines)

def main():
    root = Path(__file__).parent.parent.resolve()
    print(f"Project root detected → {root}\n")

    # Collect all text files that are NOT ignored by git
    text_files = []
    for p in root.rglob("*"):
        if p.is_file() and is_likely_text_file(p) and not is_ignored_by_git(p):
            text_files.append(p)

    total_files = len(text_files)
    total_size_kb = sum(p.stat().st_size for p in text_files) // 1024
    with open(Path(root).joinpath("log").joinpath(OUTPUT_FILE), "w", encoding="utf-8", errors="ignore") as out:
        out.write("=" * 90 + "\n")
        out.write(f"PROJECT COMPILATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Root: {root}\n")
        out.write("=" * 90 + "\n\n")

        out.write("SUMMARY\n")
        out.write("-" * 50 + "\n")
        out.write(f"Total files included : {total_files}\n")
        out.write(f"Total size           : {total_size_kb} KB\n")
        out.write(f"Generated on         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write("-" * 50 + "\n\n")

        out.write("DIRECTORY TREE\n")
        out.write("-" * 50 + "\n")
        out.write(get_directory_tree(root))          # keep your current tree function
        out.write("\n" + "=" * 90 + "\n\n")

        text_files.sort()
        for file_path in text_files:
            rel_path = file_path.relative_to(root)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            out.write(f"FILE: {rel_path}\n")
            out.write("-" * 80 + "\n")
            out.write(content.strip())
            out.write("\n\n" + "=" * 90 + "\n\n")
            print(f"✓ Added: {rel_path} ({len(content):,} chars)")
            rel_path = file_path.relative_to(root)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            out.write(f"FILE: {rel_path}\n")
            out.write("-" * 80 + "\n")
            out.write(content.strip())
            out.write("\n\n" + "=" * 90 + "\n\n")
            print(f"✓ Added: {rel_path} ({len(content):,} chars)")

    print(f"\nDone! → {OUTPUT_FILE} created ({total_files} files, {total_size_kb} KB)")


if __name__ == "__main__":
    main()