local wezterm = require("wezterm")

local module = {}

function module.apply_to_config(config)
  -- color_scheme は appearance.lua の colors テーブルで上書きされるため、
  -- ここでの設定は appearance.lua が読み込まれない場合の fallback として機能する
  -- config.color_scheme = "Overnight Slumber"
  -- config.color_scheme = "Solarized Dark - Patched"
  config.color_scheme = "Solarized Dark Higher Contrast"
end

return module
