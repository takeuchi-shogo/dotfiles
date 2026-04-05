#!/usr/bin/env bash
# Example: Capturing console logs during browser automation

URL="http://localhost:5173"
agent-browser open "$URL"
agent-browser wait

agent-browser console
agent-browser find text "Dashboard" click
agent-browser wait
agent-browser console
agent-browser errors

agent-browser console > /tmp/console.log
agent-browser close
