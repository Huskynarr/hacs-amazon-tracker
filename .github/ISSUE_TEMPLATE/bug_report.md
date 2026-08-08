---
name: Bug Report
about: Report a bug or unexpected behavior
title: "[BUG] "
labels: bug
assignees: ''
---

## Describe the Bug

A clear and concise description of what the bug is.

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. See error

## Environment

- **Integration version**: [e.g. 1.1.0 — check in HACS or the manifest]
- **Home Assistant version**: [e.g. 2024.6.1]
- **Python version**: [e.g. 3.12]
- **IMAP server**: [e.g. imap.gmail.com — do NOT share your email/password]
- **Amazon domains configured**: [e.g. amazon.de, amazon.co.uk]

## Logs

Paste relevant Home Assistant log output here. You can enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.amazon_tracker: debug
```

```
Paste log output here — remove any personal information (email addresses, passwords, IMAP server addresses)
```

## Additional Context

Add any other context about the problem here. Screenshots can be attached.
