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
        'title': '{days}-Day {setup} Home Workout Plan for {level_pl}',
        'h1': '{days}-Day {setup} Workout Plan for {level_pl}',
        'level_pl': {'beginner': 'Beginners', 'intermediate': 'Intermediate Lifters'},
        'desc': 'A {days}-day home workout plan with {eq}: every exercise, sets, reps and rest, for building muscle or losing fat. Made by Grasp\'s planner.',
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
        'hub_p': 'Free plans for training at home, by equipment and days a week. Each one is made by Grasp\'s planner.',
        'hub_item': '{days} days · {level}',
        'level': {'beginner': 'Beginner', 'intermediate': 'Intermediate'},
    },
    'ar': {
        'crumbs': 'جداول التمارين',
        'title': 'جدول تمارين في البيت {days} أيام {setup} لل{level_pl}',
        'h1': 'جدول تمارين {days} أيام {setup} لل{level_pl}',
        'level_pl': {'beginner': 'مبتدئين', 'intermediate': 'متوسطين'},
        'desc': 'جدول تمارين في البيت {days} أيام {setup}: كل تمرين بجلساته وتكراراته وراحته، لبناء العضل أو حرق الدهون. من مخطط Grasp.',
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
        'hub_p': 'جداول مجانية للتمرين في البيت حسب الأدوات وعدد الأيام. كلها من مخطط Grasp.',
        'hub_item': '{days} أيام · {level}',
        'level': {'beginner': 'مبتدئ', 'intermediate': 'متوسط'},
    },
}
WEEKDAY = {3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 4, 5]}


def key(p):
    return f"{p['setup']}-{p['days']}-day-{p['level']}"


def ppath(lang, k):
    return X.prefix(lang) + f'workout-plans/{k}/'


def hub(lang):
    return X.prefix(lang) + 'workout-plans/'


def sig(p):
    return tuple(tuple(e['slug'] for e in s['exercises']) for s in p['sessions'])


def select():
    """One plan per setup/days/level, with both goals; drop copies of another setup."""
    pages, seen = {}, {}
    for p in PLANS:
        k = key(p)
        pages.setdefault(k, {'setup': p['setup'], 'days': p['days'], 'level': p['level'],
                             'equipment': p['equipment'], 'goals': {}})['goals'][p['goal']] = p
    out = {}
    for k, pg in pages.items():
        s = sig(pg['goals']['hypertrophy'])
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


def plan_page(k, pg, pages, lang):
    s, t = S[lang], X.T[lang]
    sp = splits(lang)
    setup = SETUPS[pg['setup']]
    m, f = pg['goals']['hypertrophy'], pg['goals']['fat_loss']
    mins = round(sum(d['minutes'] for d in m['sessions']) / len(m['sessions']) / 5) * 5
    fmt = dict(days=pg['days'], setup=setup[lang], eq=setup[lang + '_eq'], level_pl=s['level_pl'][pg['level']], mins=mins)
    title, h1 = s['title'].format(**fmt), s['h1'].format(**fmt)
    split_names = []
    for d in m['sessions']:
        n = sp.get(d['split'], d['splitName'])
        if n not in split_names:
            split_names.append(n)

    # Sessions that repeat an earlier one are named A/B and not printed twice.
    first_of, labels = {}, []
    variants = {}
    for i, d in enumerate(m['sessions']):
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

    week = []
    for i, wd in enumerate(WEEKDAY[pg['days']]):
        week.append(f'<li><span class="wd">{s["weekdays"][wd]}</span> <a href="#day-{i + 1}">{esc(label(i))}</a></li>')
    days_html = []
    for i, (d, df) in enumerate(zip(m['sessions'], f['sessions'])):
        sg = labels[i][2]
        h = (f'<div class="day-head"><span class="day-num" aria-hidden="true">{i + 1}</span>'
             f'<h3 id="day-{i + 1}">{s["day"].format(n=i + 1)}: {esc(label(i))}</h3>'
             f'<span class="day-min">{s["mins"].format(n=round(d["minutes"] / 5) * 5)}</span></div>')
        if sg in first_of:
            days_html.append(f'        <section class="plan-day repeat">{h}<p class="same"><a href="#day-{first_of[sg] + 1}">{s["same_as"].format(n=first_of[sg] + 1)}</a></p></section>')
            continue
        first_of[sg] = i
        rows = []
        for e, ef in zip(d['exercises'], df['exercises']):
            nm = X.name(lang, e['slug'])
            pub = e['slug'] in PUBLISHED
            thumb = (f'<img class="ex-thumb" src="/img/exercises/{e["slug"]}.webp" alt="" width="46" height="46" loading="lazy" />'
                     if pub else '<span class="ex-thumb"></span>')
            link = f'<a href="{X.path(lang, e["slug"])}">{esc(nm)}</a>' if pub else esc(nm)
            rows.append(
                f'<tr><th scope="row"><span class="ex-cell">{thumb}<span>{link}</span></span></th>'
                f'<td><span class="gm"><bdi dir="ltr">{e["sets"]}</bdi></span><span class="gf"><bdi dir="ltr">{ef["sets"]}</bdi></span></td>'
                f'<td><span class="gm">{num(cell_reps(e, s), e)}</span><span class="gf">{num(cell_reps(ef, s), ef)}</span></td>'
                f'<td><span class="gm">{rest(lang, e["rest"])}</span><span class="gf">{rest(lang, ef["rest"])}</span></td></tr>')
        days_html.append(f'''        <section class="plan-day">{h}
          <table class="plan-table">
            <thead><tr><th scope="col">{s['th_ex']}</th><th scope="col">{s['th_sets']}</th><th scope="col">{s['th_reps']}</th><th scope="col">{s['th_rest']}</th></tr></thead>
            <tbody>
              {chr(10).join('              ' + r for r in rows).strip()}
            </tbody>
          </table>
        </section>''')

    bodyweight_only = all(not X.LIB[e['slug']]['loadable'] for d in m['sessions'] for e in d['exercises'] if e['slug'] in X.LIB)
    prog = s['prog'] if not bodyweight_only else s['prog'][1:2] + [s['prog_bw']]
    same_setup = [kk for kk, p in pages.items() if p['setup'] == pg['setup'] and kk != k]
    other = [kk for kk, p in pages.items() if p['setup'] != pg['setup'] and p['days'] == pg['days'] and p['level'] == pg['level']]

    def plan_link(kk):
        p = pages[kk]
        name = s['h1'].format(days=p['days'], setup=SETUPS[p['setup']][lang], level_pl=s['level_pl'][p['level']])
        return f'<li><a href="{ppath(lang, kk)}">{esc(name)}</a></li>'

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
    gear = pg['equipment'] or ['bodyweight_only']
    icons = ''.join(X.eq_icon(g, setup[lang + '_eq'] if j == 0 else '') for j, g in enumerate(gear))
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{hub(lang)}">{s['crumbs']}</a></nav>
        <header class="plan-hero">
          <div class="hero-gear">{icons}</div>
          <h1>{esc(h1)}</h1>
          <p class="lede">{esc(s['lede'].format(**fmt))} {s['made']}</p>
        </header>

        <dl class="plan-facts">
          <div><dt>{s['k_days']}</dt><dd>{pg['days']}</dd></div>
          <div><dt>{s['k_time']}</dt><dd>{s['mins'].format(n=mins)}</dd></div>
          <div><dt>{s['k_level']}</dt><dd>{s['level'][pg['level']]}</dd></div>
          <div><dt>{s['k_split']}</dt><dd>{esc(' / '.join(split_names))}</dd></div>
          <div class="wide"><dt>{s['k_eq']}</dt><dd><span class="eq-icons">{''.join(X.eq_icon(g) for g in gear)}</span>{esc(setup[lang + '_eq'])}</dd></div>
        </dl>

        <div class="plan">
          <input type="radio" name="goal" id="goal-m" checked />
          <input type="radio" name="goal" id="goal-f" />
          <div class="goal-switch" role="group" aria-label="{s['goal_label']}">
            <label for="goal-m">{s['g_m']}</label><label for="goal-f">{s['g_f']}</label>
          </div>

          <section class="plan-week">
            <h2>{s['week']}</h2>
            <ul>
              {chr(10).join('              ' + w for w in week).strip()}
            </ul>
          </section>

