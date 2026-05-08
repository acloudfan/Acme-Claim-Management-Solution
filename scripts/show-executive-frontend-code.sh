#!/bin/bash
#
# Show the actual API call code in the executive portal frontend
# Run this on your Mac to verify what endpoint is being called
#

echo "========================================="
echo "Executive Portal Frontend API Calls"
echo "========================================="
echo ""

echo "File: src/ui/executive/src/api/executive.js"
echo "Line 22 (fetchKPIs function):"
echo ""
sed -n '20,25p' src/ui/executive/src/api/executive.js
echo ""
echo "-----------------------------------------"
echo ""

echo "Expected: client.get('/executive/kpis', { params });"
echo ""

echo "If the file shows something different, run:"
echo "  git status src/ui/executive/src/api/executive.js"
echo "  git diff src/ui/executive/src/api/executive.js"
echo ""
