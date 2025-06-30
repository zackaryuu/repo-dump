#!/usr/bin/env python3
"""
Script to protect zip files based on TagSpaces sidecar files.

This script:
1. Loops through all zip files in the dump folder
2. Checks TagSpaces sidecar files for "PROTECT" tag
3. If PROTECT tag is found and zip is not password protected,
   recreates the zip with password from REPO_DUMP_ZIP_PASS environment variable
"""

import os
import json
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def load_sidecar_file(zip_path: Path) -> Optional[Dict]:
    """Load and parse the TagSpaces sidecar file for a given zip file."""
    sidecar_path = zip_path.parent / ".ts" / f"{zip_path.name}.json"
    
    if not sidecar_path.exists():
        print(f"No sidecar file found for {zip_path.name}")
        return None
    
    try:
        with open(sidecar_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading sidecar file {sidecar_path}: {e}")
        return None


def has_protect_tag(sidecar_data: Dict) -> bool:
    """Check if the sidecar data contains a PROTECT tag."""
    if not sidecar_data or 'tags' not in sidecar_data:
        return False
    
    tags = sidecar_data.get('tags', [])
    for tag in tags:
        if tag.get('title', '').upper() == 'PROTECT':
            return True
    
    return False


def is_password_protected(zip_path: Path) -> bool:
    """Check if a zip file is password protected."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Try to read the file list - this will fail if password protected
            zf.namelist()
            
            # If we can read the namelist, try to extract the first file
            # to confirm it's not password protected
            if zf.namelist():
                first_file = zf.namelist()[0]
                try:
                    # Try to read a small amount from the first file
                    with zf.open(first_file) as f:
                        f.read(1)  # Just read 1 byte
                    return False  # Successfully read, not password protected
                except RuntimeError as e:
                    if "Bad password" in str(e) or "password required" in str(e).lower():
                        return True
                    # Some other error, assume not password protected
                    return False
            else:
                # Empty zip file
                return False
                
    except zipfile.BadZipFile:
        print(f"Warning: {zip_path.name} is not a valid zip file")
        return False
    except Exception as e:
        print(f"Error checking password protection for {zip_path.name}: {e}")
        return False


def recreate_zip_with_password(zip_path: Path, password: str) -> bool:
    """Recreate a zip file with password protection using 7-zip."""
    print(f"Recreating {zip_path.name} with password protection...")
    
    temp_dir = None
    try:
        # Create a temporary directory to extract files
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Extract the original zip
        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            original_zip.extractall(temp_path)
        
        # Create a backup of the original zip
        backup_path = zip_path.with_suffix(zip_path.suffix + '.backup')
        shutil.copy2(zip_path, backup_path)
        print(f"Created backup: {backup_path.name}")
        
        # Use 7-zip to create password-protected zip
        # Try common 7-zip installation paths
        username = os.getenv('USERNAME', os.getenv('USER', ''))
        seven_zip_paths = [
            "7z",  # If 7z is in PATH
            rf"C:\Users\{username}\scoop\apps\7zip\current\7z.exe",
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe"
        ]
        
        seven_zip_exe = None
        for path in seven_zip_paths:
            try:
                subprocess.run([path], capture_output=True, check=False)
                seven_zip_exe = path
                break
            except FileNotFoundError:
                continue
        
        if not seven_zip_exe:
            raise Exception("7-Zip not found. Please install 7-Zip or add it to PATH")
        
        # Create password-protected zip with 7-zip
        cmd = [
            seven_zip_exe, "a", "-tzip", f"-p{password}", "-mem=AES256",
            str(zip_path), f"{temp_path}/*"
        ]
        
        # Remove the original file first (7-zip will overwrite, but let's be explicit)
        zip_path.unlink()
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_path)
        
        if result.returncode != 0:
            raise Exception(f"7-Zip failed: {result.stderr}")
        
        print(f"Successfully recreated {zip_path.name} with password protection")
        return True
        
    except Exception as e:
        print(f"Error recreating {zip_path.name}: {e}")
        # Restore from backup if it exists
        backup_path = zip_path.with_suffix(zip_path.suffix + '.backup')
        if backup_path.exists():
            shutil.copy2(backup_path, zip_path)
            print(f"Restored {zip_path.name} from backup")
        return False
        
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """Main function to process all zip files in the dump folder."""
    # Get the repository root and dump folder
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent  # Go up from .github/scripts to repo root
    dump_dir = repo_root / "dump"
    
    if not dump_dir.exists():
        raise FileNotFoundError(f"Dump directory not found at {dump_dir}")
    
    # Get password from environment variable
    password = os.getenv('REPO_DUMP_ZIP_PASS')
    if not password:
        raise EnvironmentError("REPO_DUMP_ZIP_PASS environment variable not set")
    
    # Find all zip files in the first level of dump directory only
    zip_files = [f for f in dump_dir.iterdir() if f.is_file() and f.suffix.lower() == '.zip']
    
    if not zip_files:
        print("No zip files found in the dump directory")
        return
    
    print(f"Found {len(zip_files)} zip files in {dump_dir}")
    print("-" * 50)
    
    protected_count = 0
    processed_count = 0
    
    for zip_path in zip_files:
        print(f"\nProcessing: {zip_path.name}")
        
        # Load sidecar file
        sidecar_data = load_sidecar_file(zip_path)
        if not sidecar_data:
            continue
        
        # Check for PROTECT tag
        if not has_protect_tag(sidecar_data):
            print(f"  No PROTECT tag found, skipping")
            continue
        
        print(f"  PROTECT tag found!")
        
        # Check if backup already exists (indicates already processed)
        backup_path = zip_path.with_suffix(zip_path.suffix + '.backup')
        if backup_path.exists():
            print(f"  Backup file already exists, skipping (already processed)")
            protected_count += 1
            continue
        
        # Check if already password protected
        if is_password_protected(zip_path):
            print(f"  Already password protected, skipping")
            protected_count += 1
            continue
        
        print(f"  Not password protected, recreating with password...")
        
        # Recreate with password
        if recreate_zip_with_password(zip_path, password):
            protected_count += 1
            processed_count += 1
        
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Total zip files: {len(zip_files)}")
    print(f"  Files with PROTECT tag: {protected_count}")
    print(f"  Files processed (recreated): {processed_count}")


if __name__ == "__main__":
    main()
