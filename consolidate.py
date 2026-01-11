#!/usr/bin/env python3
"""
Consolidate acrodefs.tex files from multiple locations into a single deduplicated file.
Tracks last-updated dates and keeps the latest version of each definition.
"""

import os
import re
import subprocess
from collections import OrderedDict
from datetime import datetime

def get_file_date(file_path):
    """Get file date from git history if available, otherwise use file timestamp."""
    try:
        # Try to get git commit date
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%aI', '--', file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip()
            # Parse ISO format date
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
        pass

    # Fallback to file modification time
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except OSError:
        return datetime.min

def read_acrodefs(file_path, file_date):
    """Read an acrodefs.tex file and extract definitions with dates."""
    definitions = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Find all \acrodef, \newacronym or \newcommand definitions
            # Pattern for \acrodef{label}{definition}
            acrodef_pattern = r'\\acrodef\s*\{([^}]+)\}\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
            # Pattern for \newacronym{label}{short}{long}
            newacronym_pattern = r'\\newacronym(?:\[.*?\])?\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}'
            # Pattern for \newcommand
            newcommand_pattern = r'\\newcommand\s*\{([^}]+)\}(?:\[.*?\])?\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'

            for match in re.finditer(acrodef_pattern, content, re.MULTILINE):
                full_match = match.group(0)
                label = match.group(1).strip()
                definitions.append((label, full_match, 'acrodef', file_date, file_path))

            for match in re.finditer(newacronym_pattern, content, re.MULTILINE):
                full_match = match.group(0)
                label = match.group(1).strip()
                definitions.append((label, full_match, 'newacronym', file_date, file_path))

            for match in re.finditer(newcommand_pattern, content, re.MULTILINE):
                full_match = match.group(0)
                label = match.group(1).strip()
                definitions.append((label, full_match, 'newcommand', file_date, file_path))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return definitions

def consolidate_acrodefs(list_file):
    """Consolidate all acrodefs.tex files listed in list_file, keeping latest versions."""
    # Use OrderedDict to maintain insertion order and deduplicate
    # Store: {label: (definition, def_type, date, source_file)}
    consolidated = OrderedDict()

    with open(list_file, 'r') as f:
        for line in f:
            file_path = line.strip()
            if not file_path or file_path.startswith('#'):
                continue

            if os.path.exists(file_path):
                file_date = get_file_date(file_path)
                date_str = file_date.strftime('%Y-%m-%d')
                print(f"Processing: {file_path} (dated: {date_str})")

                definitions = read_acrodefs(file_path, file_date)
                for label, definition, def_type, file_date, source_file in definitions:
                    if label not in consolidated:
                        # First occurrence - add it
                        consolidated[label] = (definition, def_type, file_date, source_file)
                    else:
                        # Check if this version is newer
                        existing_defn, existing_type, existing_date, existing_source = consolidated[label]
                        if definition != existing_defn:
                            # Definitions differ - compare dates
                            if file_date > existing_date:
                                print(f"  Updating {label}: newer version from {date_str} (was {existing_date.strftime('%Y-%m-%d')})")
                                consolidated[label] = (definition, def_type, file_date, source_file)
                            else:
                                print(f"  Skipping older version of {label} from {date_str}")
                        # If definitions are identical, silently skip
            else:
                print(f"Warning: File not found: {file_path}")

    return consolidated

def write_consolidated_file(consolidated, output_file):
    """Write consolidated definitions to output file with date comments."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("% Consolidated acrodefs.tex\n")
        f.write("% Auto-generated - DO NOT EDIT MANUALLY\n")
        f.write("% Generated from multiple sources\n")
        f.write(f"% Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Group by type with all metadata
        acrodefs = [(label, defn, date, source) for label, (defn, dtype, date, source) in consolidated.items() if dtype == 'acrodef']
        newacronyms = [(label, defn, date, source) for label, (defn, dtype, date, source) in consolidated.items() if dtype == 'newacronym']
        commands = [(label, defn, date, source) for label, (defn, dtype, date, source) in consolidated.items() if dtype == 'newcommand']

        if acrodefs:
            f.write("% Acronyms (acrodef)\n")
            for label, defn, date, source in sorted(acrodefs):
                date_str = date.strftime('%Y-%m-%d')
                # Shorten source path for readability
                short_source = source.replace('../../', '')
                f.write(f"% Last updated: {date_str} from {short_source}\n")
                f.write(defn + '\n')
            f.write('\n')

        if newacronyms:
            f.write("% Acronyms (newacronym)\n")
            for label, defn, date, source in sorted(newacronyms):
                date_str = date.strftime('%Y-%m-%d')
                short_source = source.replace('../../', '')
                f.write(f"% Last updated: {date_str} from {short_source}\n")
                f.write(defn + '\n')
            f.write('\n')

        if commands:
            f.write("% Commands\n")
            for label, defn, date, source in sorted(commands):
                date_str = date.strftime('%Y-%m-%d')
                short_source = source.replace('../../', '')
                f.write(f"% Last updated: {date_str} from {short_source}\n")
                f.write(defn + '\n')
            f.write('\n')

if __name__ == '__main__':
    list_file = 'list.txt'
    output_file = 'acrodefs.tex'

    print(f"Reading file list from: {list_file}")
    consolidated = consolidate_acrodefs(list_file)

    print(f"\nTotal unique definitions: {len(consolidated)}")
    print(f"Writing consolidated file to: {output_file}")
    write_consolidated_file(consolidated, output_file)
    print("Done!")
    print(f"\nConsolidated file created with date tracking.")
    print("Definitions are now tracked by last-updated date.")
    print("Newer versions will replace older ones automatically.")
