"""
Home workout plan pages, from plans Grasp's own planner made (build/plans/generate.ts).

    python build/plans.py

One page per setup x days x level, English and Arabic:
    workout-plans/index.html                       all plans, by equipment
    workout-plans/<setup>-<days>-day-<level>/      one plan
The goal (build muscle / lose fat) does not change which exercises the planner
picks, only reps and rest, so both are on one page behind a switch rather than
on two near-identical pages. A plan whose exercises are the same as another
setup's (a pull-up bar a beginner can't use yet) is left out for the same reason.
Exercise names link to the exercise pages.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exercises as X  # noqa: E402

LANGS = ['en', 'ar']
PLANS = json.load(open(X.PLANS, encoding='utf8'))
PUBLISHED = {l.strip() for l in open(X.PUBLISHED, encoding='utf8') if l.strip()}
esc = html.escape

SETUPS = {
    'bodyweight': {'en': 'No-Equipment', 'en_eq': 'no equipment', 'ar': 'بدون أدوات', 'ar_eq': 'بدون أي أدوات'},
    'dumbbells': {'en': 'Dumbbell-Only', 'en_eq': 'a pair of dumbbells', 'ar': 'بالدمبل فقط', 'ar_eq': 'دمبلين بس'},
    'dumbbells-bench': {'en': 'Dumbbell and Bench', 'en_eq': 'dumbbells and a bench', 'ar': 'بالدمبل والبنش', 'ar_eq': 'دمبل وبنش'},
    'dumbbells-pullup-bar': {'en': 'Dumbbell and Pull-Up Bar', 'en_eq': 'dumbbells and a pull-up bar', 'ar': 'بالدمبل وبار العقلة', 'ar_eq': 'دمبل وبار عقلة'},
    'resistance-bands': {'en': 'Resistance Band', 'en_eq': 'resistance bands', 'ar': 'بحبال المقاومة', 'ar_eq': 'حبال مقاومة'},
    'kettlebell': {'en': 'Kettlebell', 'en_eq': 'one kettlebell', 'ar': 'بالكيتل بيل', 'ar_eq': 'كيتل بيل'},
}

S = {
    'en': {
        'crumbs': 'Workout plans',
        'title': '{days}-Day {setup} Home Workout Plan for Beginners',
        'h1': '{days}-Day {setup} Home Workout Plan',
        'level_pl': {'beginner': 'Beginners', 'intermediate': 'Intermediate Lifters'},
        'desc': 'A simple {days}-day home workout plan for beginners with {eq}: every exercise with its sets, reps and rest. Made by Grasp\'s planner.',
        'lede': '{days} days a week at home, about {mins} minutes a session, with {eq}.',
        'made': 'Made by Grasp\'s planner, the one in the app.',
        'k_days': 'Days a week', 'k_time': 'Session', 'k_level': 'Level', 'k_eq': 'Equipment', 'k_split': 'Split',
        'mins': 'about {n} min', 'goal_label': 'Your goal',
        'g_m': 'Build muscle', 'g_f': 'Lose fat',
        'week': 'Your week', 'day': 'Day {n}', 'rest_day': 'Rest',
        'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'same_as': 'Same as Day {n}.',
        'th_ex': 'Exercise', 'th_sets': 'Sets', 'th_reps': 'Reps', 'th_rest': 'Rest',
        'hold': '{r} × {s} s', 'none': '—', 'ab': 'AB',
        'prog_h': 'How to progress',
        'prog': ['Pick a weight you can lift for the bottom of the rep range.',
                 'Reach the top of the range on every set, then go heavier next time.',
                 'Miss the range two sessions in a row? Go a little lighter.'],
        'prog_bw': 'No weight to add? Add reps, then move to a harder version of the exercise.',
        'faq_h': 'Questions',
        'faq': [('Can I swap an exercise?', 'Yes. Pick one that works the same muscles: each exercise page lists similar, easier and harder versions.'),
                ('How heavy should I go?', 'Heavy enough that the last reps of each set are hard but your form holds.'),
                ('Do I need a warm-up?', 'A few minutes of light movement and one lighter set of the first exercise is enough.')],
        'cta_h': 'Let Grasp run this plan for you',
        'cta_p': 'Grasp builds each session and sets your next weights. Free, no ads.',
        'more': 'More home workout plans', 'other_setups': 'Other equipment',
        'hub_title': 'Home Workout Plans: Dumbbells, Bodyweight, Bands and More',
        'hub_h1': 'Home workout plans',
        'hub_p': 'Simple, free plans for beginners training at home. Pick your equipment and how many days a week.',
        'hub_item': '{days} days a week', 'train_on': 'Train on',
        'level': {'beginner': 'Beginner', 'intermediate': 'Intermediate'},
        'used_h': 'Used in these workout plans',
        'wd_short': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'n_ex': '{n} exercises', 'mins_short': '~{n} min',
        'sticky': 'Do this plan in Grasp, free', 'sticky_btn': 'Get the app',
    },
    'ar': {
        'crumbs': 'جداول التمارين',
        'title': 'جدول تمارين في البيت {days} أيام {setup} للمبتدئين',
        'h1': 'جدول تمارين في البيت {days} أيام {setup}',
        'level_pl': {'beginner': 'مبتدئين', 'intermediate': 'متوسطين'},
        'desc': 'جدول تمارين بسيط في البيت {days} أيام {setup} للمبتدئين: كل تمرين بجلساته وتكراراته وراحته. من مخطط Grasp.',
        'lede': '{days} أيام في الأسبوع في البيت، حوالي {mins} دقيقة للتمرين، وتحتاج {eq}.',
        'made': 'من مخطط Grasp نفسه اللي في التطبيق.',
        'k_days': 'أيام الأسبوع', 'k_time': 'مدة التمرين', 'k_level': 'المستوى', 'k_eq': 'الأدوات', 'k_split': 'التقسيم',
        'mins': 'حوالي {n} دقيقة', 'goal_label': 'هدفك',
        'g_m': 'بناء العضل', 'g_f': 'حرق الدهون',
        'week': 'أسبوعك', 'day': 'اليوم {n}', 'rest_day': 'راحة',
        # The Saudi week starts on Sunday, with Friday and Saturday off: the same spacing, shifted.
        'weekdays': ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
        'same_as': 'نفس اليوم {n}.',
        'th_ex': 'التمرين', 'th_sets': 'الجلسات', 'th_reps': 'التكرارات', 'th_rest': 'الراحة',
        'hold': '{r} × {s} ثانية', 'none': '—', 'ab': 'أب',
        'prog_h': 'كيف تتطور',
        'prog': ['ابدأ بوزن تقدر ترفعه لأقل عدد في التكرارات.',
                 'إذا وصلت لأعلى التكرارات في كل الجلسات، زِد الوزن المرة الجاية.',
                 'ما وصلت مرتين ورا بعض؟ خفّف الوزن شوي.'],
        'prog_bw': 'ما فيه وزن تزيده؟ زِد التكرارات، وبعدها انتقل لنسخة أصعب من التمرين.',
        'faq_h': 'أسئلة',
        'faq': [('أقدر أبدّل تمرين؟', 'إيه. اختر تمرين يشتغل على نفس العضلات: في صفحة كل تمرين نسخ مشابهة وأسهل وأصعب.'),
                ('كم الوزن المناسب؟', 'وزن تكون آخر تكرارات كل جلسة فيه صعبة، بس أداءك يبقى صحيح.'),
                ('أحتاج إحماء؟', 'كم دقيقة حركة خفيفة، وجلسة أخف من أول تمرين، تكفي.')],
        'cta_h': 'خل Grasp يمشّي معك الجدول',
        'cta_p': 'Grasp يبني كل تمرين ويحدد أوزانك الجاية. مجاني، بدون إعلانات.',
        'more': 'جداول تمارين ثانية في البيت', 'other_setups': 'أدوات ثانية',
        'hub_title': 'جداول تمارين في البيت: دمبل، بدون أدوات، حبال مقاومة وغيرها',
        'hub_h1': 'جداول تمارين في البيت',
        'hub_p': 'جداول بسيطة ومجانية للمبتدئين في البيت. اختر أدواتك وكم يوم في الأسبوع.',
        'hub_item': '{days} أيام في الأسبوع', 'train_on': 'أيام التمرين',
        'level': {'beginner': 'مبتدئ', 'intermediate': 'متوسط'},
        'used_h': 'موجود في جداول التمارين هذي',
        'wd_short': ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'جمعة', 'سبت'],
        'n_ex': '{n} تمارين', 'mins_short': '~{n} دقيقة',
        'sticky': 'مشّ الجدول في Grasp، مجاناً', 'sticky_btn': 'حمّل التطبيق',
    },
}
WEEKDAY = {3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 4, 5]}


def key(p):
    return f"{p['setup']}-{p['days']}-day"


def ppath(lang, k):
    return X.prefix(lang) + f'workout-plans/{k}/'


def hub(lang):
    return X.prefix(lang) + 'workout-plans/'


def sig(p):
    return tuple(tuple(e['slug'] for e in s['exercises']) for s in p['sessions'])


def select():
    """One plan per setup and days a week; drop copies of another setup."""
    pages, seen = {}, {}
    for p in PLANS:
        k = key(p)
        pages.setdefault(k, {'setup': p['setup'], 'days': p['days'], 'level': p['level'],
                             'equipment': p['equipment'], 'goals': {}})['goals'][p['goal']] = p
    out = {}
    for k, pg in pages.items():
        s = sig(pg['goals']['general_fitness'])
        if s in seen:  # same exercises as a smaller setup: nothing new to say
            continue
        seen[s] = k
        out[k] = pg
    return out


def splits(lang):
    app = os.path.join(X.I18N, 'strings.ts' if lang == 'en' else f'{lang}.ts')
    return X.ts_section(app, 'splits')


def cell_reps(e, s):
    if e['seconds']:
        work = e['work'] or e['seconds']
        return s['hold'].format(r=max(1, round(e['seconds'] / work)), s=work)
    return f"{e['repMin']}–{e['repMax']}"


def num(text, e):
    """A rep range stays left-to-right in Arabic (6–10); a hold reads in the page's own direction."""
    return text if e['seconds'] else f'<bdi dir="ltr">{text}</bdi>'


