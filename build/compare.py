"""
"Grasp vs X" pages, English and Arabic, from facts checked on each app's own
pages and store listings (research of 26-27 Oct 2026).

    python build/compare.py

    compare/index.html          free alternatives to the big workout apps
    compare/<app>/index.html    Grasp vs <app>

Rules for this file — they are what keep these pages honest:
- Every price and free-tier fact comes with its source and the date it was checked.
- Anything not confirmed on an official page says "not stated", never a guess.
- No "only"/"first" claims: Hevy and Nike Training Club speak Arabic, and Hevy's
  paid Trainer raises weights by the same rule as Grasp. What is true and ours:
  plans and progression for free, with nothing locked and no ads.
- Each page says plainly when the other app is the better pick.
Re-check prices every quarter (CHECKED below).
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exercises as X  # noqa: E402

LANGS = ['en', 'ar']
CHECKED = {'en': '27 October 2026', 'ar': '27 أكتوبر 2026'}
esc = html.escape

# Values per row: (english, arabic). ok: True / False / None (unknown) drives the mark.
GRASP = {
    'name': 'Grasp',
    'price': (('Free', 'مجاني'), True),
    'free': (('Everything: nothing locked', 'كل شيء، ما فيه شيء مقفل'), True),
    'ads': (('No ads', 'بدون إعلانات'), True),
    'plans': (('Yes, free', 'إيه، مجاناً'), True),
    'weights': (('Yes, free', 'إيه، مجاناً'), True),
    'offline': (('Yes', 'إيه'), True),
    'arabic': (('Yes (15 languages)', 'إيه (15 لغة)'), True),
    'platforms': (('iPhone, Android', 'آيفون، أندرويد'), None),
}

APPS = {
    'hevy': {
        'name': 'Hevy',
        'price': (('$2.99/mo · $23.99/yr · $74.99 lifetime', '2.99 دولار شهرياً · 23.99 دولار سنوياً · 74.99 دولار مدى الحياة'), None),
        'free': (('4 routines, 7 custom exercises, 3 months of graphs', '4 جداول، 7 تمارين مخصصة، رسوم بيانية لآخر 3 شهور'), None),
        'ads': (('No ads', 'بدون إعلانات'), True),
        'plans': (('Hevy Trainer, Pro only', 'Hevy Trainer، للمشتركين فقط'), False),
        'weights': (('Hevy Trainer, Pro only', 'Hevy Trainer، للمشتركين فقط'), False),
        'offline': (('Yes', 'إيه'), True),
        'arabic': (('Yes (16 languages)', 'إيه (16 لغة)'), True),
        'platforms': (('iPhone, Android, Apple Watch, Wear OS, web', 'آيفون، أندرويد، Apple Watch، Wear OS، الويب'), None),
        'sources': ['https://help.hevyapp.com/hc/en-us/articles/35119778922263',
                    'https://apps.apple.com/us/app/hevy-workout-tracker-gym-log/id1458862350',
                    'https://www.hevyapp.com/features/workout-plan-generator/'],
        'tldr': ('A great free logger with a big community. Planning for you, and raising your weights, is in Hevy Trainer, which needs Pro. Grasp does both for free.',
                 'Hevy مسجّل تمارين ممتاز ومجتمعه كبير. بس التخطيط لك وزيادة أوزانك في Hevy Trainer، وهو للمشتركين. Grasp يسوي الثنتين مجاناً.'),
        'how': ('Hevy Trainer builds a program from your goal, equipment and days, and raises a weight once you hit the top of the rep range on every set: the same rule Grasp uses. It is part of Hevy Pro.',
                'Hevy Trainer يبني برنامج من هدفك وأدواتك وأيامك، ويزيد الوزن إذا وصلت لأعلى التكرارات في كل الجلسات، نفس قاعدة Grasp. بس هو ضمن اشتراك Hevy Pro.'),
        'pick_them': (['You want a social feed and to follow friends', 'You train with an Apple Watch or Wear OS watch', 'You want to log from a web browser too'],
                      ['تبي مجتمع وتتابع أصحابك', 'تتمرن بساعة Apple Watch أو Wear OS', 'تبي تسجّل من المتصفح بعد']),
    },
    'strong': {
        'name': 'Strong',
        'price': (('$4.99/mo · $29.99/yr · $99.99 lifetime', '4.99 دولار شهرياً · 29.99 دولار سنوياً · 99.99 دولار مدى الحياة'), None),
        'free': (('Unlimited workouts, 3 custom routines', 'تمارين بلا حد، 3 جداول مخصصة'), None),
        'ads': (('None shown on Google Play', 'ما فيه إعلانات حسب Google Play'), True),
        'plans': (('No: you build your routines', 'لا، أنت تبني جداولك'), False),
        'weights': (('No', 'لا'), False),
        'offline': (('Not stated by Strong', 'ما ذكرته Strong'), None),
        'arabic': (('No', 'لا'), False),
        'platforms': (('iPhone, Android, Apple Watch', 'آيفون، أندرويد، Apple Watch'), None),
        'sources': ['https://apps.apple.com/us/app/strong-workout-tracker-gym-log/id464254577', 'https://www.strong.app/'],
        'tldr': ('The simplest, fastest logger, if you already know what to do. It does not plan sessions or set weights; Grasp does, for free.',
                 'Strong أبسط وأسرع مسجّل، إذا تعرف وش تسوي. بس ما يخطط تمارينك ولا يحدد أوزانك، وGrasp يسويها مجاناً.'),
        'how': ('Strong is a logger: you write your routines, it records your sets and shows your history. Planning and progression are up to you.',
                'Strong مسجّل: أنت تكتب جداولك، وهو يسجّل جلساتك ويعرض تاريخك. التخطيط والتطور عليك.'),
        'pick_them': (['You already follow your own program and only want to log it', 'You want an Apple Watch app', 'You like a very minimal screen'],
                      ['عندك برنامجك وتبي تسجّل بس', 'تبي تطبيق على Apple Watch', 'تحب الشاشة البسيطة جداً']),
    },
    'jefit': {
        'name': 'JEFIT',
        'price': (('$12.99/mo · $69.99/yr', '12.99 دولار شهرياً · 69.99 دولار سنوياً'), None),
        'free': (('Routines and logging', 'الجداول والتسجيل'), None),
        'ads': (('Yes: paying removes them', 'إيه، الاشتراك يشيلها'), False),
        'plans': (('AI coach, Elite only', 'مدرب ذكاء اصطناعي، لـElite فقط'), False),
        'weights': (('AI coach, Elite only', 'مدرب ذكاء اصطناعي، لـElite فقط'), False),
        'offline': (('Not stated by JEFIT', 'ما ذكرته JEFIT'), None),
        'arabic': (('No', 'لا'), False),
        'platforms': (('iPhone, Android, Apple Watch', 'آيفون، أندرويد، Apple Watch'), None),
        'sources': ['https://www.jefit.com/elite', 'https://apps.apple.com/us/app/jefit-gym-workout-planner/id449810000'],
        'tldr': ('A huge exercise database and community. Its adaptive coach is in the paid Elite plan, which also removes ads. Grasp plans for free, with no ads.',
                 'JEFIT عنده قاعدة تمارين ضخمة ومجتمع. بس المدرب التكيّفي في اشتراك Elite المدفوع، واللي يشيل الإعلانات بعد. Grasp يخطط مجاناً وبدون إعلانات.'),
        'how': ('JEFIT\'s adaptive plan and AI coach adjust your training, and are listed under the paid Elite plan. The free version is for building and logging your own routines.',
                'الخطة التكيّفية ومدرب الذكاء الاصطناعي في JEFIT تعدّل تمرينك، وهي ضمن Elite المدفوع. النسخة المجانية لبناء جداولك وتسجيلها.'),
        'pick_them': (['You want the largest exercise database', 'You like community features and sharing', 'You want an Apple Watch app'],
                      ['تبي أكبر قاعدة تمارين', 'تحب المجتمع والمشاركة', 'تبي تطبيق على Apple Watch']),
    },
    'fitbod': {
        'name': 'Fitbod',
        'price': (('$15.99/mo · $95.99/yr', '15.99 دولار شهرياً · 95.99 دولار سنوياً'), None),
        'free': (('7-day trial, then logging needs a subscription', 'تجربة 7 أيام، بعدها التسجيل يحتاج اشتراك'), False),
        'ads': (('None shown on Google Play', 'ما فيه إعلانات حسب Google Play'), True),
        'plans': (('Yes, with a subscription', 'إيه، بالاشتراك'), None),
        'weights': (('Yes, with a subscription', 'إيه، بالاشتراك'), None),
        'offline': (('Partly', 'جزئياً'), None),
        'arabic': (('No', 'لا'), False),
        'platforms': (('iPhone, Android, Apple Watch', 'آيفون، أندرويد، Apple Watch'), None),
        'sources': ['https://help.fitbod.me/hc/en-us/articles/30542136101527',
                    'https://help.fitbod.me/hc/en-us/articles/360006572594',
                    'https://apps.apple.com/us/app/fitbod-workout-gym-planner/id1041517543'],
        'tldr': ('Fitbod plans every workout for you, and does it well, but after a 7-day trial it needs a subscription. Grasp plans and sets your weights for free.',
                 'Fitbod يخطط كل تمرين لك وبشكل ممتاز، بس بعد تجربة 7 أيام يحتاج اشتراك. Grasp يخطط ويحدد أوزانك مجاناً.'),
        'how': ('Fitbod builds each workout from your equipment, schedule and history, and adapts as you train. It is the most complete automatic planner of the big apps, and it is paid.',
                'Fitbod يبني كل تمرين من أدواتك وجدولك وتاريخك، ويتكيّف مع تمرينك. هو أكمل مخطط تلقائي بين التطبيقات الكبيرة، وهو مدفوع.'),
        'pick_them': (['You want the most mature automatic planner and don\'t mind paying', 'You want it to account for muscle recovery', 'You use an Apple Watch'],
                      ['تبي أنضج مخطط تلقائي وما عندك مشكلة تدفع', 'تبيه يحسب استشفاء العضلات', 'تستخدم Apple Watch']),
    },
    'nike-training-club': {
        'name': 'Nike Training Club',
        'price': (('Free', 'مجاني'), True),
        'free': (('All of it, with a Nike account', 'كله، بحساب Nike'), True),
        'ads': (('None shown on Google Play', 'ما فيه إعلانات حسب Google Play'), True),
        'plans': (('Fixed programs and video classes', 'برامج ثابتة وحصص فيديو'), None),
        'weights': (('No', 'لا'), False),
        'offline': (('Not stated by Nike', 'ما ذكرته Nike'), None),
        'arabic': (('Yes (17 languages)', 'إيه (17 لغة)'), True),
        'platforms': (('iPhone, Android', 'آيفون، أندرويد'), None),
        'sources': ['https://apps.apple.com/us/app/nike-training-club-wellness/id301521403'],
        'tldr': ('Free video workouts with trainers, great to follow along. It does not log your lifts or set your next weights; Grasp does, also free.',
                 'Nike Training Club فيه حصص فيديو مجانية مع مدربين، ممتاز تتبعها. بس ما يسجّل أوزانك ولا يحدد وزنك الجاي، وGrasp يسويها ومجاني بعد.'),
        'how': ('NTC gives you set programs and classes to follow. It does not track the weights you lift or change them from session to session.',
                'NTC يعطيك برامج وحصص جاهزة تتبعها. ما يتابع الأوزان اللي ترفعها ولا يغيّرها من تمرين لتمرين.'),
        'pick_them': (['You want video classes with a coach talking you through', 'You do yoga, mobility or HIIT more than lifting', 'You like structured multi-week programs'],
                      ['تبي حصص فيديو مع مدرب يشرح لك', 'تسوي يوغا أو مرونة أو HIIT أكثر من الحديد', 'تحب البرامج الجاهزة لعدة أسابيع']),
    },
    'boostcamp': {
        'name': 'Boostcamp',
        'price': (('$14.99/mo · $59.99/yr', '14.99 دولار شهرياً · 59.99 دولار سنوياً'), None),
        'free': (('Thousands of programs and the tracker', 'آلاف البرامج والمسجّل'), None),
        'ads': (('No ads', 'بدون إعلانات'), True),
        'plans': (('Coach programs free; personalised plans Pro only', 'برامج المدربين مجانية، والخطط الشخصية للمشتركين'), None),
        'weights': (('Auto progression, Pro only', 'زيادة الأوزان التلقائية، للمشتركين فقط'), False),
        'offline': (('Yes', 'إيه'), True),
        'arabic': (('No (English only)', 'لا (إنجليزي فقط)'), False),
        'platforms': (('iPhone, Android', 'آيفون، أندرويد'), None),
        'sources': ['https://www.boostcamp.app/pro', 'https://apps.apple.com/us/app/boostcamp-workout-tracker/id1529354455'],
        'tldr': ('A huge library of programs by coaches, free to follow. Personalised plans and automatic progression need Pro. Grasp builds yours and progresses it for free.',
                 'Boostcamp فيه مكتبة ضخمة من برامج المدربين، مجانية. بس الخطط الشخصية وزيادة الأوزان التلقائية للمشتركين. Grasp يبني خطتك ويطوّرها مجاناً.'),
        'how': ('Boostcamp is built around famous programs you pick and follow. Its AI coach and auto progression, which change the plan for you, are part of Pro.',
                'Boostcamp مبني على برامج معروفة تختارها وتمشي عليها. المدرب الذكي وزيادة الأوزان التلقائية، اللي تعدّل الخطة لك، ضمن Pro.'),
        'pick_them': (['You want to run a famous program exactly as written', 'You like choosing from thousands of programs', 'You plan to follow a coach\'s template'],
                      ['تبي تمشي على برنامج معروف بالحرف', 'تحب تختار من آلاف البرامج', 'تبي تتبع قالب مدرب']),
    },
    'lyfta': {
        'name': 'Lyfta',
        'price': (('Free; Pro after a 14-day trial (Lyfta does not publish its plan prices)', 'مجاني، وPro بعد تجربة 14 يوم (Lyfta ما تنشر أسعار خططها)'), None),
        'free': (('Logging, routines, the exercise library', 'التسجيل، الجداول، مكتبة التمارين'), None),
        'ads': (('No ads', 'بدون إعلانات'), True),
        'plans': (('Ready programs to follow; no planner described', 'برامج جاهزة تتبعها، وما فيه مخطط تلقائي مذكور'), None),
        'weights': (('"Progression tools" are in Pro', '"أدوات التطور" ضمن Pro'), False),
        'offline': (('Not stated by Lyfta', 'ما ذكرته Lyfta'), None),
        'arabic': (('Yes (28 languages)', 'إيه (28 لغة)'), True),
        'platforms': (('iPhone, Apple Watch, Android', 'آيفون، Apple Watch، أندرويد'), None),
        'sources': ['https://apps.apple.com/us/app/lyfta-gym-workout-tracker-log/id6443740936',
                    'https://play.google.com/store/apps/details?id=com.lyfta'],
        'tldr': ('A free, ad-free tracker in many languages, with ready programs to follow. Lyfta does not describe planning sessions for you, and its progression tools are in Pro. Grasp plans and sets your weights for free.',
                 'Lyfta مسجّل مجاني بدون إعلانات وبلغات كثيرة، وفيه برامج جاهزة تتبعها. بس ما يذكر إنه يخطط تمارينك، وأدوات التطور عنده ضمن Pro. Grasp يخطط ويحدد أوزانك مجاناً.'),
        'how': ('You build your routines or pick a ready program, such as StrongLifts 5x5, and log it. Pro adds expert programs, analytics and progression tools.',
                'أنت تبني جداولك أو تختار برنامج جاهز مثل StrongLifts 5x5 وتسجّله. Pro يضيف برامج خبراء وإحصائيات وأدوات تطور.'),
        'pick_them': (['You want to follow a known program like StrongLifts 5x5', 'You track live from an Apple Watch', 'You want an app in your language: it has 28'],
                      ['تبي تمشي على برنامج معروف مثل StrongLifts 5x5', 'تتابع تمرينك من Apple Watch', 'تبي التطبيق بلغتك، فيه 28 لغة']),
    },
}

# Compact view for the all-apps table, from the facts above.
# '+' yes / free, '$' only when paying, '-' no, '~' partly, '?' not stated by the app.
SHORT = {
    'grasp':              {'price': ('Free', 'مجاني'), 'plans': '+', 'weights': '+', 'noads': '+', 'arabic': '+', 'offline': '+'},
    'hevy':               {'price': ('Free · $23.99/yr Pro', 'مجاني · 23.99 دولار سنوياً للـPro'), 'plans': '$', 'weights': '$', 'noads': '+', 'arabic': '+', 'offline': '+'},
    'strong':             {'price': ('Free · $29.99/yr Pro', 'مجاني · 29.99 دولار سنوياً للـPro'), 'plans': '-', 'weights': '-', 'noads': '+', 'arabic': '-', 'offline': '?'},
    'jefit':              {'price': ('Free · $69.99/yr Elite', 'مجاني · 69.99 دولار سنوياً للـElite'), 'plans': '$', 'weights': '$', 'noads': '-', 'arabic': '-', 'offline': '?'},
    'fitbod':             {'price': ('$95.99/yr after a 7-day trial', '95.99 دولار سنوياً بعد تجربة 7 أيام'), 'plans': '$', 'weights': '$', 'noads': '+', 'arabic': '-', 'offline': '~'},
    'nike-training-club': {'price': ('Free', 'مجاني'), 'plans': '~', 'weights': '-', 'noads': '+', 'arabic': '+', 'offline': '?'},
    'boostcamp':          {'price': ('Free · $59.99/yr Pro', 'مجاني · 59.99 دولار سنوياً للـPro'), 'plans': '~', 'weights': '$', 'noads': '+', 'arabic': '-', 'offline': '+'},
    'lyfta':              {'price': ('Free · Pro after a 14-day trial', 'مجاني · Pro بعد تجربة 14 يوم'), 'plans': '~', 'weights': '$', 'noads': '+', 'arabic': '+', 'offline': '?'},
}
BEST = [  # (en, ar, app key): the honest "best for" line per need
    ('Free planning and weight progression', 'تخطيط وزيادة أوزان مجاناً', 'grasp'),
    ('A social feed and watch apps', 'مجتمع وتطبيقات للساعة', 'hevy'),
    ('The simplest logger', 'أبسط مسجّل', 'strong'),
    ('The biggest exercise database', 'أكبر قاعدة تمارين', 'jefit'),
    ('A mature paid AI planner', 'مخطط ذكي مدفوع ومتكامل', 'fitbod'),
    ('Follow-along video classes', 'حصص فيديو تتبعها', 'nike-training-club'),
    ('Famous coach programs', 'برامج مدربين معروفة', 'boostcamp'),
    ('A free tracker in 28 languages', 'مسجّل مجاني بـ28 لغة', 'lyfta'),
]
SYMBOL = {'+': ('ok', '✓'), '$': ('paid', '$'), '-': ('no', '✗'), '~': ('part', '~'), '?': ('unk', '?')}
COLS = [('plans', 'Plans for you', 'يخطط لك'), ('weights', 'Sets your weights', 'يحدد أوزانك'),
        ('noads', 'No ads', 'بدون إعلانات'), ('arabic', 'Arabic', 'عربي'), ('offline', 'Offline', 'بدون نت')]

ROWS = [('price', 'Price', 'السعر'), ('free', 'What\'s free', 'وش المجاني'), ('ads', 'Ads', 'الإعلانات'),
        ('plans', 'Plans your sessions', 'يخطط تمارينك'), ('weights', 'Sets your next weights', 'يحدد أوزانك الجاية'),
        ('offline', 'Works offline', 'يشتغل بدون نت'), ('arabic', 'Arabic', 'العربي'), ('platforms', 'Platforms', 'الأجهزة')]

S = {
    'en': {
        'crumbs': 'Compare',
        'title': 'Grasp vs {app} (2026): free workout planner compared',
        'h1': 'Grasp vs {app}',
        'desc': 'Grasp vs {app}: price, what is free, ads, planning, weight progression, offline use and Arabic, checked {date}.',
        'checked': 'Prices and features checked {date} on each app\'s own pages and store listings. They can change.',
        'short': 'In short', 'glance': 'At a glance', 'how_h': 'How each plans your training',
        'grasp_how': 'Grasp builds each session from your goal, days, time and equipment, then raises a weight when you reach the top of the rep range on every set, and lowers it if you miss twice. Simple rules on your phone, free.',
        'pick_grasp': 'Choose Grasp if', 'pick_them': 'Choose {app} if',
        'grasp_reasons': ['You want your sessions planned for you, for free', 'You want your next weights worked out from what you lifted', 'You train in Arabic, or with no internet'],
        'faq_h': 'Questions',
        'faq': [('Is Grasp really free?', 'Yes. No subscription, no ads, nothing locked.'),
                ('Is {app} free?', '{free}.'),
                ('Does {app} work in Arabic?', '{arabic}.')],
        'sources': 'Sources', 'others': 'More comparisons', 'feature': 'Feature',
        'tm': 'App names and icons belong to their owners and are shown only to compare.',
        'all_h': 'All apps side by side', 'best_h': 'Best for', 'app': 'App',
        'legend': '✓ yes, free · $ only when paying · ~ partly · ✗ no · ? not stated by the app',
        'one_h': 'One-on-one comparisons',
        'hub_title': 'Best Free Workout Apps Compared (2026): Grasp, Hevy, Strong, Lyfta, JEFIT, Fitbod, NTC, Boostcamp',
        'hub_h1': 'Workout apps compared',
        'hub_p': 'How Grasp compares with the big workout apps on price, planning and progression. Facts checked {date}.',
        'hub_item': 'Grasp vs {app}',
    },
    'ar': {
        'crumbs': 'مقارنات',
        'title': 'Grasp أو {app}؟ مقارنة تطبيق تمارين مجاني (2026)',
        'h1': 'Grasp أو {app}',
        'desc': 'مقارنة Grasp و{app}: السعر، وش المجاني، الإعلانات، التخطيط، زيادة الأوزان، العمل بدون نت، والعربي. تم التحقق {date}.',
        'checked': 'الأسعار والمزايا تم التحقق منها {date} من صفحات كل تطبيق ومتاجره، وممكن تتغير.',
        'short': 'باختصار', 'glance': 'المقارنة', 'how_h': 'كيف يخطط كل واحد تمرينك',
        'grasp_how': 'Grasp يبني كل تمرين من هدفك وأيامك ووقتك وأدواتك، ويزيد الوزن إذا وصلت لأعلى التكرارات في كل الجلسات، وينقصه إذا ما وصلت مرتين. قواعد بسيطة على جوالك، ومجاناً.',
        'pick_grasp': 'اختر Grasp إذا', 'pick_them': 'اختر {app} إذا',
        'grasp_reasons': ['تبي أحد يخطط تمارينك، مجاناً', 'تبي أوزانك الجاية محسوبة من اللي رفعته', 'تتمرن بالعربي أو بدون نت'],
        'faq_h': 'أسئلة',
        'faq': [('Grasp مجاني فعلاً؟', 'إيه. بدون اشتراك، بدون إعلانات، وما فيه شيء مقفل.'),
                ('{app} مجاني؟', '{free}.'),
                ('{app} يدعم العربي؟', '{arabic}.')],
        'sources': 'المصادر', 'others': 'مقارنات ثانية', 'feature': 'الميزة',
        'tm': 'أسماء التطبيقات وأيقوناتها ملك أصحابها، ومعروضة للمقارنة فقط.',
        'all_h': 'كل التطبيقات جنب بعض', 'best_h': 'الأفضل لـ', 'app': 'التطبيق',
        'legend': '✓ إيه ومجاناً · $ بالاشتراك فقط · ~ جزئياً · ✗ لا · ? ما ذكره التطبيق',
        'one_h': 'مقارنة كل تطبيق مع Grasp',
        'hub_title': 'أفضل تطبيقات التمارين المجانية: مقارنة Grasp وHevy وStrong وLyfta وJEFIT وFitbod وغيرها (2026)',
        'hub_h1': 'مقارنة تطبيقات التمارين',
        'hub_p': 'كيف يقارن Grasp بتطبيقات التمارين الكبيرة في السعر والتخطيط وزيادة الأوزان. تم التحقق {date}.',
        'hub_item': 'Grasp أو {app}',
    },
}


def logo(k, name, size=40):
    return f'<img class="app-logo" src="/img/apps/{k}.webp" alt="{esc(name)}" width="{size}" height="{size}" loading="lazy" />'


def cpath(lang, k):
    return X.prefix(lang) + f'compare/{k}/'


def hub(lang):
    return X.prefix(lang) + 'compare/'


def mark(ok):
    return {True: '<span class="ok" aria-hidden="true">✓</span> ', False: '<span class="no" aria-hidden="true">✗</span> ', None: ''}[ok]


def cell(entry, lang):
    (en, ar), ok = entry
    return mark(ok) + esc(en if lang == 'en' else ar)


def page(k, a, lang):
    s, t = S[lang], X.T[lang]
    i = 0 if lang == 'en' else 1
    app = a['name']
    rows = '\n'.join(
        f'            <tr><th scope="row">{en if lang == "en" else ar}</th><td>{cell(GRASP[key], lang)}</td><td>{cell(a[key], lang)}</td></tr>'
        for key, en, ar in ROWS)
    faq = [(q.format(app=app), ans.format(app=app, free=a['free'][0][i], arabic=a['arabic'][0][i]))
           for q, ans in s['faq']]
    others = ''.join(f'<li><a href="{cpath(lang, kk)}">{esc(s["hub_item"].format(app=aa["name"]))}</a></li>'
                     for kk, aa in APPS.items() if kk != k)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', 'name': s['h1'].format(app=app), 'inLanguage': lang, 'dateModified': '2026-10-27'},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}} for q, ans in faq]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': s['crumbs'], 'item': X.BASE + hub(lang)},
            {'@type': 'ListItem', 'position': 2, 'name': s['h1'].format(app=app), 'item': X.BASE + cpath(lang, k)}]},
    ]}
    body = f'''        <nav class="crumbs" aria-label="breadcrumb"><a href="{hub(lang)}">{s['crumbs']}</a></nav>
        <header class="cmp-hero">
          <div class="vs">{logo('grasp', 'Grasp', 64)}<span>{'vs' if lang == 'en' else 'أو'}</span>{logo(k, app, 64)}</div>
          <h1>{esc(s['h1'].format(app=app))}</h1>
          <p class="meta">{s['checked'].format(date=CHECKED[lang])}</p>
        </header>

        <section class="about-sec">
          <h2>{s['short']}</h2>
          <p class="lede">{esc(a['tldr'][i])}</p>
        </section>

        <section class="ex-dose">
          <h2>{s['glance']}</h2>
          <table class="cmp">
            <thead><tr><th scope="col">{s['feature']}</th><th scope="col">{logo('grasp', 'Grasp', 28)} Grasp</th><th scope="col">{logo(k, app, 28)} {esc(app)}</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
        </section>

        <section class="about-sec">
          <h2>{s['how_h']}</h2>
          <p><strong>Grasp:</strong> {s['grasp_how']}</p>
          <p><strong>{esc(app)}:</strong> {esc(a['how'][i])}</p>
        </section>

        <div class="cmp-pick">
          <section><h2>{s['pick_grasp']}</h2><ul class="plain">{''.join(f'<li>{r}</li>' for r in s['grasp_reasons'])}</ul></section>
          <section><h2>{esc(s['pick_them'].format(app=app))}</h2><ul class="plain">{''.join(f'<li>{esc(r)}</li>' for r in a['pick_them'][i])}</ul></section>
        </div>

{X.cta(t, pose='thumbs-up-side')}

        <section class="plan-faq">
          <h2>{s['faq_h']}</h2>
{chr(10).join(f'          <details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in faq)}
        </section>

        <section class="ex-similar">
          <h2>{s['others']}</h2>
          <ul class="plain-links">{others}</ul>
        </section>

        <p class="meta sources">{s['tm']}<br />{s['sources']}: {' · '.join(f'<a href="{u}" rel="nofollow noopener">{esc(re.sub(r"^https?://(www\.)?", "", u).split("/")[0])}</a>' for u in a['sources'])}</p>'''
    return X.shell(lang, cpath(lang, k), s['title'].format(app=app), s['desc'].format(app=app, date=CHECKED[lang]),
                   body, [(l, cpath(l, k)) for l in LANGS], ld)


def hub_page(lang):
    """All apps in one table, the honest best-for list, then the one-on-one pages."""
    s, t = S[lang], X.T[lang]
    i = 0 if lang == 'en' else 1
    names = {'grasp': 'Grasp', **{k: a['name'] for k, a in APPS.items()}}
    head = ''.join(f'<th scope="col">{c[1 + i]}</th>' for c in COLS)
    rows = []
    for k in ['grasp', *APPS]:
        sh = SHORT[k]
        cells = ''.join(f'<td><span class="sym {SYMBOL[sh[c[0]]][0]}">{SYMBOL[sh[c[0]]][1]}</span></td>' for c in COLS)
        name = f'<a href="{cpath(lang, k)}">{esc(names[k])}</a>' if k != 'grasp' else 'Grasp'
        me = ' class="me"' if k == 'grasp' else ''
        rows.append(f'<tr{me}><th scope="row"><span class="app-cell">{logo(k, "", 32)}<span>{name}<small>{esc(sh["price"][i])}</small></span></span></th>{cells}</tr>')
    best = ''.join(f'<li>{logo(b[2], "", 28)}<span><b>{esc(names[b[2]])}</b>: {esc(b[i])}</span></li>' for b in BEST)
    cards = ''.join(f'<li><a href="{cpath(lang, k)}">{logo("grasp", "", 28)}<span>{'vs' if lang == 'en' else 'أو'}</span>{logo(k, "", 28)}<b>{esc(a["name"])}</b></a></li>'
                    for k, a in APPS.items())
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': s['hub_h1'], 'inLanguage': lang,
          'dateModified': '2026-10-27'}
    body = f"""        <h1>{s['hub_h1']}</h1>
        <p class="lede">{s['hub_p'].format(date=CHECKED[lang])}</p>

        <section class="ex-dose">
          <h2>{s['all_h']}</h2>
          <div class="table-scroll">
          <table class="cmp-all">
            <thead><tr><th scope="col">{s['app']}</th>{head}</tr></thead>
            <tbody>
              {chr(10).join(rows)}
            </tbody>
          </table>
          </div>
          <p class="meta">{s['legend']}</p>
        </section>

        <section class="about-sec">
          <h2>{s['best_h']}</h2>
          <ul class="best-list">{best}</ul>
        </section>

        <section class="about-sec">
          <h2>{s['one_h']}</h2>
          <ul class="vs-cards">{cards}</ul>
        </section>

