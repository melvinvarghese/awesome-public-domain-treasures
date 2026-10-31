# Upload this repository to GitHub

1. Download and extract `awesome-public-domain-treasures.zip` on your computer.
2. Sign in to GitHub and choose **New repository**. Name it `awesome-public-domain-treasures`. Select the visibility you want. Leave automatic README, license and `.gitignore` creation unchecked, then create the repository.
3. In the empty repository, choose **uploading an existing file** (or **Add file → Upload files**).
4. Open the extracted `awesome-public-domain-treasures` folder. Drag its **contents** into the upload area, not the outer folder or the ZIP. Preserve subfolders.
5. Check that `README.md`, `data`, `scripts`, `assets` and `.github` appear at the repository root. Include `.github` and `.gitignore`; file managers sometimes hide names beginning with a dot.
6. Add a commit message and commit the files. Open the **Actions** tab to see the validation run. GitHub may ask you to enable Actions according to your account settings.

If your browser does not include hidden files or folders when dragging, explicitly enable hidden-file display and select them. The workflow is under `.github/workflows/validate.yml`; issue templates are under `.github/ISSUE_TEMPLATE/`. GitHub's website uploader has file-count and size limits, but this source-only bundle is deliberately small.

For local edits, install Python 3.11 or later and run these commands from the extracted repository folder:

```bash
python3 scripts/build_readme.py
python3 scripts/validate.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The offline validator does not contact external websites or decide legal status. See [CONTRIBUTING.md](CONTRIBUTING.md) for research standards.

Official reference: [GitHub’s instructions for uploading repository files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), checked 30 October 2026. The documented browser limits are 100 files per upload and 25 MiB per file.
