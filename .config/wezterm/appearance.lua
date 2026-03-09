local wezterm = require("wezterm")
local module = {}

local appearance = {
  color_scheme = "Solarized Dark Higher Contrast",

  -- background
  window_background_opacity = 0.7,
  macos_window_background_blur = 13,

  -- font
  font_size = 13.0,
  font = wezterm.font_with_fallback({
    "Hack Nerd Font",
    "HackGen Console NF",  -- 日本語フォールバック
  }),
  unicode_version = 14,

  -- window title
  window_decorations = "RESIZE", -- NONE, TITLE, TITLE | RESIZE, RESIZE, INTEGRATED_BUTTONS
  -- only for INTEGRATED_BUTTONS
  -- integrated_title_button_alignment = "Right",
  -- integrated_title_button_color = "Auto",
  -- integrated_title_button_style = "MacOsNative", -- Windows, Gnome, MacOsNative
  -- integrated_title_buttons = { "Hide", "Maximize", "Close" },

  window_padding = {
    left = 15,
    right = 15,
    top = 15,
    bottom = 0,
  },
  -- Disabled due to unstable font rendering
  -- window_content_alignment = {
  --   horizontal = "Center",
  --   vertical = "Center",
  -- },
  window_close_confirmation = "NeverPrompt", -- AlwaysPrompt or NeverPrompt

  --pane
  inactive_pane_hsb = {
    hue = 0.9,
    saturation = 0.9,
    brightness = 1.0,
  },
  default_cursor_style = "SteadyBlock", -- BlinkingBlock, SteadyUnderline, BlinkingUnderline, SteadyBar, BlinkingBar
  hide_mouse_cursor_when_typing = true,

  -- command palette
  -- command_palette_font = wezterm.font("Roboto"), -- Not a valid config field
  command_palette_bg_color = "#073642",
  command_palette_fg_color = "#2aa198",
  command_palette_rows = 18,
  command_palette_font_size = 14.0,

  -- char select
  -- char_select_font = wezterm.font("Roboto"), -- Not a valid config field
  char_select_bg_color = "#073642",
  char_select_fg_color = "#2aa198",

  ----------------------------------------------------
  -- Tab
  ----------------------------------------------------
  show_tabs_in_tab_bar = true,
  hide_tab_bar_if_only_one_tab = false,
  tab_bar_at_bottom = true,
  show_new_tab_button_in_tab_bar = false,
  tab_max_width = 30,
  use_fancy_tab_bar = true,
  window_frame = {
    inactive_titlebar_bg = "none",
    active_titlebar_bg = "none",
  },
  -- Hide borders between tabs
  -- Solarized Osaka color palette
  colors = {
    background = "#002b36",
    foreground = "#839496",
    tab_bar = {
      background = "none",
      inactive_tab_edge = "none",
    },
    cursor_bg = "#d33682",
    cursor_fg = "#002b36",
    cursor_border = "#d33682",
    selection_bg = "#073642",
    selection_fg = "#839496",
    ansi = {
      "#073642", -- black (base02)
      "#dc322f", -- red
      "#859900", -- green
      "#b58900", -- yellow
      "#268bd2", -- blue
      "#d33682", -- magenta
      "#2aa198", -- cyan
      "#eee8d5", -- white (base2)
    },
    brights = {
      "#586e75", -- bright black (base01)
      "#cb4b16", -- bright red (orange)
      "#586e75", -- bright green (base01)
      "#657b83", -- bright yellow (base00)
      "#839496", -- bright blue (base0)
      "#6c71c4", -- bright magenta (violet)
      "#93a1a1", -- bright cyan (base1)
      "#fdf6e3", -- bright white (base3)
    },
  },
}

function module.apply_to_config(config)
  for k, v in pairs(appearance) do
    config[k] = v
  end
end

return module
