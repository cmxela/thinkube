#!/bin/bash
# Test script to verify thinkube-control templating works

set -e

echo "Testing thinkube-control template generation..."

# Create a test directory
TEST_DIR="/tmp/test-thinkube-control-$(date +%s)"
mkdir -p "$TEST_DIR"

# Test with copier (if installed)
if command -v copier &> /dev/null; then
    echo "Using copier to generate from template..."
    copier copy ./thinkube-control "$TEST_DIR" \
        --data domain_name=test.local \
        --data github_org=testuser \
        --data namespace=test-control \
        --defaults
    
    echo "Generated files:"
    find "$TEST_DIR" -name "*.yaml" -type f | head -10
    
    echo -e "\nChecking generated ingress:"
    grep -E "(host:|namespace:)" "$TEST_DIR/k8s/ingress.yaml" || echo "No ingress.yaml found"
else
    echo "Copier not installed. Install with: pip install copier"
fi

# Cleanup
echo -e "\nCleaning up test directory..."
rm -rf "$TEST_DIR"

echo "Test complete!"