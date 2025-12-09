# Day 4: Jenkins Freestyle Power-Ups | Build Parameters, Branch Input, Poll SCM & Cron Cleanup

## Video reference for Day 4 is the following:

[![Watch the video](https://img.youtube.com/vi/56iDHrLgqxw/maxresdefault.jpg)](https://www.youtube.com/watch?v=56iDHrLgqxw)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

* [Introduction](#introduction)  
* [Inside `$JENKINS_HOME`: What Lives in the Jenkins Home Directory](#inside-jenkins_home-what-lives-in-the-jenkins-home-directory)  
  * [Top-Level Configuration (Files)](#top-level-configuration-files)  
    * [Why you still see “hudson”](#why-you-still-see-hudson)  
  * [Security & Identity](#security--identity)  
  * [Core Directories (State, Code, Users, Logs)](#core-directories-state-code-users-logs)  
    * [Jenkins is a Java web app (WAR)](#jenkins-is-a-java-web-app-war)  
  * [Workspaces & Queues](#workspaces--queues)  
    * [Where jobs live vs. where they run (Controller vs. Agents)](#where-jobs-live-vs-where-they-run-controller-vs-agents)  
  * [Backup Quick-Check](#backup-quick-check)  
* [Mini Demos — your pipeline foundation](#mini-demos--your-pipeline-foundation)  
  * [Mini Demo 1 — Add Parameters (Boolean, Choice)](#mini-demo-1--add-parameters-boolean-choice)  
  * [Mini Demo 2 — Git SCM + Branch as a Parameter](#mini-demo-2--git-scm--branch-as-a-parameter)  
  * [Mini Demo 3 — Poll SCM Trigger (no webhooks)](#mini-demo-3--poll-scm-trigger-no-webhooks)  
  * [Mini Demo 4 — Webhook Trigger (GitHub/GitLab)](#mini-demo-4--webhook-trigger-githubgitlab)  
  * [Mini Demo 5 — Scheduled Nightly (Cron) + Workspace Cleanup](#mini-demo-5--scheduled-nightly-cron--workspace-cleanup)  
* [Conclusion](#conclusion)  
* [References](#references)  

---

# Introduction

Day 4 builds practical intuition for everyday Jenkins use. We start with a quick tour of **`$JENKINS_HOME`**—what lives there, what to back up, and why you still see `hudson.*`. Then we level-up **Freestyle jobs** with real knobs teams use in production: **parameters**, **Git integration** (branch/tag input), **triggers** (Poll SCM, webhooks—theory), and a **nightly job** that generates artifacts and cleans workspaces. Along the way we keep a production lens: auditability, reproducibility, and disk hygiene. By the end, students can wire a clean Freestyle foundation that’s ready for pipelines and promotions.

---

# Inside `$JENKINS_HOME`: What Lives in the Jenkins Home Directory

A quick, well-structured map of what’s inside Jenkins’ home—**what to care about, why it’s there, and what to back up**.

---

## Top-Level Configuration (Files)

* `config.xml` — Global Jenkins configuration
* `jenkins.model.JenkinsLocationConfiguration.xml` — Base URL & admin email
* `hudson.tasks.*.xml`, `hudson.plugins.*.xml`, `org.jenkinsci.*.xml` — Tool configs (Maven/Gradle/Ant/Git) & plugin settings
* `jenkins.mvn.GlobalMavenConfig.xml`, `nodeMonitors.xml`, `jenkins.install.*` — Maven/global install state, node monitor, install wizard state
* `copy_reference_file.log` — First-run copy log

> ### Why you still see “hudson”
>
> Jenkins started life as **Hudson** at Sun. After the **2011** fork (governance/licensing), the community continued as **Jenkins**—but many core classes, file names, and plugin APIs kept the `hudson.*` packages for **backward compatibility**. Hence `hudson.tasks.*.xml` and friends inside `$JENKINS_HOME`.

---

## Security & Identity

* `secrets/` — Encrypted credential blobs and plugin keys
* `secret.key`, `secret.key.not-so-secret`, `identity.key.enc` — Keys Jenkins uses to encrypt/decrypt (**guard these**)

---

## Core Directories (State, Code, Users, Logs)

* `jobs/` — **All jobs/pipelines**

  * Each job: `config.xml`, `builds/<#>/log`, `archive/` (artifacts), etc.
  * **Critical to back up.**
* `plugins/` — Installed plugins (`.jpi/.hpi`) and their data
* `users/` — Local user records
* `tools/` — Auto-installed tool caches (e.g., Maven via *Manage Jenkins → Tools*)
* `logs/` — Controller logs (rotated)
* `updates/` — Update center cache (**safe to recreate**)
* `userContent/` — Static files Jenkins can serve
* `war/` — Webapp files for the running Jenkins version

> ### Jenkins is a Java web app (WAR)
>
> Jenkins runs on the **JVM** and ships as a **`.war`** under `$JENKINS_HOME/war/`. It boots an embedded server (Winstone/Jetty) on **HTTP 8080** by default, so you access it via a **URL**. Plugins live separately as **`.jpi/.hpi`** in `plugins/`. Jenkins can also sit behind a reverse proxy or inside an external servlet container (e.g., Tomcat).

---

## Workspaces & Queues

* `workspace/` — **Build workspaces on the node that runs the build**

  * If the **controller has executors**, controller-run builds create workspaces here
  * With **controller executors = 0**, **no new** controller workspaces are created (old ones may remain)
  * Agent workspaces live on the **agent’s filesystem** (its Remote root), **not** in `$JENKINS_HOME`
* `queue.xml.bak` — Last saved build queue snapshot (ephemeral)

> ### Where jobs live vs. where they run (Controller vs. Agents)

![Alt text](/images/4a.png)
>
> **Control plane state (controller):** Job configs, build records/logs, credentials, plugins, and archived artifacts live under `$JENKINS_HOME/jobs/...`.
> **Execution (agents):** Build steps run on the **assigned node**. Each agent uses its own **workspace** (under its *Remote root*) as scratch space.
> **Controller executors = 0:** The controller won’t run builds, so no **new** workspaces appear under `$JENKINS_HOME/workspace` (old entries linger until cleaned).
> **Agents don’t have `$JENKINS_HOME`:** They have their own directories (e.g., `/var/jenkins`) containing:
>
> * `workspace/<job>` (and branch/PR variants) — runtime work area
> * `tools/...` — caches for Tools-installed JDK/Maven/Gradle
> * Agent runtime files (e.g., downloaded `agent.jar`)
>   **Bottom line:** **Records stay on the controller; agents hold runtime working files only.**

---

## Backup Quick-Check

* **Back up (must-have):**
  `jobs/`, `plugins/`, `secrets/`, `users/`, global `*.xml`, `secret.key`, `identity.key.enc`
* **Can exclude (recreated on boot):**
  `workspace/`, `updates/`, certain caches
* **Restore tips:**
  Keep Jenkins & plugin versions compatible; **preserve `secret.key`** to decrypt credentials

---

# Mini Demos — your pipeline foundation

These quick Jenkins demos are the building blocks for everything we’ll do next. Try them now—parameters, Git integration, triggers, and a nightly job—and they’ll become the base of the full pipelines we’ll create in upcoming lessons.

---

## Mini Demo 1 — Add Parameters (Boolean, Choice)

**Goal:** Let users toggle tests and pick target env; show how params appear as env vars.

**Setup:**

* Edit job or create a new job → **This project is parameterized** →

  * **Boolean Parameter:** `RUN_TESTS` (default: true)
  * **Choice Parameter:** `ENV` choices: `dev\nstage\nprod`

**Build Step (Execute shell):**

```bash
echo "RUN_TESTS=$RUN_TESTS ENV=$ENV"
echo "Report for #$BUILD_NUMBER (env=$ENV)" > report-$ENV.txt
if [ "$RUN_TESTS" = "true" ]; then
  echo "Running tests..."; sleep 1; echo "OK"
else
  echo "Skipping tests."
fi
```

**Post-build Action:** Archive `report-*.txt`

**Production note (why it matters):**
Parameters turn “mysterious shell flags” into **auditable inputs** visible on the build page. That improves change control and rollback.

* **Hotfix example:** Tick `RUN_TESTS=false` for a critical fix where unit tests take 20 minutes and the SLA is 5 minutes; immediately after, re-run with `RUN_TESTS=true` on `dev` to validate. The build history shows exactly which run skipped tests, by whom, and for which `ENV`.
* **Regulated teams:** Keep `ENV` choices locked to `dev/stage/prod`. Release managers can enforce approvals per environment while engineers still use one job.
* **Rollback:** The archived `report-$ENV.txt` and the parameter set on the build record give a clear breadcrumb for what was deployed where.

---

## Mini Demo 2 — Git SCM + Branch as a Parameter

**Goal:** Pull a chosen branch and print commit info.

**Setup:**

* Add **String Parameter**: `BRANCH` default `main`
* SCM → **Git** → Repo URL, credentials → **Branches to build:** `$BRANCH`

**Build Step (Execute shell):**

```bash
echo "Built from BRANCH=$BRANCH"
git --version
echo "Latest commit:"
git log --oneline -n 1 || true
echo "Jenkins vars: GIT_BRANCH=$GIT_BRANCH GIT_COMMIT=$GIT_COMMIT"
```

**Production note:**
Branch/tag-as-input lets you **promote or backport** without cloning jobs or editing XML.

* **Release backport:** Security fix needs to ship on `release/1.8`. Set `BRANCH=release/1.8` and run. The build captures `GIT_COMMIT`, so you can later prove which commit went to which environment.
* **Tag pinning:** For reproducible deployments, accept `TAG` instead of `BRANCH` (`refs/tags/v1.8.3`). That turns each release into a **commit-anchored artifact**, easy to diff and roll back.
* **Ops handover:** SRE can deploy the same artifact to `stage` and `prod` by changing parameters, not jobs, reducing drift.

---

## Mini Demo 3 — Poll SCM Trigger (no webhooks)

**Goal:** Auto-build when Git changes, using polling.

**Setup:**

* Keep Git config from Demo 2.
* **Build Triggers → Poll SCM:** `H/2 * * * *`

  * **What this does:** Polls the repo about every **2 minutes** and triggers a build **only if** a new commit is detected.
  * **About `H`:** `H` is a **hash-spread** placeholder—Jenkins picks a stable minute offset per job so polls are evenly distributed (no thundering herd).


**Build Step (Execute shell):**

```bash
echo "Polling-driven build"
git log --oneline -n 3 || true
```

**Production note:**
Polling is a **firewall-friendly** trigger when webhooks aren’t possible.

* **Locked networks:** Banks or healthcare orgs often block inbound webhooks. Polling from Jenkins (outbound) still enables near-real-time CI.
* **Batch repos:** If a mono-repo changes frequently, restrict polling to specific paths (includes/excludes) to avoid unnecessary builds.
* **Coverage vs. load:** Use jittered `H/` schedules so multiple jobs don’t hammer the VCS at the same minute; this prevents “thundering herd” issues on self-hosted Git.

---

## Mini Demo 4 — Webhook Trigger (GitHub/GitLab)

**Goal:** Fire builds immediately on push.

**Setup (GitHub):**

* Job → **Build Triggers:** “GitHub hook trigger for GITScm polling.”
* GitHub → **Settings → Webhooks**: Payload URL `http://<jenkins>/github-webhook/`, `application/json`, push events, secret set.

**Build Step (Execute shell):**

```bash
echo "Triggered by webhook; branch=$GIT_BRANCH"
git log -n 1 || true
```

**Production note:**
Webhooks reduce **feedback loop** from minutes to seconds, improving quality and developer flow.

* **Fast fail:** A React app that builds in 30s should start instantly; devs fix issues before switching context, keeping PRs small.
* **Compute savings:** No polling every 2 minutes across 30 jobs. Lower idle CPU and fewer API calls on GitHub/GitLab.
* **Event breadth:** Extend to PR events to run PR validations (lint, unit, SAST) only when needed, not on cron.

> Set **Manage Jenkins → System → Jenkins URL** to your public tunnel/domain first; then use `https://<your-domain>/github-webhook/` as the Payload URL.

---

## Mini Demo 5 — Scheduled Nightly (Cron) + Workspace Cleanup

**Goal:** Run at 1:30 AM nightly and clean workspace after.

**Setup:**

* **Build periodically:** `30 1 * * *`
* Cleanup via **Workspace Cleanup** plugin (pre or post), or shell.

**Build Step (Execute shell):**

```bash
echo "Nightly maintenance on $NODE_NAME"
echo "Workspace: $WORKSPACE" > report.txt
echo "Backing up artifacts"
echo "Cleaning workspace..."
rm -rf "$WORKSPACE"/* || true
```

**Production note:**
Nightly jobs reduce **daytime risk**; cleanup controls disk growth.

* **License/report tasks:** Generate dependency license SBOMs and push to S3 each night—keeps release time fast.
* **Cache refresh:** Pre-warm Maven/npm caches on agents after weekly base image updates so day-one builds don’t spike latencies.
* **Disk hygiene:** Workspaces from multibranch builds balloon quickly; scheduled cleanup prevents agents going read-only during working hours.

---

# Conclusion

You now know what Jenkins stores, where builds actually run, and how to make Freestyle jobs behave like grown-up CI: typed parameters for safe inputs, Git checkout with traceable SHAs, event-driven or scheduled triggers, and responsible cleanup after archiving results. These patterns reduce surprises and make later pipeline work feel natural. Next, we’ll connect this to **build-once, promote-many** flows and agent best practices so teams can scale without sacrificing control.

---

# References

* [Jenkins Handbook (About Jenkins)](https://www.jenkins.io/doc/book/intro/)
* [JENKINS_HOME & Backup Guidance](https://www.jenkins.io/doc/book/system-administration/backing-up/)
* [Git Plugin (SCM Checkout & Branches)](https://plugins.jenkins.io/git/)
* [Cron Syntax & `H` Hash Token](https://www.jenkins.io/doc/book/pipeline/syntax/#cron-syntax)
* [GitHub Plugin (Webhook `/github-webhook/`)](https://plugins.jenkins.io/github/)
