Cloudflare Pages deploy settings
===============================

Copy these exact values into the Cloudflare Pages "Build configuration" when connecting your GitHub repo.

- Repository: (select) alexandamandatypeshit/TurboChef
- Branch: `main`
- Framework preset: `None` (Static)
- Install command: `npm ci`
- Build command: `npm run build`
- Build output directory: `_site`

Environment / Node version
- Node: Use `18` (the project includes `.nvmrc` and `package.json.engines` set to `>=18`). In Cloudflare Pages you can set `NODE_VERSION=18` in Environment Variables if required.

Notes
- The site build runs Tailwind then Eleventy; `npm ci` ensures devDependencies (Tailwind, Eleventy, PostCSS) are installed.
- If you use a different branch for production, change the Branch above accordingly.
- If you want preview builds for PRs, enable the default preview settings in Pages.

Quick CLI deploy test (optional)
```powershell
# build locally
npm ci
npm run build

# serve locally (Eleventy dev server)
npm start
```
