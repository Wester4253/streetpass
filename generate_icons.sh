#!/bin/bash
set -e

# First make both icons executable
chmod +x app/static/icons/icon-512x512.svg
chmod +x app/static/icons/icon-192x192.svg

# Convert SVGs to PNGs
convert app/static/icons/icon-512x512.svg app/static/icons/icon-512x512.png
convert app/static/icons/icon-192x192.svg app/static/icons/icon-192x192.png

# Create default avatar
convert app/static/icons/icon-192x192.svg -resize 128x128 app/static/icons/default.png

echo "Icons generated successfully!"
