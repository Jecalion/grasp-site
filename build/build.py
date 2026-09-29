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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://grasp.alsouq.tech"
STORE = "https://apps.apple.com/app/id6804474068"

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
ANDROID_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" '
    'd="M17.6 9.48l1.84-3.18a.38.38 0 0 0-.66-.38l-1.87 3.23a11.4 11.4 0 0 0-9.82 0L5.22 5.92a.38.38 '
    '0 0 0-.66.38L6.4 9.48A10.8 10.8 0 0 0 1 18h22a10.8 10.8 0 0 0-5.4-8.52zM7 15.25a1.25 1.25 0 1 1 '
    '0-2.5 1.25 1.25 0 0 1 0 2.5zm10 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5z"/></svg>'
)


def path_for(code: str) -> str:
    return "/" if code == "en" else f"/{code}/"


def get_block(s: dict, center: bool, lazy: bool) -> str:
    load = ' loading="lazy"' if lazy else ""
    return (
        f'            <div class="get{" center" if center else ""}">\n'
        f'              <a class="store-badge" href="{STORE}" aria-label="{s["store_aria"]}">'
        f'<img src="/img/app-store-badge.svg" alt="{s["store_alt"]}" width="180" height="60"{load} /></a>\n'
        f'              <span class="soon" aria-label="{s["android_aria"]}">{ANDROID_ICON}'
        f'<span><strong>{s["android"]}</strong><small>{s["coming_soon"]}</small></span></span>\n'
        f"            </div>"
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


def render(template: str, code: str, rtl: bool, s: dict, keys: set) -> str:
    missing = keys - set(s)
    if missing:
        sys.exit(f"{code}.json is missing: {', '.join(sorted(missing))}")
    esc = {k: html.escape(v, quote=True) for k, v in s.items() if isinstance(v, str)}
    esc["final_meta_html"] = esc["final_meta_html"].replace(
        "{email}", '<a href="mailto:grasp@alsouq.tech">grasp@alsouq.tech</a>'
    )
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
    }
    out = template
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
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        template = f.read()
    with open(os.path.join(HERE, "i18n", "en.json"), encoding="utf-8") as f:
        keys = {k for k in json.load(f) if not k.startswith("_")}
    only = sys.argv[1:]
    for code, _, _, rtl in LANGS:
        if only and code not in only:
            continue
        src = os.path.join(HERE, "i18n", f"{code}.json")
        if not os.path.exists(src):
            print(f"skip {code}: no {code}.json yet")
            continue
        with open(src, encoding="utf-8") as f:
            strings = json.load(f)
        page = render(template, code, rtl, strings, keys)
        out = os.path.join(ROOT, "index.html") if code == "en" else os.path.join(ROOT, code, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
        print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
