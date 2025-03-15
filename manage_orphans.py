#!/usr/bin/env python3
"""
Script to manage orphaned files in the Dudoxx Extraction project.

This script provides utilities to:
1. List all orphaned files
2. Move orphaned files to a specific directory
3. Delete orphaned files (with confirmation)
4. Restore orphaned files from the orphans directory
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Set, Optional

# Define categories
CATEGORIES = [
    "documentation",
    "frontend",
    "backend",
    "utilities",
    "tests",
    "misc",
]


def list_orphans(orphans_dir: str, category: Optional[str] = None) -> None:
    """
    List all orphaned files.
    
    Args:
        orphans_dir: Path to the orphans directory
        category: Optional category to filter by
    """
    orphans_path = Path(orphans_dir)
    
    if not orphans_path.exists():
        print(f"Error: Orphans directory '{orphans_dir}' does not exist.")
        return
    
    # Get all categories
    categories = [d for d in os.listdir(orphans_path) if (orphans_path / d).is_dir()]
    
    # Filter by category if specified
    if category:
        if category not in categories:
            print(f"Error: Category '{category}' not found.")
            return
        categories = [category]
    
    # Print orphaned files by category
    total_files = 0
    
    for cat in categories:
        cat_path = orphans_path / cat
        
        # Get all files in the category
        files = []
        for root, _, filenames in os.walk(cat_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(cat_path)
                files.append(str(rel_path))
        
        if files:
            print(f"\n{cat.capitalize()} ({len(files)}):")
            for file in sorted(files):
                print(f"  - {file}")
            total_files += len(files)
    
    print(f"\nTotal orphaned files: {total_files}")


def move_orphans(orphans_dir: str, target_dir: str, category: Optional[str] = None) -> None:
    """
    Move orphaned files to a target directory.
    
    Args:
        orphans_dir: Path to the orphans directory
        target_dir: Path to the target directory
        category: Optional category to filter by
    """
    orphans_path = Path(orphans_dir)
    target_path = Path(target_dir)
    
    if not orphans_path.exists():
        print(f"Error: Orphans directory '{orphans_dir}' does not exist.")
        return
    
    # Create target directory if it doesn't exist
    if not target_path.exists():
        os.makedirs(target_path)
    
    # Get all categories
    categories = [d for d in os.listdir(orphans_path) if (orphans_path / d).is_dir()]
    
    # Filter by category if specified
    if category:
        if category not in categories:
            print(f"Error: Category '{category}' not found.")
            return
        categories = [category]
    
    # Move orphaned files by category
    total_files = 0
    
    for cat in categories:
        cat_path = orphans_path / cat
        
        # Create category directory in target
        cat_target_path = target_path / cat
        if not cat_target_path.exists():
            os.makedirs(cat_target_path)
        
        # Get all files in the category
        for root, _, filenames in os.walk(cat_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(cat_path)
                
                # Get the original file path
                if os.path.islink(file_path):
                    original_path = os.readlink(file_path)
                    
                    # Create target file path
                    target_file_path = cat_target_path / rel_path
                    
                    # Create parent directories if needed
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    
                    # Copy the original file to the target directory
                    try:
                        shutil.copy2(original_path, target_file_path)
                        print(f"Copied: {rel_path} -> {target_file_path}")
                        total_files += 1
                    except Exception as e:
                        print(f"Error copying {rel_path}: {e}")
    
    print(f"\nTotal files moved: {total_files}")


def delete_orphans(orphans_dir: str, category: Optional[str] = None, force: bool = False) -> None:
    """
    Delete orphaned files.
    
    Args:
        orphans_dir: Path to the orphans directory
        category: Optional category to filter by
        force: Whether to force deletion without confirmation
    """
    orphans_path = Path(orphans_dir)
    
    if not orphans_path.exists():
        print(f"Error: Orphans directory '{orphans_dir}' does not exist.")
        return
    
    # Get all categories
    categories = [d for d in os.listdir(orphans_path) if (orphans_path / d).is_dir()]
    
    # Filter by category if specified
    if category:
        if category not in categories:
            print(f"Error: Category '{category}' not found.")
            return
        categories = [category]
    
    # Get all files to delete
    files_to_delete = []
    
    for cat in categories:
        cat_path = orphans_path / cat
        
        # Get all files in the category
        for root, _, filenames in os.walk(cat_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(orphans_path)
                
                # Get the original file path
                if os.path.islink(file_path):
                    original_path = os.readlink(file_path)
                    files_to_delete.append((str(rel_path), original_path))
    
    # Confirm deletion
    if not force:
        print(f"The following {len(files_to_delete)} files will be deleted:")
        for rel_path, original_path in files_to_delete:
            print(f"  - {original_path}")
        
        confirmation = input("\nAre you sure you want to delete these files? (y/N): ")
        if confirmation.lower() != "y":
            print("Deletion cancelled.")
            return
    
    # Delete files
    total_deleted = 0
    
    for rel_path, original_path in files_to_delete:
        try:
            os.remove(original_path)
            print(f"Deleted: {original_path}")
            total_deleted += 1
        except Exception as e:
            print(f"Error deleting {original_path}: {e}")
    
    print(f"\nTotal files deleted: {total_deleted}")


def restore_orphans(orphans_dir: str, category: Optional[str] = None) -> None:
    """
    Restore orphaned files from the orphans directory.
    
    Args:
        orphans_dir: Path to the orphans directory
        category: Optional category to filter by
    """
    orphans_path = Path(orphans_dir)
    
    if not orphans_path.exists():
        print(f"Error: Orphans directory '{orphans_dir}' does not exist.")
        return
    
    # Get all categories
    categories = [d for d in os.listdir(orphans_path) if (orphans_path / d).is_dir()]
    
    # Filter by category if specified
    if category:
        if category not in categories:
            print(f"Error: Category '{category}' not found.")
            return
        categories = [category]
    
    # Restore orphaned files by category
    total_restored = 0
    
    for cat in categories:
        cat_path = orphans_path / cat
        
        # Get all files in the category
        for root, _, filenames in os.walk(cat_path):
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Skip non-symlinks
                if not os.path.islink(file_path):
                    continue
                
                # Get the original file path
                original_path = os.readlink(file_path)
                
                # Check if the original file exists
                if os.path.exists(original_path):
                    print(f"File already exists: {original_path}")
                    continue
                
                # Create parent directories if needed
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                
                # Create a copy of the symlink target
                try:
                    # Get the absolute path of the symlink target
                    target_path = os.path.abspath(os.path.join(os.path.dirname(file_path), os.readlink(file_path)))
                    
                    # Copy the file
                    shutil.copy2(target_path, original_path)
                    print(f"Restored: {original_path}")
                    total_restored += 1
                except Exception as e:
                    print(f"Error restoring {original_path}: {e}")
    
    print(f"\nTotal files restored: {total_restored}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage orphaned files in the Dudoxx Extraction project.")
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List orphaned files")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Category to filter by")
    
    # Move command
    move_parser = subparsers.add_parser("move", help="Move orphaned files to a target directory")
    move_parser.add_argument("target_dir", help="Target directory to move files to")
    move_parser.add_argument("--category", choices=CATEGORIES, help="Category to filter by")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete orphaned files")
    delete_parser.add_argument("--category", choices=CATEGORIES, help="Category to filter by")
    delete_parser.add_argument("--force", action="store_true", help="Force deletion without confirmation")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore orphaned files")
    restore_parser.add_argument("--category", choices=CATEGORIES, help="Category to filter by")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default to list command if no command is specified
    if not args.command:
        args.command = "list"
    
    # Execute command
    if args.command == "list":
        list_orphans("orphans", args.category)
    elif args.command == "move":
        move_orphans("orphans", args.target_dir, args.category)
    elif args.command == "delete":
        delete_orphans("orphans", args.category, args.force)
    elif args.command == "restore":
        restore_orphans("orphans", args.category)


if __name__ == "__main__":
    main()
