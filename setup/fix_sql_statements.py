#!/usr/bin/env python3
"""
Fix SQL statements in mockup_project_data.py to use text() and named parameters
"""

import re

def fix_sql_statements():
    file_path = "setup/mockup_project_data.py"

    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Replace all db.execute with INSERT statements to use text() and simple positional parameters
    # This is a simpler fix - just wrap existing SQL in text()

    # Pattern to match db.execute with triple-quoted strings
    pattern = r'db\.execute\(\s*"""(.*?)"""\s*,\s*([^)]+)\)'

    def replacement(match):
        sql = match.group(1).strip()
        params = match.group(2).strip()
        return f'db.execute(text("""{sql}"""), {params})'

    # Apply the replacement
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)

    print("Fixed SQL statements in mockup_project_data.py")

if __name__ == "__main__":
    fix_sql_statements()