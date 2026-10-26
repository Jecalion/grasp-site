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

LANGS = ['en', 'ar']
TOP = 100
MIN_HUB = 3
HUBS = {}  # set in main(): the muscle pages that exist
LEVELS = ['beginner', 'intermediate', 'advanced']


def ts_map(path):
    """Flat `key: 'value'` pairs from a TS object literal."""
    text = open(path, encoding='utf8').read()
    return {k: v.replace("\\'", "'") for k, v in re.findall(r"^\s+(\w+): '((?:[^'\\]|\\.)*)',", text, re.M)}


def ts_lists(path):
    """`slug: ['step', ...]` blocks from an instructions file."""
    text = open(path, encoding='utf8').read()
    out = {}
    for slug, body in re.findall(r"^  (\w+): \[\n(.*?)\n  \],", text, re.M | re.S):
        out[slug] = [s.replace("\\'", "'") for s in re.findall(r"'((?:[^'\\]|\\.)*)',", body)]
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
NAMES = {'en': {s: e['name'] for s, e in LIB.items()}, 'ar': ts_map(os.path.join(CONTENT, 'names-ar.ts'))}
STEPS = {'en': {s: e['instructions'] for s, e in LIB.items()}, 'ar': ts_lists(os.path.join(CONTENT, 'instructions-ar.ts'))}
EQUIP = {'en': ts_map(os.path.join(APP, 'apps', 'mobile', 'src', 'lib', 'equipment.ts')), 'ar': NAMES['ar']}
MUSCLE = {}
# The muscle labels are the string-table block holding `quads`.
for lang, f in (('en', 'strings.ts'), ('ar', 'ar.ts')):
    text = open(os.path.join(I18N, f), encoding='utf8').read()
    i = text.index("    quads: '")
    block = text[text.rindex('{', 0, i): text.index('\n  },', i)]
    MUSCLE[lang] = dict(re.findall(r"^\s+(\w+): '([^']*)',", block, re.M))
GOALS, UNLOADABLE = engine_goals()

