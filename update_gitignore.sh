#!/bin/bash
# Script to update .gitignore with recommended patterns for orphaned files

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore file..."
    touch .gitignore
fi

# Add Next.js build directory to .gitignore if not already present
if ! grep -q "dudoxx_extraction_nextjs/.next/" .gitignore; then
    echo "Adding dudoxx_extraction_nextjs/.next/ to .gitignore..."
    echo -e "\n# Next.js build artifacts\ndudoxx_extraction_nextjs/.next/" >> .gitignore
    echo "Added dudoxx_extraction_nextjs/.next/ to .gitignore"
else
    echo "dudoxx_extraction_nextjs/.next/ is already in .gitignore"
fi

# Make the script executable
chmod +x update_gitignore.sh

echo "Done updating .gitignore"
