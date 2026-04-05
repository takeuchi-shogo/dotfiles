#!/usr/bin/env bash
# Example: Discovering interactive elements on a page

agent-browser open http://localhost:5173
agent-browser snapshot -i -c

# Find by role
agent-browser find role button
agent-browser find role link
agent-browser find role textbox

# Find by text/label
agent-browser find text "Sign In"
agent-browser find label "Email"

agent-browser screenshot /tmp/page_discovery.png --full
agent-browser close
