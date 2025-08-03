#!/bin/bash
# Initialize the repository and run the first data collection

# Create data directory if it doesn't exist
mkdir -p data

# Install dependencies
pip install -r requirements.txt

# Run the crawler
python crawler.py

# Initialize git if not already initialized
if [ ! -d .git ]; then
  git init
  git add .
  git commit -m "Initial commit"
fi

echo "Initialization complete. You can now push this repository to GitHub."
echo "Follow these steps:"
echo "1. Create a new repository on GitHub"
echo "2. Run: git remote add origin https://github.com/YOUR-USERNAME/prices-to-github.git"
echo "3. Run: git push -u origin main"
echo "4. Enable GitHub Pages in the repository settings (Settings > Pages)"
echo "   - Set source to 'GitHub Actions'"