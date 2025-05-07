# Amazon Package Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40Huskynarr-blue.svg)](https://github.com/Huskynarr)

This repository contains both a HACS custom component and a Home Assistant add-on for tracking Amazon packages.

## HACS Custom Component

### Installation

1. Install HACS if you haven't already
2. Add this repository to HACS:
   - Repository: `https://github.com/Huskynarr/hacs-amazon-tracker`
3. Search for "Amazon Package Tracker" in HACS
4. Click Install
5. Restart Home Assistant

### Configuration

1. Go to Home Assistant Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "Amazon Package Tracker"
4. Enter your Amazon credentials
5. The integration will automatically fetch your active orders

## Home Assistant Add-on

### Installation

1. Add this repository to your Home Assistant instance:
   ```yaml
   addons:
     - name: "Amazon Package Tracker"
       repository: https://github.com/Huskynarr/hacs-amazon-tracker
   ```
2. Install the "Amazon Package Tracker" add-on
3. Configure your Amazon credentials in the add-on configuration
4. Start the add-on

### Configuration

1. Go to the Add-ons section in Home Assistant
2. Click on "Amazon Package Tracker"
3. Configure your Amazon credentials in the Configuration tab
4. Save the configuration
5. Start the add-on

## Usage

After installation, you can add the following cards to your dashboard:

### All Packages Card
```yaml
type: custom:amazon-tracker-card
```

### Pending Packages Card
```yaml
type: custom:pending-packages-card
```

### Example Dashboard Configuration
```yaml
views:
  - title: "Amazon Pakete"
    cards:
      - type: custom:pending-packages-card
      - type: custom:amazon-tracker-card
```

## Features

- Track all active Amazon orders
- Display delivery status and expected delivery dates
- Show shipping carrier logos
- Automatic updates of delivery status
- Easy configuration through Home Assistant UI
- Separate view for pending packages
- Sorting by expected delivery date

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/Huskynarr/hacs-amazon-tracker/issues).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
