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
  command_palette_bg_color = "#1d2230",
  command_palette_fg_color = "#769ff0",
  command_palette_rows = 18,
  command_palette_font_size = 14.0,

  -- char select
  -- char_select_font = wezterm.font("Roboto"), -- Not a valid config field
  char_select_bg_color = "#1d2230",
  char_select_fg_color = "#769ff0",

  ----------------------------------------------------
  -- Tab
  ----------------------------------------------------
  show_tabs_in_tab_bar = true,
  hide_tab_bar_if_only_one_tab = false,
  tab_bar_at_bottom = true,
  show_new_tab_button_in_tab_bar = false,
  show_close_tab_button_in_tabs = false,
  tab_max_width = 30,
  use_fancy_tab_bar = true,
  window_frame = {
    inactive_titlebar_bg = "none",
    active_titlebar_bg = "none",
  },
  -- Hide borders between tabs
  colors = {
    background = "#1a1a2e",
    tab_bar = {
      background = "none",
      inactive_tab_edge = "none",
    },
    cursor_bg = "#80EBDF",
    cursor_fg = "#000000",
    cursor_border = "#80EBDF",
    selection_bg = "#ffdd00",
    selection_fg = "#000000",
  },
}

function module.apply_to_config(config)
  for k, v in pairs(appearance) do
    config[k] = v
  end
end

return module
