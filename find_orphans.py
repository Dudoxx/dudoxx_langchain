#!/usr/bin/env python3
"""
Script to identify orphaned files in the Dudoxx Extraction project.

This script analyzes the codebase to find files that are not imported or referenced
by any other file in the project.
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Define project directories to scan - excluding project_plan as it contains documentation
PROJECT_DIRS = [
    "dudoxx_extraction",
    "dudoxx_extraction_api",
    "examples",
    "langchain_sdk",
    # Root Python files will be scanned directly
]

# Define file extensions to scan - focusing only on Python files as requested
FILE_EXTENSIONS = [
    ".py",
]

# Define files to exclude from orphan analysis (entry points, README files, etc.)
EXCLUDE_FILES = [
    "README.md",
    "__init__.py",  # Python package marker files
    "setup.py",
    "requirements.txt",
    "package.json",
    "tsconfig.json",
    "next.config.ts",
    "run_servers.sh",
    "main.py",
    "server.js",
    ".env",
    ".env.dudoxx",
    ".gitignore",
    "CONTRIBUTING.md",
    "ROADMAP.md",
]

# Define directories to exclude from orphan analysis
EXCLUDE_DIRS = [
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    ".git",
    "venv",
    "env",
    ".next",  # Next.js build output directory
]


class FileReference:
    """Class to store file reference information."""
    
    def __init__(self, path: str):
        """Initialize with file path."""
        self.path = path
        self.imported_by: Set[str] = set()
        self.references: Set[str] = set()
        self.is_entry_point = False
        
    def add_imported_by(self, file_path: str):
        """Add a file that imports this file."""
        self.imported_by.add(file_path)
        
    def add_reference(self, reference: str):
        """Add a reference to another file."""
        self.references.add(reference)
        
    def mark_as_entry_point(self):
        """Mark this file as an entry point."""
        self.is_entry_point = True
        
    def is_orphan(self) -> bool:
        """Check if this file is an orphan."""
        return not self.imported_by and not self.is_entry_point
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"FileReference(path={self.path}, imported_by={len(self.imported_by)}, references={len(self.references)}, is_entry_point={self.is_entry_point})"


class OrphanFinder:
    """Class to find orphaned files in the project."""
    
    def __init__(self, project_root: str):
        """Initialize with project root directory."""
        self.project_root = Path(project_root)
        self.files: Dict[str, FileReference] = {}
        self.python_imports: Dict[str, Set[str]] = {}
        self.js_imports: Dict[str, Set[str]] = {}
        self.string_references: Dict[str, Set[str]] = {}
        
    def scan_project(self):
        """Scan the project for files."""
        print(f"Scanning project at {self.project_root}...")
        
        # Scan Python files in the root directory
        for file in os.listdir(self.project_root):
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                file_path = self.project_root / file
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.project_root)
                    self.files[str(rel_path)] = FileReference(str(rel_path))
                    
                    # Mark standalone examples and API client examples as entry points
                    if file.startswith("standalone_") or file.startswith("api_client_"):
                        self.files[str(rel_path)].mark_as_entry_point()
        
        # Scan project directories
        for project_dir in PROJECT_DIRS:
            dir_path = self.project_root / project_dir
            if not dir_path.exists():
                print(f"Warning: Directory {dir_path} does not exist, skipping.")
                continue
                
            for root, dirs, files in os.walk(dir_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    # Skip excluded files
                    if file in EXCLUDE_FILES:
                        continue
                        
                    # Check file extension
                    if not any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                        continue
                        
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.project_root)
                    self.files[str(rel_path)] = FileReference(str(rel_path))
                    
                    # Mark entry points
                    if file in ["main.py", "server.js", "run_socketio.py", "run_servers.sh"]:
                        self.files[str(rel_path)].mark_as_entry_point()
                    
                    # Mark example scripts as entry points
                    if project_dir == "examples" and file.endswith(".py"):
                        self.files[str(rel_path)].mark_as_entry_point()
        
        print(f"Found {len(self.files)} files to analyze.")
    
    def analyze_imports(self):
        """Analyze imports in all files."""
        print("Analyzing imports...")
        
        for file_path, file_ref in self.files.items():
            if file_path.endswith(".py"):
                self._analyze_python_imports(file_path)
            elif any(file_path.endswith(ext) for ext in [".js", ".jsx", ".ts", ".tsx"]):
                self._analyze_js_imports(file_path)
                
            # Analyze string references in all files
            self._analyze_string_references(file_path)
    
    def _analyze_python_imports(self, file_path: str):
        """Analyze imports in a Python file."""
        try:
            with open(self.project_root / file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        
                        # Also add the specific imported names for better tracking
                        for name in node.names:
                            if name.name != '*':
                                full_import = f"{node.module}.{name.name}"
                                imports.add(full_import)
            
            # Look for common patterns like FastAPI router inclusion
            router_pattern = r'app\.include_router\s*\(\s*([a-zA-Z0-9_]+)\s*\)'
            for match in re.finditer(router_pattern, content):
                router_name = match.group(1)
                # Add a special marker for router inclusion
                imports.add(f"__router__{router_name}")
            
            # Look for function calls that might dynamically load modules
            initialize_pattern = r'([a-zA-Z0-9_]+)\(\)'
            for match in re.finditer(initialize_pattern, content):
                function_name = match.group(1)
                # Add a special marker for function calls
                imports.add(f"__function__{function_name}")
            
            self.python_imports[file_path] = imports
            
        except Exception as e:
            print(f"Error analyzing Python imports in {file_path}: {e}")
    
    def _analyze_js_imports(self, file_path: str):
        """Analyze imports in a JavaScript/TypeScript file."""
        try:
            with open(self.project_root / file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract import statements using regex
            import_regex = r'import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
            require_regex = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            
            imports = set()
            
            # Find all import statements
            for match in re.finditer(import_regex, content):
                imports.add(match.group(1))
                
            # Find all require statements
            for match in re.finditer(require_regex, content):
                imports.add(match.group(1))
            
            self.js_imports[file_path] = imports
            
        except Exception as e:
            print(f"Error analyzing JS imports in {file_path}: {e}")
    
    def _analyze_string_references(self, file_path: str):
        """Analyze string references to other files."""
        try:
            with open(self.project_root / file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract string references to file paths
            path_regex = r'[\'"]([^\'"\s]+\.(py|js|jsx|ts|tsx|md|sh|json))[\'"]'
            
            references = set()
            
            # Find all string references to file paths
            for match in re.finditer(path_regex, content):
                references.add(match.group(1))
            
            self.string_references[file_path] = references
            
        except Exception as e:
            print(f"Error analyzing string references in {file_path}: {e}")
    
    def build_dependency_graph(self):
        """Build a dependency graph based on imports and references."""
        print("Building dependency graph...")
        
        # Process Python imports
        for file_path, imports in self.python_imports.items():
            for import_name in imports:
                # Handle special markers for router inclusion
                if import_name.startswith("__router__"):
                    router_name = import_name[len("__router__"):]
                    # Look for router variable definitions
                    for target_file in self.files:
                        if target_file.endswith(".py"):
                            try:
                                with open(self.project_root / target_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    if re.search(rf"{router_name}\s*=\s*APIRouter\(", content):
                                        self.files[target_file].add_imported_by(file_path)
                                        self.files[file_path].add_reference(target_file)
                                        break
                            except Exception:
                                pass
                    continue
                
                # Handle special markers for function calls
                if import_name.startswith("__function__"):
                    function_name = import_name[len("__function__"):]
                    # Look for function definitions
                    for target_file in self.files:
                        if target_file.endswith(".py"):
                            try:
                                with open(self.project_root / target_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    if re.search(rf"def\s+{function_name}\s*\(", content):
                                        self.files[target_file].add_imported_by(file_path)
                                        self.files[file_path].add_reference(target_file)
                                        break
                            except Exception:
                                pass
                    continue
                
                # Convert import to file path
                import_parts = import_name.split(".")
                
                # Try different combinations of import parts
                for i in range(len(import_parts)):
                    import_path = "/".join(import_parts[:i+1])
                    
                    # Check if this import path corresponds to a file
                    for target_file in self.files:
                        if target_file.endswith(".py") and target_file.replace("/", ".").startswith(import_name):
                            self.files[target_file].add_imported_by(file_path)
                            self.files[file_path].add_reference(target_file)
                            break
                            
                        if target_file.startswith(import_path):
                            self.files[target_file].add_imported_by(file_path)
                            self.files[file_path].add_reference(target_file)
                            break
        
        # Process JavaScript imports
        for file_path, imports in self.js_imports.items():
            for import_name in imports:
                # Skip external imports
                if import_name.startswith("@") or not import_name.startswith("."):
                    continue
                    
                # Convert relative import to file path
                import_path = os.path.normpath(os.path.join(os.path.dirname(file_path), import_name))
                
                # Check if this import path corresponds to a file
                for ext in [".js", ".jsx", ".ts", ".tsx"]:
                    if import_path + ext in self.files:
                        self.files[import_path + ext].add_imported_by(file_path)
                        self.files[file_path].add_reference(import_path + ext)
                        break
                        
                # Check for index files
                for ext in [".js", ".jsx", ".ts", ".tsx"]:
                    index_path = os.path.join(import_path, "index" + ext)
                    if index_path in self.files:
                        self.files[index_path].add_imported_by(file_path)
                        self.files[file_path].add_reference(index_path)
                        break
        
        # Process string references
        for file_path, references in self.string_references.items():
            for reference in references:
                # Check if this reference corresponds to a file
                for target_file in self.files:
                    if target_file.endswith(reference) or reference in target_file:
                        self.files[target_file].add_imported_by(file_path)
                        self.files[file_path].add_reference(target_file)
                        break
    
    def find_orphans(self) -> List[str]:
        """Find orphaned files."""
        print("Finding orphaned files...")
        
        orphans = []
        
        for file_path, file_ref in self.files.items():
            if file_ref.is_orphan():
                orphans.append(file_path)
        
        return sorted(orphans)
    
    def categorize_orphans(self, orphans: List[str]) -> Dict[str, List[str]]:
        """Categorize orphaned files."""
        categories = {
            "examples": [],
            "tests": [],
            "documentation": [],
            "utilities": [],
            "frontend": [],
            "backend": [],
            "misc": [],
        }
        
        for file_path in orphans:
            if file_path.startswith("examples/"):
                categories["examples"].append(file_path)
            elif "test" in file_path.lower():
                categories["tests"].append(file_path)
            elif file_path.endswith(".md") or "docs" in file_path:
                categories["documentation"].append(file_path)
            elif "utils" in file_path or "helpers" in file_path:
                categories["utilities"].append(file_path)
            elif file_path.startswith("dudoxx_extraction_frontend/") or file_path.startswith("dudoxx_extraction_nextjs/"):
                categories["frontend"].append(file_path)
            elif file_path.startswith("dudoxx_extraction/") or file_path.startswith("dudoxx_extraction_api/"):
                categories["backend"].append(file_path)
            else:
                categories["misc"].append(file_path)
        
        return categories
    
    def move_orphans_to_directory(self, orphans: List[str], target_dir: str):
        """Move orphaned files to a target directory."""
        print(f"Moving orphaned files to {target_dir}...")
        
        target_path = Path(target_dir)
        
        # Create target directory if it doesn't exist
        if not target_path.exists():
            target_path.mkdir(parents=True)
        
        # Create subdirectories for categories
        categories = self.categorize_orphans(orphans)
        
        for category, files in categories.items():
            if not files:
                continue
                
            category_path = target_path / category
            if not category_path.exists():
                category_path.mkdir(parents=True)
                
            for file_path in files:
                # Create subdirectories to maintain structure
                file_dir = os.path.dirname(file_path)
                if file_dir:
                    os.makedirs(category_path / file_dir, exist_ok=True)
                
                # Create a symlink to the original file
                src_path = self.project_root / file_path
                dst_path = category_path / file_path
                
                try:
                    # Create relative symlink
                    os.symlink(os.path.relpath(src_path, os.path.dirname(dst_path)), dst_path)
                    print(f"Created symlink: {dst_path} -> {src_path}")
                except FileExistsError:
                    print(f"Symlink already exists: {dst_path}")
                except Exception as e:
                    print(f"Error creating symlink for {file_path}: {e}")
    
    def generate_report(self, orphans: List[str], output_file: str):
        """Generate a report of orphaned files."""
        print(f"Generating report to {output_file}...")
        
        categories = self.categorize_orphans(orphans)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Orphaned Files Report\n\n")
            f.write(f"Total orphaned files: {len(orphans)}\n\n")
            
            for category, files in categories.items():
                if not files:
                    continue
                    
                f.write(f"## {category.capitalize()} ({len(files)})\n\n")
                
                for file_path in files:
                    f.write(f"- `{file_path}`\n")
                
                f.write("\n")


def main():
    """Main function."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    orphan_finder = OrphanFinder(project_root)
    orphan_finder.scan_project()
    orphan_finder.analyze_imports()
    orphan_finder.build_dependency_graph()
    
    orphans = orphan_finder.find_orphans()
    
    print(f"Found {len(orphans)} orphaned files.")
    
    if orphans:
        orphan_finder.generate_report(orphans, "orphans/orphans_report.md")
        orphan_finder.move_orphans_to_directory(orphans, "orphans")
    
    print("Done.")


if __name__ == "__main__":
    main()
