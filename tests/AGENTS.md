# TESTS KNOWLEDGE BASE

**Generated:** 2026-08-08
**Scope:** `tests/` directory only. Root AGENTS.md covers pytest invocation, conftest's sys.modules mocking rationale, and the no-pytest-homeassistant-custom-component stance. This file does not repeat any of that.

## OVERVIEW
pytest suite for the amazon_tracker integration. HA and aioimaplib are fully mocked at import time, so tests exercise integration logic in isolation, not the real HA lifecycle.

## STRUCTURE
| File | Lines | What it tests |
|------|-------|---------------|
| `conftest.py` | 24 | sys.modules injection of MagicMock for all `homeassistant.*` and `aioimaplib` before test imports. No fixtures. |
| `__init__.py` | 1 | empty package marker |
| `test_const.py` | 185 | Pure data validation of `const.py`: AMAZON_DOMAINS (7 domains, fields), EMAIL_SUBJECTS (4 statuses), STATUS_PRIORITY ordering, TRACKING_PATTERNS (8 carriers), CARRIER_PATTERNS (4 languages). No mocking. |
| `test_email_parser.py` | 308 | `AmazonEmailParser.parse_email` with raw emails built via `email.message.EmailMessage`. Sender validation, status per language, order number, carrier per language, tracking per carrier, delivery date (de/en/fr, past-date wrap), product name, `build_imap_search_query` (0/1/N domains). |
| `test_store.py` | 197 | `PackageStore`. Mocks `homeassistant.helpers.storage.Store`. async_load, `merge_packages` (new, forward-only status, fill-if-missing fields, last_updated always wins), `get_active_packages` (age + delivered filters), `cleanup_old_packages`. |
| `test_imap_client.py` | 172 | `ImapClient`. Mocks `aioimaplib.IMAP4_SSL`. connect (success/login-fail/select-fail), disconnect, `fetch_existing_emails`, `_fetch_new_emails` (last-10 limit), `test_connection` static. |
| `test_config_flow.py` | 88 | `ConfigFlow`. Mocks `ImapClient.test_connection`. `async_step_user` (form, connection test pass advances to amazon step, fail shows error), `async_step_amazon` (creates entry with data+options). |

## WHERE TO LOOK
| Source module | Test file |
|---------------|-----------|
| `const.py` | `test_const.py` |
| `email_parser.py` | `test_email_parser.py` |
| `store.py` | `test_store.py` |
| `imap_client.py` | `test_imap_client.py` |
| `config_flow.py` | `test_config_flow.py` |
| `sensor.py` | none |
| `coordinator.py` | none |
| `__init__.py` (setup/unload) | none |

## CONVENTIONS
- Raw emails built inline with `email.message.EmailMessage` + `set_content` / `set_param`. No `.eml` fixture files.
- No shared fixtures in conftest. Each test constructs its own mocks. Common shape: `store = PackageStore(MagicMock(), "test_entry")` where the hass arg is a plain MagicMock.
- Imports use `from custom_components.amazon_tracker.X import Y`. conftest's sys.modules patching runs at collection, before test modules import, so HA symbols arrive as MagicMock.
- pytest-asyncio runs in **strict** mode (pytest.ini has no `asyncio_mode` entry). Every async test must carry `@pytest.mark.asyncio` or it silently skips.
- Mock assertions: `assert_called_with` / `assert_called_once` / `assert_not_called`.

## ANTI-PATTERNS / GOTCHAS
- conftest injects module-level MagicMocks, so `isinstance(obj, DataUpdateCoordinator)` always returns False. Tests cannot assert on HA base-class types. They check integration-specific behavior only.
- Real HA lifecycle is not exercised: no `async_setup_entry` forwarding, no platform dispatch, no `async_update_listeners`, no Store persistence to disk. Classes are tested in isolation.
- `test_imap_client` mocks `aioimaplib.IMAP4_SSL` at module level. Any test importing `aioimaplib` directly gets the conftest mock, not the real library. Do not expect real IMAP semantics.
- `@pytest.mark.asyncio` is mandatory. A missing marker means the coroutine is never awaited and the test passes vacuously (0 ran or collection-only). Easy to miss.
- MagicMocks return MagicMocks for any attribute or call, so a typo'd method name on a mocked HA object will not raise. Verify calls against the real integration method names, not the mock's surface.

## NOTES
- Coverage gaps: `sensor.py` (`AmazonPackageSensor`, `PendingPackagesSensor`) and `coordinator.py` (`AmazonTrackerCoordinator`, IMAP+store+sensor orchestration, IDLE loop, reconnect backoff) have no tests. Adding them means standing up mocks for the coordinator's dependencies (ImapClient, PackageStore, hass, ConfigEntry) without real HA base classes.
- `test_const.py` is the only file that does not depend on the HA/aioimaplib mocks. It can run against the real `custom_components.amazon_tracker.const` with zero conftest support.
- New languages or carriers added to `const.py` should get parallel cases in `test_const.py` (structure) and `test_email_parser.py` (parsing per language/carrier). The data-driven design means parser tests loop over the same dicts the parser uses, so a missing language is caught structurally.
