local icons = require("icons")
local colors = require("colors")
local settings = require("settings")

-- osascript を使ってメディア情報を取得するスクリプト
local media_script = [[
app=""
state=$(osascript -e 'tell application "Music" to player state as string' 2>/dev/null)
if [ "$state" = "playing" ] || [ "$state" = "paused" ]; then
  app="music"
  title=$(osascript -e 'tell application "Music" to get name of current track' 2>/dev/null)
  artist=$(osascript -e 'tell application "Music" to get artist of current track' 2>/dev/null)
else
  state=$(osascript -e 'tell application "Spotify" to player state as string' 2>/dev/null)
  if [ "$state" = "playing" ] || [ "$state" = "paused" ]; then
    app="spotify"
    title=$(osascript -e 'tell application "Spotify" to get name of current track' 2>/dev/null)
    artist=$(osascript -e 'tell application "Spotify" to get artist of current track' 2>/dev/null)
  fi
fi

echo "${title:-}|||${artist:-}|||${state:-stopped}|||${app:-}"
]]

local media_icon = sbar.add("item", "widgets.media.icon", {
  position = "right",
  icon = {
    string = icons.media.play_pause,
    font = { size = 14 },
    color = colors.accent1,
  },
  label = { drawing = false },
  drawing = false,
  padding_right = 5,
})

local media_artist = sbar.add("item", "widgets.media.artist", {
  position = "right",
  drawing = false,
  padding_left = 3,
  padding_right = 0,
  icon = { drawing = false },
  label = {
    font = {
      size = 9,
      style = settings.font.style_map["Bold"],
    },
    color = colors.accent3,
    max_chars = 15,
    y_offset = 6,
  },
  scroll_texts = true,
  background = { drawing = false },
})

local media_title = sbar.add("item", "widgets.media.title", {
  position = "right",
  drawing = false,
  padding_left = 3,
  padding_right = 0,
  icon = { drawing = false },
  label = {
    font = {
      size = 11,
      style = settings.font.style_map["Bold"],
    },
    max_chars = 12,
    y_offset = -5,
    color = colors.accent1,
  },
  scroll_texts = true,
})

local bracket = sbar.add("bracket", "widgets.media.bracket", {
  media_icon.name,
  media_artist.name,
  media_title.name,
}, {
  background = { color = colors.tn_black3, border_color = colors.accent1 },
  drawing = false,
})

local function update_media()
  sbar.exec(media_script, function(result)
    local title, artist, state = result:match("(.-)|||(.-)|||(.-)|||")

    if (state == "playing" or state == "paused") and title and title ~= "" then
      local icon = state == "playing" and icons.media.pause or icons.media.play
      media_title:set({ drawing = true, label = title })
      media_artist:set({ drawing = true, label = artist })
      media_icon:set({ drawing = true, icon = { string = icon } })
      bracket:set({ drawing = true })
    else
      media_title:set({ drawing = false })
      media_artist:set({ drawing = false })
      media_icon:set({ drawing = false })
      bracket:set({ drawing = false })
    end
  end)
end

-- 3秒ごとに更新
media_icon:subscribe("routine", update_media)
media_icon:subscribe("forced", update_media)

-- クリックで再生/一時停止
media_icon:subscribe("mouse.clicked", function(env)
  sbar.exec([[osascript -e 'tell application "Music" to playpause']])
  update_media()
end)

-- 初回実行
update_media()

-- Padding
sbar.add("item", "widgets.media.padding", {
  position = "right",
  width = settings.group_paddings,
})
