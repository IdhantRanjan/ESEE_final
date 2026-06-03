#!/usr/bin/env python3
"""
ESEE 2026 Project Structure Visualization Script

Generates a complete visual tree of the project directory structure,
showing file sizes, modification dates, and highlighting key files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


# Files and directories to exclude
EXCLUDE_DIRS = {'venv', '__pycache__', '.git', '.pytest_cache', '.mypy_cache'}
EXCLUDE_FILES = {'.pyc', '.pyo', '.DS_Store'}
EXCLUDE_ROOT_ZIPS = True  # Exclude .zip files in project root

# Key file patterns (for highlighting)
KEY_FILE_PATTERNS = {
    'data': ['*.csv', '*.xlsx', '*.xls', '*.txt'],
    'scripts': ['*.py'],
    'reports': ['*report*.txt', '*validation*.txt', '*log*.txt'],
    'documentation': ['*.md', '*.txt', '*.html'],
}

# Emoji/icons for different file types
FILE_ICONS = {
    'csv': '📊',
    'py': '🐍',
    'txt': '📄',
    'md': '📝',
    'html': '🌐',
    'zip': '📦',
    'pkl': '💾',
    'json': '📋',
    'yaml': '⚙️',
    'yml': '⚙️',
}


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_file_icon(file_path: Path) -> str:
    """Get emoji icon for file type."""
    suffix = file_path.suffix.lower().lstrip('.')
    return FILE_ICONS.get(suffix, '📄')


def should_exclude(path: Path, is_file: bool = False) -> bool:
    """Check if path should be excluded."""
    if is_file:
        # Check file extensions
        if any(path.name.endswith(ext) for ext in EXCLUDE_FILES):
            return True
        # Check root zip files
        if EXCLUDE_ROOT_ZIPS and path.suffix.lower() == '.zip' and path.parent == PROJECT_ROOT:
            return True
    else:
        # Check directory names
        if path.name in EXCLUDE_DIRS:
            return True
    return False


def is_key_file(file_path: Path) -> bool:
    """Check if file should be highlighted as key file."""
    name_lower = file_path.name.lower()
    # Key data files
    if name_lower in ['ess10.csv', 'ess9.csv', 'eurostat_employment.csv']:
        return True
    # Validation/log files
    if any(pattern in name_lower for pattern in ['validation', 'report', 'log', 'summary']):
        return True
    # Main scripts
    if file_path.parent.name == 'src' and file_path.stem.startswith('0'):
        return True
    # Documentation
    if file_path.name in ['README.md', 'DEVELOPMENT_ROADMAP.md', 'ESEE2026_PROJECT_CONTEXT.md']:
        return True
    return False


def scan_directory(root: Path) -> Dict:
    """Recursively scan directory and collect file information."""
    structure = {
        'files': [],
        'dirs': {},
        'total_size': 0,
        'file_count': 0,
    }
    
    try:
        for item in root.iterdir():
            if should_exclude(item):
                continue
            
            if item.is_file():
                try:
                    stat = item.stat()
                    file_info = {
                        'path': item,
                        'name': item.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'relative_path': item.relative_to(PROJECT_ROOT),
                        'is_key': is_key_file(item),
                    }
                    structure['files'].append(file_info)
                    structure['total_size'] += stat.st_size
                    structure['file_count'] += 1
                except (OSError, PermissionError):
                    continue
            
            elif item.is_dir():
                if not should_exclude(item):
                    sub_structure = scan_directory(item)
                    structure['dirs'][item.name] = sub_structure
                    structure['total_size'] += sub_structure['total_size']
                    structure['file_count'] += sub_structure['file_count']
    except (OSError, PermissionError):
        pass
    
    return structure


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_date_short(dt: datetime) -> str:
    """Format datetime for display (short version)."""
    return dt.strftime('%Y-%m-%d')


def generate_tree(structure: Dict, prefix: str = '', is_last: bool = True, max_depth: int = 5, current_depth: int = 0) -> List[str]:
    """Generate tree representation of directory structure."""
    lines = []
    
    if current_depth > max_depth:
        return lines
    
    # Sort files and directories
    files = sorted(structure['files'], key=lambda x: x['name'].lower())
    dirs = sorted(structure['dirs'].items(), key=lambda x: x[0].lower())
    
    # Print directories first
    for i, (dir_name, dir_structure) in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and len(files) == 0
        dir_prefix = '└── ' if is_last_dir else '├── '
        dir_connector = '    ' if is_last_dir else '│   '
        
        # Directory size
        size_str = format_size(dir_structure['total_size'])
        dir_line = f"{prefix}{dir_prefix}📁 {dir_name}/ ({size_str})"
        if dir_structure['file_count'] == 0:
            dir_line += " (EMPTY)"
        lines.append(dir_line)
        
        # Recurse into subdirectory
        new_prefix = prefix + dir_connector
        sub_lines = generate_tree(dir_structure, new_prefix, is_last_dir, max_depth, current_depth + 1)
        lines.extend(sub_lines)
    
    # Print files
    for i, file_info in enumerate(files):
        is_last_file = i == len(files) - 1
        file_prefix = '└── ' if is_last_file else '├── '
        
        icon = get_file_icon(file_info['path'])
        size_str = format_size(file_info['size'])
        date_str = format_date_short(file_info['modified'])
        
        file_line = f"{prefix}{file_prefix}{icon} {file_info['name']} ({size_str}, modified: {date_str})"
        
        if file_info['is_key']:
            file_line += " ✓ KEY FILE"
        
        lines.append(file_line)
    
    return lines


def generate_summary(structure: Dict) -> Dict:
    """Generate summary statistics."""
    summary = {
        'total_size': structure['total_size'],
        'total_files': structure['file_count'],
        'data_size': 0,
        'scripts_size': 0,
        'results_size': 0,
        'empty_dirs': [],
        'key_files': [],
    }
    
    # Helper to traverse structure
    def traverse(sub_structure: Dict, path_parts: List[str]):
        # Check for empty directories
        if sub_structure['file_count'] == 0 and len(sub_structure['dirs']) == 0:
            summary['empty_dirs'].append('/'.join(path_parts))
        
        # Categorize files by directory
        for file_info in sub_structure['files']:
            if file_info['is_key']:
                summary['key_files'].append({
                    'name': file_info['name'],
                    'size': file_info['size'],
                    'path': str(file_info['relative_path']),
                })
            
            # Categorize by path
            path_str = str(file_info['relative_path'])
            if path_str.startswith('data/'):
                summary['data_size'] += file_info['size']
            elif path_str.startswith('src/'):
                summary['scripts_size'] += file_info['size']
            elif path_str.startswith('results/'):
                summary['results_size'] += file_info['size']
        
        # Recurse into subdirectories
        for dir_name, dir_structure in sub_structure['dirs'].items():
            traverse(dir_structure, path_parts + [dir_name])
    
    traverse(structure, [])
    
    return summary


def main():
    """Main execution function."""
    print("=" * 70)
    print("ESEE 2026 PROJECT STRUCTURE")
    print("=" * 70)
    print(f"Scanning project root: {PROJECT_ROOT}")
    print("This may take a moment...")
    print()
    
    # Scan directory structure
    structure = scan_directory(PROJECT_ROOT)
    
    # Generate tree
    tree_lines = generate_tree(structure)
    
    # Generate summary
    summary = generate_summary(structure)
    
    # Build output
    output_lines = []
    output_lines.append("ESEE 2026 PROJECT STRUCTURE")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 70)
    output_lines.append("📁 PROJECT ROOT")
    output_lines.extend(tree_lines)
    output_lines.append("=" * 70)
    output_lines.append("SUMMARY:")
    output_lines.append(f"Total project size: {format_size(summary['total_size'])}")
    output_lines.append(f"Total files: {summary['total_files']:,}")
    output_lines.append(f"Data files: {format_size(summary['data_size'])}")
    output_lines.append(f"Scripts: {format_size(summary['scripts_size'])}")
    output_lines.append(f"Results/logs: {format_size(summary['results_size'])}")
    output_lines.append(f"Empty directories: {len(summary['empty_dirs'])}")
    
    if summary['empty_dirs']:
        output_lines.append("  " + ", ".join(summary['empty_dirs']))
    
    output_lines.append("")
    output_lines.append("KEY FILES STATUS:")
    for key_file in summary['key_files']:
        size_str = format_size(key_file['size'])
        output_lines.append(f"✓ {key_file['name']} ({size_str}) - {key_file['path']}")
    
    if not summary['key_files']:
        output_lines.append("  None detected")
    
    output_lines.append("")
    output_lines.append("MISSING/ISSUES:")
    # Check for expected key files
    expected_files = [
        'data/raw/ESS10.csv',
        'data/raw/eurostat_employment.csv',
    ]
    missing = []
    for expected in expected_files:
        expected_path = PROJECT_ROOT / expected
        if not expected_path.exists():
            missing.append(expected)
    
    if missing:
        for file in missing:
            output_lines.append(f"✗ Missing: {file}")
    else:
        output_lines.append("  None detected")
    
    output_lines.append("")
    output_lines.append("READY FOR: Data preprocessing (Phase 3)")
    output_lines.append("=" * 70)
    
    # Join output
    output_text = "\n".join(output_lines)
    
    # Print to console
    print(output_text)
    
    # Save to file
    logs_dir = PROJECT_ROOT / "results" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    output_file = logs_dir / "project_structure.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"\n✓ Structure saved to: {output_file}")
    
    # Return structure as dictionary (for programmatic access)
    return {
        'structure': structure,
        'summary': summary,
        'tree_text': output_text,
    }


if __name__ == "__main__":
    try:
        result = main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


