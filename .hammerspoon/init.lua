local ok, daily_enforcer = pcall(require, "daily_enforcer")

if not ok then
  hs.alert.show("daily_enforcer failed to load")
  print(daily_enforcer)
  return
end

daily_enforcer.start()
