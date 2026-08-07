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
2. In repository settings, enable Pages and select GitHub Actions as the source. If Pages is set to deploy from the branch instead, GitHub will publish the repository README rather than the Hugo site.
3. Update `baseURL` in `config.toml`.
4. Push to `master` to deploy. The workflow also accepts `main` if the default branch is renamed later.

### Fallback when Pages is locked to branch publishing

If you cannot switch the repository to GitHub Actions publishing, you can keep the Hugo source on a separate branch such as `build` and publish the generated static files into `master`.

This repository includes [.github/workflows/hugo-branch-publish.yml](.github/workflows/hugo-branch-publish.yml), which builds on pushes to `build` and force-publishes `public/` to `master`.

Important constraints:

- GitHub Pages branch publishing does not rebuild when a workflow pushes with `GITHUB_TOKEN`.
- The fallback workflow therefore requires a repository secret named `PAGES_DEPLOY_TOKEN` containing a personal access token from an account that can push to this repository.
- The `master` branch becomes the published static output branch, not the source branch.
- The `build` branch becomes the Hugo source branch.

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
