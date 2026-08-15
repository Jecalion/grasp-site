# grasp.alsouq.tech

The Grasp website. Three static pages, no build step, no dependencies —
whatever is on the `main` branch is what the site serves.

```
index.html      landing page
privacy.html    privacy policy   ← both app stores point at this
support.html    support and FAQ  ← Apple requires a working support URL
style.css       all styling, both light and dark
favicon.png     browser tab icon
fonts/          IBM Plex Sans, self-hosted, with its licence
```

## Deployment

Hostinger pulls this repo into the `grasp.alsouq.tech` document root. Push to
`main` and the site updates.

To set it up in hPanel: **Websites → grasp.alsouq.tech → Advanced → GIT**,
repository `https://github.com/Jecalion/grasp-site.git`, branch `main`, and an
empty install path so it deploys to the root of the subdomain.

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
