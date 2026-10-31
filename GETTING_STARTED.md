# Getting started

This guide covers working on the catalogue from a local clone. Contributing to the project through GitHub's website needs no setup beyond the issue forms; see [CONTRIBUTING.md](CONTRIBUTING.md) for the research standards.

## Set up

1. Clone the repository and open the folder in a terminal.
2. Install Python 3.11 or later. On Windows, install it from [python.org](https://www.python.org/downloads/) or the Microsoft Store and make sure `python` runs from a new terminal window. No third-party packages are needed.

## Edit and check

Edit `data/treasures.json`, never the generated section of `README.md`. Then run:

```bash
python3 scripts/build_readme.py
python3 scripts/validate.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

On Windows, use `python` or `py` in place of `python3` if that is the command your installation provides.

The offline validator does not contact external websites or decide legal status. The same checks run on every push and pull request through the **Validate catalogue** workflow under the repository's **Actions** tab.

## Check links

`python3 scripts/check_external_links.py` audits every item and rights URL and writes `docs/link-audit.json`. The **Link audit** workflow runs the same script each quarter and on demand, and attaches the report to the run as a downloadable artifact. A 403, 429 or timeout is not proof that a link is broken; see [CONTRIBUTING.md](CONTRIBUTING.md).