{chr(10).join(days_html)}
        </div>

        <section class="about-sec">
          <h2>{s['prog_h']}</h2>
          <ul class="plain">{''.join(f'<li>{p}</li>' for p in prog)}</ul>
        </section>

{X.cta(t, s['cta_h'], s['cta_p'])}

        <section class="plan-faq">
          <h2>{s['faq_h']}</h2>
{faq}
        </section>

        <section class="ex-similar">
          <h2>{s['more']}</h2>
          <ul class="plain-links">{''.join(plan_link(kk) for kk in same_setup)}</ul>
          <h2>{s['other_setups']}</h2>
          <ul class="plain-links">{''.join(plan_link(kk) for kk in other)}</ul>
        </section>

        <p class="meta disclaimer">{t['disclaimer']}</p>'''
    return X.shell(lang, ppath(lang, k), title, s['desc'].format(**fmt), body,
                   [(l, ppath(l, k)) for l in LANGS], ld)


def hub_page(pages, lang):
    s, t = S[lang], X.T[lang]
    groups = []
    for setup in SETUPS:
        items = [(k, p) for k, p in pages.items() if p['setup'] == setup]
        if not items:
            continue
        li = ''.join(f'<li><a href="{ppath(lang, k)}"><b>{p["days"]}</b> {s["hub_item"].format(days=p["days"], level=s["level"][p["level"]]).split("·", 1)[0].replace(str(p["days"]), "").strip()}<small>{s["level"][p["level"]]}</small></a></li>'
                     for k, p in sorted(items, key=lambda kp: (kp[1]['level'] != 'beginner', kp[1]['days'])))
        gear = items[0][1]['equipment'] or ['bodyweight_only']
        icons = ''.join(X.eq_icon(g) for g in gear)
        groups.append(f'        <section class="setup-card"><div class="setup-head"><span class="hero-gear">{icons}</span><h2>{SETUPS[setup][lang]}</h2></div><ul class="plan-tiles">{li}</ul></section>')
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': s['hub_h1'], 'inLanguage': lang,
          'description': s['hub_p']}
    body = f'''        <h1>{s['hub_h1']}</h1>
        <p class="lede">{s['hub_p']}</p>
{chr(10).join(groups)}

{X.cta(t)}'''
    return X.shell(lang, hub(lang), s['hub_title'], s['hub_p'], body, [(l, hub(l)) for l in LANGS], ld, og_type='website')


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
    sitemap(pages)
    print(f'{len(pages)} plans x {len(LANGS)} languages')
