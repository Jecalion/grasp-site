"""
The page for coaches, in English and Arabic: what a coach gets in Grasp, and
how to start (owner, 2026-11-01: "a page to invite coaches to start building
their page and answer followers' questions, showcase their links and merch,
and their programs"). Led by what serves the following a coach already has
(owner, 2026-11-02: "a coach must have built a following base and grasp
doesn't mean much to them now"): answers posted to their socials, then their
product picks; being found in the Library comes last.

    python build/coaches.py

Uses the exercise pages' shell, so it has the same header, footer and styles.
The screens are the app's own, in img/coaches/<lang>/, captured from the
test build with its sample coach; no real person is on them.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exercises as X  # noqa: E402

LANGS = ['en', 'ar']

C = {
    'en': {
        'title': 'Grasp for coaches: answer your followers once, post it everywhere',
        'desc': 'Your followers keep asking. Answer once in Grasp and post it as a story, a sticker or on X; put your products and codes in one link; build programs that set each client’s weights. Free.',
        'kicker': 'For coaches',
        'h1': 'Answer your followers once. Post it everywhere.',
        'lede': 'You already have the following. Grasp keeps their questions in one place, turns every answer into a post for your story, X or TikTok in a tap, and puts your products, programs and clients one link away. Free for you and for them.',
        'sections': [
            ('share', 'Every answer, ready to post',
             'Followers ask on your page, without their name if they like. Write the answer once and post it as a story card, as a sticker over your own video, or on X. The question everyone asks gets an answer you can link to.',
             'A coach’s answer as a story card in Grasp'),
            ('shop', '“What do you use?” answered',
             'Your protein, your straps, your shoes: each with your link and your code, in one place your bio can point to. See how many tapped each one, whether you earn a commission or just stop answering the same DM.',
             'A coach’s product picks in Grasp'),
            ('program', 'Programs that set the weights',
             'Build a program day by day from 600+ exercises, add your own YouTube video to any exercise so it’s done the way you teach it, and publish it or keep it for your clients. Grasp sets each trainee’s weights from what they log, and raises them as they get stronger.',
             'A coach’s program in Grasp, with its days'),
            ('dashboard', 'Your clients at a glance',
             'Invite clients with a link. See who trained, who missed two in a row and who is falling behind, and send each one their own program. Put them in a crew and they climb the crews leaderboard together.',
             'A coach’s clients and questions in Grasp'),
            ('page', 'One link for your bio',
             'Your page carries your Instagram, TikTok, Snapchat, WhatsApp, your answers, your picks, your programs and your clients’ results, with the verified tick by your name. One link in your bio, everything behind it.',
             'A coach’s page in Grasp'),
            ('library', 'And new people find you',
             'Your programs sit in the Library beside Grasp’s, and you are listed under Coaches, so people who don’t follow you yet can.',
             'Coaches and their programs in the Grasp Library'),
        ],
        'steps_h': 'Start in three steps',
        'steps': [
            'Get Grasp and sign in.',
            'Tap your name on You, then “Are you a coach?”, and fill in your page, your links and your picks.',
            'Put your page in your bio and post your first answer.',
        ],
        'money': 'Grasp takes no cut and charges no fees: your commissions and what your clients pay you stay yours.',
        'cta_h': 'Make your coach page today. It’s free.',
        'cta_p': 'For iPhone and Android.',
    },
    'ar': {
        'title': 'Grasp للمدربين: جاوب متابعينك مرة، وانشرها في حساباتك',
        'desc': 'متابعينك يسألونك كل يوم. جاوبهم مرة في Grasp وانشر الجواب ستوري أو ملصق أو تغريدة، وحط منتجاتك وأكوادك في رابط واحد، وابنِ برامج تحسب أوزان كل عميل. مجانًا.',
        'kicker': 'للمدربين',
        'h1': 'جاوب متابعينك مرة، وانشرها في كل حساباتك',
        'lede': 'جمهورك موجود. Grasp يجمع أسئلتهم في مكان واحد، ويحوّل كل جواب لمنشور للستوري أو إكس أو تيك توك بضغطة، ويخلّي منتجاتك وبرامجك وعملاءك في رابط واحد. مجاني لك ولهم.',
        'sections': [
            ('share', 'كل جواب، منشور جاهز',
             'متابعينك يسألونك في صفحتك، ولو يبون بدون اسمهم. تكتب الجواب مرة، وتنشره بطاقة ستوري، أو ملصق فوق مقطعك، أو تغريدة. والسؤال اللي يتكرر، جوابه جاهز برابط.',
             'جواب مدرب كبطاقة ستوري في Grasp'),
            ('shop', '«وش تستخدم؟» انحلّت',
             'البروتين، والستراب، والجزمة: كل منتج برابطك وكودك، في مكان واحد يوديهم له البايو. وتشوف كم واحد ضغط على كل منتج، سواء تاخذ عمولة أو بس ترتاح من نفس السؤال في الخاص.',
             'منتجات مدرب في Grasp'),
            ('program', 'برامج تحسب الأوزان',
             'ابنِ برنامجك يوم بيوم من أكثر من 600 تمرين، وحط فيديو يوتيوب منك على أي تمرين عشان يأدّونه مثل ما تعلّمهم، وانشره للكل أو خلّه لعملائك. وGrasp يحسب أوزان كل متدرب من اللي يسجّله، ويرفعها كل ما قوي.',
             'برنامج مدرب في Grasp بأيامه'),
            ('dashboard', 'عملاؤك بنظرة',
             'ادعُ عملاءك برابط. تشوف مين تمرّن، ومين غاب مرتين ورا بعض، ومين متأخر، وترسل لكل واحد برنامجه. وحطهم في شلة تتنافس مع باقي الشلل في الترتيب.',
             'عملاء المدرب وأسئلتهم في Grasp'),
            ('page', 'رابط واحد للبايو',
             'صفحتك فيها إنستقرامك وتيك توكك وسنابك وواتسابك، وأجوبتك ومنتجاتك وبرامجك ونتائج متدربينك، وعلامة التوثيق جنب اسمك. رابط واحد في البايو، وكل شي وراه.',
             'صفحة مدرب في Grasp'),
            ('library', 'وناس جدد يلقونك',
             'برامجك في المكتبة جنب برامج Grasp، واسمك في قائمة المدربين، فاللي ما يتابعك للحين يقدر يلقاك.',
             'المدربين وبرامجهم في مكتبة Grasp'),
        ],
        'steps_h': 'ابدأ بثلاث خطوات',
        'steps': [
            'نزّل Grasp وسجّل دخولك.',
            'اضغط على اسمك في «أنت»، ثم «أنت مدرب؟»، وعبّ صفحتك وروابطك ومنتجاتك.',
            'حط رابط صفحتك في البايو، وانشر أول جواب.',
        ],
        'money': 'Grasp ما ياخذ نسبة ولا رسوم: عمولاتك وفلوس عملائك لك.',
        'cta_h': 'سوّ صفحتك كمدرب اليوم. مجانًا.',
        'cta_p': 'للآيفون والأندرويد.',
    },
}


def cpath(lang):
    return X.prefix(lang) + 'coaches/'


def page(lang):
    c, t = C[lang], X.T[lang]
    sections = '\n'.join(
        f'''        <section class="feature coach-feature{' flip' if i % 2 else ''}">
          <div class="feature-copy">
            <h2>{h}</h2>
            <p>{p}</p>
          </div>
          <div class="feature-shot"><div class="phone"><img src="/img/coaches/{lang}/{shot}.webp" alt="{alt}" width="540" height="1200" loading="{'eager' if i == 0 else 'lazy'}" /></div></div>
        </section>'''
        for i, (shot, h, p, alt) in enumerate(c['sections']))
    steps = '\n'.join(f'            <li>{s}</li>' for s in c['steps'])
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', 'name': c['h1'], 'inLanguage': lang, 'description': c['desc'],
         'url': X.BASE + cpath(lang)},
        {'@type': 'SoftwareApplication', 'name': 'Grasp', 'operatingSystem': 'iOS, Android',
         'applicationCategory': 'HealthApplication', 'offers': {'@type': 'Offer', 'price': '0'},
         'url': X.BASE + '/'},
    ]}
    body = f'''        <span class="kicker">{c['kicker']}</span>
        <h1>{c['h1']}</h1>
        <p class="lede">{c['lede']}</p>
{sections}

        <section class="about-sec coach-steps">
          <h2>{c['steps_h']}</h2>
          <ol>
{steps}
          </ol>
          <p class="meta">{c['money']}</p>
        </section>

{X.cta(t, c['cta_h'], c['cta_p'], pose='coach')}'''
    return X.shell(lang, cpath(lang), c['title'], c['desc'], body, [(l, cpath(l)) for l in LANGS], ld,
                   og_type='website')


def sitemap():
    sm = os.path.join(X.SITE, 'sitemap.xml')
    text = open(sm, encoding='utf8').read()
    text = re.sub(r'\n  <!-- coaches:start -->.*<!-- coaches:end -->', '', text, flags=re.S)
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{X.BASE}{cpath(l)}"/>' for l in LANGS)
    alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{X.BASE}{cpath("en")}"/>'
    block = '\n  <!-- coaches:start -->\n' + '\n'.join(
        f'  <url>\n    <loc>{X.BASE}{cpath(l)}</loc>{alts}\n  </url>' for l in LANGS) + '\n  <!-- coaches:end -->'
    text = text.replace('\n</urlset>', block + '\n</urlset>')
    with open(sm, 'w', encoding='utf8', newline='\n') as f:
        f.write(text)


if __name__ == '__main__':
    for lang in LANGS:
        X.write(cpath(lang), page(lang))
    sitemap()
    print('coaches:', ', '.join(cpath(l) for l in LANGS))
