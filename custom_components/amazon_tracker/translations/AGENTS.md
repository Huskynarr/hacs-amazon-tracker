# translations/ — config-flow i18n

Child of `custom_components/amazon_tracker/AGENTS.md`. Covers only `translations/*.json`.

## OVERVIEW
HA config-flow + options-flow UI strings. 4 languages: `de.json`, `en.json`, `es.json`, `fr.json`. Not runtime email-parsing i18n (that lives in `const.py`).

## STRUCTURE
All 4 files share an identical JSON skeleton (50 lines each), differing only in string values:

```
config.step.user           # IMAP connection form (6 data keys)
config.step.amazon         # Amazon settings form (4 data keys)
config.error               # invalid_auth, cannot_connect, unknown
config.abort               # already_configured
options.step.init          # Options-flow form (same 4 Amazon data keys)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a UI label | `data` block in the matching step in every `*.json` | Key must match the `CONF_*` constant in `const.py` |
| Add a new language | Copy `en.json` → rename to `<lang>.json` → translate values | Also add `EMAIL_SUBJECTS`/`CARRIER_PATTERNS`/months in `const.py`/`email_parser.py` for email parsing |
| Add an options-flow field | `options.step.init.data` in all 4 files | Schema key must match `OptionsFlowHandler` in `config_flow.py` |
| Add an error message | `config.error` in all 4 files | Key must match `errors["base"]` set in `ConfigFlow.async_step_user` |

## CONVENTIONS
- Data keys are the raw `CONF_*` snake_case names (`imap_server`, `tracking_duration`, etc.), not display labels. HA maps the schema key to the translation key automatically.
- `config.step.user` corresponds to `ConfigFlow.async_step_user`; `config.step.amazon` to `async_step_amazon`; `options.step.init` to `OptionsFlowHandler.async_step_init`. Step IDs must match the `step_id=` argument in `async_show_form`.
- Error keys (`invalid_auth`, `cannot_connect`, `unknown`) are the exact values assigned to `errors["base"]` in `config_flow.py`.
- Abort key `already_configured` maps to the `async_set_unique_id` + `_abort_if_unique_id_configured` flow.

## ANTI-PATTERNS
- Do not rename JSON keys without updating the matching `CONF_*` constant or `step_id` — HA silently shows the raw key if the translation is missing.
- Do not add a language here without also adding email-parsing support in `const.py` (`EMAIL_SUBJECTS`, `CARRIER_PATTERNS`) and `email_parser.py` (months dict). Config-flow i18n alone does not make a domain usable.

## NOTES
- **No `it.json`.** `amazon.it` is in `AMAZON_DOMAINS` (language=`"it"`) but has no config-flow translation file. HA falls back to `en.json` for the Italian config-flow UI. This is a separate gap from the missing Italian email-parsing patterns (see parent AGENTS.md NOTES).
- The 4 files are structurally identical — any structural divergence (missing key, extra key, renamed step) is a bug, not an intentional difference. Diff against `en.json` to find drift.
- These translations cover only the config/options UI. The Lovelace cards in `../static/` carry their own independent translation dicts (different keys, different strings).
