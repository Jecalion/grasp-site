/*
  Offers the page in the reader's own language, once.

  If the browser's preferred language is one the site has and it is not the
  page's, a slim bar appears at the top: that language's flag and its own
  name, linking to its page. It needs no translation, because it is written
  in the language it offers.

  Never a redirect: a redirect would take the English page away from search
  engines and from anyone who wanted it. Dismissing the bar, or choosing any
  language from the switcher, is remembered, and the bar does not come back.
*/
(function () {
  var KEY = 'grasp-lang';
  var LANGS = {
    en: ['English', 'gb'], ar: ['العربية', 'sa'], fr: ['Français', 'fr'], de: ['Deutsch', 'de'],
    es: ['Español', 'es'], it: ['Italiano', 'it'], tr: ['Türkçe', 'tr'], pl: ['Polski', 'pl'],
    ru: ['Русский', 'ru'], hi: ['हिन्दी', 'in'], zh: ['中文', 'cn'], ko: ['한국어', 'kr'],
    ja: ['日本語', 'jp'], id: ['Bahasa Indonesia', 'id'], pt: ['Português', 'br'],
  };

  function remembered() {
    try {
      return localStorage.getItem(KEY);
    } catch (error) {
      return null;
    }
  }
  function remember(value) {
    try {
      localStorage.setItem(KEY, value);
    } catch (error) {
      /* Storage refused; the bar may show again next time, which is harmless. */
    }
  }

  function wanted() {
    var list = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
    for (var i = 0; i < list.length; i++) {
      var code = String(list[i]).toLowerCase().split('-')[0];
      if (LANGS[code]) return code;
    }
    return null;
  }

  function start() {
    var page = document.documentElement.lang;
    document.querySelectorAll('.lang-switch a[hreflang], .flag-grid a[lang]').forEach(function (a) {
      a.addEventListener('click', function () {
        remember(a.getAttribute('hreflang') || a.getAttribute('lang'));
      });
    });
    if (remembered()) return;
    var code = wanted();
    if (!code || code === page) return;

    var bar = document.createElement('div');
    bar.className = 'lang-offer';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', LANGS[code][0]);
    bar.innerHTML =
      '<a href="' + (code === 'en' ? '/' : '/' + code + '/') + '" lang="' + code + '" hreflang="' + code + '"' +
      (code === 'ar' ? ' dir="rtl"' : '') + '>' +
      '<img src="/img/flags/' + LANGS[code][1] + '.svg" alt="" width="22" height="16" />' +
      '<span>' + LANGS[code][0] + '</span><span aria-hidden="true">' + (code === 'ar' ? '←' : '→') + '</span></a>' +
      '<button type="button" aria-label="×">×</button>';
    bar.querySelector('a').addEventListener('click', function () {
      remember(code);
    });
    bar.querySelector('button').addEventListener('click', function () {
      remember(page);
      bar.remove();
    });
    document.body.insertBefore(bar, document.body.firstChild);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
