#!/usr/bin/env bash
# Example: Automating interaction with a static HTML file

HTML_FILE="$(realpath path/to/your/file.html)"
agent-browser open "file://${HTML_FILE}"
agent-browser snapshot -c
agent-browser screenshot /tmp/static_page.png --full

agent-browser find text "Click Me" click
agent-browser find label "Name" fill "John Doe"
agent-browser find label "Email" fill "john@example.com"
agent-browser find role button --name "Submit" click
agent-browser wait

agent-browser screenshot /tmp/after_submit.png --full
agent-browser close
