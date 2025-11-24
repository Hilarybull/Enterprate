#!/bin/bash

echo "=========================================="
echo "Packaging Enterprate OS Codebase"
echo "=========================================="

# Create export directory
mkdir -p /tmp/enterprate-os-export

# Copy all important files
echo "Copying backend files..."
mkdir -p /tmp/enterprate-os-export/backend
cp -r /app/backend/* /tmp/enterprate-os-export/backend/

echo "Copying frontend files..."
mkdir -p /tmp/enterprate-os-export/frontend
cp -r /app/frontend/* /tmp/enterprate-os-export/frontend/

echo "Copying documentation..."
cp /app/README.md /tmp/enterprate-os-export/
cp /app/CHANGELOG.md /tmp/enterprate-os-export/
cp /app/DEPLOYMENT.md /tmp/enterprate-os-export/
cp /app/BUGFIX.md /tmp/enterprate-os-export/
cp /app/CODEBASE_STRUCTURE.md /tmp/enterprate-os-export/
cp /app/.env.example /tmp/enterprate-os-export/
cp /app/test_enterprate.sh /tmp/enterprate-os-export/

echo "Creating archive..."
cd /tmp
tar -czf enterprate-os-complete.tar.gz enterprate-os-export/

echo ""
echo "✓ Codebase packaged successfully!"
echo "Location: /tmp/enterprate-os-complete.tar.gz"
echo "Size: $(du -h /tmp/enterprate-os-complete.tar.gz | cut -f1)"
echo ""
echo "To extract:"
echo "  tar -xzf enterprate-os-complete.tar.gz"
echo "=========================================="
