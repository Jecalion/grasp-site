"""
The link preview each page shows when it is shared (WhatsApp, X, iMessage,
LinkedIn): 1200x630 JPEG, the kettlebell Grasp with the page's own headline.

    python build/og.py

Writes img/og/<lang>.jpg for the fifteen landing pages, from the same
build/i18n/<lang>.json the pages are built from, and img/og/get.jpg for the
/get link, in Arabic and English because that link is shared in Arabic posts
first. Rendered by headless Chrome (a tool for whoever runs this, not part of
the site). Run it again when a headline changes.
"""
import html
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'img', 'og')
CHROME = os.environ.get('CHROME', r'C:/Program Files/Google/Chrome/Application/chrome.exe')
LANGS = 'en ar fr de es it tr pl ru hi zh ko ja id pt'.split()


def url(path: str) -> str:
    return 'file:///' + os.path.join(ROOT, path).replace(os.sep, '/')


def page(lang: str, bubble: str, before: str, highlight: str, badge: str, second: str = '') -> str:
    rtl = lang == 'ar'
    side = 'right' if rtl else 'left'
    fade = '270deg' if rtl else '90deg'
    flip = 'transform: scaleX(-1);' if rtl else ''
    extra = f'<p class="second">{html.escape(second)}</p>' if second else ''
    return f"""<!doctype html><html lang="{lang}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Plex; src: url('{url('fonts/IBMPlexSans_700Bold.woff2')}'); font-weight: 700; }}
@font-face {{ font-family: Plex; src: url('{url('fonts/IBMPlexSans_600SemiBold.woff2')}'); font-weight: 600; }}
@font-face {{ font-family: Kufi; src: url('{url('fonts/NotoKufiArabic_700Bold.ttf')}'); font-weight: 600 700; }}
* {{ margin: 0; box-sizing: border-box; }}
html, body {{ width: 1200px; height: 630px; overflow: hidden; background: #07090c; color: #fff;
  font-family: Plex, Kufi, 'Nirmala UI', 'Microsoft YaHei', 'Yu Gothic', 'Malgun Gothic', sans-serif; }}
.photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 80% 18%; {flip} }}
.fade {{ position: absolute; inset: 0; background: linear-gradient({fade}, rgba(7,9,12,.96) 0%, rgba(7,9,12,.86) 40%, rgba(7,9,12,0) 72%); }}
.copy {{ position: absolute; top: 0; bottom: 0; {side}: 64px; width: 640px; display: flex; flex-direction: column; justify-content: center; gap: 22px; }}
.mark {{ position: absolute; top: 44px; {side}: 64px; height: 34px; direction: ltr; }}
.bubble {{ align-self: flex-start; background: #c6f84e; color: #0d0e10; font-weight: 700; font-size: 26px; line-height: 1.25;
  padding: 12px 20px; border-radius: 20px; border-end-end-radius: 5px; }}
h1 {{ font-size: 62px; line-height: 1.08; letter-spacing: -1.5px; font-weight: 700; text-wrap: balance; }}
[dir=rtl] h1 {{ letter-spacing: 0; line-height: 1.35; }}
h1 span {{ color: #c6f84e; }}
.second {{ font-size: 30px; font-weight: 600; color: #c3c8ce; direction: ltr; text-align: {side}; }}
.badge {{ font-size: 22px; font-weight: 700; color: #c6f84e; letter-spacing: 1px; }}
[dir=rtl] .badge {{ letter-spacing: 0; }}
</style></head><body>
<img class="photo" src="{url('img/gym/kettlebell.webp')}">
<div class="fade"></div>
<svg class="mark" viewBox="-4 25 264 50" fill="none"><g stroke="#fff" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round">
<line x1="10" y1="30" x2="10" y2="70"/><line x1="25" y1="30" x2="25" y2="70"/><line x1="40" y1="30" x2="40" y2="70"/><line x1="55" y1="30" x2="55" y2="70"/>
<path d="M 112 30 L 93 30 L 93 70 L 112 70 L 112 52 L 103 52"/><path d="M 129 70 L 129 30 L 147 30 L 147 48 L 129 48"/><path d="M 137 48 L 148 70"/>
<path d="M 165 70 L 165 38 L 174 30 L 183 38 L 183 70"/><path d="M 165 54 L 183 54"/><path d="M 220 30 L 201 30 L 201 50 L 219 50 L 219 70 L 200 70"/>
<path d="M 237 70 L 237 30 L 255 30 L 255 50 L 237 50"/></g><line x1="1" y1="64" x2="64" y2="36" stroke="#c6f84e" stroke-width="8.5" stroke-linecap="round"/></svg>
<div class="copy">
<p class="bubble">{html.escape(bubble).replace(chr(10), ' ')}</p>
<h1>{html.escape(before)} <span>{html.escape(highlight)}</span></h1>
{extra}
<p class="badge">{html.escape(badge)}</p>
</div></body></html>"""


def render(markup: str, out: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'og.html')
        png = os.path.join(tmp, 'og.png')
        open(src, 'w', encoding='utf8').write(markup)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', f'--user-data-dir={os.path.join(tmp, "profile")}',
                        '--hide-scrollbars', '--allow-file-access-from-files', '--window-size=1200,630',
                        '--virtual-time-budget=4000', f'--screenshot={png}', 'file:///' + src.replace(os.sep, '/')],
                       check=True, capture_output=True)
        from PIL import Image
        Image.open(png).convert('RGB').crop((0, 0, 1200, 630)).save(out, quality=86, optimize=True, progressive=True)


def main(langs: list[str]) -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in langs:
        s = json.load(open(os.path.join(HERE, 'i18n', f'{lang}.json'), encoding='utf8'))
        render(page(lang, s['hero_bubble'], s['hero_h1_before'], s['hero_h1_highlight'], s['hero_badge']),
               os.path.join(OUT, f'{lang}.jpg'))
        print('wrote', f'img/og/{lang}.jpg')
    if not sys.argv[1:] or 'get' in sys.argv[1:]:
        ar = json.load(open(os.path.join(HERE, 'i18n', 'ar.json'), encoding='utf8'))
        en = json.load(open(os.path.join(HERE, 'i18n', 'en.json'), encoding='utf8'))
        render(page('ar', ar['hero_bubble'], ar['hero_h1_before'], ar['hero_h1_highlight'], ar['hero_badge'],
                    second=f"{en['hero_h1_before']} {en['hero_h1_highlight']}"),
               os.path.join(OUT, 'get.jpg'))
        print('wrote img/og/get.jpg')


if __name__ == '__main__':
    main([l for l in sys.argv[1:] if l != 'get'] or LANGS)
