# PROJECT KNOWLEDGE BASE

**Generated:** 2026-08-08
**Commit:** 040f935
**Branch:** main

## OVERVIEW
HACS custom component for Home Assistant that tracks Amazon packages by parsing order/shipping/delivery notification emails via IMAP IDLE push. Python 3.12+, async, aioimaplib.

## STRUCTURE
```
hacs-amazon-tracker/
├── custom_components/amazon_tracker/   # The integration (domain: amazon_tracker)
│   ├── __init__.py                     # async_setup_entry / async_unload_entry
│   ├── config_flow.py                  # 2-step UI config + options flow
│   ├── coordinator.py                  # DataUpdateCoordinator: IMAP + store + sensors
│   ├── email_parser.py                 # AmazonEmailParser + build_imap_search_query
│   ├── imap_client.py                  # ImapClient: connect/IDLE/fetch/reconnect
│   ├── sensor.py                       # AmazonPackageSensor + PendingPackagesSensor
│   ├── store.py                        # PackageStore: HA Store-backed persistence
│   ├── const.py                        # Domains, patterns, statuses, attrs
│   ├── manifest.json                   # HA manifest (v1.0.0, aioimaplib, config_flow)
│   ├── static/                         # Lovelace JS cards (not Python)
│   └── translations/                   # de/en/es/fr config-flow i18n
├── tests/                              # pytest, mocks HA via sys.modules in conftest
├── .github/workflows/                  # hacs.yml (HACS validation) + hassfest.yml (hassfest + test matrix)
├── hacs.json                           # HACS metadata
├── manifest.json                       # Root-level copy (HACS requirement)
├── pytest.ini                          # testpaths=tests
└── requirements.txt                    # aioimaplib, voluptuous, pytest, pytest-asyncio
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a config option | `const.py` (CONF_ + default) → `config_flow.py` (user/options schema) → `coordinator.py` (`_get_option`) | Options live in `entry.options`, fall back to `entry.data` |
| Add a new Amazon domain | `const.py` `AMAZON_DOMAINS` (+ sender + language) → add subject/carrier patterns if new language | Sender must be `order-update@<domain>` |
| Add a new carrier | `const.py` `TRACKING_PATTERNS` (number regex) + `CARRIER_PATTERNS[language]` (detection regex) | Parser tries carrier-specific then generic patterns |
| Add a new email language | `const.py` `EMAIL_SUBJECTS` + `CARRIER_PATTERNS` + date/month names in `email_parser.py` `_extract_delivery_date` | Months dict is hardcoded per language |
| Change poll/IDLE timing | `const.py` `DEFAULT_SCAN_INTERVAL` (30min) / `imap_client.py` `IDLE_TIMEOUT` (29min) | IDLE < 30min per RFC |
| Change retention | `coordinator.py` `cleanup_old_packages(max_age_days=60)` + options `tracking_duration`/`delivered_duration` | 60-day hard cleanup, 14-day active window |
| Add a sensor attribute | `const.py` `ATTR_*` → `sensor.py` `extra_state_attributes` → `email_parser.py` `parse_email` return dict | |
| Debug IMAP connection | `imap_client.py` `connect`/`_idle_loop`/`_reconnect` | Backoff: 30s → 600s exponential |
| Persistent storage schema | `store.py` `PackageStore` + `const.py` `STORAGE_KEY`/`STORAGE_VERSION` | HA `Store` API, key `amazon_tracker_packages_<entry_id>` |

## CODE MAP
From codegraph (16 symbols, centrality by callers):

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `AmazonTrackerCoordinator` | class | coordinator.py:36 | — | Orchestrates IMAP client + store + sensor updates; `async_initialize` → connect → fetch_existing → start_idle |
| `ImapClient` | class | imap_client.py:24 | 8 callers (config_flow, coordinator) | IMAP connect/IDLE/fetch/reconnect; `test_connection` static for config flow |
| `AmazonEmailParser` | class | email_parser.py:94 | — | Parse raw email bytes → package dict; sender validation, status/carrier/tracking/date/product extraction |
| `parse_email` | method | email_parser.py:260 | 22 callers (imap_client) | Entry point: raw bytes → dict or None |
| `build_imap_search_query` | func | email_parser.py:315 | — | Build nested `OR FROM ... SINCE` IMAP query for multi-domain |
| `PackageStore` | class | store.py:20 | 2 callers (coordinator) | HA Store-backed persistence; merge with forward-only status |
| `AmazonPackageSensor` | class | sensor.py:71 | — | Per-order sensor; native_value=status, attrs=tracking/carrier/delivery |
| `PendingPackagesSensor` | class | sensor.py:123 | — | Count of non-delivered; `packages` attr sorted by delivery date |
| `ConfigFlow` | class | config_flow.py:39 | — | 2-step: `async_step_user` (IMAP) → `async_step_amazon` (domains/options); VERSION=2 |
| `OptionsFlowHandler` | class | config_flow.py:170 | — | Editable: domains, tracking_duration, show_delivered, delivered_duration |
| `merge_packages` | method | store.py:48 | — | Dedupe by order_number; status only moves forward via `STATUS_PRIORITY` |
| `async_setup_entry` | func | __init__.py:18 | — | Creates coordinator, forwards to SENSOR platform |

## CONVENTIONS
- `from __future__ import annotations` in every module — use `dict[str, Any]` not `Dict`, `list[str]` not `List`.
- Config values read via `coordinator._get_option(key, default)` — checks `entry.options` then `entry.data`. Never access `entry.data` directly for user-tunable options.
- Status is forward-only: `STATUS_PRIORITY` in `const.py` (`ordered`=0 → `delivered`=3). `store.merge_packages` enforces — never override a higher status with a lower one.
- Unique IDs: `f"{DOMAIN}_{entry.entry_id}_{order_number}"` for package sensors, `..._pending_packages` for the aggregate.
- IMAP email address is the config-flow unique ID (`async_set_unique_id`).
- Logging: module-level `_LOGGER = logging.getLogger(__name__)` in every file; `_LOGGER.debug` for routine, `.info` for connect/parse counts, `.error`/`.warning` for failures.
- `config_flow.VERSION = 2` — schema changed since initial release.

## ANTI-PATTERNS (THIS PROJECT)
- **No `configuration.yaml` entries.** UI config flow only. README explicitly warns: remove any `amazon_tracker` YAML before re-adding.
- **No web scraping.** Replaced by IMAP email parsing (commit ee88d41). Do not reintroduce HTTP scraping of Amazon.
- **IDLE timeout must stay < 30 min** (RFC 2177). Currently 29 min — do not increase.
- **Reconnect backoff caps at 600s** (`MAX_BACKOFF`). Do not remove the cap.
- **Only fetch last 10 messages on IDLE push** (`_fetch_new_emails`: `recent_ids = message_ids[-10:]`). Intentional — full scan is `fetch_existing_emails`.
- **Do not add `aioimaplib` to root `requirements.txt` only** — it must also be in `manifest.json` `requirements` (it is) or HA won't install it.

## UNIQUE STYLES
- Tests run **without** Home Assistant installed — `tests/conftest.py` injects `MagicMock` for all `homeassistant.*` and `aioimaplib` modules via `sys.modules` before imports. This is deliberate; do not add `pytest-homeassistant-custom-component` as a hard test dependency without reworking conftest.
- Multi-language parsing is data-driven from `const.py` (`AMAZON_DOMAINS`, `EMAIL_SUBJECTS`, `CARRIER_PATTERNS`) — add languages there, not by branching in parser code.
- `static/` Lovelace cards are plain JS shipped inside the component dir, loaded via `custom:` card references — no build step, no npm.

## COMMANDS
```bash
# Tests (no HA needed — conftest mocks it)
python -m pytest tests/ -v

# Install test deps
pip install aioimaplib voluptuous pytest pytest-asyncio

# CI runs: HACS validation + hassfest + pytest on Python 3.12 & 3.13
```

## NOTES
- `manifest.json` exists in **two** places: repo root (HACS requirement) and `custom_components/amazon_tracker/` (HA requirement). Keep both in sync — version, requirements, codeowners.
- `hacs.json` `homeassistant: "2024.1.0"` is the minimum HA version.
- `_extract_delivery_date` assumes past dates wrap to next year (line 234) — fine for delivery estimates, wrong for arbitrary dates.
- `coordinator._async_update_data` accesses `self._imap_client._client` (private attr) to detect disconnect — known smell, not yet refactored.
- `email_parser._extract_product_name` is brittle (regex on free-text body); often returns None. Not a bug, a known limitation.
- No `.venv/` should be committed — `.gitignore` covers `__pycache__` but not `.venv/`; a `.venv/` is present locally (excluded from analysis).
