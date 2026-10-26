"""
Exercise pages: one page per exercise per language, built from the app's own
library and planner settings, so the site and the app never disagree about how
a lift is done or how it is programmed.

    python build/exercises.py              the top TOP exercises by prominence
    python build/exercises.py slug ...     just these

Reads the app repo at ../fitbud (override with FITBUD=...). Writes, per language
(English at the root, others under /<lang>/):

    exercises/index.html                 all published exercises, by muscle
    exercises/muscle/<muscle>/index.html exercises for one muscle
    exercises/<slug>/index.html          the exercise
    img/exercises/<slug>.mp4|.webp       the animation and its poster (shared)

and rewrites the exercise block in sitemap.xml.

What makes a page worth indexing, and so what each one carries beyond the name:
the app's steps, the muscles, the equipment, the sets/reps/rest Grasp's planner
prescribes for it by goal, and easier and harder versions from the same family.
Keep that bar when adding anything: a page that only swaps the name in is the
"scaled content" Google demotes, and it drags the whole site down with it.

Animations are RepDB, licensed for Grasp's own pages: one clip per page, inside
our own layout and text. Hub pages list names only, never a gallery of clips:
the licence forbids anything that works as a browsable catalogue of the assets.
"""
import html
import json
import os
import re
import shutil
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('FITBUD', os.path.join(os.path.dirname(SITE), 'fitbud'))
CONTENT = os.path.join(APP, 'packages', 'content', 'src')
ANIM = os.path.join(APP, 'apps', 'mobile', 'assets', 'exercises', 'animations')
I18N = os.path.join(APP, 'apps', 'mobile', 'src', 'i18n')
ENGINE = os.path.join(APP, 'packages', 'fitness-engine', 'src', 'config', 'index.ts')
BASE = 'https://grasp.alsouq.tech'
APPSTORE = 'https://apps.apple.com/app/id6804474068'
PLAY = 'https://play.google.com/store/apps/details?id=com.graspapp.mobile'

# Same order as the site's language switcher.
ALL_LANGS = ['en', 'ar', 'fr', 'de', 'es', 'it', 'tr', 'pl', 'ru', 'hi', 'zh', 'ko', 'ja', 'id', 'pt']
STRINGS = os.path.join(SITE, 'build', 'exercise-i18n')
# A language goes live when its page strings exist (build/exercise-i18n/<lang>.json).
LANGS = [l for l in ALL_LANGS if os.path.exists(os.path.join(STRINGS, l + '.json'))]
TOP = 100
MIN_HUB = 3
HUBS = {}  # set in main(): the muscle pages that exist
LEVELS = ['beginner', 'intermediate', 'advanced']
STR = r"'((?:[^'\\]|\\.)*)'"


def unq(v):
    return v.replace("\\'", "'")


def ts_map(path):
    """Flat `key: 'value'` pairs from a TS object literal (a value may sit on the next line)."""
    text = open(path, encoding='utf8').read()
    return {k: unq(v) for k, v in re.findall(r"^\s+(\w+):\s*\n?\s*" + STR + ",", text, re.M)}


def ts_section(path, name):
    text = open(path, encoding='utf8').read()
    i = text.index('\n  ' + name + ': {')
    block = text[i: text.index('\n  },', i)]
    return {k: unq(v) for k, v in re.findall(r"^\s+(\w+):\s*\n?\s*" + STR + ",", block, re.M)}


def ts_lists(path):
    """`slug: ['step', ...]` blocks from an instructions file."""
    text = open(path, encoding='utf8').read()
    out = {}
    for slug, body in re.findall(r"^  (\w+): \[\n(.*?)\n  \],", text, re.M | re.S):
        out[slug] = [unq(s) for s in re.findall(STR + ",", body)]
    return out


def engine_goals():
    """Rep ranges and rests per goal, read from the planner's own config."""
    text = open(ENGINE, encoding='utf8').read()
    goals = {}
    for goal in ('strength', 'hypertrophy', 'fat_loss', 'general_fitness'):
        block = re.search(goal + r": \{(.*?)\n    \},", text, re.S).group(1)
        num = lambda k: int(re.search(k + r": (\d+)", block).group(1))
        rng = lambda k: tuple(map(int, re.search(k + r": \{ min: (\d+), max: (\d+) \}", block).groups()))
        goals[goal] = {'compound': (rng('compoundReps'), num('compoundRestSeconds')),
                       'isolation': (rng('isolationReps'), num('isolationRestSeconds'))}
    unl = tuple(map(int, re.search(r"unloadableReps: \{ min: (\d+), max: (\d+) \}", text).groups()))
    return goals, unl


