#!/bin/bash

# Create GitHub issues from markdown files
# Usage: ./create_github_issues.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO="thinkube/thinkube"  # Change this to your actual repo
ISSUES_DIR="/home/thinkube/thinkube/.github/issues"
PROJECT_NAME="Thinkube Migration"  # Optional: project board name

echo -e "${YELLOW}Creating GitHub issues for Thinkube Migration...${NC}"

# Function to extract title from markdown file
get_title() {
    local file=$1
    grep -m1 "^# " "$file" | sed 's/^# //'
}

# Function to extract component type and priority
get_labels() {
    local file=$1
    local labels="migration"
    
    # Extract type
    if grep -q "**Type**: Core" "$file"; then
        labels="$labels,core-component"
    elif grep -q "**Type**: Optional" "$file"; then
        labels="$labels,optional-component"
    fi
    
    # Extract priority
    if grep -q "**Priority**: High" "$file"; then
        labels="$labels,priority-high"
    elif grep -q "**Priority**: Medium" "$file"; then
        labels="$labels,priority-medium"
    elif grep -q "**Priority**: Low" "$file"; then
        labels="$labels,priority-low"
    fi
    
    echo "$labels"
}

# Create issues from CORE components
echo -e "${GREEN}Creating CORE component issues...${NC}"
for file in "$ISSUES_DIR"/CORE-*.md; do
    if [ -f "$file" ]; then
        title=$(get_title "$file")
        labels=$(get_labels "$file")
        body=$(cat "$file")
        
        echo -e "Creating issue: ${YELLOW}$title${NC}"
        
        # Create the issue
        gh issue create \
            --repo "$REPO" \
            --title "$title" \
            --body "$body" \
            --label "$labels" \
            --project "$PROJECT_NAME" 2>/dev/null || \
        gh issue create \
            --repo "$REPO" \
            --title "$title" \
            --body "$body" \
            --label "$labels"
        
        echo -e "${GREEN}✓ Created${NC}"
        sleep 1  # Rate limiting
    fi
done

# Create issues from OPT components
echo -e "${GREEN}Creating OPT component issues...${NC}"
for file in "$ISSUES_DIR"/OPT-*.md; do
    if [ -f "$file" ]; then
        title=$(get_title "$file")
        labels=$(get_labels "$file")
        body=$(cat "$file")
        
        echo -e "Creating issue: ${YELLOW}$title${NC}"
        
        # Create the issue
        gh issue create \
            --repo "$REPO" \
            --title "$title" \
            --body "$body" \
            --label "$labels" \
            --project "$PROJECT_NAME" 2>/dev/null || \
        gh issue create \
            --repo "$REPO" \
            --title "$title" \
            --body "$body" \
            --label "$labels"
        
        echo -e "${GREEN}✓ Created${NC}"
        sleep 1  # Rate limiting
    fi
done

echo -e "${GREEN}All issues created successfully!${NC}"
echo -e "${YELLOW}View your issues at: https://github.com/$REPO/issues${NC}"