# grasp.alsouq.tech

The Grasp website. Three static pages, no build step, no dependencies —
whatever is on the `main` branch is what the site serves.

```
index.html      landing page
privacy.html    privacy policy   ← both app stores point at this
support.html    support and FAQ  ← Apple requires a working support URL
style.css       all styling, both light and dark
theme.js        the light / system / dark switch
favicon.png     browser tab icon
fonts/          IBM Plex Sans, self-hosted, with its licence
CNAME           the custom domain, read by GitHub Pages
.nojekyll       stop Pages running the files through Jekyll
```

## The theme switch

Three states. **System** is the default and means exactly the `prefers-color-scheme`
media query; **Light** and **Dark** override it and are remembered in
`localStorage` under `grasp-theme`.

`theme.js` is loaded from `<head>` without `defer`, which is deliberate: the
stored choice has to reach `<html>` before the first paint or every page load
flashes the wrong colour at the reader. The control itself is built in
JavaScript rather than written into the three pages, so if scripting is off no
dead switch appears — the site just follows the operating system, as it did
before.

## Deployment

GitHub Pages serves this repository at **https://grasp.alsouq.tech**, from
`main`, root directory. Push and the site updates a minute or so later.

Hostinger holds the domain but no longer holds the files. Its Git tool was
retired from the plan — the hPanel sidebar offers SSH, FTP and a file manager
and nothing else — and its replacement, Deployments, only applies to Web Apps,
which this is not. The only thing left in hPanel is one DNS record:

```
Type   CNAME
Name   grasp
Value  jecalion.github.io
```

`CNAME` in this repository is what tells Pages to answer for that name; delete
it and the site reverts to `jecalion.github.io/grasp-site`. `.nojekyll` stops
Pages from running the files through Jekyll, which it does by default and which
this site has no use for.

## Why the fonts are here rather than on a CDN

A privacy policy that ships the reader's IP address to a third party in order
to render itself contradicts its own first paragraph. IBM Plex Sans is SIL
Open Font Licence, so self-hosting is both permitted and the only honest
option. `fonts/OFL.txt` is the licence, which that licence requires to travel
with the font.

The stylesheet falls back to the system typeface, so the pages stay readable
even if the font files fail to load.

## Changing the privacy policy

The prose lives at `docs/PRIVACY.md` in the app repository, because it has to
describe what the app actually does. `privacy.html` here is the published
version of it.

**Change both together.** Google compares the policy against the Data safety
form, and a policy that contradicts the app is worse than no policy at all.
