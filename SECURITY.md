# Security Policy

## Supported Versions

We release security fixes for the latest version of the Amazon Package Tracker integration only. Make sure you are running the newest version available via HACS.

| Version | Supported          |
|---------|--------------------|
| 1.1.x   | :white_check_mark: |
| < 1.1   | :x:                |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please use GitHub's **private vulnerability reporting** feature:

1. Go to the [Security tab](https://github.com/Huskynarr/hacs-amazon-tracker/security) of this repository.
2. Click **"Report a vulnerability"**.
3. Fill in the form with:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

Alternatively, you can email the maintainer directly at `admin@huskynarr.de`.

### Response Timeline

- **Acknowledgement**: within 48 hours
- **Initial assessment**: within 7 days
- **Fix or mitigation**: depends on severity, typically within 30 days for critical issues

### What to Expect

- We will acknowledge your report promptly.
- We will investigate and validate the issue.
- We will coordinate a fix and disclosure timeline with you.
- You will be credited in the release notes (unless you prefer to remain anonymous).

## Security Considerations

This integration handles IMAP email credentials. Please note:

- **Credentials are stored** in Home Assistant's encrypted config entry storage. They are never logged or transmitted outside of the IMAP connection.
- **IMAP connections** use SSL/TLS by default (port 993). Non-SSL connections are supported but not recommended.
- **Email parsing** happens locally — no data is sent to any external service besides your IMAP server.
- **No web scraping** — the integration does not make HTTP requests to Amazon. It only reads notification emails.
