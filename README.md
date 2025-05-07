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

### Option 1: HACS Installation

1. Install HACS if you haven't already
2. Add this repository to HACS:
   - Repository: `https://github.com/Huskynarr/hacs-amazon-tracker`
3. Search for "Amazon Package Tracker" in HACS
4. Click Install
5. Restart Home Assistant

### Option 2: Add-on Installation

1. Add this repository to your Home Assistant instance:
   ```yaml
   addons:
     - name: "Amazon Package Tracker"
       repository: https://github.com/Huskynarr/hacs-amazon-tracker
   ```
2. Install the "Amazon Package Tracker" add-on
3. Configure your Amazon credentials in the add-on configuration
4. Start the add-on

## Configuration

### HACS Installation

1. Go to Home Assistant Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "Amazon Package Tracker"
4. Enter your Amazon credentials
5. The integration will automatically fetch your active orders

### Add-on Installation

1. Go to the Add-ons section in Home Assistant
2. Click on "Amazon Package Tracker"
3. Configure your Amazon credentials in the Configuration tab
4. Save the configuration
5. Start the add-on

## Usage

After installation, you can add the following to your dashboard:

```yaml
type: custom:amazon-tracker-card
```

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/Huskynarr/hacs-amazon-tracker/issues).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
