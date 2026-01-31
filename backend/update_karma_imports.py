"""
Script to update Karma Tracker imports to work within backend structure
"""
import os
import re
from pathlib import Path

# Base directory
base_dir = Path(__file__).parent

# Files to update
routes_dir = base_dir / "app" / "routers" / "karma_tracker"
utils_dir = base_dir / "app" / "utils" / "karma"

# Import mappings
import_mappings = {
    r"^from database import": "from app.core.karma_database import",
    r"^from config import": "from app.core.karma_config import",
    r"^from validation_middleware import": "from app.middleware.karma_validation import",
    r"^from utils\.(.*) import": r"from app.utils.karma.\1 import",
    r"^import database": "from app.core import karma_database as database",
    r"^import config": "from app.core import karma_config as config",
}

def update_file_imports(file_path):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply import mappings
        for pattern, replacement in import_mappings.items():
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def update_all_files():
    """Update all Python files in karma_tracker routes and utils"""
    updated_count = 0
    
    # Update route files
    if routes_dir.exists():
        for py_file in routes_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                if update_file_imports(py_file):
                    updated_count += 1
    
    # Update utils files
    if utils_dir.exists():
        for py_file in utils_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                if update_file_imports(py_file):
                    updated_count += 1
    
    print(f"\n✅ Updated {updated_count} files")

if __name__ == "__main__":
    update_all_files()

