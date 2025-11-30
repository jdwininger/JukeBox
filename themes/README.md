# Theme authoring quick guide

This folder contains themes for JukeBox. Each theme is a directory with image assets and an optional
`theme.conf` INI file to provide editable color overrides.

This short guide explains how to edit `theme.conf`.

Files & conventions
- Theme directories live under `themes/<theme-name>/`.
- Images: `background.png`, `button.png`, `button_hover.png`, `play_button.png`, etc. Use PNG or SVG.
- Optional file: `theme.conf` — put it in the theme root (next to images).

Supported `theme.conf` sections
- `[colors]` — overrides app-wide color keys. Keys available by default:
  - `background`, `text`, `text_secondary`, `accent`, `button`, `button_hover`, `button_pressed`
  - Values may be a comma-separated RGB triple (e.g. `32,32,32`) or a hex color (`#RRGGBB`).

- `[button_colors]` — optional per-button color overrides for text-labeled buttons.
  - Use the button label as the key (case-insensitive). Examples: `clr`, `ent`, `credits`.
  - These will affect the fill color used when the button renders text (not icon-only buttons).
  - You may also specify hover/pressed variants using suffixes: e.g. `credits_hover = 255,230,128` or `credits_pressed = 200,150,0`.

Example theme.conf
```
[colors]
background = 32,32,32
text = #ffffff
button = 64,64,64

[button_colors]
credits = 255,215,0
clr = 200,50,50
ent = 100,200,100
```

Precedence & behavior
- For text buttons the UI will first check `[button_colors]` and use that color if present.
- Otherwise it falls back to the generic `button` color from `[colors]`.
- If a color value cannot be parsed, the app will retain its built-in defaults.

Tips for theme authors
- Keep contrast high between `background` and `text` for readability.
- Use per-button colors sparingly — they are best for highlighting special actions.
- Prefer small PNGs or SVGs for icons and test them at the UI size (the app often scales them).

If you want more advanced options (per-button hover/pressed colors or per-button icons), open an issue or PR so we can standardize conventions.
