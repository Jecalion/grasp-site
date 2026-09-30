/*
  Counts this page view, and presses of the App Store badge, for the
  dashboard at /stats.html. Nothing that identifies a person leaves the page.

  What is sent: the page's path, its language, the host of the page that
  linked here (or a ?ref= / ?utm_source= tag), and the browser's time zone
  name so the country can be told without the IP address. No cookie is set,
  nothing is stored in the browser, and there is no visitor id: two visits
  from the same person are two anonymous counts.

  Not sent at all when the browser asks not to be tracked (Global Privacy
  Control or Do Not Track), on a local preview, or once the site's owner has
  signed in to the dashboard on this browser (stats.html sets that flag), so
  their own visits don't inflate the numbers.

  The receiving end (supabase/functions/hit in the app repository) checks
  every value against a fixed list and adds one to a daily total.
*/
(function () {
  var ENDPOINT = 'https://krwwhpdetdcqimaqwphd.supabase.co/functions/v1/hit';

  function optedOut() {
    if (navigator.globalPrivacyControl) return true;
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1') return true;
    if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) return true;
    try {
      if (localStorage.getItem('grasp-no-count') === '1') return true;
    } catch (error) {
      /* Storage refused; count as usual. */
    }
    return false;
  }

  function send(event) {
    if (optedOut() || !navigator.sendBeacon) return;
    var params = new URLSearchParams(location.search);
    var referrer = '';
    try {
      referrer = document.referrer ? new URL(document.referrer).hostname : '';
    } catch (error) {
      /* An unparseable referrer is simply "direct". */
    }
    var zone = '';
    try {
      zone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    } catch (error) {
      /* No time zone; the country becomes unknown. */
    }
    var body = JSON.stringify({
      p: location.pathname,
      l: document.documentElement.lang || 'en',
      e: event,
      r: referrer,
      s: params.get('ref') || params.get('utm_source') || '',
      z: zone,
    });
    // text/plain needs no CORS preflight; the answer is never read.
    navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'text/plain' }));
  }

  send('view');
  document.addEventListener('click', function (event) {
    if (event.target.closest && event.target.closest('.store-badge')) send('store_click');
  });
})();
