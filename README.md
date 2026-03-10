# service.subtitles.dualsubtitles

Dual-only Kodi subtitle addon with smart folder selection and optional auto-match.

## What it does

- Shows only two actions in the subtitle screen:
  - `Choose Dual Subtitles...`
  - `Addon Settings...`
- Uses a smarter browse start folder:
  1. current video folder
  2. last used subtitle folder
  3. Kodi `special://subtitles`
  4. Kodi default browser root
- Supports automatic subtitle matching in the current video folder when both preferred languages are set:
  - file names must match `VideoName.xx.srt`, `VideoName-xx.srt`, or `VideoName_xx.srt`
  - matching is case-insensitive

## Notes

- Manual browse supports `.srt` and `.zip` files (zip must contain `.srt`).
- If only one preferred language match is found, the addon can reuse that match and ask for the other subtitle manually.
- Existing dual subtitle style and timing options are preserved.
