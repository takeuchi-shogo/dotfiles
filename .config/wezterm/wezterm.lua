local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()
config.automatically_reload_config = true
config.audible_bell = "Disabled"

config.font_size = 12.0
config.use_ime = true
config.window_background_opacity = 0.75
config.macos_window_background_blur = 20

local shell = os.getenv("SHELL")

-- config.window_decorations = "RESIZE"

config.launch_menu = {
  {
    label = "🗓 作業日報を書く",
    cwd = os.getenv("HOME") .. "/dotfiles",
    args = { shell, "-l", "-c", "bash .bin/gen_daily_report.sh" },
  },
  -- {
  --   label = "Show WezTerm Path",
  --   args = { shell, "-c", "echo $PATH && read" },
  -- },
}

-- Alt key behavior
config.send_composed_key_when_left_alt_is_pressed = false -- Treat left Alt as Meta key (sends escape sequences)
config.send_composed_key_when_right_alt_is_pressed = true -- Keep right Alt for key composition

local SOLID_LEFT_ARROW = wezterm.nerdfonts.ple_lower_right_triangle
local SOLID_RIGHT_ARROW = wezterm.nerdfonts.ple_upper_left_triangle

local color = require("color")
local keymaps = require("keymaps")
local functions = require("functions")
local appearance = require("appearance")
local workspace = require("workspace")
local hyperlinks = require("hyperlinks")
local tab = require("tab")

color.apply_to_config(config)
keymaps.apply_to_config(config)
functions.apply_to_config(config)
appearance.apply_to_config(config)
workspace.apply_to_config(config)
hyperlinks.apply_to_config(config)
tab.apply_to_config(config)

return config
