#!/bin/bash

# Script to open the Extractor AI brochure in a web browser

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the index.html file
INDEX_FILE="$SCRIPT_DIR/index.html"

# Check if the file exists
if [ ! -f "$INDEX_FILE" ]; then
    echo "Error: Brochure file not found at $INDEX_FILE"
    exit 1
fi

# Detect operating system and open the brochure accordingly
case "$(uname -s)" in
    Darwin*)    # macOS
        open "$INDEX_FILE"
        ;;
    Linux*)     # Linux
        if command -v xdg-open > /dev/null; then
            xdg-open "$INDEX_FILE"
        elif command -v gnome-open > /dev/null; then
            gnome-open "$INDEX_FILE"
        else
            echo "Error: Could not find a suitable command to open the brochure."
            echo "Please open the file manually: $INDEX_FILE"
            exit 1
        fi
        ;;
    CYGWIN*|MINGW*|MSYS*)  # Windows
        start "$INDEX_FILE"
        ;;
    *)
        echo "Error: Unsupported operating system."
        echo "Please open the file manually: $INDEX_FILE"
        exit 1
        ;;
esac

echo "Opening Extractor AI brochure in your default web browser..."
echo "If the brochure doesn't open automatically, please open this file manually: $INDEX_FILE"

exit 0
