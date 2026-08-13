# CI/CD and deployment strategies

Git-based CI on a Pull Request, then deploy to **prod** on merge to `main`.

**Repo:** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  
**Files:** `.github/workflows/dbt-ci.yml`, `.github/workflows/dbt-deploy.yml`, `dbt_project/profiles.yml.example`

Command index: [`student-commands.md`](student-commands.md) §2

---

## What “gate” means

A **gate** is a **must-pass quality check** after the build.

- It is **not** a special dbt command — here it is a GitHub Actions **job** (or step) that runs `dbt test --select tag:critical`.
- **Build** = run the project (may show WARN).  
- **Gate** = only must-pass tests; expect `WARN=0 ERROR=0`.
- If the gate fails, the Actions check is **red**. Whether that **blocks merging** the PR depends on GitHub branch protection (optional).

Same idea on deploy: after `dbt build --target prod`, the critical-test step is the **prod gate**.

---

## At work vs in this class

| In a company | What we show here |
|--------------|-------------------|
| PR pipeline builds and tests a **dev** warehouse | **dbt CI** → `dbt build --target dev` → schema `ANALYTICS_DEV` |
| A **gate** check fails if must-pass tests fail | Second CI job: `dbt test --select tag:critical` (merge is blocked only if branch protection requires that check) |
| Deploy **promotes** to production | **dbt Deploy Prod** → `dbt build --target prod` → schema `ANALYTICS` |
| Prod is not “the same table moved” | Two copies of `FCT_ORDERS` in two schemas |

---

## Workflows (easy graph)

```text
Pull Request  →  dbt CI
                   job 1: Build (dev)
                   job 2: Gate (critical tests)   [needs job 1]

Merge to main →  dbt Deploy Prod
                   one job: parse → build prod → critical tests
```

Open **Actions** (or the Checks tab on the PR). You should see **two boxes** on CI (Build, then Gate).

---

## What each piece does

### dbt CI (on Pull Request)

| Job | Steps | What “green” means |
|-----|--------|-------------------|
| **Build (dev)** | debug → parse → `dbt build --target dev` | Models + all tests ran on `ANALYTICS_DEV`. **WARN=2** on warn_only tests is OK if **ERROR=0**. |
| **Gate (critical tests)** | `dbt test --select tag:critical` | Must-pass tests only. Expect **WARN=0 ERROR=0**. |

The gate job also uploads `run_results.json` / `manifest.json` as an artifact (optional to open).

**Does `dbt build` already run critical tests?** Yes. `dbt build` runs models **and** their tests (including `tag:critical`). If a critical test fails, **Build (dev)** is already red.

**Why a separate Gate job then?**

| Reason | Plain meaning |
|--------|----------------|
| Clear Actions story | Box 1 = build (WARN OK). Box 2 = must-pass only (no WARN noise). |
| Same idea as Airflow | Orchestrator often runs `dbt test --select tag:critical` as its own step — not a full rebuild. |
| Explicit release check | Production pipelines often keep a dedicated quality gate even when build already tested. |

So Gate is **not** “critical was skipped in build.” It is a **focused re-check** of must-pass tests (and a teaching parallel to Airflow).

### dbt Deploy Prod (on push to `main`)

| Step | Command | Writes to |
|------|---------|-----------|
| parse | `dbt parse --target prod` | (compile check) |
| build | `dbt build --target prod` | `OLIST_DB.ANALYTICS` |
| gate | `dbt test --target prod --select tag:critical` | same prod schema |

---

## Three deployment strategies (live)

| Strategy | How you prove it |
|----------|------------------|
| **1. Dev vs prod environments** | CI uses `dev` / `ANALYTICS_DEV`. Deploy uses `prod` / `ANALYTICS`. |
| **2. Gate before release** | Deploy has a **critical test** step after the prod build. |
| **3. Promotion by rebuild** | dbt does **not** move tables. It builds again into the prod schema. Two `COUNT(*)` queries (below). |

**If asked (say only, do not demo unless extra time):** rollback = revert the merge commit on `main` and let Deploy Prod run again.

---

## Student git steps (from repo root)

```bash
git checkout -b practice/ci-check
# optional: small comment or whitespace change
git add -A
git commit -m "practice: ci check"
git push -u origin HEAD
```

1. GitHub → **Compare & pull request** → Create PR.  
2. Wait for **dbt CI** — both jobs green.  
3. Open **Build (dev)** log: you may see `WARN=2` and still green.  
4. Open **Gate (critical tests)** log: `PASS=3 WARN=0 ERROR=0`.  
5. Merge the PR to `main`.  
6. **Actions** → **dbt Deploy Prod** → green.

### What to click (Actions)

1. Repo → **Actions** (or PR → **Checks**).  
2. Click the run named **dbt CI**.  
3. Click job **Build (dev)**, then job **Gate (critical tests)**.  
4. After merge: Actions → **dbt Deploy Prod** → job **Deploy (prod)**.  
5. Optional: run page → **Artifacts** → `dbt-ci-run-results`.

---

## Snowflake proof (two copies)

```sql
-- After CI / local dev build
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;

-- After a successful Deploy Prod only
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

If prod was never deployed, the second query errors (`object does not exist`) — that is expected.

---

## Expected look

| Place | Typical result |
|-------|----------------|
| Local / CI `dbt build --target dev` | `Done. PASS=35 WARN=2 ERROR=0` |
| CI / Deploy `tag:critical` | `Done. PASS=3 WARN=0 ERROR=0` |
| Actions CI graph | Two jobs; Gate starts after Build |

---

## Glossary

| Term | Meaning here |
|------|----------------|
| **Job** | A box on the Actions graph (own machine, own checkout) |
| **Gate** | A must-pass check after the build (here: `dbt test --select tag:critical`). Not a dbt keyword — the job/step name we use for that check |
| **Artifact** | A file GitHub saves from the job (here: dbt `run_results.json`) |
| **Target** | dbt `dev` or `prod` in `profiles.yml` (different schemas) |

---

## FAQ

| Question | Answer |
|----------|--------|
| Why is CI green with WARN? | warn_only tests are heads-up. `dbt build` exits 0 when ERROR=0. |
| Why a second CI job? | Build already runs all tests (critical included). Gate is a **focused re-check** of `tag:critical` only — clearer Actions story and same pattern as Airflow. The gate fails the Actions check; whether merge is blocked depends on branch protection. |
| Did my table “move” to prod? | No. Prod is a second build into `ANALYTICS`. |
| Gate vs Airflow? | Same selection: `tag:critical`. warn_only is not in the gate. |

---

## Trainer checklist (pre-open)

- [ ] Repo + **Actions** tab  
- [ ] Snowflake worksheet with the two `COUNT(*)` queries  
- [ ] `dbt-ci.yml` / `dbt-deploy.yml` / `profiles.yml.example` ready to show  
- [ ] Secrets already set on the student GitHub repo  
- [ ] Prefer one live demo PR at a time (shared `ANALYTICS_DEV`)
