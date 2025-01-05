import os
import sys
import pyperclip  # Import pyperclip for clipboard operations

ignored_names = ["__pycache__"]
ignored_extensions = [".ipynb", ".log"]

def build_directory_tree(root_paths):
    """
    Build a directory tree representation for the given paths.
    Returns a list of strings representing the tree structure.
    """
    tree_lines = []
    
    def add_to_tree(path, prefix=""):
        # Check if the path is a directory and not in ignored names
        if os.path.isdir(path) and os.path.basename(path) not in ignored_names:
            tree_lines.append(f"{prefix}|-- {os.path.basename(path)}/")
            # Get children and sort them
            children = sorted(os.listdir(path))
            # Filter out ignored names and extensions for files
            children = [
                child for child in children
                if child not in ignored_names and not any(child.endswith(ext) for ext in ignored_extensions)
            ]
            for i, child in enumerate(children):
                child_path = os.path.join(path, child)
                is_last = (i == len(children) - 1)
                new_prefix = prefix + ("    " if is_last else "|   ")
                add_to_tree(child_path, new_prefix)
        elif not os.path.isdir(path):  # It's a file
            # Include only non-ignored files
            if not any(path.endswith(ext) for ext in ignored_extensions):
                tree_lines.append(f"{prefix}|-- {os.path.basename(path)}")

    # Process all root paths
    for path in root_paths:
        if not os.path.exists(path):
            tree_lines.append(f"Path not found: {path}")
            continue
        if os.path.isfile(path):
            tree_lines.append(f"|-- {os.path.basename(path)}")
        else:
            tree_lines.append(f"{os.path.basename(path)}/")
            add_to_tree(path, "    ")
    
    return tree_lines

def collect_file_contents(root_paths):
    """
    Collect the contents of all files from the given paths, ignoring __pycache__ and specified extensions.
    Returns a list of tuples (relative_file_path, file_content).
    """
    file_contents = []
    
    for path in root_paths:
        if os.path.isfile(path):
            # Add the file if it doesn't match ignored extensions
            if not any(path.endswith(ext) for ext in ignored_extensions):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    file_contents.append((path, f.read()))
        elif os.path.isdir(path):
            # Recursively add all files in the directory, ignoring __pycache__ and ignored extensions
            for root, dirs, files in os.walk(path):
                # Exclude ignored directories
                dirs[:] = [
                    d for d in dirs 
                    if d not in ignored_names
                ]
                # Exclude files with ignored extensions
                for file in sorted(files):  # Sort for consistent order
                    if not any(file.endswith(ext) for ext in ignored_extensions):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                                relative_path = os.path.relpath(file_path, os.path.commonpath(root_paths))
                                file_contents.append((relative_path, f.read()))
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
    
    return file_contents

def write_combined_to_clipboard(tree_structure, file_contents):
    """
    Copy the directory tree and file contents to the clipboard.
    """
    combined_text = "# DIRECTORY STRUCTURE\n"
    combined_text += "\n".join(tree_structure)
    combined_text += "\n\n# FILE CONTENTS\n"
    for file_path, content in file_contents:
        combined_text += f"## File: {file_path}\n"
        combined_text += content
        combined_text += "\n\n"
    
    try:
        pyperclip.copy(combined_text)
        print("Output successfully copied to clipboard.")
    except pyperclip.PyperclipException as e:
        print(f"Failed to copy to clipboard: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python compress.py <path1> [<path2> ...]")
        sys.exit(1)
    
    root_paths = sys.argv[1:]
    
    # Build directory tree
    tree_structure = build_directory_tree(root_paths)
    
    # Collect file contents
    file_contents = collect_file_contents(root_paths)
    
    # Copy to clipboard
    write_combined_to_clipboard(tree_structure, file_contents)

if __name__ == "__main__":
    main()



