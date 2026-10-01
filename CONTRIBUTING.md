# Contributing

1. Create short-lived branches from `develop`; reserve `main` for stable, demo-ready releases.
2. Use focused branches such as `feature/...`, `fix/...`, `docs/...` or `codex/...`, and reference the Jira/GitHub ticket in the pull request.
3. Open pull requests against `develop`. Promote tested integration changes from `develop` to `main` through a separate pull request.
4. Keep public API and schema changes explicit and update the relevant documentation.
5. Run `python -m pytest -q tests` before opening a pull request and require the GitHub Actions CI check to pass.
6. Never commit `.env`, API keys, database passwords or OCI credentials.
7. Include tests for contract, persistence or domain changes.
