#!/usr/bin/env python3
"""
Update task status in START_HERE.md

Usage:
  python3 scripts/update_task_status.py task_id status

Where:
  task_id is the line number of the task line in START_HERE.md
  status is either "complete" or "pending"

Example:
  python3 scripts/update_task_status.py 42 complete
"""

import sys
import re

def update_task(task_id, status):
    """
    Update the status of a task in START_HERE.md
    """
    if status not in ["complete", "pending"]:
        print("Status must be 'complete' or 'pending'")
        sys.exit(1)
    
    try:
        task_id = int(task_id)
    except ValueError:
        print("Task ID must be a number")
        sys.exit(1)
    
    with open("START_HERE.md", "r") as f:
        lines = f.readlines()
    
    if task_id < 1 or task_id > len(lines):
        print(f"Task ID must be between 1 and {len(lines)}")
        sys.exit(1)
    
    # Convert to 0-based index
    line_index = task_id - 1
    line = lines[line_index]
    
    # Only process lines that have checkbox format
    if not re.match(r"\s*- \[[ xX]\]", line):
        print(f"Line {task_id} is not a task item")
        sys.exit(1)
    
    # Update the checkbox
    if status == "complete":
        lines[line_index] = re.sub(r"- \[[ ]\]", "- [x]", line)
    else:
        lines[line_index] = re.sub(r"- \[[xX]\]", "- [ ]", line)
    
    with open("START_HERE.md", "w") as f:
        f.writelines(lines)
    
    print(f"Updated task on line {task_id} to {status}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    
    update_task(sys.argv[1], sys.argv[2])