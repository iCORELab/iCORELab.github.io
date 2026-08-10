# Bibliography Files

Store your BibTeX files here (for example, `lab-publications.bib`).

Recommended workflow:

1. Keep one primary BibTeX file for the lab, or split by topic if needed.
2. Convert/update Hugo publication entries with:

   uv run tools/bibtex_to_hugo.py bibliography/lab-publications.bib --merge

   You can pass multiple BibTeX files in one run:

   uv run tools/bibtex_to_hugo.py bibliography/lab-publications.bib bibliography/collaborator-publications.bib --merge

   Duplicate entries are deduplicated by DOI (normalized), with title/year fallback when DOI is missing.
   Patent-like entries with a BibTeX `number` field are formatted into `venue` as `U.S. Patent <number>`.

3. Use `--overwrite` only when you want to replace existing publication files entirely.
