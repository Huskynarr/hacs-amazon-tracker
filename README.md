# Amazon Package Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40Huskynarr-blue.svg)](https://github.com/Huskynarr)

This custom component allows you to track your Amazon packages directly in Home Assistant. It integrates with your Amazon account to fetch active orders and their delivery status.

## Features

- Track all active Amazon orders
- Display delivery status and expected delivery dates
- Show shipping carrier logos
- Automatic updates of delivery status
- Easy configuration through Home Assistant UI

## Installation

1. Install HACS if you haven't already
2. Add this repository to HACS:
   - Repository: `https://github.com/Huskynarr/hacs-amazon-tracker`
3. Search for "Amazon Package Tracker" in HACS
4. Click Install
5. Restart Home Assistant

## Configuration

1. Go to Home Assistant Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "Amazon Package Tracker"
4. Enter your Amazon credentials
5. The integration will automatically fetch your active orders

## Usage

After installation, you can add the following to your dashboard:

```yaml
type: custom:amazon-tracker-card
```

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/Huskynarr/hacs-amazon-tracker/issues).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
