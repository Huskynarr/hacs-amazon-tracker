# Amazon Paket-Tracker für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40Huskynarr-blue.svg)](https://github.com/Huskynarr)
[![license](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![HA](https://img.shields.io/badge/Home%20Assistant-2025.6%2B-41bdf5.svg)](https://www.home-assistant.io/)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ff69b4.svg)](https://github.com/sponsors/Huskynarr)

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Huskynarr&repository=hacs-amazon-tracker&category=integration)

> **Englische Version:** [README.md](README.md)

Verfolge Amazon-Pakete durch das Parsen von Bestell-, Versand- und Lieferbenachrichtigungs-E-Mails über IMAP. Kein Web-Scraping, kein Amazon-Login — nur dein E-Mail-Postfach.

Unterstützt **15 Amazon-Domains**: amazon.de, amazon.com, amazon.co.uk, amazon.fr, amazon.es, amazon.it, amazon.ie, amazon.ca, amazon.com.au, amazon.nl, amazon.pl, amazon.se, amazon.com.mx, amazon.in und amazon.co.jp. Mehrere Domains können gleichzeitig ausgewählt werden.

## Funktionen

- IMAP IDLE Push-Benachrichtigungen für Echtzeit-Updates (kein Polling nötig)
- Multi-Domain-Unterstützung: Pakete von mehreren Amazon-Regionen gleichzeitig verfolgen
- Mehrsprachige E-Mail-Parsing (Deutsch, Englisch, Französisch, Spanisch, Italienisch)
- Paketdienst-Erkennung: DHL, DPD, Hermes, UPS, GLS, FedEx, Amazon Logistics, Deutsche Post, Canada Post, Royal Mail, USPS, Colissimo, Chronopost, Correos, SEUR, Poste Italiane, SDA, BRT
- Pro-Paket-Sensoren mit Status, Sendungsverfolgungsnummer, Paketdienst und Lieferdatum
- Aggregierter "Ausstehende Pakete"-Sensor mit sortierbarer Paketliste
- Eigene Lovelace-Karten für dein Dashboard
- Vollständig über die UI konfiguriert (keine YAML-Konfiguration nötig)
- Status-Verlauf ist nur vorwärts gerichtet (bestellt -> versendet -> in Zustellung -> zugestellt)
- Persistenter Speicher — übersteht Neustarts
- HA-Services: `amazon_tracker.scan_now` (manuelle E-Mail-Abfrage) und `amazon_tracker.remove_package` (Paket entfernen)

## Screenshots

> **Screenshots gesucht!** Wenn du diese Integration nutzt, teile Screenshots über ein [GitHub-Issue](https://github.com/Huskynarr/hacs-amazon-tracker/issues) und wir fügen sie hier hinzu.

## Installation

### Voraussetzungen

- Home Assistant 2025.6.0 oder neuer
- Ein E-Mail-Konto mit IMAP-Zugang, das Amazon-Bestellbenachrichtigungen empfängt
- HACS in Home Assistant installiert

### HACS-Installation

1. Installiere [HACS](https://hacs.xyz), falls noch nicht geschehen
2. Füge dieses Repository zu HACS hinzu:
   - Gehe zu HACS > Integrationen > "Custom Repositories"
   - Repository: `https://github.com/Huskynarr/hacs-amazon-tracker`
   - Kategorie: Integration
3. Suche nach "Amazon Package Tracker" in HACS
4. Klicke **Install**
5. Starte Home Assistant neu

### Konfiguration

1. Gehe zu **Einstellungen** > **Geräte & Dienste** > **Integration hinzufügen**
2. Suche nach "Amazon Package Tracker"
3. **Schritt 1 — IMAP-Verbindung**: IMAP-Server-Daten eingeben (Server, Port, E-Mail, Passwort, SSL, Ordner)
4. **Schritt 2 — Amazon-Einstellungen**: Amazon-Regionen und Tracking-Optionen auswählen
5. Fertig! Die Integration scannt vorhandene E-Mails und überwacht neue via IMAP IDLE

> **Wichtig**: Keine Konfiguration in der `configuration.yaml` hinzufügen. Diese Integration wird ausschließlich über die UI konfiguriert.

### Unterstützte Amazon-Domains

| Domain | Region | Sprache | Absender |
|--------|--------|---------|----------|
| amazon.de | Deutschland | Deutsch | order-update@amazon.de |
| amazon.com | USA | Englisch | order-update@amazon.com |
| amazon.co.uk | Großbritannien | Englisch | order-update@amazon.co.uk |
| amazon.ie | Irland | Englisch | order-update@amazon.ie |
| amazon.fr | Frankreich | Französisch | order-update@amazon.fr |
| amazon.es | Spanien | Spanisch | order-update@amazon.es |
| amazon.it | Italien | Italienisch | order-update@amazon.it |
| amazon.ca | Kanada | Englisch | order-update@amazon.ca |
| amazon.com.au | Australien | Englisch | order-update@amazon.com.au |
| amazon.nl | Niederlande | Niederländisch | order-update@amazon.nl |
| amazon.pl | Polen | Polnisch | order-update@amazon.pl |
| amazon.se | Schweden | Schwedisch | order-update@amazon.se |
| amazon.com.mx | Mexiko | Spanisch | order-update@amazon.com.mx |
| amazon.in | Indien | Englisch | order-update@amazon.in |
| amazon.co.jp | Japan | Japanisch | order-update@amazon.co.jp |

> **Hinweis:** Niederländisch, Polnisch, Schwedisch und Japanisch haben config-flow Übersetzungen, aber das E-Mail-Parsing fällt auf Englisch zurück. Italienisch wird vollständig unterstützt.

### Optionen

Alle Optionen können unter **Einstellungen** > **Geräte & Dienste** > **Amazon Package Tracker** > **Konfigurieren** geändert werden:

| Option | Standard | Beschreibung |
|--------|----------|-------------|
| Amazon-Regionen | amazon.de | Welche Amazon-Domains überwacht werden (Mehrfachauswahl) |
| Pakete verfolgen für (Tage) | 14 | Wie lange nicht zugestellte Pakete verfolgt werden |
| Zugestellte Pakete anzeigen | true | Ob zugestellte Pakete angezeigt werden |
| Zugestellte anzeigen für (Tage) | 3 | Wie lange zugestellte Pakete angezeigt werden |

## Verwendung

### Lovelace-Dashboard-Karten

**Alle Pakete-Karte:**
```yaml
type: custom:amazon-tracker-card
```

**Ausstehende Pakete-Karte:**
```yaml
type: custom:pending-packages-card
```

**Beispiel-Dashboard-Konfiguration:**
```yaml
views:
  - title: "Amazon Pakete"
    cards:
      - type: custom:pending-packages-card
      - type: custom:amazon-tracker-card
```

### Paketdienst-Logos

Die Lovelace-Karten zeigen Paketdienst-Logos. Die Integration liefert bereits SVG-Logos für alle erkannten Paketdienste mit. Eigene Logos können unter `/config/www/carrier-logos/` abgelegt werden, um die mitgelieferten zu überschreiben.

### Services

| Service | Beschreibung |
|---------|-------------|
| `amazon_tracker.scan_now` | Manuelle IMAP-E-Mail-Abfrage auslösen. Optional `entry_id` für spezifischen Config Entry. |
| `amazon_tracker.remove_package` | Paket aus dem Speicher entfernen. Benötigt `order_number`. Optional `entry_id`. |

**Beispiel-Automatisierung:**
```yaml
automation:
  - alias: "Amazon-Pakete manuell scannen"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: amazon_tracker.scan_now
```

## Fehlerbehebung

Bei dem Fehler "Invalid config for 'amazon_tracker'":
1. Entferne jegliche `amazon_tracker`-Konfiguration aus der `configuration.yaml`
2. Entferne die Integration aus Home Assistant
3. Starte Home Assistant neu
4. Füge die Integration erneut über die UI hinzu

### Debug-Logging aktivieren

```yaml
logger:
  default: info
  logs:
    custom_components.amazon_tracker: debug
```

### Häufige Probleme

- **Keine Pakete erkannt**: Stelle sicher, dass Amazon-Benachrichtigungs-E-Mails an das konfigurierte IMAP-Konto gesendet werden. Prüfe, ob die richtigen Amazon-Domains ausgewählt sind.
- **IMAP-Verbindung schlägt fehl**: Serveradresse, Port (993 für SSL) und Zugangsdaten überprüfen. Manche Anbieter erfordern App-spezifische Passwörter.
- **Italienische E-Mails werden nicht geparst**: Italienisch wird vollständig unterstützt, aber bei einigen E-Mail-Formaten kann der Absender abweichen.

## Mitwirken

Beiträge sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien.

- **Fehlerberichte**: [Issue öffnen](https://github.com/Huskynarr/hacs-amazon-tracker/issues/new?assignees=&labels=bug&template=bug_report.md)
- **Feature-Wünsche**: [Feature-Request öffnen](https://github.com/Huskynarr/hacs-amazon-tracker/issues/new?assignees=&labels=enhancement&template=feature_request.md)
- **Sicherheitslücken**: Siehe [SECURITY.md](SECURITY.md) — KEIN öffentliches Issue öffnen
- **Pull Requests**: Verwende die [PR-Vorlage](.github/PULL_REQUEST_TEMPLATE.md)

Bitte lies den [Verhaltenskodex](CODE_OF_CONDUCT.md) vor der Teilnahme.

## Dieses Projekt unterstützen

Wenn dir diese Integration Zeit spart, erwäge die Entwicklung zu unterstützen:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor%20auf%20GitHub-%E2%9D%A4-ff69b4.svg)](https://github.com/sponsors/Huskynarr)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%E2%98%95-yellow.svg)](https://www.buymeacoffee.com/huskynarr)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Unterst%C3%BCtzen-%23FF5E5B.svg)](https://ko-fi.com/Huskynarr)

Jeder Beitrag hilft, das Projekt zu pflegen, neue Amazon-Domains hinzuzufügen und die Integration mit den neuesten Home-Assistant-Versionen kompatibel zu halten. Danke!

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz — siehe [LICENSE](LICENSE)-Datei für Details.
