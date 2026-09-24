# Git workflow — CommunityLab Backend v0.1.0

## Permanent branches
- `main`: stable/demo-ready.
- `develop`: team integration.

## Suggested short-lived branches
- `feature/api-contracts`
- `feature/postgres-ingestion`
- `feature/llm-gateway`
- `feature/langgraph`
- `feature/streamlit-curation`
- `feature/oci-storage`
- `test/e2e-demo`

## Suggested initial commits
1. `chore: bootstrap CommunityLab backend v0.1.0`
2. `feat(api): add FastAPI v1 health and process contracts`
3. `feat(schemas): add versioned Pydantic domain contracts`
4. `feat(db): add PostgreSQL service and database healthcheck`
5. `feat(dashboard): add Streamlit integration dashboard`
6. `test: add API contract and fingerprint tests`
7. `ci: add GitHub Actions test workflow`
8. `docs: add architecture API contract and team integration guides`

## First push
```bash
git init
git add .
git commit -m "chore: bootstrap CommunityLab backend v0.1.0"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main

git checkout -b develop
git push -u origin develop
```