T = {
    'en': {
        'dir': 'ltr', 'home': '/', 'title': 'How to do the {name}: form, muscles, sets and reps',
        'h1': 'How to do the {name}',
        'desc': '{name}: step-by-step form, the muscles it works ({muscles}), sets and reps for your goal, and easier and harder versions.',
        'crumbs': 'Exercises',
        'intro': 'A {level} {mechanic} exercise for the {primary}. You need {equipment}.',
        'intro_bw': 'A {level} {mechanic} exercise for the {primary}. No equipment needed.',
        'level': {'beginner': 'beginner', 'intermediate': 'intermediate', 'advanced': 'advanced'},
        'Level': {'beginner': 'Beginner', 'intermediate': 'Intermediate', 'advanced': 'Advanced'},
        'mechanic': {'compound': 'compound', 'isolation': 'isolation'},
        'and': ' and ', 'or': ' or ', 'list': ', ',
        'how': 'How to do it', 'works': 'Muscles worked', 'primary': 'Main', 'secondary': 'Also',
        'needs': 'Equipment', 'none': 'None', 'lvl': 'Level',
        'dose': 'Sets, reps and rest by goal',
        'dose_p': 'What Grasp prescribes for the {name}. In the app, the weight then goes up when you reach the top of the range on every set.',
        'dose_p_bw': 'What Grasp prescribes for the {name}. It is your body weight, so there is no weight to add: work up through the rep range, then move on to a harder version.',
        'dose_hold': 'Grasp times this one rather than counting reps: hold for the time set in your plan, rest, repeat.',
        'goal': 'Goal', 'sets': 'Sets', 'reps': 'Reps', 'rest': 'Rest',
        'goals': {'hypertrophy': 'Build muscle', 'strength': 'Get stronger', 'fat_loss': 'Lose fat', 'general_fitness': 'General fitness'},
        'easier': 'Easier versions', 'harder': 'Harder versions', 'similar': 'Similar exercises',
        'cta_h': 'Let Grasp put it in your workout',
        'cta_p': 'Grasp builds your session around your goal and the equipment you have, then works out your next weights from what you lifted last time. Free, no ads, works offline.',
        'badge_a': 'Download on the App Store', 'badge_aria_a': 'Download Grasp on the App Store',
        'badge_aria_p': 'Get Grasp on Google Play',
        'video': 'Animation of the {name}',
        'disclaimer': 'General information, not medical advice. Stop if anything hurts, and talk to a doctor before starting a new training program, particularly if you have an injury or a health condition.',
        'hub_title': 'Exercises by muscle: how to do them, sets and reps',
        'hub_h1': 'Exercises by muscle',
        'hub_p': 'How to do each exercise, the muscles it works and the sets and reps for your goal — the same library the Grasp app plans your workouts from.',
        'm_title': '{muscle} exercises: how to do them, sets and reps',
        'm_h1': '{muscle} exercises',
        'm_p': '{n} exercises that work the {muscle_l}, from beginner to advanced. Each page has the steps, the equipment and the sets and reps for your goal.',
        'count': '{n} exercises',
        'rest_fmt': lambda s: f'{s // 60} min' if s % 60 == 0 else f'{s} s',
    },
    'ar': {
        'dir': 'rtl', 'home': '/ar/', 'title': 'طريقة {name}: الأداء والعضلات والمجموعات والتكرارات',
        'h1': 'طريقة أداء {name}',
        'desc': '{name}: الخطوات بالترتيب، والعضلات اللي يشتغل عليها ({muscles})، وكم مجموعة وتكرار حسب هدفك، ونسخ أسهل وأصعب منه.',
        'crumbs': 'التمارين',
        'intro': 'تمرين {mechanic} لمستوى {level}، يستهدف {primary}. تحتاج له {equipment}.',
        'intro_bw': 'تمرين {mechanic} لمستوى {level}، يستهدف {primary}. ما يحتاج أي أدوات.',
        'level': {'beginner': 'مبتدئ', 'intermediate': 'متوسط', 'advanced': 'متقدّم'},
        'Level': {'beginner': 'مبتدئ', 'intermediate': 'متوسط', 'advanced': 'متقدّم'},
        'mechanic': {'compound': 'مركّب', 'isolation': 'عزل'},
        'and': ' و', 'or': ' أو ', 'list': '، ',
        'how': 'طريقة الأداء', 'works': 'العضلات المستهدفة', 'primary': 'الأساسية', 'secondary': 'المساعدة',
        'needs': 'الأدوات', 'none': 'بدون أدوات', 'lvl': 'المستوى',
        'dose': 'المجموعات والتكرارات والراحة حسب هدفك',
        'dose_p': 'هذي الأرقام اللي يعطيك إياها Grasp لتمرين {name}. وفي التطبيق يزيد الوزن لما توصل لأعلى التكرارات في كل المجموعات.',
        'dose_p_bw': 'هذي الأرقام اللي يعطيك إياها Grasp لتمرين {name}. التمرين بوزن جسمك، فما فيه وزن تزيده: زِد التكرارات لين توصل لأعلاها، وبعدها انتقل لنسخة أصعب.',
        'dose_hold': 'هذا التمرين يُحسب بالوقت مو بالتكرارات: اثبت للمدة اللي في خطتك، ارتاح، وكرّر.',
        'goal': 'الهدف', 'sets': 'المجموعات', 'reps': 'التكرارات', 'rest': 'الراحة',
        'goals': {'hypertrophy': 'بناء العضل', 'strength': 'القوة', 'fat_loss': 'حرق الدهون', 'general_fitness': 'لياقة عامة'},
        'easier': 'نسخ أسهل', 'harder': 'نسخ أصعب', 'similar': 'تمارين مشابهة',
        'cta_h': 'خل Grasp يحطه في تمرينك',
        'cta_p': 'Grasp يبني تمرينك على هدفك والأدوات اللي عندك، ويحسب أوزانك الجاية من اللي رفعته آخر مرة. مجاني، بدون إعلانات، ويشتغل بدون نت.',
        'badge_a': 'حمّله من App Store', 'badge_aria_a': 'حمّل Grasp من App Store',
        'badge_aria_p': 'حمّل Grasp من Google Play',
        'video': 'رسم متحرك لتمرين {name}',
        'disclaimer': 'معلومات عامة وليست استشارة طبية. وقّف لو حسيت بألم، واستشر دكتور قبل ما تبدأ برنامج تمارين جديد، خصوصاً لو عندك إصابة أو حالة صحية.',
        'hub_title': 'التمارين حسب العضلة: طريقة الأداء والمجموعات والتكرارات',
        'hub_h1': 'التمارين حسب العضلة',
        'hub_p': 'طريقة أداء كل تمرين، والعضلات اللي يشتغل عليها، وكم مجموعة وتكرار حسب هدفك — نفس مكتبة التمارين اللي يبني منها تطبيق Grasp تمارينك.',
        'm_title': 'تمارين {muscle}: طريقة الأداء والمجموعات والتكرارات',
        'm_h1': 'تمارين {muscle}',
        'm_p': '{n} تمرين لـ{muscle_l}، من المبتدئ إلى المتقدّم. في كل صفحة الخطوات والأدوات وكم مجموعة وتكرار حسب هدفك.',
        'count': '{n} تمرين',
        'rest_fmt': lambda s: {60: 'دقيقة', 120: 'دقيقتين'}.get(s, f'{s // 60} دقائق' if s % 60 == 0 else f'{s} ثانية'),
    },
}

