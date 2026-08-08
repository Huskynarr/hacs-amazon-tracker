# static/ — Lovelace custom cards

Child of `custom_components/amazon_tracker/AGENTS.md`. Covers only `static/*.js`.

## OVERVIEW
Two Lovelace custom elements (Web Components, no framework, no build step): `amazon-tracker-card` (all packages) and `pending-packages-card` (pending only). Loaded via `type: custom:amazon-tracker-card` / `custom:pending-packages-card` in dashboard YAML.

## STRUCTURE
| File | Lines | Element | Data source |
|------|-------|---------|-------------|
| `amazon-tracker-card.js` | 217 | `AmazonTrackerCard` | All `sensor.amazon_package_*` entities (per-order sensors) |
| `pending-packages-card.js` | 222 | `PendingPackagesCard` | Single `sensor.amazon_*pending_packages` entity's `packages` attr |

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a card translation | `static get translations()` in both files | Keys are independent from `translations/*.json`; add to all 4 language blocks |
| Change card layout | `render()` (card shell + `<style>`) and `updateContent()` (package rows) | Shadow DOM; styles are scoped inside |
| Change sort order | `updateContent()` sort lambda in `amazon-tracker-card.js` | Uses `9999-99-99` sentinel for null dates (mirrors `PendingPackagesSensor`) |
| Add a status badge style | `_statusClass()` + `.status-*` CSS in `pending-packages-card.js` | `amazon-tracker-card` has no badges, only text |
| Change carrier logo | `carrier-logos/${carrierLower}.png` path in both files | Logos served from HA `/local/` (i.e. `/www/carrier-logos/`); `onerror` falls back to `default.png` |

## CONVENTIONS
- Both cards: `HTMLElement` + Shadow DOM (`attachShadow({ mode: 'open' })`). No Lit, no framework.
- `setConfig(config)` stores config and calls `render()`. Neither card reads any config options — `config` is unused beyond storage.
- `set hass(hass)` stores hass and calls `updateContent()`. HA pushes new hass on every state change.
- `connectedCallback` subscribes to `state_changed` events via `this._hass.connection.subscribeEvents`. Re-renders on every entity state change in HA.
- Translations: `static get translations()` returns `{ en, de, fr, es }`. `_t(key)` resolves via `hass.language` (first 2 chars), falls back to `en`, then to the raw key.
- Carrier name → logo filename: `carrier.toLowerCase().replace(/\s+/g, '-')` (e.g. `Amazon Logistics` → `amazon-logistics.png`).
- CSS uses HA theme vars: `--ha-card-background`, `--primary-color`, `--secondary-text-color`, `--warning-color`, `--info-color`, `--success-color`.

## ANTI-PATTERNS
- Do not add `disconnectedCallback` without unsubscribing from `state_changed`. Currently neither card unsubscribes — see NOTES.
- Do not import the config-flow `translations/*.json` here. Card translations are separate dicts with different keys (e.g. `no_packages`, `unknown_carrier` vs config-flow `invalid_auth`).
- Do not assume `hass.states` filter on `entity_id.startsWith('sensor.amazon_package_')` is precise. It matches any sensor with that prefix, including sensors from other integrations if named collidingly.

## NOTES
- **No `disconnectedCallback`.** Both cards subscribe to `state_changed` in `connectedCallback` but never unsubscribe. If the card is removed from the dashboard, the subscription leaks until HA reload. Adding `disconnectedCallback` with `this._hass.connection.unsubscribeEvents` is a real fix.
- **Re-render on every state change.** `subscribeEvents` fires for all entities, not just Amazon ones. `updateContent()` rebuilds the full innerHTML on every fire. Fine for a few packages; costly with many entities.
- **No Italian card translations.** Both `translations` dicts have `en/de/fr/es` only — no `it`. `amazon.it` users see English card labels. Matches the missing `it.json` config-flow file and missing Italian email-parsing patterns (see parent NOTES).
- **Carrier logos are user-supplied.** Neither file bundles logo images. Users must place `dhl.png`, `dpd.png`, `default.png`, etc. in `/config/www/carrier-logos/`. Missing logos silently fall back to `default.png`.
- **XSS surface.** `product_name` and `carrier` from entity attributes are interpolated into template literals without escaping. HA entity attributes are generally trusted, but a malicious or malformed email product name could inject markup.
- `amazon-tracker-card.js` truncates product names to 25 chars (22 + `...`). `pending-packages-card.js` does not truncate.
