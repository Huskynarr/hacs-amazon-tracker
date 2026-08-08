## Description

Brief description of what this PR does and why.

## Related Issues

- Closes #123
- Related to #456

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] New Amazon domain added
- [ ] New carrier added
- [ ] New language support

## Changes Made

- Change 1
- Change 2

## Checklist

- [ ] My code follows the project's code style (`from __future__ import annotations`, lowercase generics, module-level logger)
- [ ] I have added tests for any new functionality
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] If a new Amazon domain was added, I also added matching `EMAIL_SUBJECTS`/`CARRIER_PATTERNS`/month names (or the language already exists)
- [ ] If a new language was added, I added a `translations/<lang>.json` file
- [ ] I updated both `manifest.json` files (repo root + `custom_components/amazon_tracker/`) if the version changed
- [ ] I have not introduced any `as any`, `@ts-ignore`, or type suppressions
- [ ] I have not added `aioimaplib` to only `requirements.txt` (it must also be in `manifest.json`)
- [ ] I did not change `IDLE_TIMEOUT` above 29 minutes or remove the `MAX_BACKOFF` cap
