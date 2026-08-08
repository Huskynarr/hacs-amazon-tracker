# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-08-08

### Added
- 7 new Amazon domains: amazon.com.au, amazon.nl, amazon.pl, amazon.se, amazon.com.mx, amazon.in, amazon.co.jp
- Config-flow translations for Dutch (nl), Polish (pl), Swedish (sv), Japanese (ja)
- Italian language support: subject patterns, carrier patterns, month names, it.json translation
- Tracking number patterns for 9 carriers: Royal Mail, USPS, Colissimo, Chronopost, Correos, SEUR, Poste Italiane, SDA, BRT
- HA services: `scan_now` (manual IMAP email scan) and `remove_package` (remove package from store)
- 19 bundled carrier logo SVGs in `static/carrier-logos/`
- Coordinator test coverage (9 tests)
- Sensor test coverage (15 tests)
- Ruff linting in CI with custom rule config
- Pre-commit hooks (ruff check+format, trailing whitespace, YAML/JSON validation)
- pyproject.toml (replaces pytest.ini + requirements.txt)
- Basedpyright type-checking in CI
- Coverage reporting with pytest-cov + codecov upload
- MIT LICENSE file
- SECURITY.md with private vulnerability reporting instructions
- CODE_OF_CONDUCT.md (Contributor Covenant v2.0)
- CONTRIBUTING.md with dev setup and PR process
- .github/FUNDING.yml (GitHub Sponsors, Ko-fi, Buy Me a Coffee)
- Issue templates: bug_report.md, feature_request.md, config.yml
- Pull request template with checklist
- .github/dependabot.yml for pip and GitHub Actions
- "Open in HACS" button in README
- "Sponsor this Project" section with badges
- AGENTS.md knowledge base (root + 4 subdirectories)

### Changed
- Bumped minimum Home Assistant version from 2024.1.0 to 2025.6.0
- Pass `config_entry=entry` explicitly to DataUpdateCoordinator (required since HA 2026.8)
- Overhauled README: 8 badges, domain table, options table, carrier logos guide, debug guide
- Manifest keys sorted alphabetically (hassfest requirement)
- Removed root-level manifest.json (caused phantom integration in hassfest)
- hacs.json: removed deprecated `domains` and `iot_class` keys
- Brand icon added for HACS validation

### Fixed
- Sensor leak: AmazonPackageSensor entities are now removed when packages leave the active list
- Card memory leak: both Lovelace cards now unsubscribe from `state_changed` in `disconnectedCallback`
- Locale-dependent IMAP date: `build_imap_search_query` now hardcodes English month abbreviations instead of using `strftime`
- Private attribute access: coordinator uses `ImapClient.is_connected` property instead of `_client`
- Italian emails from amazon.it now parse correctly (were falling back to English defaults)

## [1.1.0] - 2026-08-08

### Added
- Amazon Canada (amazon.ca) domain support
- Canada Post carrier tracking patterns

### Fixed
- Issue #1: Multi-domain selection was already implemented; amazon.ca added as selectable domain
- Issue #3: 404 login page error (from old web scraping) and duplicate unique IDs (old format without entry_id) — both resolved by IMAP email parsing migration
- Issue #4: Amazon Canada support added as requested

## [1.0.0] - 2025-02-15

### Added
- Initial release
- IMAP IDLE push notification support for real-time package tracking
- Multi-domain support: amazon.de, amazon.com, amazon.co.uk, amazon.fr, amazon.es, amazon.it, amazon.ie
- Multi-language email parsing (German, English, French, Spanish)
- Carrier detection: DHL, DPD, Hermes, UPS, GLS, FedEx, Amazon Logistics, Deutsche Post
- Per-package sensors with status, tracking number, carrier, delivery date
- Aggregate "pending packages" sensor
- Custom Lovelace cards: amazon-tracker-card, pending-packages-card
- UI-only configuration (no YAML)
- Persistent storage via HA Store API
- Forward-only status progression (ordered → shipped → out_for_delivery → delivered)