{X.cta(t, pose='thumbs-up-side')}

        <p class="meta sources">{s['tm']}</p>"""
    return X.shell(lang, hub(lang), s['hub_title'], s['hub_p'].format(date=CHECKED[lang]), body,
                   [(l, hub(l)) for l in LANGS], ld, og_type='website')


def sitemap():
    sm = os.path.join(X.SITE, 'sitemap.xml')
    text = open(sm, encoding='utf8').read()
    text = re.sub(r'\n  <!-- compare:start -->.*<!-- compare:end -->', '', text, flags=re.S)
    entries = []
    for paths in [[(l, hub(l)) for l in LANGS]] + [[(l, cpath(l, k)) for l in LANGS] for k in APPS]:
        alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{X.BASE}{p}"/>' for l, p in paths)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{X.BASE}{paths[0][1]}"/>'
        entries += [f'  <url>\n    <loc>{X.BASE}{p}</loc>{alts}\n  </url>' for _, p in paths]
    text = text.replace('\n</urlset>', '\n  <!-- compare:start -->\n' + '\n'.join(entries) + '\n  <!-- compare:end -->\n</urlset>')
    with open(sm, 'w', encoding='utf8', newline='\n') as f:
        f.write(text)


if __name__ == '__main__':
    for lang in LANGS:
        X.write(hub(lang), hub_page(lang))
        for k, a in APPS.items():
            X.write(cpath(lang, k), page(k, a, lang))
    sitemap()
    print(f'{len(APPS)} comparisons x {len(LANGS)} languages')
