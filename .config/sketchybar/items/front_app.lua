local colors = require("colors")
local settings = require("settings")
local icon_map = require("helpers.icon_map")

local front_app = sbar.add("item", "front_app", {
  display = "active",
  icon = {
    font = { family = "sketchybar-app-font", size = 16 },
    color = colors.accent1,
  },
  label = {
    font = {
      style = settings.font.style_map["Black"],
      size = 12.0,
    },
  },
  updates = true,
})

front_app:subscribe("front_app_switched", function(env)
  local icon = icon_map[env.INFO] or icon_map["default"] or ":default:"
  front_app:set({
    label = { string = env.INFO },
    icon = { string = icon },
  })
end)

front_app:subscribe("mouse.clicked", function(env)
  sbar.trigger("swap_menus_and_spaces")
end)