def rest(lang, sec):
    # The planner shortens rests to fit a 45-minute session (55 s); a printed plan reads better in 15 s steps.
    sec = int(round(sec / 15) * 15) if sec else 0
    return X.rest_text(lang, sec) if sec else S[lang]['none']


def sets_txt(lang, n):
    if lang == 'ar':
        return {1: 'جلسة', 2: 'جلستين'}.get(n, f'{n} جلسات')
    return f'{n} set' if n == 1 else f'{n} sets'


def rounds_txt(lang, n):
    if lang == 'ar':
        return {1: 'جولة', 2: 'جولتين'}.get(n, f'{n} جولات')
    return f'{n} round' if n == 1 else f'{n} rounds'


def dose(lang, e):
    """'3 sets × 6–10 reps · 90 s rest', the way a coach writes it on a card."""
    if e['seconds']:
        work = e['work'] or e['seconds']
        r = max(1, round(e['seconds'] / work))
        unit = f'{work} ثانية' if lang == 'ar' else f'{work} s'
        main = f'{rounds_txt(lang, r)} × {unit}'
    else:
        rng = f'<bdi dir="ltr">{e["repMin"]}–{e["repMax"]}</bdi>'
        main = f'{sets_txt(lang, e["sets"])} × {rng} ' + ('تكرار' if lang == 'ar' else 'reps')
    sec = int(round(e['rest'] / 30) * 30) if e['rest'] else 0  # beginners: 30 s steps (45 s → 1 min, 75 s → 90 s)
    if not sec:
        return main
    r = X.rest_text(lang, sec)
    return f'{main} · ' + (f'راحة {r}' if lang == 'ar' else f'{r} rest')


