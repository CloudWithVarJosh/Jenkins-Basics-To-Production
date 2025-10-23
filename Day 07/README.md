# Day 7: Jenkins Multibranch Pipelines | CI/CD with GitHub PRs & Docker Deploy

## Video reference for Day 7 is the following:

[![Watch the video](https://img.youtube.com/vi/Eq-HHLtSJM4/maxresdefault.jpg)](https://www.youtube.com/watch?v=Eq-HHLtSJM4)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## Table of Contents

* [Introduction](#introduction)
* [Multi-Branch Pipelines (MBP)](#multi-branch-pipelines-mbp)

  * [Multi-Branch Pipelines — What they are and why they matter](#multi-branch-pipelines--what-they-are-and-why-they-matter)
* [How Jenkins discovers and builds (at a glance)](#how-jenkins-discovers-and-builds-at-a-glance)
* [Trunk-Based CI/CD: Multibranch Flow](#trunk-based-cicd-multibranch-flow)

  * [1) Create branch (`feature/ui-font`)](#1-create-branch-featureui-font)
  * [2) Push → Branch job (build-only, target ≤5m)](#2-push--branch-job-build-only-target-5m)
  * [3) Open PR → PR job (needs app running)](#3-open-pr--pr-job-needs-app-running)
  * [4) Gate the merge on deploy success](#4-gate-the-merge-on-deploy-success)
  * [5) Post-merge on `main`](#5-post-merge-on-main)
  * [6) Cleanup](#6-cleanup)
* [Demo: Jenkins Multi-Branch Pipeline (MBP)](#demo-jenkins-multi-branch-pipeline-mbp)

  * [Why MBP (vs a single Pipeline with many branches)](#why-mbp-vs-a-single-pipeline-with-many-branches)
  * [What we’ll do](#what-well-do)
  * [Prerequisites](#prerequisites)
  * [Step 0: Create the MBP job](#step-0-create-the-mbp-job)
  * [Build strategies (what to build)](#build-strategies-what-to-build)

    * [Branch build strategy (affects branch jobs, not PR jobs)](#branch-build-strategy-affects-branch-jobs-not-pr-jobs)
    * [Discover pull requests from origin (same-repo PRs)](#discover-pull-requests-from-origin-same-repo-prs)
    * [Discover pull requests from forks](#discover-pull-requests-from-forks)
    * [Quick cheat-sheet](#quick-cheat-sheet)
  * [What you should see](#what-you-should-see)
  * [Step 1: Create another branch (`feature/ui`) locally and push](#step-1-create-another-branch-featureui-locally-and-push)
  * [Step 2: Let MBP discover and build the new branch](#step-2-let-mbp-discover-and-build-the-new-branch)
  * [Steps 3, 4, 5 & 6: Open PR → Gate → Merge to `main` → Cleanup](#steps-3-4-5--6-open-pr--gate--merge-to-main--cleanup)
  * [Verify the result (code + running app)](#verify-the-result-code--running-app)
* [Conclusion](#conclusion)
* [References](#references)

---

## Introduction

In this session we’ll set up a **Jenkins Multi-Branch Pipeline (MBP)** that automatically discovers branches/PRs and runs the pipeline wherever a `Jenkinsfile` exists. You’ll see how MBP maps cleanly to **trunk-based development**: short-lived feature branches, PR-aware builds, and `main` that stays releasable.
We’ll create an MBP against a **private GitHub repo**, push a new branch, open a PR, manually rescan (no webhooks yet), and watch Jenkins build/deploy a **Dockerized Python app** that listens on **port 5000**.

---


# Multi-Branch Pipelines (MBP)
### Multi-Branch Pipelines — What they are and why they matter

![Alt text](/images/7a.png)

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

![Alt text](/images/7b.png)

Assumptions: **Jenkins Multibranch Pipeline (MBP)**, **branch protection + required checks**, and **containerized builds**.

---

### 1) Create branch (`feature/ui-font`)

**What happens:** Branch from the latest `main`. Keep branches short-lived and predictably named (`feature/*`, `bugfix/*`) so CI filters work well.
**Why:** Small, frequent changes keep reviews quick and merges clean.
**Good practice:** Rebase/merge with `main` often (or enforce **Require branch to be up to date before merging**). Enforce naming with repo rules or a pre-receive hook.

---

### 2) Push → **Branch job** *(build-only, target ≤5m)*

**Trigger:** Every push to the feature branch (webhook preferred; scheduled scan as backup). With **Exclude branches that are also filed as PRs**, branch builds **stop** once a PR opens.
**What runs:** **Lint/format → compile → unit tests → coverage**; **package & build container image** (do **not** run it); **publish artifacts/metadata** (image digest, build info; optional SBOM/signature).
**Why:** Fast feedback for obvious breakages without consuming environments.
**Ops tip:** Cache dependencies; add `disableConcurrentBuilds()` + `milestone()` so the newest push wins.

---

### 3) Open PR → **PR job** *(needs app running)*

**Trigger:** On PR open and each update. Prefer PR strategies **Head + Merge** to test the PR tip and its merge with current `main`.
**What runs (shift-left order):**

1. **Light SAST + dependency scan** on code/manifests.
2. **Build image → image scan** (block on High/Critical).
3. **Deploy ephemeral preview** (namespace/stack per PR).
4. **Integration/E2E smoke** against the running app.
5. **Teardown** preview on completion/PR close (TTL as safety).
   **Why:** Proves the change **runs** and **integrates** before merge—things unit tests alone can’t surface.
   **Forks/secrets:** Use trust policies; run reduced checks when secrets aren’t available.

---

### 4) **Gate the merge on deploy success** *(required checks)*

**Rule:** All required checks must be **green**, including a status like **`deploy-preview: succeeded`**, and the PR must be **up-to-date with base**.
**Flow:** If any check is red, fix → push → PR job auto-rebuilds. Optionally enable **auto-merge on green** (or use a merge queue/train).
**Why:** Keeps `main` continuously releasable.

---

### 5) **Merge to `main`** *(promote artifact)*

**Trigger:** Merging (squash/merge/rebase) creates a new commit on `main`; MBP runs the **main** job.
**What runs:** **Reuse the signed artifact/image** built in the PR (preferred) or **rebuild deterministically**; **deploy to dev/stage**, run smoke checks; **promote** onward with approvals/change control; run **full, authenticated DAST** here (not in PR) and block on High/Critical.
**Why reuse:** Promoting the **same digest** from PR → stage → prod improves auditability and eliminates “works on my build” drift.
**Hygiene:** Record release notes/provenance; attach SBOM/signatures.

---

### 6) **Cleanup**

**What happens:** Git host can **auto-delete the source branch** after merge (same-repo PRs). MBP’s **orphan cleanup** prunes the retired branch job/workspace. A preview-env **GC/TTL** reaps stray namespaces/volumes/DBs.
**Why:** Keeps Jenkins lean and your cloud bill down; removes stale jobs and environments.

---

# Demo: Jenkins **Multi-Branch Pipeline (MBP)**

![Alt text](/images/7c.png)

## Why MBP (vs a single Pipeline with many branches)

* **Auto-discovery:** Jenkins scans your repo and **creates one child job per branch/PR/tag** that contains a `Jenkinsfile`. No manual job sprawl.
* **PR awareness:** Builds **PR “Head”** and/or a **synthetic “Merge”** so you validate integration before merge.
* **Lifecycle automation:** New branch/PR → job created. PR closed/branch deleted → job retired.
* **Per-branch history:** Each branch/PR has its own build history, test reports, and checks.
* **Policy at scale:** Enforce quality gates (tests/coverage/lint/scans) **per branch/PR**; protect `main` with required checks.

> Key idea: You don’t list branches. MBP **finds them** and runs the pipeline where a `Jenkinsfile` exists.

---

## What we’ll do

* **Create an MBP job** (GitHub Branch Source) → scan the repo, discover the `Jenkinsfile`, and run a **baseline `main` build**.
* **Create `feature/ui`**, make a tiny UI change, **push**, then **manually rescan** (no webhooks) so MBP finds the branch and runs its **branch job**.
* **Open a PR** (`feature/ui` → `main`) → MBP switches to a **PR job**; we run the same pipeline and **report status back to GitHub**.
* **Merge when green**, then **rescan** so MBP detects the new commit on `main` and runs the **main deploy**.
* **Verify** locally at **[http://localhost:5000](http://localhost:5000)** and inspect the archived **deploy-info** artifact.
* **Cleanup:** optionally auto-delete the feature branch on merge; MBP prunes retired branch jobs/workspaces.

---

## Prerequisites

* A **private GitHub repo** with: application code, `Dockerfile`, and `Jenkinsfile` (use the one from the previous lecture).
* Jenkins has **GitHub credentials** (PAT or GitHub App) saved and working.
* (Optional but recommended) GitHub **webhook** is enabled so builds trigger immediately; a periodic scan remains as a safety net.

---

## Step 0: Create the MBP job

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

### Discover pull requests from origin (same-repo PRs)

Pick **one** strategy (or **Both**) for how Jenkins builds PRs:

1. **The current pull request revision (Head)** — *“your code only”*

   * **Builds:** PR tip **as-is** (no merge with `main`).
   * **Rebuilds when:** the **PR updates** (not when `main` moves).
   * **What it tells you (PR job):** Does **your change alone** build/test/deploy?
   * **Limit:** Can miss failures that appear **after** merging with newer `main`.
   * **Example:** `main` added a breaking API—Head passes; merge would fail.

2. **Merging the pull request with the current target branch revision (Merge)** — *“your code + current main”*

   * **Builds:** **synthetic merge** = `main@tip` + `PR@head` (what would land **right now**).
   * **Rebuilds when:** the **PR updates** **or** when **`main` moves** (via webhook/scan).
   * **What it tells you (PR job):** Would the **post-merge** build succeed? Catches integration drift and conflicts.
   * **Relation to the `main` build:** If you merged **immediately**, the `main` build should look like **this** result.
   * **Example:** `main` bumped a library; Merge build fails until PR adapts.

3. **Both (Head + Merge)** — *verify both views*

   * **Builds:** **two** jobs per PR event: **Head** *(your code only)* and **Merge** *(your code + current main)*.
   * **What it tells you:** You get **both signals**: PR-only regressions **and** after-merge outcome.
   * **Production tip:** Make the **Merge** status a **required check**, since it reflects what `main` would be **after** the merge.

> **Rule of thumb:** If you must choose one, pick **Merge** to know what `main` will look like after merging. If you have capacity, choose **Both** to verify **your code alone** *and* **your code + current main**.

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

## Step 1: Create another branch (`feature/ui`) locally and push

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

## Step 2: Let MBP discover and build the new branch

If webhooks are set up, Jenkins will discover `feature/ui` automatically. If not:

* In the MBP job, click **Scan Repository Now**.

**Observation**

* You now see **two child jobs**: `main` and `feature/ui`.
* Because we chose **Exclude branches that are also filed as PRs**, the **branch job will build on every push** *until* you open a PR from `feature/ui`.
* If/when you open a PR, Jenkins will **stop building the `feature/ui` branch job** and will **build the PR job** on open and each update.

---

## Steps 3, 4, 5 & 6: Open PR → Gate → Merge to `main` → Cleanup

> **Heads-up about ports:** our Flask app listens on **port 5000**. Jenkins’ JNLP/inbound agent uses **port 50,000** by default, which we’re not using here—so there’s no conflict.


---

### 3) Open PR → PR job runs (preview-style build)

**Goal:** create a PR from `feature/ui` to `main` and have MBP build it.

**Do this (GitHub → Jenkins):**

1. **Open the PR (GitHub)**

   * In your repo, click **Compare & pull request** (or **Pull requests → New pull request**).
   * Set **base:** `main`, **compare:** `feature/ui`.
   * Add a short Title/Description → **Create pull request**.
2. **(Optional) Auto-delete branch on merge (GitHub)**

   * **Settings → General → Pull Requests →** enable **Automatically delete head branches**.
3. **Rescan in Jenkins (manual, since no webhooks yet)**

   * Open your MBP (e.g., **flask-mbp**) → **Scan Repository Now**.
   * You should now see a **PR job** (e.g., `PR-1`) under the MBP.
4. **Run the PR job**

   * Open the **PR job** → **Build Now** (or it may start right after the scan).
   * With our shared `Jenkinsfile`, the PR job will:

     * **Build & push** `docker.io/cloudwithvarjosh/cwvj-flask:$BUILD_NUMBER` (and `:latest`)
     * **Deploy** a container on the **local agent** as `cwvj-flask` on **port 5000**
     * **Write & archive** `deploy-info-$BUILD_NUMBER.txt`
   * Jenkins posts the build status back to the PR in GitHub.

> **Note — Protecting `main` in GitHub (quick setup)**
>
> * **Where:** Repo → **Settings** → **Branches** → **Add rule** (classic) **or** **Add ruleset** (newer model).
> * **Pattern:** Set **Branch name pattern** to `main`.
> * **Common protections you’ll enable for `main`:**
>
>   * **Require a pull request before merging** (blocks direct pushes to `main`—you’ll often see “you can’t push directly to this branch”).
>   * **Require status checks to pass** (e.g., Jenkins “PR Head/Merge” checks).
>   * **Require branches to be up to date** (forces a rebase/merge with the latest `main` before merging).
>   * **Require approvals** (e.g., at least 1 reviewer, dismiss stale reviews on new commits).
>   * Optional hardening: **restrict who can push**, **require signed commits**, **enforce linear history**, **lock branch**.
> * **Ruleset vs classic rule:** Rulesets add richer targeting and org-level control; classic rules are simpler. Either is fine for this demo.
> * **Heads-up (plans):** Some options may be limited or “not enforced” on personal private repos without GitHub Team/Enterprise.


---

### 4) Gate the merge on success (required checks)

**Idea:** merge only when the PR build(s) are **green**.

* In a production setup you’d enforce **required checks** (e.g., “Build”, “Deploy preview succeeded”, “Up-to-date with base”).
* For this demo, once the Jenkins check on the PR shows **success**, you can proceed to merge.
* If any check is **red**, fix the code, push, **rescan**, and the PR job will re-run.

---

### 5) Merge to `main` → run `main` job

**Do this:**

1. **Merge the PR (GitHub)**

   * Click **Merge**. If auto-delete is enabled, GitHub removes `feature/ui` after merge.
2. **Rescan so MBP sees the new commit on `main`**

   * Back in Jenkins MBP, click **Scan Repository Now**.
   * The **`main` job** will run (or click **Build Now**) and execute the same pipeline: **Build / Push / Deploy / Archive / Test**.
3. **Verify locally**

   * The container runs on the agent host at **[http://localhost:5000](http://localhost:5000)**.

---

### 6) Cleanup

* **GitHub** (optional): auto-deletes the source branch after merge.
* **Jenkins MBP**: prunes retired **branch/PR jobs** and their **workspaces** per orphan-cleanup policy.

---

### Verify the result (code + running app)

**A) Container is running**

```bash
docker ps
# Expect a container named cwvj-flask publishing 0.0.0.0:5000->5000/tcp
```

**B) App responds on localhost:5000**

```bash
curl -s http://localhost:5000
# Expect output containing: "We've added a new Feature"
```

**C) Deployment info archived in Jenkins**

* In the PR (or main) job → **Build #N** → **Artifacts** → open `deploy-info-N.txt`:

  ```
  build: N
  image: docker.io/cloudwithvarjosh/cwvj-flask:N
  commit: <GIT_COMMIT>
  branch: <GIT_BRANCH>
  time: <UTC timestamp>
  url: <Jenkins build URL>
  ```

**D) Code landed on `main`**

* On **GitHub → main**, open `app.py` and confirm it contains:

  ```python
  UI = "We've added a new Feature"
  ```

> *Tip:* If Jenkins runs on a remote agent/VM, run the `docker`/`curl` commands **on that agent host**, since the container starts there.

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




