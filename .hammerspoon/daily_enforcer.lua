local M = {}

local log = hs.logger.new("daily-enforcer", "info")

local home = os.getenv("HOME")
local config = {
  vault_candidates = {
    os.getenv("OBSIDIAN_VAULT_PATH"),
    home .. "/Documents/Obsidian Vault",
  },
  vault_daily_dir = "01-Projects/Daily",
  fallback_daily_dir = home .. "/daily-notes",
  template_path = home .. "/dotfiles/docs/templates/daily.md",
  report_start_hour = 18,
  remind_interval_seconds = 15 * 60,
  auto_open_cooldown_seconds = 30 * 60,
  snooze_minutes = 10,
}

local markers = {
  morning = {
    start = "<!-- daily-enforcer:morning:start -->",
    ["end"] = "<!-- daily-enforcer:morning:end -->",
    block = table.concat({
      "## 朝TODO",
      "<!-- daily-enforcer:morning:start -->",
      "- [ ] ",
      "- [ ] ",
      "- [ ] ",
      "<!-- daily-enforcer:morning:end -->",
    }, "\n"),
  },
  report = {
    start = "<!-- daily-enforcer:report:start -->",
    ["end"] = "<!-- daily-enforcer:report:end -->",
    block = table.concat({
      "## 日報",
      "<!-- daily-enforcer:report:start -->",
      "- Done:",
      "- Blockers:",
      "- Next:",
      "<!-- daily-enforcer:report:end -->",
    }, "\n"),
  },
}

local state = {
  menu = nil,
  watcher = nil,
  timer = nil,
  snooze_until = 0,
  last_opened_at = 0,
  last_prompt_key = nil,
  last_status = nil,
}

local function shell_quote(value)
  return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function is_directory(path)
  return hs.fs.attributes(path, "mode") == "directory"
end

local function read_file(path)
  local file = io.open(path, "r")
  if not file then
    return nil
  end

  local content = file:read("*a")
  file:close()
  return content
end

local function ensure_directory(path)
  hs.execute("/bin/mkdir -p " .. shell_quote(path))
end

local function write_file(path, content)
  local parent = path:match("^(.*)/[^/]+$")
  if parent then
    ensure_directory(parent)
  end

  local file = assert(io.open(path, "w"))
  file:write(content)
  file:close()
end

local function resolve_storage_root()
  for _, candidate in ipairs(config.vault_candidates) do
    if candidate and candidate ~= "" and is_directory(candidate) then
      return candidate .. "/" .. config.vault_daily_dir, "obsidian"
    end
  end

  return config.fallback_daily_dir, "fallback"
end

local function fallback_template(date)
  return table.concat({
    "# Daily Note - " .. date,
    "",
    markers.morning.block,
    "",
    "## 進捗メモ",
    "",
    markers.report.block,
    "",
  }, "\n")
end

local function render_template(date)
  local template = read_file(config.template_path)
  if not template or template == "" then
    return fallback_template(date)
  end

  return template:gsub("{{ YYYY%-MM%-DD }}", date)
end

local function append_block_if_missing(content, definition)
  if content:find(definition.start, 1, true) then
    return content, false
  end

  local updated = content:gsub("%s*$", "")
  updated = updated .. "\n\n" .. definition.block .. "\n"
  return updated, true
end

local function ensure_today_note(date)
  local root, storage = resolve_storage_root()
  local path = root .. "/" .. date .. ".md"
  local content = read_file(path)
  local changed = false

  if not content then
    content = render_template(date)
    changed = true
  end

  local morning_changed
  content, morning_changed = append_block_if_missing(content, markers.morning)
  changed = changed or morning_changed

  local report_changed
  content, report_changed = append_block_if_missing(content, markers.report)
  changed = changed or report_changed

  if changed then
    write_file(path, content)
  end

  return {
    path = path,
    storage = storage,
    content = content,
  }
end

local function extract_section(content, definition)
  local start_pos = content:find(definition.start, 1, true)
  if not start_pos then
    return ""
  end

  local end_pos = content:find(definition["end"], start_pos, true)
  if not end_pos then
    return ""
  end

  local from = start_pos + #definition.start
  return content:sub(from + 1, end_pos - 1)
end

local function has_meaningful_morning_content(section)
  for line in section:gmatch("[^\r\n]+") do
    local trimmed = line:match("^%s*(.-)%s*$")
    if trimmed ~= "" and not trimmed:match("^<!%-%-") then
      local task = trimmed:match("^%- %[[xX ]%]%s*(.*)$")
      if task then
        if task:match("%S") then
          return true
        end
      elseif trimmed:match("%S") then
        return true
      end
    end
  end

  return false
end

