# EliteKYC documentation site

MkDocs Material. All content is Markdown under `docs/`.

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

mkdocs serve          # http://127.0.0.1:8000, live reload
mkdocs build --strict # fails on any broken internal link
python3 check.py      # fails if screenshots and MANIFEST.md drift apart
```

`.github/workflows/docs.yml` builds and publishes to GitHub Pages on every push
to `main` that touches `docs-site/`. Enable Pages with source "GitHub Actions"
in the repo settings and it works as-is.

## Changing the brand

Two CSS variables at the top of `docs/assets/stylesheets/extra.css`:

```css
:root {
  --ek-brand:  #0d634e;
  --ek-accent: #5ba888;
}
```

Logo and favicon are hand-written SVGs in `docs/assets/img/`.

## Screenshots

Every page that wants one has a dashed placeholder box naming the exact file it
expects. `docs/assets/img/MANIFEST.md` lists all 18, with the page each belongs
to and what to capture.

Drop a file with the matching name into `docs/assets/img/`, then replace the
placeholder block with a normal image reference:

```markdown
<!-- before -->
<div class="ek-shot" markdown>
Screenshot pending: `assets/img/portal-dashboard.png`
</div>

<!-- after -->
![Tenant dashboard](../assets/img/portal-dashboard.png)
```

`check.py` keeps the manifest and the placeholders in sync, so it will tell you
if you add one and forget the other.

## Notes

Mermaid diagrams load `mermaid@11` from unpkg at runtime, which is how Material
ships them. Fine for public hosting. If this ever has to run on a network with
no outbound access, vendor `mermaid.min.js` into `docs/assets/javascripts/` and
add it to `extra_javascript` in `mkdocs.yml`.

The REST reference is hand-written and links out to the live Swagger UI for the
exhaustive schema. Nothing here is generated from the OpenAPI document, so a
new endpoint means a new section on the relevant `docs/api/*.md` page.
