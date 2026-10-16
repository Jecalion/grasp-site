"""
Puts the realistic Grasp, in the gym, on the landing page in every language.

    python build/gym.py

Runs on the generated pages (index.html and <lang>/index.html), after
build.py, the way the cartoon poses were put in: those pages carry sections
the template does not have yet. Run it once on pages that still have the
cartoon poses; it refuses to run twice.

  - The hero is a full-bleed photo, the wide deadlift on a desktop and the
    tall chalk shot on a phone, with the text over its dark side. Mirrored
    for Arabic, so Grasp stands on the side the text does not.
  - Every feature picture gets a photo panel behind its phone instead of a
    cartoon pose.

The photos are in img/gym/, from ChatGPT, each at full size and at 820 px
wide (-sm) for phones.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = 'en ar fr de es it tr pl ru hi zh ko ja id pt'.split()

# Full-size dimensions of each photo, and the -sm width.
SIZES = {
    'bench': (1672, 941), 'battle-ropes': (1672, 941), 'chalk': (941, 1672), 'deadlift': (1672, 941),
    'leg-day': (1916, 821), 'mirror': (1122, 1402), 'phone': (1254, 1254), 'pull-up': (1122, 1402),
    'record': (1536, 1024), 'squat': (1122, 1402),
}
# Cartoon pose beside a feature picture -> the photo that replaces it, and
# where Grasp is across the photo, for the 4:5 crop of the wide ones.
SHOTS = {
    'explain-plan': ('bench', '60%'),
    'coach': ('mirror', '50%'),
    'deadlift-heavy': ('squat', '50%'),
    'trophy': ('record', '62%'),
    'dance': ('pull-up', '50%'),
    'phone-wave': ('phone', '50%'),
    'banana-lounge': ('leg-day', '24%'),
    'counting': ('deadlift', '79%'),
    'jump-rope': ('battle-ropes', '17%'),
    'calendar': ('chalk', '50%'),
}


def srcset(name: str) -> str:
    return f'/img/gym/{name}-sm.webp 820w, /img/gym/{name}.webp {SIZES[name][0]}w'


def photo(name: str, position: str) -> str:
    w, h = SIZES[name]
    return (
        f'<img class="gym" src="/img/gym/{name}.webp" srcset="{srcset(name)}" '
        f'sizes="(max-width: 900px) 80vw, 400px" alt="" width="{w}" height="{h}" loading="lazy" '
        f'style="object-position: {position} 50%" />'
    )


def hero_photo() -> str:
    return (
        '        <picture class="hero-photo">'
        '<source media="(max-width: 700px)" srcset="/img/gym/chalk-sm.webp" width="820" height="1457" />'
        f'<img src="/img/gym/deadlift.webp" srcset="{srcset("deadlift")}" sizes="100vw" alt="" '
        'width="1672" height="941" fetchpriority="high" /></picture>\n'
    )


def patch(s: str, lang: str) -> str:
    assert 'class="gym"' not in s, f'{lang}: already patched'

    # Hero: the photo behind, the phones out, Grasp's first line kept as a bubble over the text.
    m = re.search(r'<figcaption class="bubble">(.*?)</figcaption>', s)
    assert m, lang
    bubble = m.group(1)
    start = s.index('          <div class="hero-phones">')
    end = s.index('          </div>\n', s.index('</figure>', start)) + len('          </div>\n')
    s = s[:start] + s[end:]
    s = s.replace('\n\n        </div>\n      </section>\n\n      <section class="stats"', '\n        </div>\n      </section>\n\n      <section class="stats"', 1)
    old = '      <section class="hero">\n        <div class="wrap wide hero-grid">\n'
    assert s.count(old) == 1, lang
    s = s.replace(old, '      <section class="hero gym-hero">\n' + hero_photo() + '        <div class="wrap wide hero-grid">\n')
    old = '            <span class="badge">'
    assert s.count(old) == 1, lang
    s = s.replace(old, f'            <p class="hero-bubble">{bubble}</p>\n{old}')

    # Features: a photo panel behind each phone instead of the cartoon pose.
    for pose, (name, position) in SHOTS.items():
        tag = re.search(rf'<img class="grasp-pose" src="/img/grasp/{pose}\.webp"[^>]*/>', s)
        assert tag, (lang, pose)
        shot = s.rindex('<div class="feature-shot">', 0, tag.start())
        section = s.rindex('<section class="feature', 0, shot)
        s = s[: tag.start()] + s[tag.end():]
        s = s[:shot] + '<div class="feature-shot gym-shot">' + photo(name, position) + s[shot + len('<div class="feature-shot">'):]
        s = s[:section] + s[section:].replace('<section class="feature', '<section class="feature gym-feature', 1)
    assert 'grasp-pose' not in s, lang

    # The final call: the cartoon wave goes; the page has its Grasp now.
    s = re.sub(r'\n *<img class="grasp-final"[^>]*/>', '', s)
    return s


def main(langs: list[str]) -> None:
    for lang in langs:
        path = os.path.join(ROOT, 'index.html' if lang == 'en' else f'{lang}/index.html')
        raw = open(path, encoding='utf8', newline='').read()
        crlf = chr(13) + chr(10) in raw
        out = patch(raw.replace(chr(13) + chr(10), chr(10)), lang)
        if crlf:
            out = out.replace(chr(10), chr(13) + chr(10))
        open(path, 'w', encoding='utf8', newline='').write(out)
        print(lang)


if __name__ == '__main__':
    main(sys.argv[1:] or LANGS)