LIB = {e['slug']: e for e in json.load(open(os.path.join(CONTENT, 'generated', 'library.json'), encoding='utf8'))}
REPDB_STEPS = json.load(open(os.path.join(CONTENT, 'generated', 'instructions-repdb.json'), encoding='utf8'))
GOALS, UNLOADABLE = engine_goals()
NAMES, STEPS, EQUIP, MUSCLE, T = {}, {}, {}, {}, {}

for lang in LANGS:
    app = os.path.join(I18N, 'strings.ts' if lang == 'en' else lang + '.ts')
    if lang == 'en':
        NAMES[lang] = {s: e['name'] for s, e in LIB.items()}
        STEPS[lang] = {s: e['instructions'] for s, e in LIB.items()}
        EQUIP[lang] = ts_map(os.path.join(APP, 'apps', 'mobile', 'src', 'lib', 'equipment.ts'))
    else:
        NAMES[lang] = ts_map(os.path.join(CONTENT, f'names-{lang}.ts'))
        STEPS[lang] = REPDB_STEPS[lang] if lang in REPDB_STEPS else ts_lists(os.path.join(CONTENT, f'instructions-{lang}.ts'))
        EQUIP[lang] = NAMES[lang]  # equipment names live in the same file
    text = open(app, encoding='utf8').read()
    i = text.index("    quads: '")
    MUSCLE[lang] = {k: unq(v) for k, v in re.findall(r"^\s+(\w+): " + STR + ",", text[text.rindex('{', 0, i): text.index('\n  },', i)], re.M)}

    # The page's own phrases, then the words the app already uses for the same things.
    t = json.load(open(os.path.join(STRINGS, lang + '.json'), encoding='utf8'))
    ex, goals, summ = ts_section(app, 'exercise'), ts_section(app, 'goals'), ts_section(app, 'summary')
    site = json.load(open(os.path.join(SITE, 'build', 'i18n', lang + '.json'), encoding='utf8'))
    vocab = {
        'how': ex['howTo'], 'primary': ex['primary'], 'secondary': ex['secondary'], 'needs': ex['equipment'],
        'Level': {l: ex[l] for l in LEVELS}, 'mechanic': {m: ex[m] for m in ('compound', 'isolation')},
        'goals': {'hypertrophy': goals['hypertrophyTitle'], 'strength': goals['strengthTitle'],
                  'fat_loss': goals['fatLossTitle'], 'general_fitness': goals['generalTitle']},
        'sets': summ['sets'], 'reps': summ['reps'],
        'badge_a': site['store_alt'], 'badge_aria_a': site['store_aria'], 'badge_aria_p': site['play_aria'],
    }
    for k, v in vocab.items():
        t.setdefault(k, v)
    lower = t.get('lower_muscles', False)
    t.setdefault('level', {l: ((({'İ': 'i', 'I': 'ı'}.get(w[0], w[0].lower()) + w[1:]) if lang == 'tr' else w.lower())
                               if lower else w) for l, w in t['Level'].items()})
    if lower:
        t['mechanic'] = {m: (({'İ': 'i', 'I': 'ı'}.get(w[0], w[0].lower()) + w[1:]) if lang == 'tr' else w.lower())
                         for m, w in t['mechanic'].items()}
    t['dir'] = 'rtl' if lang == 'ar' else 'ltr'
    t['home'] = '/' if lang == 'en' else f'/{lang}/'
    T[lang] = t


def has_mp(lang):
    """Whether this language gets muscle pages (off where the safe phrasing reads stiffly)."""
    return T[lang].get('muscle_pages', True)