def thumb(slug):
    """The exercise's animation still; Grasp's own holds have none, so they get the app's drawing of the body."""
    if slug in PUBLISHED:
        return f'<img class="exr-img" src="/img/exercises/{slug}.webp" alt="" width="56" height="56" loading="lazy" />'
    gear = [q['equipment'] for q in X.LIB.get(slug, {}).get('equipment', []) if q.get('required', True)]
    icon = X.eq_icon(next((g for g in gear if g != 'bodyweight_only'), 'bodyweight_only'))
    return f'<span class="exr-img exr-draw">{icon}</span>'


def plan_page(k, pg, pages, lang):
    s, t = S[lang], X.T[lang]
    sp = splits(lang)
    setup = SETUPS[pg['setup']]
    m = pg['goals']['general_fitness']
    mins = round(sum(d['minutes'] for d in m['sessions']) / len(m['sessions']) / 5) * 5
    fmt = dict(days=pg['days'], setup=setup[lang], eq=setup[lang + '_eq'], level_pl=s['level_pl'][pg['level']], mins=mins)
    title, h1 = s['title'].format(**fmt), s['h1'].format(**fmt)

    # Sessions that repeat an earlier one are named A/B and shown once.
    labels, variants = [], {}
    for d in m['sessions']:
        sg = tuple(e['slug'] for e in d['exercises'])
        name = sp.get(d['split'], d['splitName'])
        variants.setdefault(name, [])
        if sg not in variants[name]:
            variants[name].append(sg)
        labels.append((name, variants[name].index(sg), sg))
    multi = {n for n, v in variants.items() if len(v) > 1}

    def label(i):
        n, v, _ = labels[i]
        return f'{n} {s["ab"][v] if v < 2 else v + 1}' if n in multi else n

    first_of, days_html = {}, []
    for i, d in enumerate(m['sessions']):
        sg = labels[i][2]
        head = (f'<div class="day-head"><span class="day-num" aria-hidden="true">{i + 1}</span>'
                f'<div><h3 id="day-{i + 1}">{s["day"].format(n=i + 1)}: {esc(label(i))}</h3>'
                f'<span class="day-min">{s["mins"].format(n=round(d["minutes"] / 5) * 5)} · '
                f'{s["n_ex"].format(n=len(d["exercises"]))}</span></div></div>')
        if sg in first_of:
            days_html.append(f'        <section class="plan-day repeat">{head}'
                             f'<a class="same" href="#day-{first_of[sg] + 1}">{s["same_as"].format(n=first_of[sg] + 1)} ↑</a></section>')
            continue
        first_of[sg] = i
        rows = []
        for n, e in enumerate(d['exercises'], 1):
            nm = esc(X.name(lang, e['slug']))
            name = (f'<a class="exr-name" href="{X.path(lang, e["slug"])}">{nm}</a>' if e['slug'] in PUBLISHED
                    else f'<span class="exr-name">{nm}</span>')
            rows.append(f'<li class="exr">{thumb(e["slug"])}<div class="exr-main">{name}'
                        f'<span class="exr-meta">{dose(lang, e)}</span>'
                        f'</div><span class="exr-n" aria-hidden="true">{n}</span></li>')
        days_html.append(f'        <section class="plan-day">{head}\n          <ol class="exr-list">{"".join(rows)}</ol>\n        </section>')

    bodyweight_only = all(not X.LIB[e['slug']]['loadable'] for d in m['sessions'] for e in d['exercises'] if e['slug'] in X.LIB)
    prog = s['prog'] if not bodyweight_only else s['prog'][1:2] + [s['prog_bw']]
    related = [kk for kk, p in pages.items() if p['setup'] == pg['setup'] and kk != k]
    related += [kk for kk, p in pages.items() if p['setup'] != pg['setup'] and p['days'] == pg['days']]

    def card(kk):
        p = pages[kk]
        icons = ''.join(X.eq_icon(g) for g in (p['equipment'] or ['bodyweight_only']))
        return (f'<li><a href="{ppath(lang, kk)}"><span class="eq-icons">{icons}</span>'
                f'<b>{esc(SETUPS[p["setup"]][lang])}</b>'
                f'<span>{s["hub_item"].format(days=p["days"])}</span></a></li>')

    gear = pg['equipment'] or ['bodyweight_only']
    icons = ''.join(X.eq_icon(g, setup[lang + '_eq'] if j == 0 else '') for j, g in enumerate(gear))
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'ExercisePlan', 'name': h1, 'inLanguage': lang, 'description': s['desc'].format(**fmt),
         'activityFrequency': f"{pg['days']}/week", 'activityDuration': f'PT{mins}M',
         'exerciseType': 'Strength training'},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': s['crumbs'], 'item': X.BASE + hub(lang)},
            {'@type': 'ListItem', 'position': 2, 'name': h1, 'item': X.BASE + ppath(lang, k)}]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                                            for q, a in s['faq']]},
    ]}
    faq = '\n'.join(f'          <details><summary>{q}</summary><p>{a}</p></details>' for q, a in s['faq'])
    steps = ''.join(f'<li><span class="step-n">{n}</span><p>{p}</p></li>' for n, p in enumerate(prog, 1))
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{hub(lang)}">{s['crumbs']}</a></nav>
        <header class="plan-hero">
          <div class="hero-gear">{icons}</div>
          <h1>{esc(h1)}</h1>
          <p class="lede">{esc(s['lede'].format(**fmt))} {s['made']}</p>
          <dl class="hero-stats">
            <div><dt>{s['k_days']}</dt><dd>{pg['days']}</dd></div>
            <div><dt>{s['k_time']}</dt><dd>{s['mins_short'].format(n=mins)}</dd></div>
            <div><dt>{s['k_level']}</dt><dd>{s['level'][pg['level']]}</dd></div>
          </dl>
          <p class="train-on"><span>{s['train_on']}</span> {' · '.join(s['weekdays'][wd] for wd in WEEKDAY[pg['days']])}</p>
        </header>

        <div class="plan">
{chr(10).join(days_html)}
        </div>

        <section class="plan-steps">
          <h2>{s['prog_h']}</h2>
          <ol>{steps}</ol>
        </section>

