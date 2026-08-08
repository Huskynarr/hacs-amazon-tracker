# Contributing to Amazon Package Tracker

Thank you for your interest in contributing! This document covers the basics of getting started.

## Prerequisites

- Python 3.12 or later
- [git](https://git-scm.com/)
- A GitHub account

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Huskynarr/hacs-amazon-tracker.git
cd hacs-amazon-tracker

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install aioimaplib voluptuous pytest pytest-asyncio
```

## Running Tests

Tests run without Home Assistant installed — the test conftest mocks all `homeassistant.*` and `aioimaplib` modules via `sys.modules`.

```bash
python -m pytest tests/ -v
```

All tests must pass before a pull request can be merged.

## Code Style

- Use `from __future__ import annotations` in every Python module.
- Use lowercase `dict[str, Any]` and `list[str]` instead of `Dict` / `List`.
- Module-level logger: `_LOGGER = logging.getLogger(__name__)`.
- Follow the existing patterns in the codebase. When in doubt, match what you see.

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `custom_components/amazon_tracker/` | The integration itself |
| `tests/` | pytest test suite |
| `.github/workflows/` | CI pipelines (HACS validation, hassfest, tests) |

See `AGENTS.md` in the repo root and subdirectories for a detailed code map and conventions.

## Making Changes

1. **Fork** the repository and create a branch from `main`.
2. **Write tests** for any new functionality. The project uses a data-driven design — if you add a language, carrier, or domain to `const.py`, add matching test cases in `tests/test_const.py` and `tests/test_email_parser.py`.
3. **Run tests**: `python -m pytest tests/ -v`
4. **Commit** with a clear, descriptive message.
5. **Open a pull request** using the PR template.

### Adding a New Amazon Domain

1. Add an entry to `AMAZON_DOMAINS` in `const.py` with `name`, `sender`, and `language`.
2. If the language is new, add subject patterns to `EMAIL_SUBJECTS`, carrier patterns to `CARRIER_PATTERNS`, and month names to `email_parser.py` `_extract_delivery_date`.
3. Add a translation file in `translations/<lang>.json`.
4. Add test cases in `tests/test_const.py`.

### Adding a New Carrier

1. Add tracking number regex patterns to `TRACKING_PATTERNS` in `const.py`.
2. Add carrier detection regex to `CARRIER_PATTERNS[language]` for each relevant language.
3. Add test cases in `tests/test_const.py` and `tests/test_email_parser.py`.

## Pull Request Process

1. Ensure all tests pass: `python -m pytest tests/ -v`
2. Update the `manifest.json` version in **both** locations (repo root and `custom_components/amazon_tracker/`) if you are releasing a new version.
3. Keep both `manifest.json` files in sync — version, requirements, codeowners.
4. Reference any related issues in your PR description (e.g., `Closes #123`).
5. Wait for CI checks (HACS validation, hassfest, tests on Python 3.12 and 3.13) to pass.

## Reporting Issues

Use the GitHub issue templates for bug reports and feature requests. For security vulnerabilities, see [SECURITY.md](SECURITY.md) — do not open a public issue.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
