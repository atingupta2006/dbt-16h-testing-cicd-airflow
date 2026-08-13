# CI/CD and deployment strategies

Git-based CI on a Pull Request, then deploy to **prod** on merge to `main`.

**Repo:** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  
**Files:** `.github/workflows/dbt-ci.yml`, `.github/workflows/dbt-deploy.yml`, `dbt_project/profiles.yml.example`

Command index: [`student-commands.md`](student-commands.md) §2

---

## What “gate” means (in this class)

A **gate** = must-pass quality. Here that is the **`critical`** tests inside **`dbt build`**.

- `dbt build` runs models **and** tests **once**.
- Critical tests use `severity: error` → if they fail, the Actions job is **red**.
- warn_only tests may show **WARN** → job can stay **green** when `ERROR=0`.

We do **not** run `dbt test` again in a second job (that would cost extra Snowflake time for no class benefit).

Airflow is different on purpose: it often runs `dbt test --select tag:critical` as its **own** task after `dbt run` (see [`airflow-dags.md`](airflow-dags.md)).

---

## At work vs in this class

| In a company | What we show here |
|--------------|-------------------|
| PR pipeline builds and tests a **dev** warehouse | **dbt CI** → one job: `dbt build --target dev` → `ANALYTICS_DEV` |
| Must-pass checks fail the pipeline | Critical tests inside that build (severity error) |
| Deploy **promotes** to production | **dbt Deploy Prod** → `dbt build --target prod` → `ANALYTICS` |
| Prod is not “the same table moved” | Two copies of `FCT_ORDERS` in two schemas |

---

## Workflows (easy graph)

```text
Pull Request  →  dbt CI
                   one job: debug → parse → dbt build --target dev

Merge to main →  dbt Deploy Prod
                   one job: parse → dbt build --target prod
```

Open **Actions** (or the Checks tab on the PR). You should see **one** CI job: **Build (dev)**.

---

## What each piece does

### dbt CI (on Pull Request)

| Step | Command | What “green” means |
|------|---------|-------------------|
| debug / parse | connection + project OK | |
| **dbt build (dev)** | models + **all** tests once | `ANALYTICS_DEV` updated. **WARN=2** OK if **ERROR=0**. Critical failure → job red. |

### dbt Deploy Prod (on push to `main`)

| Step | Command | Writes to |
|------|---------|-----------|
| parse | `dbt parse --target prod` | (compile check) |
| **dbt build (prod)** | models + all tests once | `OLIST_DB.ANALYTICS` |

---

## Three deployment strategies (live)

| Strategy | How you prove it |
|----------|------------------|
| **1. Dev vs prod environments** | CI uses `dev` / `ANALYTICS_DEV`. Deploy uses `prod` / `ANALYTICS`. |
| **2. Gate = critical inside build** | Critical tests fail the job if they fail (`severity: error`). |
| **3. Promotion by rebuild** | dbt does **not** move tables. It builds again into the prod schema. Two `COUNT(*)` queries (below). |

**If asked (say only):** rollback = revert the merge on `main` and let Deploy Prod run again.

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
2. Wait for **dbt CI** → job **Build (dev)** green.  
3. Open the build log: you may see `WARN=2` and still green (`ERROR=0`).  
4. Merge the PR to `main`.  
5. **Actions** → **dbt Deploy Prod** → green.

### What to click (Actions)

1. Repo → **Actions** (or PR → **Checks**).  
2. Click the run **dbt CI** → job **Build (dev)**.  
3. After merge: Actions → **dbt Deploy Prod** → job **Deploy (prod)**.

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
| Actions CI | One job **Build (dev)** |
| Deploy | One job **Deploy (prod)** |

---

## Glossary

| Term | Meaning here |
|------|----------------|
| **Job** | A box on the Actions graph |
| **Gate** | Must-pass quality — here, **critical** tests inside `dbt build` |
| **Target** | dbt `dev` or `prod` in `profiles.yml` (different schemas) |

---

## FAQ

| Question | Answer |
|----------|--------|
| Why is CI green with WARN? | warn_only is heads-up. `dbt build` exits 0 when ERROR=0. |
| Why not a second test job? | Build already ran all tests once. Re-running critical only costs warehouse time. |
| Why does Airflow still run `tag:critical` alone? | After `dbt run` (models only), Airflow adds a dedicated test task — different shape than CI `build`. |
| Did my table “move” to prod? | No. Prod is a second build into `ANALYTICS`. |

---

## Trainer checklist (pre-open)

- [ ] Repo + **Actions** tab  
- [ ] Snowflake worksheet with the two `COUNT(*)` queries  
- [ ] `dbt-ci.yml` / `dbt-deploy.yml` / `profiles.yml.example` ready to show  
- [ ] Secrets already set on the student GitHub repo  
- [ ] Prefer one live demo PR at a time (shared `ANALYTICS_DEV`)
