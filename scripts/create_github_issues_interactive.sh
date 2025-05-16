#!/bin/bash

# Create GitHub issues interactively from markdown files
# Usage: ./create_github_issues_interactive.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO="thinkube/thinkube"  # Change this to your actual repo
ISSUES_DIR="/home/thinkube/thinkube/.github/issues"

echo -e "${YELLOW}Interactive GitHub issue creation for Thinkube Migration${NC}"
echo -e "${BLUE}Repository: $REPO${NC}"
echo ""

# Function to extract title from markdown file
get_title() {
    local file=$1
    grep -m1 "^# " "$file" | sed 's/^# //'
}

# Process each markdown file
for file in "$ISSUES_DIR"/{CORE,OPT}-*.md; do
    if [ -f "$file" ]; then
        title=$(get_title "$file")
        filename=$(basename "$file")
        
        echo -e "${YELLOW}─────────────────────────────────────────${NC}"
        echo -e "${GREEN}File: $filename${NC}"
        echo -e "${BLUE}Title: $title${NC}"
        echo ""
        
        # Show preview
        echo -e "${YELLOW}Preview (first 10 lines):${NC}"
        head -n 10 "$file"
        echo "..."
        echo ""
        
        # Ask for confirmation
        read -p "Create this issue? (y/N/q to quit): " response
        
        case $response in
            [yY])
                echo -e "${GREEN}Creating issue...${NC}"
                
                # Create the issue
                gh issue create \
                    --repo "$REPO" \
                    --title "$title" \
                    --body-file "$file" \
                    --label "migration"
                
                echo -e "${GREEN}✓ Issue created!${NC}"
                echo ""
                ;;
            [qQ])
                echo -e "${YELLOW}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Skipped${NC}"
                echo ""
                ;;
        esac
    fi
done

echo -e "${GREEN}Process complete!${NC}"
echo -e "${YELLOW}View your issues at: https://github.com/$REPO/issues${NC}"