def rest_text(lang, s):
    t = T[lang]
    if lang == 'ar' and s in (60, 120):
        return {60: 'دقيقة', 120: 'دقيقتين'}[s]
    return t['min'].format(n=s // 60) if s % 60 == 0 else t['sec'].format(n=s)


def low(lang, word):
    """Mid-sentence form of a label: lower-cased where the language does that (keeps "EZ bar")."""
    if not T[lang].get('lower_muscles') or word[1:2].isupper():
        return word
    if lang == 'tr':  # Turkish dotted/dotless i: İ→i, I→ı (Python's lower() gets İ wrong)
        return {'İ': 'i', 'I': 'ı'}.get(word[0], word[0].lower()) + word[1:]
    return word[0].lower() + word[1:]


esc = html.escape


def join(items, t):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return t['list'].join(items[:-1]) + conj(t['and'], items[-1]) + items[-1]


def conj(word, nxt):
    """Spanish 'y' is 'e' before an i- sound, and 'o' is 'u' before an o- sound."""
    w, n = word.strip(), nxt.lower()
    if w == 'y' and (n.startswith('i') or n.startswith('hi')) and not n.startswith('hie'):
        return word.replace('y', 'e')
    if w == 'o' and (n.startswith('o') or n.startswith('ho')):
        return word.replace('o', 'u')
    return word


def orjoin(parts, t):
    out = parts[0]
    for p in parts[1:]:
        out += conj(t['or'], p) + p
    return out


def prefix(lang):
    return '/' if lang == 'en' else f'/{lang}/'


def path(lang, slug):
    return prefix(lang) + f'exercises/{slug}/'


def mpath(lang, muscle):
    return prefix(lang) + f'exercises/muscle/{muscle}/'


def is_cardio(slug):
    return any(m['pattern'] == 'cardio' for m in LIB[slug]['movements'])


def has_anim(slug):
    return os.path.exists(os.path.join(ANIM, slug + '.mp4'))


def primaries(e):
    return [m['muscle'] for m in e['muscles'] if m['role'] == 'primary']


def name(lang, slug):
    return NAMES[lang].get(slug, NAMES['en'][slug])


def family(slug):
    """Same main muscle and movement pattern, split into easier, same-level and harder."""
    e = LIB[slug]
    prim, pats = set(primaries(e)), {m['pattern'] for m in e['movements']}
    lvl = LEVELS.index(e['difficulty'])
    groups = {'easier': [], 'similar': [], 'harder': []}
    for s, o in LIB.items():
        if s == slug or not o.get('active', True) or not has_anim(s):
            continue
        op, pp = set(primaries(o)), {m['pattern'] for m in o['movements']}
        if not (prim & op and pats & pp) or (not e['loadable'] and o['loadable']):
            continue
        score = (2 * len(prim & op) + len(pats & pp), o.get('prominence', 0))
        d = LEVELS.index(o['difficulty'])
        groups['easier' if d < lvl else 'harder' if d > lvl else 'similar'].append((score, s))
    return {k: [s for _, s in sorted(v, reverse=True)[:4]] for k, v in groups.items()}


def chrome(lang):
    """Header and footer lifted from the language's home page, so pages stay in step with it."""
    page = open(os.path.join(SITE, 'index.html' if lang == 'en' else f'{lang}/index.html'), encoding='utf8').read()
    head = page[page.index('    <header class="site">'): page.index('</header>') + len('</header>')]
    foot = page[page.index('    <footer class="site">'): page.index('</footer>') + len('</footer>')]
    head = head.replace('href="#', f'href="{T[lang]["home"]}#')
    return head, foot


def equipment_text(e, t, lang):
    parts = []
    for q in e['equipment']:
        if not q.get('required', True) or q['equipment'] == 'bodyweight_only':
            continue
        names = [EQUIP[lang].get(q['equipment'], q['equipment'].replace('_', ' '))]
        names += [EQUIP[lang].get(a, a.replace('_', ' ')) for a in q.get('alternatives', [])]
        parts.append(orjoin(names, t))
    return parts


def shell(lang, url_path, title, desc, body, alternates, ld, og_image=None, og_type='article'):
    t = T[lang]
    head, foot = chrome(lang)
    # The language menu goes to this same page in the other language, not to that language's home page.
    for l, p in alternates:
        head = head.replace(f'href="{prefix(l)}" hreflang="{l}"', f'href="{p}" hreflang="{l}"')
    url = BASE + url_path
    alts = '\n'.join(f'    <link rel="alternate" hreflang="{l}" href="{BASE}{p}" />' for l, p in alternates)
    img = f'\n    <meta property="og:image" content="{og_image}" />' if og_image else ''
    return f'''<!doctype html>
<!-- GENERATED by build/exercises.py from the app's exercise library. Edit the script, not this file. -->
<html lang="{lang}" dir="{t['dir']}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)} | Grasp</title>
    <meta name="description" content="{esc(desc)}" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(desc)}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:url" content="{url}" />{img}
    <link rel="canonical" href="{url}" />
{alts}
    <link rel="alternate" hreflang="x-default" href="{BASE}{alternates[0][1]}" />
    <link rel="icon" href="/favicon.png" />
    <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
    </script>
    <link rel="stylesheet" href="/style.css" />
    <link rel="stylesheet" href="/exercise.css" />
    <script src="/theme.js"></script>
    <script src="/lang.js" defer></script>
    <script src="/hit.js" defer></script>
  </head>
  <body class="exercise">
{head}

    <main>
      <article class="wrap ex">
{body}
      </article>
    </main>

{foot}
  </body>
</html>
'''


def cta(t):
    return f'''        <section class="ex-cta">
          <h2>{t['cta_h']}</h2>
          <p>{t['cta_p']}</p>
          <div class="stores">
            <a class="store-badge" href="{APPSTORE}" aria-label="{t['badge_aria_a']}"><img src="/img/app-store-badge.svg" alt="{t['badge_a']}" width="180" height="60" loading="lazy" /></a>
            <a class="store-badge play" href="{PLAY}" aria-label="{t['badge_aria_p']}"><img src="/img/google-play-badge.png" alt="Get it on Google Play" width="231" height="89" loading="lazy" /></a>
          </div>
        </section>'''


def links(lang, slugs, built):
    return '\n'.join(
        f'            <li><a href="{path(lang, s)}">{esc(name(lang, s))}</a></li>' if s in built
        else f'            <li>{esc(name(lang, s))}</li>' for s in slugs)


def dose_table(e, t, nm, lang):
    if e['tracking'] == 'duration':
        return f'''        <section class="ex-dose">
          <h2>{t['dose']}</h2>
          <p>{t['dose_hold']}</p>
        </section>'''
    rows = []
    for goal in ('hypertrophy', 'strength', 'fat_loss', 'general_fitness'):
        (lo, hi), rest = GOALS[goal][e['mechanic']]
        if not e['loadable']:
            lo, hi = UNLOADABLE
        rows.append(f'            <tr><th scope="row">{t["goals"][goal]}</th><td><bdi dir="ltr">3–4</bdi></td><td><bdi dir="ltr">{lo}–{hi}</bdi></td><td>{rest_text(lang, rest)}</td></tr>')
    return f'''        <section class="ex-dose">
          <h2>{t['dose']}</h2>
          <p>{esc(t['dose_p' if e['loadable'] else 'dose_p_bw'].format(name=nm))}</p>
          <table>
            <thead><tr><th scope="col">{t['goal']}</th><th scope="col">{t['sets']}</th><th scope="col">{t['reps']}</th><th scope="col">{t['rest']}</th></tr></thead>
            <tbody>
{chr(10).join(rows)}
            </tbody>
          </table>
        </section>'''


def exercise_page(slug, lang, built):
    e, t = LIB[slug], T[lang]
    nm = name(lang, slug)
    prim_keys = primaries(e)
    prim = [MUSCLE[lang][m] for m in prim_keys]
    sec = [MUSCLE[lang][m['muscle']] for m in e['muscles'] if m['role'] != 'primary']
    eq = equipment_text(e, t, lang)
    eq_s = eq
    if lang == 'en':
        # Mid-sentence: "a barbell and a squat rack or power rack", but "an EZ bar" keeps its capitals.
        art = lambda x: '' if x.endswith('s') else ('an ' if x[0] in 'aeiouAEIOU' else 'a ')
        eq_s = [art(x) + t['or'].join(low(lang, p) for p in x.split(t['or'])) for x in eq]
    intro = (t['intro'] if eq else t['intro_bw']).format(
        level=t['level'][e['difficulty']], mechanic=t['mechanic'][e['mechanic']],
        primary=join([low(lang, p) for p in prim], t), equipment=join(eq_s, t))
    if lang == 'en':
        intro = ('An ' if intro[2] in 'aeiou' else 'A ') + intro[2:]
    steps = STEPS[lang].get(slug) or STEPS['en'][slug]
    fam = family(slug)
    h1 = t['h1'].format(name=nm)
    first = next((m for m in prim_keys if m in HUBS), None) if has_mp(lang) else None

    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'HowTo', 'name': h1, 'description': intro, 'inLanguage': lang,
         'image': f'{BASE}/img/exercises/{slug}.webp',
         'tool': [{'@type': 'HowToTool', 'name': x} for x in eq],
         'step': [{'@type': 'HowToStep', 'position': i + 1, 'text': s} for i, s in enumerate(steps)]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['crumbs'], 'item': BASE + prefix(lang) + 'exercises/'},
        ] + ([{'@type': 'ListItem', 'position': 2, 'name': MUSCLE[lang][first], 'item': BASE + mpath(lang, first)}] if first else [])
          + [{'@type': 'ListItem', 'position': 3 if first else 2, 'name': nm, 'item': BASE + path(lang, slug)}]},
    ]}
    groups = ''.join(f'''
        <section class="ex-similar">
          <h2>{t[k]}</h2>
          <ul>
{links(lang, fam[k], built)}
          </ul>
        </section>''' for k in ('easier', 'harder', 'similar') if fam[k])
    crumb_m = f' <span aria-hidden="true">›</span> <a href="{mpath(lang, first)}">{esc(MUSCLE[lang][first])}</a>' if first else ''
    sec_row = f"<dt>{t['secondary']}</dt><dd>{esc(join(sec, t))}</dd>" if sec else ''
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{prefix(lang)}exercises/">{t['crumbs']}</a>{crumb_m}</nav>
        <h1>{esc(h1)}</h1>
        <p class="lede">{esc(intro)}</p>

        <figure class="ex-demo">
          <video autoplay muted loop playsinline preload="metadata" poster="/img/exercises/{slug}.webp" aria-label="{esc(t['video'].format(name=nm))}" width="1056" height="480">
            <source src="/img/exercises/{slug}.mp4" type="video/mp4" />
          </video>
        </figure>

        <div class="ex-grid">
          <section>
            <h2>{t['how']}</h2>
            <ol class="ex-steps">
{chr(10).join(f'              <li>{esc(s)}</li>' for s in steps)}
            </ol>
          </section>
          <aside class="ex-facts">
            <h2>{t['works']}</h2>
            <dl>
              <dt>{t['primary']}</dt><dd>{esc(join(prim, t))}</dd>
              {sec_row}
              <dt>{t['needs']}</dt><dd>{esc(t['list'].join(eq)) if eq else t['none']}</dd>
              <dt>{t['lvl']}</dt><dd>{t['Level'][e['difficulty']]}</dd>
            </dl>
          </aside>
        </div>

