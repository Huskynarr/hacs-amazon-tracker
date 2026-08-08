# Amazon Package Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40Huskynarr-blue.svg)](https://github.com/Huskynarr)
[![license](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![tests](https://img.shields.io/badge/tests-80%20passed-brightgreen.svg)](.github/workflows/hassfest.yml)
[![python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![HA](https://img.shields.io/badge/Home%20Assistant-2025.6%2B-41bdf5.svg)](https://www.home-assistant.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ff69b4.svg)](https://github.com/sponsors/Huskynarr)

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Huskynarr&repository=hacs-amazon-tracker&category=integration)

Track Amazon packages by parsing order, shipping, and delivery notification emails via IMAP. No web scraping, no Amazon login — just your email inbox.

Supports **8 Amazon domains**: amazon.de, amazon.com, amazon.co.uk, amazon.fr, amazon.es, amazon.it, amazon.ie, and amazon.ca. Multiple domains can be selected simultaneously.

## Features

- IMAP IDLE push notifications for real-time updates (no polling required)
- Multi-domain support: track packages from multiple Amazon regions at once
- Multi-language email parsing (German, English, French, Spanish)
- Carrier detection: DHL, DPD, Hermes, UPS, GLS, FedEx, Amazon Logistics, Deutsche Post, Canada Post
- Per-package sensors with status, tracking number, carrier, and delivery date
- Aggregate "pending packages" sensor with sortable package list
- Custom Lovelace cards for your dashboard
- Fully configured via UI (no YAML configuration needed)
- Status progression is forward-only (ordered -> shipped -> out for delivery -> delivered)
- Persistent storage — survives restarts

## Screenshots

> **Screenshots wanted!** If you use this integration, please share screenshots via a [GitHub issue](https://github.com/Huskynarr/hacs-amazon-tracker/issues) and we will add them here.

### Lovelace Cards

| Card | YAML | Description |
|------|------|-------------|
| All Packages | `type: custom:amazon-tracker-card` | Shows all tracked packages with carrier, status, and delivery date |
| Pending Packages | `type: custom:pending-packages-card` | Shows only non-delivered packages with status badges |

### Sensors

| Sensor | Description |
|--------|-------------|
| `sensor.amazon_package_<order_number>` | One per order. State = status, attributes = tracking number, carrier, delivery date, product name |
| `sensor.amazon_pending_packages` | Count of non-delivered packages. Attributes include sorted package list |

## Installation

### Prerequisites

- Home Assistant 2024.1.0 or later
- An email account with IMAP access that receives Amazon order notifications
- HACS installed in Home Assistant

### HACS Installation

1. Install [HACS](https://hacs.xyz) if you haven't already
2. Add this repository to HACS:
   - Go to HACS > Integrations > "Custom Repositories"
   - Repository: `https://github.com/Huskynarr/hacs-amazon-tracker`
   - Category: Integration
3. Search for "Amazon Package Tracker" in HACS
4. Click **Install**
5. Restart Home Assistant

### Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for "Amazon Package Tracker"
3. **Step 1 — IMAP Connection**: Enter your IMAP server details (server, port, email, password, SSL, folder)
4. **Step 2 — Amazon Settings**: Select the Amazon regions to monitor and tracking preferences
5. Done! The integration will scan existing emails and start watching for new ones via IMAP IDLE

> **Important**: Do not add any configuration to your `configuration.yaml` file. This integration is configured through the UI only.

### Supported Amazon Domains

| Domain | Region | Language | Sender |
|--------|--------|----------|--------|
| amazon.de | Germany | German | order-update@amazon.de |
| amazon.com | United States | English | order-update@amazon.com |
| amazon.co.uk | United Kingdom | English | order-update@amazon.co.uk |
| amazon.ie | Ireland | English | order-update@amazon.ie |
| amazon.fr | France | French | order-update@amazon.fr |
| amazon.es | Spain | Spanish | order-update@amazon.es |
| amazon.it | Italy | Italian | order-update@amazon.it |
| amazon.ca | Canada | English | order-update@amazon.ca |

### Options

All options can be changed via **Settings** > **Devices & Services** > **Amazon Package Tracker** > **Configure**:

| Option | Default | Description |
|--------|---------|-------------|
| Amazon Regions | amazon.de | Which Amazon domains to monitor (multi-select) |
| Track packages for (days) | 14 | How long to track non-delivered packages |
| Show delivered packages | true | Whether to display delivered packages |
| Show delivered for (days) | 3 | How long to show delivered packages before hiding |

## Usage

### Lovelace Dashboard Cards

**All Packages Card:**
```yaml
type: custom:amazon-tracker-card
```

**Pending Packages Card:**
```yaml
type: custom:pending-packages-card
```

**Example Dashboard Configuration:**
```yaml
views:
  - title: "Amazon Packages"
    cards:
      - type: custom:pending-packages-card
      - type: custom:amazon-tracker-card
```

### Carrier Logos

The Lovelace cards display carrier logos from `/local/carrier-logos/`. To add logos:

1. Place logo images in your HA `www/` directory: `/config/www/carrier-logos/`
2. Name them after the carrier (lowercase, spaces as hyphens): `dhl.png`, `amazon-logistics.png`, etc.
3. Include a `default.png` fallback for unknown carriers

Supported carrier logo filenames: `dhl.png`, `dpd.png`, `hermes.png`, `ups.png`, `gls.png`, `fedex.png`, `amazon-logistics.png`, `deutsche-post.png`, `canada-post.png`, `royal-mail.png`, `usps.png`

## Troubleshooting

If you encounter the error "Invalid config for 'amazon_tracker'":
1. Remove any `amazon_tracker` configuration from your `configuration.yaml`
2. Remove the integration from Home Assistant
3. Restart Home Assistant
4. Add the integration again through the UI

### Enable Debug Logging

```yaml
logger:
  default: info
  logs:
    custom_components.amazon_tracker: debug
```

### Common Issues

- **No packages detected**: Ensure Amazon notification emails go to the IMAP account you configured. Check that the correct Amazon domains are selected.
- **IMAP connection fails**: Verify server address, port (993 for SSL), and credentials. Some providers require app-specific passwords.
- **Italian emails not parsed**: Italian language support is partial — status detection and carrier/date extraction may fall back to English defaults.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- **Bug reports**: [Open an issue](https://github.com/Huskynarr/hacs-amazon-tracker/issues/new?assignees=&labels=bug&template=bug_report.md)
- **Feature requests**: [Open a feature request](https://github.com/Huskynarr/hacs-amazon-tracker/issues/new?assignees=&labels=enhancement&template=feature_request.md)
- **Security vulnerabilities**: See [SECURITY.md](SECURITY.md) — do NOT open a public issue
- **Pull requests**: Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## Sponsor

If this integration saves you time, consider [sponsoring on GitHub](https://github.com/sponsors/Huskynarr) or [buying a coffee](https://www.buymeacoffee.com/huskynarr).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
