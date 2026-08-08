# amazon_tracker component internals

Child of repo-root AGENTS.md. Covers only what is local to `custom_components/amazon_tracker/`. Read the root file first for project-wide structure, conventions, code map, anti-patterns, and commands.

## OVERVIEW
The integration package: config flow, IMAP coordinator, email parser, sensors, persistence. All state flows through `AmazonTrackerCoordinator`.

## STRUCTURE
9 Python modules + `manifest.json` + `static/` (Lovelace JS) + `translations/` (de/en/es/fr config-flow JSON). No build step.

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Add a tracked Amazon domain | `const.py` `AMAZON_DOMAINS` | Also add matching `EMAIL_SUBJECTS`/`CARRIER_PATTERNS`/months dict in parser, else fallback to English (see GAPS) |
| Add a carrier | `const.py` `TRACKING_PATTERNS` (number regex) + `CARRIER_PATTERNS[language]` (detection) | Parser tries carrier-specific then generic keyword+regex |
| Add a status | `const.py` `EMAIL_SUBJECTS` + `STATUS_PRIORITY` | `store.merge_packages` enforces forward-only via priority |
| Add a sensor attribute | `const.py` `ATTR_*` → `sensor.py` `extra_state_attributes` → `email_parser.parse_email` return dict | All three must move together |
| Edit merge semantics | `store.py` `merge_packages` | Non-status fields fill-once-never-overwrite |
| Edit IMAP query | `email_parser.py` `build_imap_search_query` | Binary-nested OR per domain; SINCE uses `%d-%b-%Y` |
| Edit reconnect/backoff | `imap_client.py` `_reconnect` | 30s to 600s exponential, cap at MAX_BACKOFF |
| Edit poll fallback | `coordinator.py` `_async_update_data` | Accesses private `_imap_client._client` to detect disconnect |

## CONVENTIONS (local)
- `__init__.py` only wires `async_setup_entry`/`async_unload_entry`. No logic.
- Config flow: `entry.data` holds IMAP credentials (set once), `entry.options` holds Amazon settings (editable). Never read `entry.data` for Amazon options.
- `ConfigFlow.VERSION = 2`. Bump if the schema changes.
- Unique ID of the config entry is the IMAP email address (`async_set_unique_id`).
- `sensor.py` adds per-order `AmazonPackageSensor` lazily from a `_async_add_new_sensors` callback keyed on `tracked_orders` set. Sensors are never removed (see GAPS).
- `PendingPackagesSensor` sorts packages by `estimated_delivery` using a `"9999-99-99"` sentinel so None sorts last.
- `email_parser.AmazonEmailParser.__init__` derives `_valid_senders` and `_domain_languages` from `AMAZON_DOMAINS` at construction. No runtime re-derivation.
- `_extract_delivery_date` keeps hardcoded `german_months`/`english_months`/`french_months` dicts inside the method. No `italian_months`.

## ANTI-PATTERNS (local gotchas)
- Do not add Italian-only assumptions assuming coverage. `amazon.it` is listed but Italian patterns/months do not exist; emails fall back to English defaults.
- Do not rely on `merge_packages` to correct a bad parse. Once `carrier`/`tracking_number`/`estimated_delivery`/`product_name` are set, later emails never overwrite them. Only `status` moves forward.
- Do not read `_imap_client._client` outside `coordinator._async_update_data`. It is a known smell tied to that one call site; touching it elsewhere spreads the coupling.
- Do not assume `_extract_product_name` returns a value. It is regex on free text and frequently returns None.
- IDLE timeout, backoff cap, and the 10-message IDLE-fetch slice are enforced root-wide — see root AGENTS.md ANTI-PATTERNS.
- Do not add `homeassistant` imports at module top in tests-facing modules without matching the conftest mock pattern (see root file).

## NOTES (gaps)
- amazon.it has `language="it"` in `AMAZON_DOMAINS` but no `EMAIL_SUBJECTS["it"]`, no `CARRIER_PATTERNS["it"]`, no `italian_months`. Italian emails degrade: status detection may miss, carrier extraction returns None, delivery date returns None.
- `CARRIER_PATTERNS` keys are de/en/fr/es only. Any new domain with another language gets no carrier detection until patterns are added.
- `_extract_tracking_number` generic fallback keywords are German-centric (`Sendungsnummer`, `Paketnummer`) plus English `tracking`. No French/Spanish/Italian keyword fallback.
- `_async_update_data` reaches into `_imap_client._client` (private attr) to detect a dropped connection. If `ImapClient` internals change, the coordinator's poll fallback breaks.
- `_async_add_new_sensors` never tears down `AmazonPackageSensor` entities for orders that leave `get_active_packages` (aged out or filtered). Entities persist for the HA session. Adding cleanup is a real fix, not a refactor.
- `build_imap_search_query` nests `OR` binary, depth O(n) for n domains. Fine at 7 domains; would blow the stack at hundreds.
- `build_imap_search_query` formats `SINCE` with `strftime("%d-%b-%Y")`. IMAP requires English month abbreviations (`Aug`), but strftime honors the process locale. Under a non-English locale (`fr_FR`) this emits `Août` and most IMAP servers reject the search. Run under `C`/en locale or hardcode English month names.
- `manifest.json` here must stay in sync with the repo-root `manifest.json` (HACS requirement). Version, requirements, codeowners duplicated across both.
