# Ev Dark - Redmine theme (By Ramin)

1. Copy this folder to:  <redmine>/public/themes/Ev-dark/
   (final path: public/themes/Ev-dark/stylesheets/application.css)
2. Restart Redmine (Passenger: touch tmp/restart.txt).
3. Administration > Settings > Display > Theme = "Ev Dark" > Save.

Requires Redmine 4.1+ (for javascripts/theme.js; the CSS alone works on older versions).
No external resources are loaded.

## Colour schemes (GoGogh palettes)

The theme ships with a curated set of **10 colour schemes** from
[Gogh](https://github.com/Gogh-Co/Gogh) (MIT/Apache-2.0) and lets the user pick one:

- **Top bar**: 🎨 button opens a dropdown with the schemes of the current mode
  (Dark/Light) + a "toggle dark mode" action. Choice is saved per browser and per
  mode (`rm-scheme`, `rm-scheme-dark`, `rm-scheme-light`).
- **My account → Preferences**: full scheme picker (Default / Dark / Light groups)
  injected by `javascripts/theme.js`.

How it works:

- Colour tokens live in the `:root` block at the top of `stylesheets/application.css`
  (fallback = the Ev Dark palette). When a scheme is picked, `html[data-scheme="<id>"]`
  + `html[data-scheme].dark-mode` / `html[data-scheme]:not(.dark-mode)` derive every
  token from the raw `--s-*` values of that scheme (via `color-mix()`).
- The raw `--s-*` values per scheme live in the generated blocks between the
  `@schemes:begin` / `@schemes:end` markers at the bottom of `stylesheets/application.css`.
- **Do not edit those generated blocks by hand.** Change the curated palette list in
  `src/gen-schemes.py` (the `SCHEMES` dict) and rerun:

  ```bash
  python3 src/gen-schemes.py      # regenerates application.css + javascripts/theme.js blocks
  ```

- Dark mode is the default (the Ev Dark aesthetic). A light scheme clears
  `html.dark-mode`; the choice is kept per mode.

## Development

- Source of truth for schemes: `src/gen-schemes.py`, `stylesheets/application.css`,
  `javascripts/theme.js`.
- Only `stylesheets/application.css` and `javascripts/theme.js` are theme sources.
  No Redmine core files are modified.