{dose_table(e, t, nm, lang)}

{cta(t)}
{groups}

        <p class="meta disclaimer">{t['disclaimer']}</p>'''
    desc = t['desc'].format(name=nm, muscles=join([low(lang, m) for m in prim + sec[:2]], t))
    return shell(lang, path(lang, slug), t['title'].format(name=nm), desc, body,
                 [(l, path(l, slug)) for l in LANGS], ld, f'{BASE}/img/exercises/{slug}.webp')


def by_muscle(built):
    out = {}
    for s in built:
        for m in primaries(LIB[s]):
            out.setdefault(m, []).append(s)
    order = list(MUSCLE['en'])  # the app's own order: chest, shoulders, arms, back, core, legs
    # A muscle page with one or two exercises on it is the thin page we are avoiding.
    return {m: sorted(out[m], key=lambda s: (LEVELS.index(LIB[s]['difficulty']), -LIB[s].get('prominence', 0)))
            for m in order if len(out.get(m, [])) >= MIN_HUB}


def exercise_list(lang, slugs):
    t = T[lang]
    return '\n'.join(
        f'            <li><a href="{path(lang, s)}">{esc(name(lang, s))}</a> <span class="lvl">{t["Level"][LIB[s]["difficulty"]]}</span></li>'
        for s in slugs)


def muscle_page(muscle, slugs, lang):
    t = T[lang]
    mn = MUSCLE[lang][muscle]
    # Mid-sentence the muscle takes the language's lower case ("Ejercicios de pecho"); first word keeps its capital.
    mfmt = lambda key: t[key].format(muscle=mn if t[key].startswith('{muscle}') else low(lang, mn))
    title = mfmt('m_title')
    intro = t['m_p'].format(n=len(slugs), muscle=low(lang, mn), muscle_l=low(lang, mn))
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': mfmt('m_h1'), 'inLanguage': lang, 'description': intro},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['crumbs'], 'item': BASE + prefix(lang) + 'exercises/'},
            {'@type': 'ListItem', 'position': 2, 'name': mn, 'item': BASE + mpath(lang, muscle)}]}]}
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{prefix(lang)}exercises/">{t['crumbs']}</a></nav>
        <h1>{esc(mfmt('m_h1'))}</h1>
        <p class="lede">{esc(intro)}</p>
        <ul class="ex-list">
{exercise_list(lang, slugs)}
        </ul>

{cta(t)}'''
    return shell(lang, mpath(lang, muscle), title, intro, body, [(l, mpath(l, muscle)) for l in LANGS if has_mp(l)], ld,
                 og_type='website')


