# Dual Subtitles for Kodi - service.subtitles.dualsubtitles

Dual subtitle addon for Kodi, focused on speed and fewer clicks.

## Credits

- Original addon and core idea by **peno64**:
  - Original project: <https://github.com/peno64/service.subtitles.localsubtitle>
- This repository is a customized fork focused on dual subtitles and smarter selection behavior.

## Main Features

- Dual-subtitle workflow only:
  - `Choose Dual Subtitles...`
  - `Addon Settings...`
- Smart start folder for browsing subtitles:
  1. current video folder (or last used first, configurable)
  2. last used subtitle folder
  3. Kodi `special://subtitles`
  4. Kodi default browser root
- Automatic subtitle matching based on:
  - current video filename
  - preferred language 1
  - preferred language 2
- Supports `.srt` and `.zip` (zip must contain `.srt`).
- Keeps advanced dual-sub rendering options:
  - top/bottom (or left-right) layout
  - font, colors, outline/shadow, margins
  - minimum display time and auto-shift sync

## Settings Overview

### Auto Match

- `Preferred Language 1` and `Preferred Language 2`
- `Match Strictness`
  - `Strict`: only exact patterns like `Movie.nl.srt`, `Movie-nl.srt`, `Movie_nl.srt`
  - `Relaxed`: also allows extra tokens like `Movie.forced.nl.srt`
- `Start Folder Priority`
  - `Video folder first`
  - `Last used folder first`

### Fallback

- `No Match Behavior`
  - Manual pick both subtitles
  - Pick first subtitle only
  - Stop with message
- `Partial Match Behavior` (only one preferred language found)
  - Ask confirmation
  - Auto use found subtitle and ask missing
  - Ignore auto match and pick both manually
- `Require second subtitle`
  - If enabled, loading stops when second subtitle is missing

### Layout

- `Subtitle Layout`
  - Bottom-Top
  - Bottom, Left-Right
  - Bottom-Bottom
- `Swap Bottom/Left - Top/Right Subtitles`

### Timing and Sync

- `Minimal Time (milliseconds) Subtitles on Screen`
- `Auto Shift`
- `Time Difference Threshold (milliseconds)`

### Bottom/Left Style

- Font, character set, font size, bold
- Color/background
- Shadow, outline, vertical margin

### Top/Right Style

- Font, character set, font size, bold
- Color/background
- Shadow, outline, vertical margin

## Runtime Notifications

The addon shows short messages during use, for example:

- both subtitles were auto-matched
- only one language match was found
- no match was found and fallback was used
- subtitles loaded successfully
- loading/preparation errors
