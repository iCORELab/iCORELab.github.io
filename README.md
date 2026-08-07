# iCORE Laboratory Website (Hugo)

This is a static Hugo website starter for the iCORE laboratory at Louisiana State University.

## Why this setup

- Static HTML output suitable for GitHub Pages.
- Easy maintenance with Markdown content files.
- Reusable templates so editors only update content.

## Quick start

1. Install Hugo Extended.
2. Run local server:

```bash
hugo server -D
```

3. Open the URL shown in the terminal.

## Deploy to GitHub Pages

1. Push this repository to GitHub.
2. In repository settings, enable Pages and select GitHub Actions as the source.
3. Update `baseURL` in `config.toml`.
4. Push to `main` to deploy.

## Editing workflow

- Edit page text in `content/` Markdown files.
- Edit navigation and site metadata in `config.toml`.
- Edit visual style in `static/css/site.css`.
- Add people, projects, and publications by copying existing content file examples.

## Publications from BibTeX

Publications render as CV-style rows and are sorted by `year` descending.

To convert BibTeX entries into publication files:

```bash
uv run tools/bibtex_to_hugo.py refs.bib
```

Optional flags:

- `--output content/publications`
- `--overwrite`
- `--merge` (update front matter fields from BibTeX while preserving existing body text)

## Content model included

- About
- Research
- People
- Publications
- Contact

See `docs/content-model.md` for the starter schema and front matter fields.