{X.cta(t, s['cta_h'], s['cta_p'])}

        <section class="plan-faq">
          <h2>{s['faq_h']}</h2>
{faq}
        </section>

        <section class="plan-related">
          <h2>{s['more']}</h2>
          <ul class="rel-cards">{''.join(card(kk) for kk in related)}</ul>
        </section>

        <p class="meta disclaimer">{t['disclaimer']}</p>
'''
    return X.shell(lang, ppath(lang, k), title, s['desc'].format(**fmt), body,
                   [(l, ppath(l, k)) for l in LANGS], ld)


def hub_page(pages, lang):
    s, t = S[lang], X.T[lang]
    groups = []
    for setup in SETUPS:
        items = [(k, p) for k, p in pages.items() if p['setup'] == setup]
        if not items:
            continue
        li = ''.join(f'<li><a href="{ppath(lang, k)}"><b>{p["days"]}</b><small>{s["hub_item"].format(days=p["days"]).replace(str(p["days"]), "", 1).strip()}</small></a></li>'
                     for k, p in sorted(items, key=lambda kp: kp[1]['days']))
        gear = items[0][1]['equipment'] or ['bodyweight_only']
        icons = ''.join(X.eq_icon(g) for g in gear)
        groups.append(f'        <section class="setup-card" id="{setup}"><div class="setup-head"><span class="hero-gear">{icons}</span><h2>{SETUPS[setup][lang]}</h2></div><ul class="plan-tiles">{li}</ul></section>')
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': s['hub_h1'], 'inLanguage': lang,
          'description': s['hub_p']}
    body = f'''        <h1>{s['hub_h1']}</h1>
        <p class="lede">{s['hub_p']}</p>
{chr(10).join(groups)}

