package category

import "strings"

const (
	FileRead  = "file_read"
	FileWrite = "file_write"
	Shell     = "shell"
	Web       = "web"
	Agent     = "agent"
	System    = "system"
	Mcp       = "mcp"
	Unknown   = "unknown"
)

func Categorize(name string) string {
	switch name {
	case "Read", "Glob", "Grep", "LSP":
		return FileRead
	case "Write", "Edit", "NotebookEdit":
		return FileWrite
	case "Bash":
		return Shell
	case "WebSearch", "WebFetch":
		return Web
	case "Agent", "Task", "TaskOutput", "TaskCreate",
		"TaskGet", "TaskList", "TaskStop", "TaskUpdate",
		"SendMessage", "TeamCreate", "TeamDelete":
		return Agent
	case "EnterPlanMode", "ExitPlanMode",
		"EnterWorktree", "ExitWorktree",
		"AskUserQuestion", "Skill", "ToolSearch",
		"CronCreate", "CronDelete", "CronList":
		return System
	}
	if strings.HasPrefix(name, "mcp__") {
		return Mcp
	}
	return Unknown
}

// Color returns an ANSI color name for terminal output.
func Color(cat string) string {
	switch cat {
	case FileRead:
		return "cyan"
	case FileWrite:
		return "green"
	case Shell:
		return "yellow"
	case Web:
		return "magenta"
	case Agent:
		return "red"
	case System:
		return "blue"
	case Mcp:
		return "white"
	default:
		return "white"
	}
}
