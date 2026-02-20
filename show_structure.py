import os
from pathlib import Path


def show_structure(start_path='.', ignore_patterns=None):
    """Display clean directory structure"""
    if ignore_patterns is None:
        ignore_patterns = {
            'venv', 'env', '.venv', '__pycache__', '.git',
            '.vscode', '.idea', '.pytest_cache', '.mypy_cache',
            '.coverage', 'htmlcov', '*.pyc', '*.pyo', '*.pyd',
            '.DS_Store', 'Thumbs.db', '*.log', '*.pot', '*.mo',
            '*.egg-info', 'build', 'dist', '*.db-journal'
        }

    print(f"\n📁 Project Structure: {os.path.basename(os.path.abspath(start_path))}/")
    print("=" * 60)

    total_files = 0
    total_folders = 0

    for root, dirs, files in os.walk(start_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_patterns and not d.startswith('.')]

        level = root.replace(start_path, '').count(os.sep)
        indent = '│   ' * level + '├── '
        folder_indent = '│   ' * level + '└── '

        if level == 0:
            print(f"📂 ./")
        else:
            folder_name = os.path.basename(root)
            print(f"{folder_indent}{folder_name}/")
            total_folders += 1

        file_indent = '│   ' * (level + 1) + '├── '
        for f in sorted(files):
            if not any(f.endswith(ext.replace('*', '')) for ext in ignore_patterns if ext.startswith('*')):
                print(f"{file_indent}{f}")
                total_files += 1

    print("=" * 60)
    print(f"📊 Summary: {total_folders} folders, {total_files} files")


if __name__ == "__main__":
    # Change to the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    show_structure('.')