local function has_meaningful_report_content(section)
  for line in section:gmatch("[^\r\n]+") do
    local trimmed = line:match("^%s*(.-)%s*$")
    if trimmed ~= "" and not trimmed:match("^<!%-%-") then
      local value = trimmed:match("^%- [^:]+:%s*(.*)$")
      if value then
        if value:match("%S") then
          return true
        end
      elseif trimmed:match("%S") then
        return true
      end
    end
  end

  return false
end

local function build_status()
  local now = os.date("*t")
  local today = os.date("%Y-%m-%d")
  local note = ensure_today_note(today)
  local morning_done = has_meaningful_morning_content(extract_section(note.content, markers.morning))
  local report_done = has_meaningful_report_content(extract_section(note.content, markers.report))
  local pending = {}

  if not morning_done then
    table.insert(pending, "morning")
  end

  if now.hour >= config.report_start_hour and not report_done then
    table.insert(pending, "report")
  end

  return {
    date = today,
    hour = now.hour,
    path = note.path,
    storage = note.storage,
    morning_done = morning_done,
    report_done = report_done,
    pending = pending,
  }
end

local function status_title(status)
  if #status.pending == 0 then
    return "DAY"
  end

  if #status.pending == 2 then
    return "TODO+EOD"
  end

  if status.pending[1] == "morning" then
    return "TODO"
  end

  return "EOD"
end

local function status_message(status)
  if #status.pending == 0 then
    return "今日の daily note は埋まっています"
  end

  local labels = {}
  for _, item in ipairs(status.pending) do
    if item == "morning" then
      table.insert(labels, "朝TODO")
    elseif item == "report" then
      table.insert(labels, "日報")
    end
  end

  return table.concat(labels, " / ") .. " が未記入です"
end

local function open_note(status)
  local path = status.path
  if status.storage == "obsidian" then
    hs.urlevent.openURL("obsidian://open?path=" .. hs.http.encodeForQuery(path))
    return
  end

  hs.execute("/usr/bin/open " .. shell_quote(path))
end

local function build_menu(status)
  local items = {
    {
      title = status_message(status),
      disabled = true,
    },
    {
      title = "Open today's note",
      fn = function()
        open_note(state.last_status or status)
      end,
    },
    {
      title = "Check now",
      fn = function()
        M.check("manual", true)
      end,
    },
  }

  if os.time() < state.snooze_until then
    table.insert(items, {
      title = "Clear snooze",
      fn = function()
        state.snooze_until = 0
        M.check("unsnooze", true)
      end,
    })
  else
    table.insert(items, {
      title = "Snooze " .. config.snooze_minutes .. "m",
      fn = function()
        state.snooze_until = os.time() + (config.snooze_minutes * 60)
      end,
    })
  end

  table.insert(items, { title = "-" })
  table.insert(items, {
    title = status.path,
    disabled = true,
  })

  return items
end

local function refresh_menu(status)
  state.last_status = status

  if not state.menu then
    state.menu = hs.menubar.new()
  end

  state.menu:setTitle(status_title(status))
  state.menu:setTooltip(status_message(status))
  state.menu:setMenu(build_menu(status))
end

local function notify(status, reason, ignore_cooldown)
  local now = os.time()
  if now < state.snooze_until then
    return
  end

  local prompt_key = status.date .. ":" .. table.concat(status.pending, "+")
  if not ignore_cooldown
    and prompt_key == state.last_prompt_key
    and (now - state.last_opened_at) < config.auto_open_cooldown_seconds then
    return
  end

  local message = status_message(status)
  hs.alert.show(message, 4)
  hs.notify.new({
    title = "Daily Enforcer",
    informativeText = message .. " (" .. reason .. ")",
  }):send()

  open_note(status)
  state.last_prompt_key = prompt_key
  state.last_opened_at = now
end

function M.check(reason, force_notify)
  local status = build_status()
  refresh_menu(status)

  if #status.pending == 0 then
    state.last_prompt_key = nil
    return status
  end

  if force_notify then
    notify(status, reason, reason == "manual" or reason == "unsnooze")
    return status
  end

  if reason == "timer" then
    notify(status, reason)
  end

  return status
end

local function handle_caffeinate_event(event)
  if event == hs.caffeinate.watcher.systemDidWake then
    M.check("wake", true)
  elseif event == hs.caffeinate.watcher.screensDidUnlock then
    M.check("unlock", true)
  end
end

function M.start()
  if state.watcher then
    return
  end

  state.watcher = hs.caffeinate.watcher.new(handle_caffeinate_event)
  state.watcher:start()

  state.timer = hs.timer.doEvery(config.remind_interval_seconds, function()
    M.check("timer", false)
  end)

  M.check("startup", false)
  log.i("daily enforcer started")
end

return M
