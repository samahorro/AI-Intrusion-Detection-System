# Sprint 4 push instructions

These files are **prepared from the uploaded ZIP**, not pushed to remote GitHub. Apply the changed files onto a fresh working clone, preferably a feature branch. Do not replace teammates' newer changes.

From a clone on your computer:

```powershell
git checkout main
git pull origin main
git checkout -b robert/sprint4-soc2-cc61
# Copy the files from this bundle, preserving their relative paths.
python -m pip install -r backend/requirements.txt
python -m pytest backend/tests/test_soc2_access_control.py -v
python -m pytest backend/tests -q
python -m ruff check backend
# Check output; fix failures before committing.
git status
git add backend/app/main.py backend/tests/test_soc2_access_control.py .github/workflows/soc2-access-control.yml docs/sprint4
git commit -m "feat(security): add Sprint 4 SOC 2 CC6.1 validation and CI evidence"
git push -u origin robert/sprint4-soc2-cc61
```

Create a GitHub pull request against `main`, request review, and download the Actions evidence after the workflow runs. The workflow needs working GitHub Actions permissions and can be triggered manually once available on a workflow-enabled branch.

### Production environment notes

`APP_ENV=production` requires `SECRET_KEY` containing at least 32 characters and `FRONTEND_ORIGIN` beginning with `https://`. Inject secrets from the deployment provider, not `.env` committed to Git. Keep development defaults for local testing only.