esc = html.escape


def join(items, t):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return t['list'].join(items[:-1]) + t['and'] + items[-1]


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
        parts.append(t['or'].join(names))
    return parts


def shell(lang, url_path, title, desc, body, alternates, ld, og_image=None, og_type='article'):
    t = T[lang]
    head, foot = chrome(lang)
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


def dose_table(e, t, nm):
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
        rows.append(f'            <tr><th scope="row">{t["goals"][goal]}</th><td><bdi dir="ltr">3–4</bdi></td><td><bdi dir="ltr">{lo}–{hi}</bdi></td><td>{t["rest_fmt"](rest)}</td></tr>')
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
        low = lambda x: x if x[1:2].isupper() else x[0].lower() + x[1:]
        art = lambda x: '' if x.endswith('s') else ('an ' if x[0] in 'aeiouAEIOU' else 'a ')
        eq_s = [art(x) + t['or'].join(low(p) for p in x.split(t['or'])) for x in eq]
    intro = (t['intro'] if eq else t['intro_bw']).format(
        level=t['level'][e['difficulty']], mechanic=t['mechanic'][e['mechanic']],
        primary=join([p if lang != 'en' else p.lower() for p in prim], t), equipment=join(eq_s, t))
    if lang == 'en':
        intro = ('An ' if intro[2] in 'aeiou' else 'A ') + intro[2:]
    steps = STEPS[lang].get(slug) or STEPS['en'][slug]
    fam = family(slug)
    h1 = t['h1'].format(name=nm)
    first = next((m for m in prim_keys if m in HUBS), None)

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

{dose_table(e, t, nm)}

{cta(t)}
{groups}

        <p class="meta disclaimer">{t['disclaimer']}</p>'''
    desc = t['desc'].format(name=nm, muscles=join(prim + sec[:2], t))
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
    title = t['m_title'].format(muscle=mn)
    intro = t['m_p'].format(n=len(slugs), muscle_l=mn if lang != 'en' else mn.lower())
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': t['m_h1'].format(muscle=mn), 'inLanguage': lang, 'description': intro},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['crumbs'], 'item': BASE + prefix(lang) + 'exercises/'},
            {'@type': 'ListItem', 'position': 2, 'name': mn, 'item': BASE + mpath(lang, muscle)}]}]}
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{prefix(lang)}exercises/">{t['crumbs']}</a></nav>
        <h1>{esc(t['m_h1'].format(muscle=mn))}</h1>
        <p class="lede">{esc(intro)}</p>
        <ul class="ex-list">
{exercise_list(lang, slugs)}
        </ul>

{cta(t)}'''
    return shell(lang, mpath(lang, muscle), title, intro, body, [(l, mpath(l, muscle)) for l in LANGS], ld,
                 og_type='website')


def hub_page(groups, lang):
    t = T[lang]
    sections = '\n'.join(f'''        <section class="ex-group">
          <h2><a href="{mpath(lang, m)}">{esc(MUSCLE[lang][m])}</a> <span class="lvl">{t['count'].format(n=len(s))}</span></h2>
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
            write(mpath(lang, m), muscle_page(m, s, lang))
        for slug in slugs:
            write(path(lang, slug), exercise_page(slug, lang, built))
    sitemap([[(l, prefix(l) + 'exercises/') for l in LANGS]]
            + [[(l, mpath(l, m)) for l in LANGS] for m in groups]
            + [[(l, path(l, s)) for l in LANGS] for s in slugs])
    print(f'{len(slugs)} exercises, {len(groups)} muscles, {len(LANGS)} languages')


if __name__ == '__main__':
    main(sys.argv[1:])
