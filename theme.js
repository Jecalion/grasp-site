/*
  Light / System / Dark.

  Loaded from <head> without `defer`, on purpose. The stored choice has to be
  on <html> before the first paint, or a reader who picked light gets a black
  flash on every page load — the one bug a theme switcher exists to avoid.
  Everything after the first function runs on DOMContentLoaded instead.

  The control is built here rather than written into the three pages. If
  JavaScript is off it cannot work, and a switch that does nothing when you
  press it is worse than no switch: this way the page simply follows the
  operating system, which is what it did before.
*/
(function () {
  var KEY = 'grasp-theme';
  var root = document.documentElement;

  function stored() {
    try {
      var value = localStorage.getItem(KEY);
      return value === 'light' || value === 'dark' ? value : 'system';
    } catch (error) {
      /* Private browsing can throw on read. Follow the system and carry on. */
      return 'system';
    }
  }

  function apply(choice) {
    if (choice === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', choice);
  }

  /* Before the body exists. */
  apply(stored());

  var OPTIONS = [
    {
      value: 'light',
      label: 'Light',
      icon:
        '<circle cx="12" cy="12" r="4"/>' +
        '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    },
    {
      value: 'system',
      label: 'System',
      icon: '<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M8.5 21h7M12 17v4"/>',
    },
    {
      value: 'dark',
      label: 'Dark',
      icon: '<path d="M20.5 13.2A8.5 8.5 0 1 1 11.3 3.5a6.6 6.6 0 0 0 9.2 9.7z"/>',
    },
  ];

  function build() {
    var header = document.querySelector('header.site .wrap');
    if (!header) return;

    var group = document.createElement('div');
    group.className = 'theme-toggle';
    group.setAttribute('role', 'radiogroup');
    group.setAttribute('aria-label', 'Colour theme');

    var buttons = OPTIONS.map(function (option) {
      var button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('role', 'radio');
      button.setAttribute('title', option.label);
      /* Icon-only, so the name has to come from the label rather than the text. */
      button.setAttribute('aria-label', option.label);
      button.dataset.theme = option.value;
      button.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
        option.icon +
        '</svg>';
      group.appendChild(button);
      return button;
    });

    function mark(choice) {
      buttons.forEach(function (button) {
        var on = button.dataset.theme === choice;
        button.setAttribute('aria-checked', on ? 'true' : 'false');
        /* Only the selected control stays in the tab order, which is how a
           radio group is meant to behave. */
        button.tabIndex = on ? 0 : -1;
      });
    }

    function choose(choice) {
      apply(choice);
      mark(choice);
      try {
        if (choice === 'system') localStorage.removeItem(KEY);
        else localStorage.setItem(KEY, choice);
      } catch (error) {
        /* Storage refused. The choice still holds for this page. */
      }
    }

    group.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-theme]');
      if (button) choose(button.dataset.theme);
    });

    group.addEventListener('keydown', function (event) {
      var step = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1 : 0;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') step = -1;
      if (!step) return;
      event.preventDefault();
      var index = buttons.indexOf(document.activeElement);
      if (index < 0) return;
      var next = buttons[(index + step + buttons.length) % buttons.length];
      choose(next.dataset.theme);
      next.focus();
    });

    mark(stored());
    header.appendChild(group);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
