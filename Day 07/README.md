# Day 7: Jenkins Multibranch Pipelines | CI/CD with GitHub PRs & Docker Deploy

## Video reference for Day 7 is the following:


---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## Table of Contents
- [Introduction](#introduction)

- [Multi-Branch Pipelines (MBP)](#multi-branch-pipelines-mbp)
  - [Multi-Branch Pipelines — What they are and why they matter](#multi-branch-pipelines--what-they-are-and-why-they-matter)

- [How Jenkins discovers and builds (at a glance)](#how-jenkins-discovers-and-builds-at-a-glance)

- [Trunk-Based CI/CD: Multibranch Flow](#trunk-based-cicd-multibranch-flow)
  - [1) Create branch (`feature/ui-font`)](#1-create-branch-featureui-font)
  - [2) Push → Branch job (build-only, fast)](#2-push--branch-job-build-only-fast)
  - [3) Open PR → PR job (preview environment)](#3-open-pr--pr-job-preview-environment)
  - [4) Gate the merge on deploy success](#4-gate-the-merge-on-deploy-success)
  - [5) Post-merge on `main`](#5-post-merge-on-main)
  - [6) Cleanup](#6-cleanup)

- [Demo: Jenkins Multi-Branch Pipeline (MBP)](#demo-jenkins-multi-branch-pipeline-mbp)
  - [Why MBP (vs a single Pipeline with many branches)](#why-mbp-vs-a-single-pipeline-with-many-branches)
  - [What we’ll do](#what-well-do)
  - [Prerequisites](#prerequisites)
  - [Step 1: Create the MBP job](#step-1-create-the-mbp-job)
  - [Step 2: Create another branch (`feature/ui`) locally and push](#step-2-create-another-branch-featureui-locally-and-push)
  - [Step 3: Let MBP discover and build the new branch](#step-3-let-mbp-discover-and-build-the-new-branch)
  - [Step 4: Open PR and Cleanup](#step-4-open-pr-and-cleanup)
    - [Verify the result (code + running app)](#verify-the-result-code--running-app)

- [Conclusion](#conclusion)

- [References](#references)

---

## Introduction

In this session we’ll set up a **Jenkins Multi-Branch Pipeline (MBP)** that automatically discovers branches/PRs and runs the pipeline wherever a `Jenkinsfile` exists. You’ll see how MBP maps cleanly to **trunk-based development**: short-lived feature branches, PR-aware builds, and `main` that stays releasable.
We’ll create an MBP against a **private GitHub repo**, push a new branch, open a PR, manually rescan (no webhooks yet), and watch Jenkins build/deploy a **Dockerized Python app** that listens on **port 5000**. (Note: 5000 is also commonly used by Jenkins agents in JNLP mode—we’re **not** using that agent port here; this is just informational.) We’ll finish by merging to `main`, rescanning, and verifying the app locally.

---


# Multi-Branch Pipelines (MBP)
### Multi-Branch Pipelines — What they are and why they matter

**Multi-Branch Pipeline (MBP)** is a Jenkins job type that scans your SCM and **automatically creates a child pipeline for every branch/PR/tag** that contains a `Jenkinsfile`. Builds are triggered by **webhooks** on pushes and PR updates, and jobs are **retired** when branches/PRs are closed. In practice, MBP maps CI directly to your branching strategy and adds **PR-aware** builds (Head/Merge) with status checks back to the repo.

With that mental model, here’s the **“what & why”** of MBP at a glance:


* **Repository-driven CI that mirrors your branching model:** Jenkins scans your Git host (GitHub/GitLab/Gitea/on-prem) and **creates one sub-job per discovered branch/PR/tag** → **no manual job sprawl**; CI automatically reflects trunk-based development where **`main` is the single source of truth** and feature/bugfix branches are short-lived.

  * **Use case:** A fintech team spins up 20 feature branches during a sprint—Jenkins auto-creates jobs for each and retires them on branch delete, no admin work.

* **Jenkinsfile-first, per branch/PR:** A ref is “buildable” only if it **contains a `Jenkinsfile`** at the expected path → **pipeline as code** per branch/PR; no Jenkinsfile → no build.

  * **Use case:** Platform team enforces that new microservices must include `Jenkinsfile`; branches without it are ignored, keeping CI clean and policy-compliant.

* **Fast feedback where code lives:** Every push to a branch—and every **PR update**—triggers CI so developers catch failures **before merging to `main`**, reducing integration pain.

  * **Use case:** Developer pushes a failing test to `feature/x`; CI fails within minutes on the branch/PR, preventing a broken `main`.

* **Lifecycle automation via webhooks:** Push a new branch → job auto-created; open/update a PR → PR job updated; close PR or delete branch → job retired. Webhooks keep discovery and builds current with zero manual effort.

  * **Use case:** After a PR is merged and `feature/y` is auto-deleted by the host, Jenkins marks the branch job orphaned and removes it (including workspace) per cleanup policy—no manual cleanup.

* **Policy by configuration (quality gates):** Enforce tests, lint, coverage **per branch/PR** and require green checks before merge.

  * **Use case:** Branch protection requires “Tests” + “Coverage ≥ 80%” checks from Jenkins; PRs can’t be merged until both are green.

* **Lower blast radius:** Build/test **in isolation** on the branch or PR job; only clean, reviewed changes land in `main`.

  * **Use case:** A risky dependency bump runs e2e tests only on the PR job; `main` remains stable for on-call.

* **Scales with teams:** New contributors and short-lived topic branches are discovered automatically—**CI stays in sync** as the repo evolves.

  * **Use case:** Hackathon week creates 50 short-lived branches; Jenkins discovers and builds them all, then prunes jobs as branches are closed.


> In trunk-based CI/CD, MBP is the glue: feature/bugfix branches stay small, PRs get tested automatically, and `main` stays releasable.


---

## How Jenkins discovers and builds (at a glance)

1. **Scan / Webhook:** Jenkins scans the repo on schedule and on webhook events (push, PR open/sync).
2. **Filter/Traits apply:** Include/exclude rules, branch build strategy, PR strategies, and fork-trust policies decide what to build.
3. **Per-branch/PR job:** Jenkins evaluates the **branch’s `Jenkinsfile`** and runs the pipeline for that ref.
4. **Status reporting:** Commit/PR status is posted back to the host (checks). Branch protection can require these to pass before merge.

---

## Trunk-Based CI/CD: Multibranch Flow

Assumptions: **Jenkins Multibranch Pipeline (MBP)**, repo with **branch protection + required checks**, containerized builds.

---

### 1) Create branch (`feature/ui-font`)

**What happens**

* Developer branches from the latest `main`. Branches are short-lived and consistently named (`feature/*`, `bugfix/*`) for CI filters.

**Why it matters**

* Trunk-based works because changes are small and fast to review/merge; staying close to `main` minimizes rework.

**Good practice**

* Rebase/merge with `main` early and often, or enable **Require branch to be up to date before merging**.
* Enforce naming via server-side rules or a pre-receive hook.

---

### 2) Push → **Branch job (build-only, fast)**

**Trigger**

* Every push to the feature branch (webhook-first; periodic scan as safety net).
  With MBP **“Exclude branches that are also filed as PRs”**, branch builds **stop** once a PR opens.

**What runs**

* **Lint/format → Compile → Unit tests → Coverage** (fast, code-centric checks).
* **Package + build the container image** (do not run it).
* **Publish artifacts/metadata** (JAR/image digest, build info; optional SBOM/signature).

**Why build-only**

* Keeps feedback ≤ **5 minutes** and avoids spending environment resources on obvious breakages.

**Operator tips**

* Cache deps (e.g., Maven `.m2`).
* Serialize per branch: `disableConcurrentBuilds()` + `milestone()` so the newest push “wins”.

---

### 3) Open PR → **PR job (preview environment)**

**Trigger**

* On PR open and each update. Use PR strategies **Head + Merge** to test both the branch tip and its merge projection into `main`.

**What runs (order to “shift left”)**

1. **Light SAST + dependency (manifest) scan** on code/lockfiles.
2. **Build image → image scan** (e.g., Trivy); **block on High/Critical**.
3. **Deploy an ephemeral preview** (namespace/stack per PR).
4. **Integration/E2E smoke** against the running app.
5. **Teardown** preview on completion/PR close (TTL just in case).

**Why it matters**

* You prove the change **runs** and integrates *before* it can merge—unit tests can’t catch integration or deploy issues.

**Forks & secrets**

* Trust policies restrict what runs for forks; run reduced checks when secrets aren’t available.

---

### 4) **Gate the merge on deploy success**

**Rule**

* PR must have **all required checks green**, including a status such as **`deploy-preview: succeeded`**, plus **“up-to-date with base”** so results reflect current `main`.

**Flow**

* If anything is red: fix → push → PR job re-runs automatically.
* Optional: **auto-merge on green** (opt-in label). High-throughput teams may add a **merge queue/train** to serialize and auto-retest.

**Why**

* This is what keeps `main` continuously releasable.

---

### 5) **Post-merge on `main`**

**Trigger**

* Merging (squash/merge/rebase) creates commits on `main`; MBP runs the `main` job.

**What runs**

* **Reuse the signed artifact/image** built in the PR (preferred) or **rebuild deterministically**.
* **Deploy to dev/stage**, run smoke checks; **promote** to higher environments with approvals/change control.
* **Full, authenticated DAST** belongs here (staging), not in PR; block on High/Critical.

**Why reuse artifacts**

* Promoting the **same digest** PR → stage → prod gives auditability and prevents “works on my build” drift.

**Release hygiene**

* Record release notes/provenance; attach SBOM and signatures to the artifact.

---

### 6) **Cleanup**

**What happens**

* Git host **auto-deletes the source branch** on merge (same-repo PRs, if enabled).
  Jenkins MBP **orphan cleanup** then prunes the retired branch job and workspace.
  A preview-env **GC/TTL** reaps stray namespaces/volumes/DBs.

**Why**

* Keeps Jenkins lean and cloud costs down; removes stale jobs and environments.

---

# Demo: Jenkins **Multi-Branch Pipeline (MBP)**

## Why MBP (vs a single Pipeline with many branches)

* **Auto-discovery:** Jenkins scans your repo and **creates one child job per branch/PR/tag** that contains a `Jenkinsfile`. No manual job sprawl.
* **PR awareness:** Builds **PR “Head”** and/or a **synthetic “Merge”** so you validate integration before merge.
* **Lifecycle automation:** New branch/PR → job created. PR closed/branch deleted → job retired.
* **Per-branch history:** Each branch/PR has its own build history, test reports, and checks.
* **Policy at scale:** Enforce quality gates (tests/coverage/lint/scans) **per branch/PR**; protect `main` with required checks.

> Key idea: You don’t list branches. MBP **finds them** and runs the pipeline where a `Jenkinsfile` exists.

---

## What we’ll do

* Create a **Multibranch Pipeline** that points at a private GitHub repo.
* Push a new branch (`feature/ui`) and watch MBP discover it.
* Discuss the **branch/PR strategies** you should use.

---

## Prerequisites

* A **private GitHub repo** with: application code, `Dockerfile`, and `Jenkinsfile` (use the one from the previous lecture).
* Jenkins has **GitHub credentials** (PAT or GitHub App) saved and working.
* (Optional but recommended) GitHub **webhook** is enabled so builds trigger immediately; a periodic scan remains as a safety net.

---

## Step 1: Create the MBP job

**New Item →** name `flask-mbp` → choose **Multibranch Pipeline**.

### Branch Sources → Add source → **GitHub**

(You could choose “Git”, but “GitHub” gives PR awareness and auto-webhook.)

> You see **GitHub** under *Branch Sources* because the **GitHub Branch Source** plugin is installed. Similar host-specific plugins exist—**Bitbucket Branch Source** and **GitLab Branch Source**—which add PR/MR discovery, Head/Merge strategies, auto-webhooks, and status checks. You can choose plain **Git**, but you’ll miss those richer integrations.


* **Credentials:** select the GitHub App/PAT you configured.
* **Repository URL:**

  ```
  https://github.com/CloudWithVarJosh/cwvj-private-repo.git
  ```

  *(Replace with your account name & private repo)*

---

## Build strategies (what to build)

### Branch build strategy (affects **branch jobs**, not PR jobs)

1. **Exclude branches that are also filed as PRs** *(recommended)*

   * **Behavior:** Build a branch on every push **until** a PR is opened from it; then **stop** the branch job and let the **PR job** run. If the PR closes and the branch remains, the **branch job resumes** on the next push.
   * **Example:** Push to `feature/x` → branch job builds. Open PR `feature/x → main` → PR job builds; branch job pauses. Close PR, push again → branch job builds.

2. **Only branches that are also filed as PRs**

   * **Behavior:** Build a **branch job only if that branch has an open PR**. Long-lived branches like `main`/`release/*` won’t build unless explicitly included elsewhere.
   * **Example:** Push to `feature/y` (no PR) → **no build**. Open PR `feature/y → main` → branch job builds (and PR job, depending on PR settings). `main` after merge → **won’t build** unless separately included.

3. **All branches**

   * **Behavior:** Build **every** branch on push, even if a PR exists—so you’ll likely build both the branch job **and** the PR job (duplicates).
   * **Example:** Open PR from `feature/z` → push again → **branch job builds** and **PR job builds** for the same change.

---

### Discover pull requests from origin (same repo PRs)

Choose **one** PR strategy (or **Both**):

1. **The current pull request revision** *(Head)*

   * **What it tests:** The PR tip **as-is** (no merge with `main`).
   * **Good for:** Quick feedback on the change itself.
   * **Example:** `main` added a new API last hour; PR still compiles against the old API → Head build passes but might fail after merge.

2. **Merging the pull request with the current target branch revision** *(Merge)*

   * **What it tests:** A **synthetic merge** = current **`main` tip + PR head**.
   * **Good for:** “Will it work if we merge **right now**?”
   * **Example:** `main` bumped a dependency; the PR forgot to adapt → Merge build fails, preventing a broken `main`.

3. **Both the current pull request revision and the pull request merged with the current target branch revision**

   * **What it tests:** **Two builds per PR update**: Head **and** Merge.
   * **Good for:** Maximum coverage (PR-only issues + integration drift).
   * **Example:** Head passes; Merge fails because `main` moved—developer rebases/updates, then both pass.

> **Tip:** If you pick **Both**, make the **Merge** status the **required check** in branch protection.

---

### Discover pull requests from forks

**What to build for forked PRs** (pick one):

1. **The current pull request revision** *(Head)* — **safest default**

   * Runs the fork’s code **as-is**. Often combined with **no credentials** to avoid secret leakage.
   * **Example:** External contributor opens PR from fork → Head build runs with target’s Jenkinsfile but without your secrets.

2. **Merging the pull request with the current target branch revision** *(Merge)*

   * Builds the synthetic **merge** of target + fork PR. Use only if you’re comfortable with the security posture and secret handling.
   * **Example:** Org-internal fork where secrets are allowed; you validate integration with latest `main`.

3. **Both** (Head + Merge)

   * Strongest signal, but use cautiously with secrets. Typically reserved for **trusted forks** only.

**Trust policy** (who gets “full” treatment with your credentials/webhooks):

* **From users with Admin or Write permission** *(common)*
* (Other options depend on plugin/version; pick the tightest that fits your repo model.)

**Example trust flow:**

* PR from team member (write access) → full pipeline (image build/push, preview deploy).
* PR from unknown fork → reduced pipeline (no creds; maybe Head-only checks).

---

### Quick cheat-sheet

* **Best general setup:**

  * Branch strategy: **Exclude branches that are also filed as PRs**
  * Origin PRs: **Both (Head + Merge)** → require **Merge** status
  * Fork PRs: **Head** only + Trust **“Admin or Write”** for full runs

* **Capacity constrained:**

  * Origin PRs: **Merge** only (still catches integration drift)
  * Keep **Exclude…** to avoid duplicate branch + PR builds


> Quick example of the three branch strategies:
>
> * You push `feature/x` (no PR yet): **Exclude** = builds; **Only** = doesn’t build; **All** = builds.
> * You open a PR from `feature/x`: **Exclude** = builds PR job only; **Only** = builds (because PR exists); **All** = builds both (duplication).

Click **Save**.

### What you should see

* Jenkins immediately **scans the repo**, finds branches with a `Jenkinsfile`, and creates child jobs.
* Open **flask-mbp → Scan Repository Log** to see which refs were discovered and why some were skipped.
* You should see at least **`main`** listed as a child job (since `main` has a `Jenkinsfile`).

---

## Step 2: Create another branch (`feature/ui`) locally and push

> ⚠️ You’ll use a **Personal Access Token (PAT)** in the clone URL for a private repo. Be careful not to paste it on screen.

```bash
# Clone (I name the remote to indicate the repo)
git clone --origin flask-private https://<YOUR-PAT>@github.com/CloudWithVarJosh/cwvj-private-repo.git
cd cwvj-private-repo

git remote -v         # Shows URLs (avoid showing PAT on screen)
git branch -l

# Create and switch to a new feature branch
git switch -c feature/ui      # (preferred) creates + checks out
# Why `switch`? It's clearer and safer defaults than `checkout`.

# Make a change
# open in your editor:
vim app.py
# UI = "We've added a new Feature"
# then press Esc, type :wq and Enter to save & quit


git status
git add app.py
git commit -m "feature(ui): update UI string"

git switch main
cat app.py   # main still has the old content.
             # main’s app.py changes ONLY after you merge the PR.


# Push the new branch to the remote you named earlier
git push flask-private feature/ui
```

**Result:** Your repo now has **two branches** (`main`, `feature/ui`). `main` is your releasable trunk; `feature/ui` holds work-in-progress.

---

## Step 3: Let MBP discover and build the new branch

If webhooks are set up, Jenkins will discover `feature/ui` automatically. If not:

* In the MBP job, click **Scan Repository Now**.

**Observation**

* You now see **two child jobs**: `main` and `feature/ui`.
* Because we chose **Exclude branches that are also filed as PRs**, the **branch job will build on every push** *until* you open a PR from `feature/ui`.
* If/when you open a PR, Jenkins will **stop building the `feature/ui` branch job** and will **build the PR job** on open and each update.

---

## Step 4: Open PR and Cleanup

> **Heads-up about port 5000:** our Python app listens on **port 5000**. That’s also the port commonly used by the **Jenkins agent’s JNLP** mode. We’re **not** using that agent port in this demo, so there’s no conflict; this is just informational.

### What we’re doing

Open a PR from `feature/ui` → `main`, **manually** rescan so Jenkins MBP discovers/builds the PR, merge it, then **verify** the change landed and the app runs on `localhost:5000`.

---

### Create and run the PR (GitHub → Jenkins)

1. **Open the PR (GitHub)**

   * In your repo, click **Compare & pull request** (or **Pull requests → New pull request**).
   * Set **base:** `main`, **compare:** `feature/ui`.
   * Add a short Title/Description → **Create pull request**.

2. **(Optional) Auto-delete branch on merge (GitHub)**

   * **Settings → General → Pull Requests →** enable **Automatically delete head branches**.

3. **Rescan in Jenkins to discover the PR (manual)**

   * In Jenkins, open your MBP (e.g., **flask-mbp**) → **Scan Repository Now**.
   * Refresh; a **PR job** (e.g., `PR-1`) should appear under the MBP.

4. **Run the PR job**

   * Open the **PR job** → **Build Now** (or it may start right after the scan).
   * With your shared `Jenkinsfile`, the build will:

     * **Build & push** `docker.io/cloudwithvarjosh/cwvj-flask:$BUILD_NUMBER` (and `:latest`),
     * **Deploy** a container **locally on the agent** as `cwvj-flask` on **port 5000**,
     * Write & archive `deploy-info-$BUILD_NUMBER.txt`.

5. **Merge the PR (GitHub)**

   * When the Jenkins check is **success**, click **Merge**.
   * If auto-delete is enabled, GitHub deletes `feature/ui` after merge.

6. **Rescan to build `main` (manual)**

   * Back in Jenkins MBP, click **Scan Repository Now** again so Jenkins sees the merge.
   * The **`main`** job will run (or click **Build Now**) and deploy the new tag the same way.

---

### Verify the result (code + running app)

**A) Container is running**

```bash
docker ps --filter "name=cwvj-flask"
# Expect a container named cwvj-flask publishing 0.0.0.0:5000->5000/tcp
```

**B) App responds on localhost:5000**

```bash
curl -s http://localhost:5000
# Expect output containing: "We've added a new Feature"
```

**C) Deployment info archived in Jenkins**

* In the PR (or main) job → **Build #N** → **Artifacts** → open `deploy-info-N.txt`.
  It should include:

  ```
  build: N
  image: docker.io/cloudwithvarjosh/cwvj-flask:N
  commit: <GIT_COMMIT>
  branch: <GIT_BRANCH>
  time: <UTC timestamp>
  url: <Jenkins build URL>
  ```

**D) Code landed on `main`**

* On **GitHub → main branch**, open `app.py` and confirm it contains:

  ```python
  UI = "We've added a new Feature"
  ```

*(Tip: if Jenkins runs on a remote agent/VM, run the `docker`/`curl` commands **on that agent host**, since the container is started there.)*


---

## Conclusion

You just built an end-to-end **MBP workflow**:

1. Jenkins **discovered** branches/PRs from your repo,
2. ran a **branch job** until a PR opened, then a **PR job**,
3. **built/pushed** an image and **deployed** it locally on the agent,
4. **merged** the PR and **rescanned** to run `main`, and
5. **verified** the change via `localhost:5000` and archived deploy info.

This pattern scales: add **webhooks** for instant triggers, enable **required checks** to protect `main`, choose **PR strategies** (Head/Merge), and later layer in **tests, scans, and promotion**. MBP keeps CI aligned to your branching model while avoiding manual job sprawl.

---

## References

* Jenkins: [Multibranch Pipeline (overview)](https://www.jenkins.io/doc/book/pipeline/multibranch/)
* Jenkins: [GitHub Branch Source Plugin](https://plugins.jenkins.io/github-branch-source/)
* Jenkins: [Declarative Pipeline (Jenkinsfile) syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
* Jenkins MBP: [Orphaned Item Strategy](https://www.jenkins.io/doc/book/pipeline/multibranch/#orphaned-item-strategy)
* GitHub: [Automatically delete head branches](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/automatically-delete-head-branches)
* Docker: [CLI reference — build, push, run](https://docs.docker.com/reference/cli/docker/)

---




