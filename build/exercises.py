"""
Exercise pages: one page per exercise per language, built from the app's own
library so the site and the app never disagree about how a lift is done.

    python build/exercises.py [slug ...]

With no slugs it builds every exercise that has an animation. Reads the app
repo at ../fitbud (override with FITBUD=...). Writes:

    exercises/<slug>/index.html          English
    <lang>/exercises/<slug>/index.html   other languages
    img/exercises/<slug>.mp4|.webp       the animation and its poster

Animations are RepDB, licensed for Grasp's own pages: one clip per page, inside
our own layout and text, never a bulk download. Keep it that way.
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
BASE = 'https://grasp.alsouq.tech'
APPSTORE = 'https://apps.apple.com/app/id6804474068'
PLAY = 'https://play.google.com/store/apps/details?id=com.graspapp.mobile'

LANGS = ['en', 'ar']


def ts_map(path, start=None):
    """Flat `key: 'value'` pairs from a TS object literal (optionally only the block after `start`)."""
    text = open(path, encoding='utf8').read()
    if start:
        text = text[text.index(start):]
        text = text[: text.index('\n  },')]
    return {k: v.replace("\\'", "'") for k, v in re.findall(r"^\s+(\w+): '((?:[^'\\]|\\.)*)',", text, re.M)}


def ts_lists(path):
    """`slug: ['step', ...]` blocks from an instructions file."""
    text = open(path, encoding='utf8').read()
    out = {}
    for slug, body in re.findall(r"^  (\w+): \[\n(.*?)\n  \],", text, re.M | re.S):
        out[slug] = [s.replace("\\'", "'") for s in re.findall(r"'((?:[^'\\]|\\.)*)',", body)]
    return out


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

T = {
    'en': {
        'dir': 'ltr', 'home': '/', 'title': 'How to do the {name}: steps, muscles, equipment',
        'h1': 'How to do the {name}',
        'desc': '{name}: step-by-step form, the muscles it works ({muscles}) and the equipment you need. Free in the Grasp workout app.',
        'crumbs': 'Exercises',
        'intro': 'A {level} {mechanic} exercise for the {primary}. You need {equipment}.',
        'intro_bw': 'A {level} {mechanic} exercise for the {primary}. No equipment needed.',
        'level': {'beginner': 'beginner', 'intermediate': 'intermediate', 'advanced': 'advanced'},
        'mechanic': {'compound': 'compound', 'isolation': 'isolation'},
        'and': ' and ', 'or': ' or ', 'list': ', ',
        'how': 'How to do it', 'works': 'Muscles worked', 'primary': 'Main', 'secondary': 'Also',
        'needs': 'Equipment', 'none': 'None', 'similar': 'Similar exercises',
        'cta_h': 'Let Grasp put it in your workout',
        'cta_p': 'Grasp builds your session around your goal and the equipment you have, then works out your next weights from what you lifted last time. Free, no ads, works offline.',
        'badge_a': 'Download on the App Store', 'badge_aria_a': 'Download Grasp on the App Store',
        'badge_aria_p': 'Get Grasp on Google Play',
        'video': 'Animation of the {name}',
        'disclaimer': 'General information, not medical advice. Stop if anything hurts, and talk to a doctor before starting a new training program, particularly if you have an injury or a health condition.',
    },
    'ar': {
        'dir': 'rtl', 'home': '/ar/', 'title': 'طريقة {name}: الخطوات والعضلات والأدوات',
        'h1': 'طريقة أداء {name}',
        'desc': '{name}: الخطوات بالترتيب، والعضلات اللي يشتغل عليها ({muscles})، والأدوات اللي تحتاجها. مجاناً في تطبيق Grasp.',
        'crumbs': 'التمارين',
        'intro': 'تمرين {mechanic} لمستوى {level}، يستهدف {primary}. تحتاج له {equipment}.',
        'intro_bw': 'تمرين {mechanic} لمستوى {level}، يستهدف {primary}. ما يحتاج أي أدوات.',
        'level': {'beginner': 'مبتدئ', 'intermediate': 'متوسط', 'advanced': 'متقدّم'},
        'mechanic': {'compound': 'مركّب', 'isolation': 'عزل'},
        'and': ' و', 'or': ' أو ', 'list': '، ',
        'how': 'طريقة الأداء', 'works': 'العضلات المستهدفة', 'primary': 'الأساسية', 'secondary': 'المساعدة',
        'needs': 'الأدوات', 'none': 'بدون أدوات', 'similar': 'تمارين مشابهة',
        'cta_h': 'خل Grasp يحطه في تمرينك',
        'cta_p': 'Grasp يبني تمرينك على هدفك والأدوات اللي عندك، ويحسب أوزانك الجاية من اللي رفعته آخر مرة. مجاني، بدون إعلانات، ويشتغل بدون نت.',
        'badge_a': 'حمّله من App Store', 'badge_aria_a': 'حمّل Grasp من App Store',
        'badge_aria_p': 'حمّل Grasp من Google Play',
        'video': 'رسم متحرك لتمرين {name}',
        'disclaimer': 'معلومات عامة وليست استشارة طبية. وقّف لو حسيت بألم، واستشر دكتور قبل ما تبدأ برنامج تمارين جديد، خصوصاً لو عندك إصابة أو حالة صحية.',
    },
}


def join(items, t):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return t['list'].join(items[:-1]) + t['and'] + items[-1]


def path(lang, slug):
    return ('/' if lang == 'en' else f'/{lang}/') + f'exercises/{slug}/'


def similar(slug, n=5):
    """Same main muscle and movement pattern, most common first."""
    e = LIB[slug]
    prim = {m['muscle'] for m in e['muscles'] if m['role'] == 'primary'}
    pats = {m['pattern'] for m in e['movements']}
    scored = []
    for s, o in LIB.items():
        if s == slug or not o.get('active', True) or not has_anim(s):
            continue
        op = {m['muscle'] for m in o['muscles'] if m['role'] == 'primary'}
        pp = {m['pattern'] for m in o['movements']}
        score = 2 * len(prim & op) + len(pats & pp)
        if prim & op and pats & pp:
            scored.append((score, o.get('prominence', 0), s))
    scored.sort(reverse=True)
    return [s for _, _, s in scored[:n]]


def has_anim(slug):
    return os.path.exists(os.path.join(ANIM, slug + '.mp4'))


def chrome(lang):
    """Header and footer lifted from the language's home page, so pages stay in step with it."""
    page = open(os.path.join(SITE, 'index.html' if lang == 'en' else f'{lang}/index.html'), encoding='utf8').read()
    head = page[page.index('    <header class="site">'): page.index('</header>') + len('</header>')]
    foot = page[page.index('    <footer class="site">'): page.index('</footer>') + len('</footer>')]
    home = T[lang]['home']
    head = head.replace('href="#', f'href="{home}#')
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