{X.cta(t)}'''
    return X.shell(lang, hub(lang), s['hub_title'], s['hub_p'], body, [(l, hub(l)) for l in LANGS], ld, og_type='website')


def used_in_plans(pages, lang):
    """Fill each exercise page's placeholder with the plans that use it: a way in from the exercise."""
    s = S[lang]
    uses = {}
    for k, pg in sorted(pages.items(), key=lambda kp: (kp[1]['level'] != 'beginner', kp[1]['days'], kp[0])):
        for d in pg['goals']['general_fitness']['sessions']:
            for e in d['exercises']:
                if k not in uses.setdefault(e['slug'], []):
                    uses[e['slug']].append(k)
    for slug in PUBLISHED:
        f = os.path.join(X.SITE, X.path(lang, slug).strip('/'), 'index.html')
        if not os.path.exists(f):
            continue
        html_ = open(f, encoding='utf8').read()
        block = ''
        if uses.get(slug):
            li = ''
            for k in uses[slug][:4]:
                p = pages[k]
                name = s['h1'].format(days=p['days'], setup=SETUPS[p['setup']][lang])
                icons = ''.join(X.eq_icon(g) for g in (p['equipment'] or ['bodyweight_only']))
                li += f'<li><a href="{ppath(lang, k)}"><span class="eq-icons">{icons}</span>{esc(name)}</a></li>'
            block = f'        <section class="used-in"><h2>{s["used_h"]}</h2><ul class="plain-links">{li}</ul></section>'
        html_ = re.sub(r'<!-- used-in-plans -->(.*?<!-- /used-in-plans -->)?',
                       lambda m: f'<!-- used-in-plans -->{block}<!-- /used-in-plans -->', html_, count=1, flags=re.S)
        with open(f, 'w', encoding='utf8', newline='\n') as fh:
            fh.write(html_)


def sitemap(pages):
    sm = os.path.join(X.SITE, 'sitemap.xml')
    text = open(sm, encoding='utf8').read()
    text = re.sub(r'\n  <!-- plans:start -->.*<!-- plans:end -->', '', text, flags=re.S)
    entries = []
    for paths in [[(l, hub(l)) for l in LANGS]] + [[(l, ppath(l, k)) for l in LANGS] for k in pages]:
        alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{X.BASE}{p}"/>' for l, p in paths)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{X.BASE}{paths[0][1]}"/>'
        entries += [f'  <url>\n    <loc>{X.BASE}{p}</loc>{alts}\n  </url>' for _, p in paths]
    text = text.replace('\n</urlset>', '\n  <!-- plans:start -->\n' + '\n'.join(entries) + '\n  <!-- plans:end -->\n</urlset>')
    with open(sm, 'w', encoding='utf8', newline='\n') as fh:
        fh.write(text)


if __name__ == '__main__':
    import shutil
    pages = select()
    for lang in LANGS:
        d = os.path.join(X.SITE, X.prefix(lang).strip('/'), 'workout-plans')
        if os.path.isdir(d):
            shutil.rmtree(d)
        X.write(hub(lang), hub_page(pages, lang))
        for k, pg in pages.items():
            X.write(ppath(lang, k), plan_page(k, pg, pages, lang))
    for lang in LANGS:
        used_in_plans(pages, lang)
    sitemap(pages)
    print(f'{len(pages)} plans x {len(LANGS)} languages')
