"""
Writes the landing page in every language the app speaks.

    python build/build.py

template.html + i18n/<lang>.json -> index.html (English, at /) and
<lang>/index.html for the other fourteen. The output is committed: GitHub
Pages serves the repository as it is, with no build step of its own.

The fifteen languages, their order, native names and flags are the app's
(apps/mobile/src/i18n/languages.ts in the app repository). A key missing
from a language file stops the build rather than shipping English in the
middle of a Japanese page.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://grasp.alsouq.tech"
STORE = "https://apps.apple.com/app/id6804474068"
PLAY = "https://play.google.com/store/apps/details?id=com.graspapp.mobile"

# (code, native name, flag file, right to left) in the app's picker order.
LANGS = [
    ("en", "English", "gb", False),
    ("ar", "العربية", "sa", True),
    ("fr", "Français", "fr", False),
    ("de", "Deutsch", "de", False),
    ("es", "Español", "es", False),
    ("it", "Italiano", "it", False),
    ("tr", "Türkçe", "tr", False),
    ("pl", "Polski", "pl", False),
    ("ru", "Русский", "ru", False),
    ("hi", "हिन्दी", "in", False),
    ("zh", "中文", "cn", False),
    ("ko", "한국어", "kr", False),
    ("ja", "日本語", "jp", False),
    ("id", "Bahasa Indonesia", "id", False),
    ("pt", "Português", "br", False),
]
KIT = [
    ("dumbbell", "dumbbell", "home gym"),
    ("kettlebell", "kettlebell", "home gym"),
    ("resistance_band", "resistance-band", "home gym"),
    ("pullup_bar", "pull-up-bar", "home gym"),
    ("flat_bench", "flat-bench", "home gym"),
    ("barbell", "barbell", "gym"),
    ("cable_machine", "cable", "gym"),
    ("leg_press_machine", "leg-press", "gym"),
    ("smith_machine", "smith-machine", "gym"),
    ("treadmill", "treadmill", "gym"),
]
# The trophy and the tick on the drawn records screen, as in the app.
ICONS = {
    "icon_trophy": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" '
        'd="M7 3h10v2h3v3a4 4 0 0 1-4 4h-.3A5 5 0 0 1 13 14.9V17h3v2H8v-2h3v-2.1A5 5 0 0 1 8.3 12H8a4 4 0 0 '
        '1-4-4V5h3V3zm0 4H6v1a2 2 0 0 0 1 1.7V7zm10 0v2.7A2 2 0 0 0 18 8V7h-1z"/></svg>'
    ),
    "icon_check": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" '
        'd="M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6L20.1 8.4 18.7 7z"/></svg>'
    ),
}
# The realistic Grasp in the gym (img/gym/, from ChatGPT), each photo at full
# size and at 820 px wide (-sm) for phones: full-size width and height.
GYM = {
    "bench": (1672, 941), "battle-ropes": (1672, 941), "chalk": (1260, 2239), "deadlift": (2560, 1441),
    "leg-day": (1916, 821), "mirror": (1122, 1402), "phone": (1254, 1254), "pull-up": (1122, 1402),
    "record": (1536, 1024), "squat": (1122, 1402),
}


def path_for(code: str) -> str:
    return "/" if code == "en" else f"/{code}/"


def get_block(s: dict, center: bool, lazy: bool) -> str:
    load = ' loading="lazy"' if lazy else ""
    return (
        f'            <div class="get{" center" if center else ""}">\n'
        f'              <a class="store-badge" href="{STORE}" aria-label="{s["store_aria"]}">'
        f'<img src="/img/app-store-badge.svg" alt="{s["store_alt"]}" width="180" height="60"{load} /></a>\n'
        f'              <a class="store-badge play" href="{PLAY}" aria-label="{s["play_aria"]}">'
        f'<img src="/img/google-play-badge.png" alt="Get it on Google Play" width="231" height="89"{load} /></a>\n'
        f"            </div>"
    )


def gym_srcset(name: str) -> str:
    return f"/img/gym/{name}-sm.webp 820w, /img/gym/{name}.webp {GYM[name][0]}w"


def gym_photo(name: str, position: str) -> str:
    """The photo panel behind a feature's phone. `position` is where Grasp
    stands across the photo, for the 4:5 crop of the wide ones."""
    w, h = GYM[name]
    return (
        f'<img class="gym" src="/img/gym/{name}.webp" srcset="{gym_srcset(name)}" '
        f'sizes="(max-width: 900px) 80vw, 400px" alt="" width="{w}" height="{h}" loading="lazy" '
        f'style="object-position: {position} 50%" />'
    )


def hero_photo() -> str:
    """Full bleed behind the hero text: the wide deadlift on a desktop, the
    tall chalk shot on a phone. style.css mirrors it for Arabic, so Grasp
    stands on the side the text does not."""
    return (
        '        <picture class="hero-photo">'
        f'<source media="(max-width: 700px)" srcset="{gym_srcset("chalk")}" sizes="100vw" width="1260" height="2239" />'
        f'<img src="/img/gym/deadlift.webp" srcset="{gym_srcset("deadlift")}" sizes="100vw" alt="" '
        'width="2560" height="1441" fetchpriority="high" /></picture>'
    )


def switcher(code: str, s: dict) -> str:
    current = next(l for l in LANGS if l[0] == code)
    items = "\n".join(
        f'            <li><a href="{path_for(c)}" hreflang="{c}" lang="{c}"'
        f'{" aria-current=\"page\"" if c == code else ""}>'
        f'<img src="/img/flags/{flag}.svg" alt="" width="24" height="18" />'
        f'<span{" dir=\"rtl\"" if rtl else ""}>{html.escape(name)}</span></a></li>'
        for c, name, flag, rtl in LANGS
    )
    return (
        f'        <details class="lang-switch">\n'
        f'          <summary aria-label="{s["language"]}: {html.escape(current[1])}">'
        f'<img src="/img/flags/{current[2]}.svg" alt="" width="24" height="18" />'
        f'<span class="lang-code">{code.upper()}</span></summary>\n'
        f'          <ul>\n{items}\n          </ul>\n'
        f"        </details>"
    )


def flag_grid() -> str:
    items = "\n".join(
        f'            <li><a href="{path_for(c)}" lang="{c}"><img src="/img/flags/{flag}.svg" alt="" width="36" height="27" />'
        f'<span{" dir=\"rtl\"" if rtl else ""}>{html.escape(name)}</span></a></li>'
        for c, name, flag, rtl in LANGS
    )
    return f'          <ul class="flag-grid">\n{items}\n          </ul>'


def kit(s: dict) -> str:
    items = "\n".join(
        f'            <li data-in="{where}"><img src="/img/equipment/{img}.webp" alt="" width="160" height="160" loading="lazy" />'
        f'<span>{html.escape(s["equipment"][key])}</span></li>'
        for key, img, where in KIT
    )
    return f'          <ul class="kit" data-setup="home">\n{items}\n          </ul>'


FAQ_COUNT = 9


def faq_list(esc: dict) -> str:
    """Native <details>: the answers are in the page for crawlers and screen
    readers, closed until opened, and need no script."""
    items = "\n".join(
        f'            <details><summary>{esc[f"faq{i}_q"]}</summary><p>{esc[f"faq{i}_a"]}</p></details>'
        for i in range(1, FAQ_COUNT + 1)
    )
    return f'          <div class="faq-list">\n{items}\n          </div>'


def jsonld(code: str, s: dict) -> str:
    """What the page is, for search engines and the AI answers built on them:
    the app (name, platform, price, languages, where to get it) and the FAQ.
    Only facts the store listing states; no ratings, because there are none
    to cite yet."""
    app = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "Grasp: Workout Planner",
        "alternateName": "Grasp",
        "description": s["description"],
        "operatingSystem": "Android, iOS",
        "applicationCategory": "HealthApplication",
        "applicationSubCategory": "Fitness",
        "inLanguage": [c for c, *_ in LANGS],
        "url": SITE + path_for(code),
        "downloadUrl": "{stores}",
        "installUrl": "{stores}",
        "image": f"{SITE}/img/screens/{code}/home.webp",
        "screenshot": [f"{SITE}/img/screens/{code}/{n}.webp" for n in ("home", "exercise", "body", "goals")],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": "Grasp", "url": SITE + "/", "email": "grasp@alsouq.tech"},
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": code,
        "mainEntity": [
            {"@type": "Question", "name": s[f"faq{i}_q"],
             "acceptedAnswer": {"@type": "Answer", "text": s[f"faq{i}_a"]}}
            for i in range(1, FAQ_COUNT + 1)
        ],
    }

    def block(data: dict) -> str:
        # </ cannot appear inside a script element; escape it the JSON way.
        text = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
        # Both store links on one line.
        text = text.replace('"{stores}"', json.dumps([STORE, PLAY]))
        return '    <script type="application/ld+json">\n' + text + "\n    </script>"

    return block(app) + "\n" + block(faq)


def sitemap() -> str:
    """Every language's landing page, each listing all of its alternates, plus
    the two English pages the stores link to."""
    alts = "\n".join(
        f'    <xhtml:link rel="alternate" hreflang="{c}" href="{SITE}{path_for(c)}"/>' for c, *_ in LANGS
    ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>'
    urls = "\n".join(
        f"  <url>\n    <loc>{SITE}{path_for(c)}</loc>\n{alts}\n  </url>" for c, *_ in LANGS
    )
    extra = "\n".join(f"  <url>\n    <loc>{SITE}/{p}</loc>\n  </url>" for p in ("support.html", "privacy.html"))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}\n{extra}\n</urlset>\n"
    )


def render(template: str, code: str, rtl: bool, s: dict, keys: set) -> str:
    missing = keys - set(s)
    if missing:
        sys.exit(f"{code}.json is missing: {', '.join(sorted(missing))}")
    esc = {k: html.escape(v, quote=True) for k, v in s.items() if isinstance(v, str)}
    esc["final_meta_html"] = esc["final_meta_html"].replace(
        "{email}", '<a href="mailto:grasp@alsouq.tech">grasp@alsouq.tech</a>'
    )
    # Grasp's speech bubble over the hero breaks where the language file does.
    esc["hero_bubble"] = esc["hero_bubble"].replace("\n", "<br />")
    note = esc.get("footer_note", "")
    alternates = "\n".join(
        f'    <link rel="alternate" hreflang="{c}" href="{SITE}{path_for(c)}" />' for c, *_ in LANGS
    ) + f'\n    <link rel="alternate" hreflang="x-default" href="{SITE}/" />'
    extra = {
        "lang": code,
        "dir": "rtl" if rtl else "ltr",
        "home": path_for(code),
        "canonical": SITE + path_for(code),
        "screens": f"/img/screens/{code}",
        "alternates": alternates,
        "switcher": switcher(code, esc),
        "flag_grid": flag_grid(),
        "kit": kit(s),
        "get": get_block(esc, center=False, lazy=False),
        "get_center": get_block(esc, center=True, lazy=True),
        "footer_note_block": f'        <span class="footer-note">{note}</span>' if note else "",
        "faq_list": faq_list(esc),
        "jsonld": jsonld(code, s),
        "hero_photo": hero_photo(),
        **ICONS,
    }
    # {{gym <photo> <x position>}}: a feature's photo panel.
    out = re.sub(r"\{\{gym (\S+) (\S+)\}\}", lambda m: gym_photo(m.group(1), m.group(2)), template)
    # Chinese and Japanese put no space between words, and the first half of
    # their headlines ends in full-width punctuation already.
    if code in ("zh", "ja"):
        out = out.replace('{{hero_h1_before}} <span class="hl">', '{{hero_h1_before}}<span class="hl">')
    for k, v in {**esc, **extra}.items():
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        left = out[out.index("{{"):out.index("{{") + 40]
        sys.exit(f"{code}: unfilled placeholder near {left!r}")
    return out


def main() -> None:
    with open(os.path.join(HERE, "template.html"), encoding="utf-8-sig") as f:
        template = f.read()
    with open(os.path.join(HERE, "i18n", "en.json"), encoding="utf-8-sig") as f:
        keys = {k for k in json.load(f) if not k.startswith("_")}
    only = sys.argv[1:]
    for code, _, _, rtl in LANGS:
        if only and code not in only:
            continue
        src = os.path.join(HERE, "i18n", f"{code}.json")
        if not os.path.exists(src):
            print(f"skip {code}: no {code}.json yet")
            continue
        with open(src, encoding="utf-8-sig") as f:
            strings = json.load(f)
        page = render(template, code, rtl, strings, keys)
        out = os.path.join(ROOT, "index.html") if code == "en" else os.path.join(ROOT, code, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
        print("wrote", os.path.relpath(out, ROOT))
    if not only:
        with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
            f.write(sitemap())
        print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