def hub_page(groups, lang):
    t = T[lang]
    sections = '\n'.join(f'''        <section class="ex-group">
          <h2>{f'<a href="{mpath(lang, m)}">{esc(MUSCLE[lang][m])}</a>' if has_mp(lang) else esc(MUSCLE[lang][m])} <span class="lvl">{t['count'].format(n=len(s))}</span></h2>
          <ul class="ex-list">
{exercise_list(lang, s[:8])}
          </ul>
        </section>''' for m, s in groups.items())
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': t['hub_h1'], 'inLanguage': lang,
          'description': t['hub_p']}
    body = f'''        <h1>{t['hub_h1']}</h1>
        <p class="lede">{t['hub_p']}</p>
{sections}

{cta(t)}'''
    hub = prefix(lang) + 'exercises/'
    return shell(lang, hub, t['hub_title'], t['hub_p'], body,
                 [(l, prefix(l) + 'exercises/') for l in LANGS], ld, og_type='website')


def write(rel, text):
    out = os.path.join(SITE, rel.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # Many Arabic names already start with "تمرين" (push-up = تمرين الضغط); don't say it twice.
    text = text.replace('تمرين تمرين', 'تمرين')
    with open(out, 'w', encoding='utf8', newline='\n') as f:
        f.write(text)


def sitemap(paths):
    """Replace the exercise block of sitemap.xml, leaving the hand-written entries alone."""
    sm = os.path.join(SITE, 'sitemap.xml')
    text = open(sm, encoding='utf8').read()
    text = re.sub(r'\n  <!-- exercises:start -->.*<!-- exercises:end -->', '', text, flags=re.S)
    entries = []
    for alts in paths:
        links_ = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{p}"/>' for l, p in alts)
        links_ += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{alts[0][1]}"/>'
        for _, p in alts:
            entries.append(f'  <url>\n    <loc>{BASE}{p}</loc>{links_}\n  </url>')
    block = '\n  <!-- exercises:start -->\n' + '\n'.join(entries) + '\n  <!-- exercises:end -->'
    text = text.replace('\n</urlset>', block + '\n</urlset>')
    with open(sm, 'w', encoding='utf8', newline='\n') as f:
        f.write(text)


def main(slugs):
    if not slugs:
        pool = [s for s, e in LIB.items() if e.get('active', True) and has_anim(s) and not is_cardio(s)]
        slugs = sorted(pool, key=lambda s: -LIB[s].get('prominence', 0))[:TOP]
    built = set(slugs)
    os.makedirs(os.path.join(SITE, 'img', 'exercises'), exist_ok=True)
    for f in os.listdir(os.path.join(SITE, 'img', 'exercises')):
        if f.rsplit('.', 1)[0] not in built:  # never leave clips online that no page shows
            os.remove(os.path.join(SITE, 'img', 'exercises', f))
    for slug in slugs:
        for ext in ('mp4', 'webp'):
            shutil.copyfile(os.path.join(ANIM, f'{slug}.{ext}'), os.path.join(SITE, 'img', 'exercises', f'{slug}.{ext}'))
    groups = by_muscle(built)
    HUBS.clear()
    HUBS.update(groups)
    for lang in LANGS:
        base = os.path.join(SITE, prefix(lang).strip('/'), 'exercises')
        if os.path.isdir(base):
            shutil.rmtree(base)
        write(prefix(lang) + 'exercises/', hub_page(groups, lang))
        for m, s in groups.items():
            if has_mp(lang):
                write(mpath(lang, m), muscle_page(m, s, lang))
        for slug in slugs:
            write(path(lang, slug), exercise_page(slug, lang, built))
    sitemap([[(l, prefix(l) + 'exercises/') for l in LANGS]]
            + [[(l, mpath(l, m)) for l in LANGS if has_mp(l)] for m in groups]
            + [[(l, path(l, s)) for l in LANGS] for s in slugs])
    print(f'{len(slugs)} exercises, {len(groups)} muscles, {len(LANGS)} languages')


if __name__ == '__main__':
    main(sys.argv[1:])