def page(slug, lang, built):
    e, t = LIB[slug], T[lang]
    name = NAMES[lang].get(slug, NAMES['en'][slug])
    prim = [MUSCLE[lang][m['muscle']] for m in e['muscles'] if m['role'] == 'primary']
    sec = [MUSCLE[lang][m['muscle']] for m in e['muscles'] if m['role'] != 'primary']
    eq = equipment_text(e, t, lang)
    eq_lower = eq
    if lang == 'en':
        # Mid-sentence: "a barbell and a squat rack or power rack", but "an EZ bar" keeps its capitals.
        low = lambda x: x if x[1:2].isupper() else x[0].lower() + x[1:]
        art = lambda x: '' if x.endswith('s') else ('an ' if x[0] in 'aeiouAEIOU' else 'a ')
        eq_lower = [art(x) + t['or'].join(low(p) for p in x.split(t['or'])) for x in eq]
    intro = (t['intro'] if eq else t['intro_bw']).format(
        level=t['level'][e['difficulty']], mechanic=t['mechanic'][e['mechanic']],
        primary=join([p if lang != 'en' else p.lower() for p in prim], t), equipment=join(eq_lower, t))
    if lang == 'en':
        intro = ('An ' if intro[2] in 'aeiou' else 'A ') + intro[2:]
    steps = STEPS[lang].get(slug) or STEPS['en'][slug]
    sims = [s for s in similar(slug)]
    url = BASE + path(lang, slug)
    title = t['title'].format(name=name)
    desc = t['desc'].format(name=name, muscles=join(prim + sec[:2], t))
    head, foot = chrome(lang)
    esc = html.escape

    alts = '\n'.join(f'    <link rel="alternate" hreflang="{l}" href="{BASE}{path(l, slug)}" />' for l in LANGS)
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'HowTo', 'name': t['h1'].format(name=name), 'description': intro, 'inLanguage': lang,
             'image': f'{BASE}/img/exercises/{slug}.webp',
             'tool': [{'@type': 'HowToTool', 'name': x} for x in eq],
             'step': [{'@type': 'HowToStep', 'position': i + 1, 'text': s} for i, s in enumerate(steps)]},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Grasp', 'item': BASE + t['home']},
                {'@type': 'ListItem', 'position': 2, 'name': name, 'item': url}]},
        ],
    }
    sim_items = '\n'.join(
        f'            <li><a href="{path(lang, s)}">{esc(NAMES[lang].get(s, NAMES["en"][s]))}</a></li>' if s in built
        else f'            <li>{esc(NAMES[lang].get(s, NAMES["en"][s]))}</li>' for s in sims)
    step_items = '\n'.join(f'          <li>{esc(s)}</li>' for s in steps)

    return f'''<!doctype html>
<!-- GENERATED by build/exercises.py from the app's exercise library. Edit the script, not this file. -->
<html lang="{lang}" dir="{t['dir']}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)} | Grasp</title>
    <meta name="description" content="{esc(desc)}" />
    <meta property="og:title" content="{esc(t['h1'].format(name=name))}" />
    <meta property="og:description" content="{esc(desc)}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{BASE}/img/exercises/{slug}.webp" />
    <link rel="canonical" href="{url}" />
{alts}
    <link rel="alternate" hreflang="x-default" href="{BASE}{path('en', slug)}" />
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
        <nav class="crumbs" aria-label="breadcrumb"><a href="{t['home']}">Grasp</a> <span aria-hidden="true">›</span> <span>{t['crumbs']}</span></nav>
        <h1>{esc(t['h1'].format(name=name))}</h1>
        <p class="lede">{esc(intro)}</p>

        <figure class="ex-demo">
          <video autoplay muted loop playsinline preload="metadata" poster="/img/exercises/{slug}.webp" aria-label="{esc(t['video'].format(name=name))}" width="1056" height="480">
            <source src="/img/exercises/{slug}.mp4" type="video/mp4" />
          </video>
        </figure>

        <div class="ex-grid">
          <section>
            <h2>{t['how']}</h2>
            <ol class="ex-steps">
{step_items}
            </ol>
          </section>
          <aside class="ex-facts">
            <h2>{t['works']}</h2>
            <dl>
              <dt>{t['primary']}</dt><dd>{esc(join(prim, t))}</dd>
              {f"<dt>{t['secondary']}</dt><dd>{esc(join(sec, t))}</dd>" if sec else ''}
              <dt>{t['needs']}</dt><dd>{esc(t['list'].join(eq)) if eq else t['none']}</dd>
            </dl>
          </aside>
        </div>

        <section class="ex-cta">
          <h2>{t['cta_h']}</h2>
          <p>{t['cta_p']}</p>
          <div class="stores">
            <a class="store-badge" href="{APPSTORE}" aria-label="{t['badge_aria_a']}"><img src="/img/app-store-badge.svg" alt="{t['badge_a']}" width="180" height="60" /></a>
            <a class="store-badge play" href="{PLAY}" aria-label="{t['badge_aria_p']}"><img src="/img/google-play-badge.png" alt="Get it on Google Play" width="231" height="89" /></a>
          </div>
        </section>

        {f"""<section class="ex-similar">
          <h2>{t['similar']}</h2>
          <ul>
{sim_items}
          </ul>
        </section>""" if sims else ''}

        <p class="meta disclaimer">{t['disclaimer']}</p>
      </article>
    </main>

{foot}
  </body>
</html>
'''


def main(slugs):
    if not slugs:
        slugs = [s for s, e in LIB.items() if e.get('active', True) and has_anim(s)]
    built = set(slugs)
    os.makedirs(os.path.join(SITE, 'img', 'exercises'), exist_ok=True)
    for slug in slugs:
        for ext in ('mp4', 'webp'):
            shutil.copyfile(os.path.join(ANIM, f'{slug}.{ext}'), os.path.join(SITE, 'img', 'exercises', f'{slug}.{ext}'))
        for lang in LANGS:
            out = os.path.join(SITE, path(lang, slug).strip('/'), 'index.html')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w', encoding='utf8', newline='\n') as f:
                f.write(page(slug, lang, built))
    print(f'{len(slugs)} exercises x {len(LANGS)} languages')


if __name__ == '__main__':
    main(sys.argv[1:])
