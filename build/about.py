"""
The About page, in English and Arabic: what Grasp is and how its plans are made.

    python build/about.py

Short on purpose, and only facts the app keeps (the same ones llms.txt lists).
No people on it — the owner's choice. Uses the exercise pages' shell, so it has
the same header, footer and styles.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exercises as X  # noqa: E402

LANGS = ['en', 'ar']

A = {
    'en': {
        'title': 'About Grasp: the free workout planner',
        'desc': 'Grasp is a free workout planner for iPhone and Android. How it plans your workouts and sets your weights.',
        'h1': 'About Grasp',
        'lede': 'Grasp is a free workout planner for iPhone and Android. It plans each workout and works out your next weights from what you logged.',
        'sections': [
            ('What it does', [
                'Builds each workout from your goal, your days, your time and the equipment you have.',
                'You log your sets. Grasp sets your next weights from what you actually lifted.',
                'Works offline. Free: no ads, no subscription.',
            ]),
            ('How the plans are made', [
                'Simple rules on your phone, not AI.',
                'Your goal sets the reps and the rest between sets.',
                'Hit the top of the rep range on every set and the weight goes up. Miss it twice and it comes down.',
                'An exercise only shows up if you have the equipment for it.',
            ]),
            ('The exercise library', [
                '600+ exercises, most of them animated, with the muscles they work and the steps, in 15 languages.',
                '<a href="/exercises/">The exercise pages</a> on this site use the same library and the same numbers as the app.',
            ]),
            ('Your data', [
                'No ads and no ad tracking. Grasp counts which screens are used, never your weights or health data, and you can turn that off.',
                'Details in the <a href="/privacy.html">privacy policy</a>.',
            ]),
            ('Contact', [
                '<a href="mailto:grasp@alsouq.tech">grasp@alsouq.tech</a> · <a href="/support.html">Support</a>',
            ]),
        ],
        'disclaimer': 'Not medical advice.',
    },
    'ar': {
        'title': 'عن Grasp: مخطط التمارين المجاني',
        'desc': 'Grasp مخطط تمارين مجاني للآيفون والأندرويد. كيف يخطط تمارينك ويحدد أوزانك.',
        'h1': 'عن Grasp',
        'lede': 'Grasp مخطط تمارين مجاني للآيفون والأندرويد. يخطط لك كل تمرين، ويحسب أوزانك الجاية من اللي سجّلته.',
        'sections': [
            ('وش يسوي', [
                'يبني تمرينك على هدفك، وأيامك، ووقتك، والأدوات اللي عندك.',
                'تسجّل جلساتك، ويحدد لك Grasp أوزانك الجاية من اللي رفعته فعلاً.',
                'يشتغل بدون نت. مجاني: بدون إعلانات وبدون اشتراك.',
            ]),
            ('كيف تنبني الخطة', [
                'قواعد بسيطة على جوالك، مو ذكاء اصطناعي.',
                'هدفك يحدد التكرارات والراحة بين الجلسات.',
                'إذا وصلت لأعلى التكرارات في كل الجلسات يزيد الوزن، وإذا ما وصلت مرتين ينقص.',
                'ما يطلع لك تمرين إلا إذا عندك أدواته.',
            ]),
            ('مكتبة التمارين', [
                'أكثر من 600 تمرين، أغلبها برسوم متحركة، مع العضلات المستهدفة والخطوات، بـ15 لغة.',
                '<a href="/ar/exercises/">صفحات التمارين</a> في هذا الموقع من نفس مكتبة التطبيق ونفس أرقامه.',
            ]),
            ('بياناتك', [
                'بدون إعلانات وبدون تتبّع إعلاني. Grasp يحسب أي الشاشات تُستخدم، وما يحسب أوزانك ولا بياناتك الصحية، وتقدر توقف هذا.',
                'التفاصيل في <a href="/privacy.html">سياسة الخصوصية</a>.',
            ]),
            ('تواصل معنا', [
                '<a href="mailto:grasp@alsouq.tech">grasp@alsouq.tech</a> · <a href="/support.html">الدعم</a>',
            ]),
        ],
        'disclaimer': 'مو استشارة طبية.',
    },
}


def apath(lang):
    return X.prefix(lang) + 'about/'


def page(lang):
    a, t = A[lang], X.T[lang]
    sections = '\n'.join(
        f'        <section class="about-sec">\n          <h2>{h}</h2>\n'
        + '\n'.join(f'          <p>{p}</p>' for p in ps) + '\n        </section>'
        for h, ps in a['sections'])
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'AboutPage', 'name': a['h1'], 'inLanguage': lang, 'description': a['desc'],
         'url': X.BASE + apath(lang)},
        {'@type': 'Organization', 'name': 'Grasp', 'url': X.BASE + '/', 'logo': X.BASE + '/favicon.png',
         'email': 'grasp@alsouq.tech',
         'sameAs': ['https://www.instagram.com/grasp.workout/', 'https://www.tiktok.com/@graspapp',
                    X.APPSTORE, X.PLAY]},
    ]}
    body = f'''        <h1>{a['h1']}</h1>
        <p class="lede">{a['lede']}</p>
{sections}

{X.cta(t)}

        <p class="meta disclaimer">{a['disclaimer']}</p>'''
    return X.shell(lang, apath(lang), a['title'], a['desc'], body, [(l, apath(l)) for l in LANGS], ld,
                   og_type='website')


def sitemap():
    sm = os.path.join(X.SITE, 'sitemap.xml')
    text = open(sm, encoding='utf8').read()
    text = re.sub(r'\n  <!-- about:start -->.*<!-- about:end -->', '', text, flags=re.S)
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{X.BASE}{apath(l)}"/>' for l in LANGS)
    alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{X.BASE}{apath("en")}"/>'
    block = '\n  <!-- about:start -->\n' + '\n'.join(
        f'  <url>\n    <loc>{X.BASE}{apath(l)}</loc>{alts}\n  </url>' for l in LANGS) + '\n  <!-- about:end -->'
    text = text.replace('\n</urlset>', block + '\n</urlset>')
    with open(sm, 'w', encoding='utf8', newline='\n') as f:
        f.write(text)


if __name__ == '__main__':
    for lang in LANGS:
        X.write(apath(lang), page(lang))
    sitemap()
    print('about:', ', '.join(apath(l) for l in LANGS))
