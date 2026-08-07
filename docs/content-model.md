# iCORE Hugo Starter Content Model

This website starter uses one Markdown file per page/item.

## Sections

### About

- Path: `content/about/`
- Landing page: `content/about/_index.md`
- Use for mission, facilities, collaborations, values.

### Research

- Path: `content/research/`
- Landing page: `content/research/_index.md`
- One file per project, for example `content/research/my-project.md`.
- Suggested front matter:

```yaml
---
title: "Project Title"
summary: "1-2 sentence summary"
weight: 10
---
```

### People

- Path: `content/people/`
- Landing page: `content/people/_index.md`
- One file per person.
- Suggested front matter:

```yaml
---
title: "Full Name"
role: "Position"
summary: "Short bio line"
headshot: "/images/people/full-name.jpg"
weight: 10
---
```

- Store headshots in `static/images/people/`.
- Use 4:5 portrait images for best card and profile layout results.

### Publications

- Path: `content/publications/`
- Landing page: `content/publications/_index.md`
- One file per publication.
- Display format: CV-style rows sorted by `year` descending.
- Suggested front matter:

```yaml
---
title: "Paper Title"
authors: "Last, F.; Last, F."
year: 2026
venue: "Journal or Conference Name"
summary: "Short contribution summary"
doi: "10.xxxx/xxxxx"
pdf: "https://..."
code: "https://github.com/..."
external_url: "https://publisher-site/..."
---
```

- Optional extra field: `external_url`.
- You can convert BibTeX to this format using:

```bash
uv run tools/bibtex_to_hugo.py refs.bib
```

- Use `--overwrite` to replace existing generated publication files.
- Use `--merge` to refresh front matter from BibTeX without replacing your manually edited publication body text.

### Capabilities

- Path: `content/capabilities/`
- Landing page: `content/capabilities/_index.md`
- Use for laboratory equipment, software stacks, fabrication resources, and testing workflows.

Suggested front matter:

```yaml
---
title: "Capability Area"
summary: "Short description"
weight: 10
---
```

### Contact

- Path: `content/contact/`
- Landing page: `content/contact/_index.md`
- Maintain inquiry channels, recruitment details, and location.

## Maintenance pattern

1. Duplicate a section's sample file.
2. Update front matter fields.
3. Replace body content.
4. Commit and push.

No CMS is required for normal editing.
