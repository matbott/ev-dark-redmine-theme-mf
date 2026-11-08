#!/usr/bin/env python3
"""Generate the colour-scheme blocks in application.css and theme.js.

Usage:
    python3 src/gen-schemes.py

The Ev Dark theme ships a curated set of 10 GoGogh palettes
(https://github.com/Gogh-Co/Gogh, MIT/Apache-2.0). Each scheme contributes the
raw --s-* values (background, foreground, muted text, accent, text-on-accent and
the red/green/yellow/blue status slots) that the CSS derives the Ev Dark tokens
from. The blocks between the @schemes markers are generated - do not edit them by
hand, change the SCHEMES dict and rerun.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / 'stylesheets' / 'application.css'
JS = ROOT / 'javascripts' / 'theme.js'

# Curated GoGogh palettes for Ev Dark. Keep in sync with the picker in theme.js
# (the SCHEMES array lives between // @schemes markers there).
# (name, dark, bg, fg, muted, accent, on_accent, red, green, yellow, blue)
SCHEMES = [
    ('Dracula',          True,  '#282A36', '#F8F8F2', '#BEBEBD', '#C098F9', '#282A36', '#FF8888', '#50FA7B', '#F1FA8C', '#BD93F9'),
    ('Nord',             True,  '#2E3440', '#D8DEE9', '#ACB2BD', '#88C0D0', '#2E3440', '#DCA8AD', '#A3BE8C', '#EBCB8B', '#81A1C1'),
    ('Gruvbox Dark',     True,  '#282828', '#EBDBB2', '#B4A98B', '#D79921', '#282828', '#E6928E', '#98971A', '#D79921', '#458588'),
    ('Tokyo Night',      True,  '#1A1B26', '#C0CAF5', '#9299BB', '#7AA2F7', '#1A1B26', '#F7768E', '#9ECE6A', '#E0AF68', '#7AA2F7'),
    ('Catppuccin Mocha', True,  '#1E1E2E', '#CDD6F4', '#9CA2BD', '#89B4FA', '#1E1E2E', '#F38BA8', '#A6E3A1', '#F9E2AF', '#89B4FA'),
    ('One Dark',         True,  '#282C34', '#CDD1D9', '#A5A9B1', '#61AFEF', '#282C34', '#E89198', '#98C379', '#D19A66', '#61AFEF'),
    ('Everforest Dark', True,  '#2D353B', '#E5DDCC', '#B9B5A9', '#85BEB7', '#2D353B', '#EC9EA0', '#A7C080', '#DBBC7F', '#7FBBB3'),
    ('Rosé Pine',        True,  '#191724', '#E0DEF4', '#A8A6BA', '#C4A7E7', '#191724', '#EB6F92', '#31748F', '#F6C177', '#9CCFD8'),
    ('Solarized Light', False, '#FCF4DC', '#42535A', '#647071', '#1F70BD', '#FFFFFF', '#D11C24', '#738A05', '#A57706', '#2176C7'),
    ('Gruvbox Light',   False, '#FBF1C7', '#3C3836', '#716C5F', '#3B7174', '#FFFFFF', '#CC241D', '#98971A', '#D79921', '#458588'),
    ('One Dark Pro',      True,  '#282C34', '#ABB2BF', '#3F4451', '#61AFEF', '#282C34', '#E06C75', '#98C379', '#D19A66', '#61AFEF'),
    ('Catppuccin Macchiato', True, '#24273A', '#CAD3F5', '#494D64', '#8AADF4', '#24273A', '#ED8796', '#A6DA95', '#EED49F', '#8AADF4'),
    ('GitHub Dark',       True,  '#101216', '#E6EDF3', '#484F58', '#58A6FF', '#101216', '#FF7B72', '#56D364', '#E3B341', '#58A6FF'),
    ('Kanagawa Wave',     True,  '#1F1F28', '#DCD7BA', '#090618', '#7E9CD8', '#1F1F28', '#C34043', '#76946A', '#C0A36E', '#7E9CD8'),
    ('Monokai Pro',       True,  '#2D2A2E', '#FCFCFA', '#2D2A2E', '#FC9867', '#2D2A2E', '#FF6188', '#A9DC76', '#FFD866', '#FC9867'),
    ('Ayu Dark',          True,  '#0A0E14', '#B3B1AD', '#0A0E14', '#59C2FF', '#0A0E14', '#FF3333', '#C2D94C', '#FF8F40', '#59C2FF'),
    # --- añadidas: 10 dark + 10 light (variedad) ---
    ('Material Dark', True, '#232322', '#E5E5E5', '#ABABAA', '#F6981E', '#232322', '#C65960', '#457B24', '#F6981E', '#134EB2'),
    ('Palenight', True, '#292D3E', '#BFC7D5', '#9299A8', '#FFCB6B', '#292D3E', '#E08D97', '#C3E88D', '#FFCB6B', '#82AAFF'),
    ('Cobalt2', True, '#132738', '#FFFFFF', '#B8BEC3', '#FFE50A', '#132738', '#FF5454', '#38DE21', '#FFE50A', '#1460D2'),
    ('Nightfox', True, '#192330', '#CDCECF', '#979B9F', '#DBC074', '#192330', '#CA798D', '#81B29A', '#DBC074', '#719CD6'),
    ('Solarized Dark', True, '#001E27', '#708284', '#4E6468', '#259286', '#001E27', '#B13E44', '#738A05', '#A57706', '#2176C7'),
    ('Zenburn', True, '#3F3F3F', '#DCDCCC', '#ADADA2', '#8CD0D3', '#3F3F3F', '#947E79', '#60B48A', '#F0DFAF', '#506070'),
    ('Molokai', True, '#121212', '#BBBBBB', '#888888', '#DFD460', '#121212', '#E5568B', '#98E123', '#DFD460', '#1080D0'),
    ('Spacegray', True, '#20242D', '#B3B8C3', '#878C96', '#E5C179', '#20242D', '#B16F7B', '#87B379', '#E5C179', '#7D8FA4'),
    ('Wild Cherry', True, '#1F1726', '#DAFAFF', '#A2B6BE', '#FFD16F', '#1F1726', '#D97DAD', '#2AB250', '#FFD16F', '#883CDC'),
    ('Tomorrow Night', True, '#1D1F21', '#C5C8C6', '#939594', '#F0C674', '#1D1F21', '#CA8686', '#B5BD68', '#F0C674', '#81A2BE'),
    ('Ayu Light', False, '#F8F9FA', '#5C6166', '#8B8F92', '#9E75C7', '#FFFFFF', '#BB686B', '#6CBF43', '#ECA944', '#3199E1'),
    ('Catppuccin Latte', False, '#EFF1F5', '#4C4F69', '#7D8093', '#1E66F5', '#FFFFFF', '#A62449', '#40A02B', '#DF8E1D', '#1E66F5'),
    ('Github Light', False, '#F6F8FA', '#1F2328', '#606367', '#0969DA', '#FFFFFF', '#95222C', '#1A7F37', '#9A6700', '#0969DA'),
    ('One Light', False, '#F8F8F8', '#2A2B32', '#68686D', '#930092', '#FFFFFF', '#A03837', '#41933E', '#855504', '#315EEE'),
    ('Kanagawa Lotus', False, '#F2ECBC', '#545464', '#83827E', '#4D699B', '#FFFFFF', '#A24759', '#6F894E', '#77713F', '#4D699B'),
    ('Paper', False, '#F2EEDE', '#000000', '#494743', '#5C21A5', '#FFFFFF', '#892A1B', '#216609', '#B58900', '#1E6FCC'),
    ('Spring', False, '#FFFFFF', '#4D4D4C', '#828282', '#8959A8', '#FFFFFF', '#C44D71', '#1F8C3B', '#1FC95B', '#1DD3EE'),
    ('Light Owl', False, '#FBFBFB', '#403F53', '#787785', '#D6438A', '#FFFFFF', '#AA3E43', '#08916A', '#E0AF02', '#288ED7'),
    ('Atom One Light', False, '#F9F9F9', '#2A2C33', '#686A6E', '#950095', '#FFFFFF', '#A33834', '#3F953A', '#D2B67C', '#2F5AF3'),
    ('Belafonte Day', False, '#D5CCBA', '#45373C', '#706462', '#97522C', '#FFFFFF', '#961D1D', '#858162', '#EAA549', '#426A79'),
]


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def css_block(s):
    return (f'  /* Gogh: {s[0]} */\n'
            f'  html[data-scheme="{slug(s[0])}"] {{\n'
            f'    --s-bg: {s[2]};  --s-fg: {s[3]};  --s-muted: {s[4]};\n'
            f'    --s-accent: {s[5]};  --s-on-accent: {s[6]};\n'
            f'    --s-red: {s[7]};  --s-green: {s[8]};  --s-yellow: {s[9]};  --s-blue: {s[10]};\n'
            f'  }}\n')


def js_line(s):
    return (f"    {{ id: '{slug(s[0])}', name: '{s[0]}', dark: {'true' if s[1] else 'false'}, "
            f"swatch: ['{s[2]}', '{s[3]}', '{s[5]}'] }},")


def replace_between(path, begin, end, body):
    text = path.read_text()
    pat = re.compile(rf'({re.escape(begin)}\n).*?([ \t]*{re.escape(end)})', re.S)
    if not pat.search(text):
        sys.exit(f'markers {begin!r} / {end!r} not found in {path}')
    path.write_text(pat.sub(lambda m: m.group(1) + body.rstrip('\n') + '\n' + m.group(2), text, count=1))


def main():
    body = ''.join(css_block(s) for s in SCHEMES)
    replace_between(CSS, '/* @schemes:begin — generated by src/gen-schemes.py, do not edit */',
                    '/* @schemes:end */', body)
    replace_between(JS, '// @schemes:begin — generated by src/gen-schemes.py, do not edit',
                    '// @schemes:end', '\n'.join(js_line(s) for s in SCHEMES))
    print(f'wrote {CSS.relative_to(ROOT)} and {JS.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
