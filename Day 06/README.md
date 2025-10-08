# Day 6: Jenkins Project 2: Pipeline

## Video reference for Day 6 is the following:



---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## Table of Contents

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Why Pipelines? (the big wins)](#why-pipelines-the-big-wins)

  * [Pipeline Job vs Chained Freestyle](#pipeline-job-vs-chained-freestyle)
  * [Pipeline vs Freestyle — Top 5](#pipeline-vs-freestyle--top-5)
  * [Bottom line](#bottom-line)
* [Two ways to use a Pipeline](#two-ways-to-use-a-pipeline)
* [Groovy: how much do you need?](#groovy-how-much-do-you-need)
* [Declarative Pipeline — the core building blocks](#declarative-pipeline--the-core-building-blocks)

  * [Minimal shape](#minimal-shape)
  * [What each block means](#what-each-block-means)
  * [Useful companions you’ll meet shortly](#useful-companions-youll-meet-shortly)
* [Create a Skeleton Jenkinsfile](#create-a-skeleton-jenkinsfile)
* [Build a Production-grade Jenkinsfile (replicates Day-5)](#build-a-production-grade-jenkinsfile-replicates-day-5)

  * [Step 1: Add credentials via the Snippet Generator](#step-1-add-credentials-via-the-snippet-generator)
  * [Step 2: Define reusable environment variables](#step-2-define-reusable-environment-variables)
  * [Step 3: Full Jenkinsfile (simple, clear, production-ish)](#step-3-full-jenkinsfile-simple-clear-production-ish)
* [Improving our Day-5 flow with a Jenkinsfile](#improving-our-day-5-flow-with-a-jenkinsfile)

  * [1) Use Pipeline Script from SCM (so checkout happens automatically)](#1-use-pipeline-script-from-scm-so-checkout-happens-automatically)
  * [2) Post actions](#2-post-actions)
  * [3) Generate and archive deploy-info.txt](#3-generate-and-archive-deploy-infottxt)
  * [4) Clean the workspace](#4-clean-the-workspace)
  * [Consolidated Jenkinsfile (simple + improvements)](#consolidated-jenkinsfile-simple--improvements)
* [Conclusion](#conclusion)
* [References](#references)

---

## Introduction

Today we’ll convert our Day-5 Freestyle flow into a **Jenkinsfile**: same steps (checkout → build → push → deploy → test), but now **as code** so it’s versioned, reviewable, and easy to evolve. We’ll keep the core simple (build number as the image tag), then add practical upgrades: **post actions**, a **deploy-info.txt** artifact for traceability, and a final **workspace cleanup**. By the end, you’ll have a production-shaped pipeline that’s still beginner-friendly.

---

## Prerequisites

Before Day 6, make sure you’re comfortable with the Day-5 flow (Docker-outside-of-Docker, credentials, build → push → deploy → test).
Review these:

* **Day 5 — GitHub Notes:** [Jenkins-Basics-To-Production / Day 05](https://github.com/CloudWithVarJosh/Jenkins-Basics-To-Production/tree/main/Day%2005)
* **Day 5 — YouTube Video:** [Build, Push & Deploy a Dockerized Flask App with Jenkins](https://www.youtube.com/watch?v=UYlVTs_yK8U&ab_channel=CloudWithVarJosh)

---

## Why Pipelines? (the big wins)

* **Code-as-config:** One **Jenkinsfile** in Git — reviewed, versioned, rollbackable.
* **Reliable & visible:** Stages with clear fail points; `post {}` for cleanup; easy **timeouts/retries**.
* **Parallel + conditional:** `parallel {}` for fast feedback; `when {}` for branch/tag/file-based logic.
* **Secure & audited:** **Credentials by ID** (masked), sandboxed, every change = a commit.
* **Less plugin sprawl:** Most orchestration is native to Pipeline.

### Pipeline Job vs Chained Freestyle

### Pipeline vs Freestyle — Top 5

| Area                       | **Pipeline Job (Jenkinsfile)**                                       | **Chained Freestyle Jobs**                                    |
| -------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Code-as-config & audit** | One **Jenkinsfile in Git**; PR-reviewed, versioned, rollbackable.    | Logic scattered in UI across jobs; weak history/traceability. |
| **Parallelism**            | Native `parallel {}` for fast, concurrent stages.                    | Requires extra jobs/plugins; clunky to coordinate.            |
| **Conditionals**           | `when {}` cleanly gates by branch/tag/files.                         | Imitated with duplicated jobs/params; gets messy.             |
| **Approvals / input**      | Built-in `input` step with timeouts/roles.                           | No native gate; rely on plugins or manual steps.              |
| **Maintenance & plugins**  | Minimal plugin sprawl; one file per project; reusable via libraries. | Many jobs to maintain; heavy plugin reliance and drift.       |

### Bottom line

Pipelines keep CI/CD **in code**, so changes are reviewable and rollbackable, with **parallelism**, **conditionals**, and **approvals** built in.
Yes, you *can* approximate this with Freestyle—e.g., a chain of jobs plus **Parameterized Trigger**, **Copy Artifact**, and cron/webhook plugins—but it’s brittle and high-maintenance.
Every new branch, gate, or fan-out means **more jobs to wire and keep in sync**, which becomes real toil for DevOps teams.
Use **Pipelines** for anything beyond a tiny flow; Freestyle chains are best left for quick, one-off tasks.






---

## Two ways to use a Pipeline

1. **From SCM (Recommended for prod)**
   In Jenkins: **Pipeline → Definition: Pipeline script from SCM** → point to your repo/branch. Jenkins loads `Jenkinsfile` from the repo.
   *Benefits:* version control, code review, simple rollbacks.

2. **Inline (Script in the job)**
   **Definition: Pipeline script** and paste the Jenkinsfile into the job UI.
   *Use for labs or quick tests.*

   > For inline Scripted Groovy, Jenkins may use the **Groovy Sandbox** to require approvals for dangerous APIs.

---

## Groovy: how much do you need?

Pipelines use Groovy syntax, but you don’t need “deep Groovy.” You’ll mostly write **Declarative Pipeline**, which is structured and opinionated. We’ll teach the Groovy you need as we go.

**Two pipeline styles**

* **Declarative Pipeline** (newer, simpler): `pipeline { agent any; stages { … } }`
* **Scripted Pipeline** (flexible, Groovy-first): `node { stage('…'){ … } }`
  We’ll use **Declarative** in this course; you can always drop to Scripted for advanced logic.

---

## Declarative Pipeline — the core building blocks

### Minimal shape

```groovy
pipeline {
  agent any                       // where the build runs
  stages {
    stage('checkout') {
      steps {
        echo 'Checking out from private repo'
      }
    }
  }
}
```

### What each block means

* **pipeline { }** – required top-level block.
* **agent** – where to execute:

  * `agent any` → any available node.
  * `agent { label 'docker' }` → run on agents with label `docker`.
  * `agent none` → define agents per-stage (advanced).
* **stages** – ordered list of **stage('name')** blocks.
* **steps** – the actual work: `sh`, `echo`, `git`, `archiveArtifacts`, etc.

### Useful companions you’ll meet shortly

* **environment { }** – set env vars (e.g., `IMAGE`, `TAG`).
* **options { }** – timeouts, timestamps, durability.
* **parameters { }** – user inputs (e.g., `string(name: 'TAG', …)`).
* **post { }** – always/changed/failure/success actions (e.g., `cleanWs()`).
* **when { }** – conditional execution (e.g., only on `main`).
* **tools { }** – auto-provision Maven/JDK for the run.

---


## Create a Skeleton Jenkinsfile

**1) Make a Pipeline job**

* **New Item → Pipeline →** name it `flask-pipeline` → **OK**.
* Scroll to **Pipeline** → **Definition: Pipeline script**.

**2) Paste this minimal Jenkinsfile**

```groovy
pipeline {
  agent any

  stages {
    stage('checkout') {
      steps {
        echo 'this is checkout step'
      }
    }
    stage('build') {
      steps {
        echo 'this is build step'
      }
    }
    stage('push') {
      steps {
        echo 'this is push step'
      }
    }
    stage('deploy') {
      steps {
        echo 'this is deploy step'
      }
    }
    stage('test') {
      steps {
        echo 'this is test step'
      }
    }
  }
}
```

**3) Run it**

* Click **Save**, then **Build Now**.
* Open the build → **Stages** tab: you’ll see a bar for each stage (green = passed, red = failed).
* Click any stage to jump straight to its logs.
* **Console Output** shows the full log, similar to Freestyle.

**Why this?**

* The stages mirror **Day 5: Project 1** (checkout → build → push → deploy → test).
* We’re just echoing for now to learn the **syntax and stage view**. We’ll replace echoes with real steps next.

**Next (coming soon)**

* We’ll move this Jenkinsfile **into your repo (Pipeline from SCM)** so it’s versioned and reviewable, then wire in **real checkout/build/push/deploy** steps.

---

# Build a Production-grade Jenkinsfile (replicates Day-5)

## Step 1: Add credentials via the Snippet Generator

Open: `http://localhost:8080/job/pipeline-1/pipeline-syntax/`

**A) Git checkout (private repo)**

* **Sample Step:** `git: Git`
* **Repository URL:** `https://github.com/CloudWithVarJosh/cwvj-private-repo.git` *(use **your** private repo URL)*
* **Branch:** `main`
* **Credentials:** your GitHub PAT (e.g., `github-pat`)
* Optional: **Include in polling?** off (we’ll trigger manually), **Include in changelog?** on

> When **changelog: true** (or the box is checked), Jenkins records commit messages, authors, timestamps, and the commit IDs between the last built revision and the new one.

This generates something like:

```groovy
git branch: 'main', credentialsId: 'github-pat', poll: false,
    url: 'https://github.com/CloudWithVarJosh/cwvj-private-repo.git'
```

**B) Docker Hub login**

* **Sample Step:** `withCredentials: Bind credentials to variables`
* **Binding:** *Username and password (separated)*

  * **Credentials:** your Docker Hub cred (ID: `dockerhub`)
  * **Username variable:** `DOCKERHUB_USER`
  * **Password variable:** `DOCKERHUB_PWD`

Generated wrapper:

```groovy
withCredentials([usernamePassword(credentialsId: 'dockerhub',
  usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PWD')]) {
  // docker commands go here
}
```

> Why these two?
> `git` with `credentialsId` is the safe/fast way to checkout.
> `withCredentials` injects Docker Hub secrets just for the block (masked in logs, not saved in `.git/config` or `ps`).

---

## Step 2: Define reusable environment variables

We’ll reference these in **build/push/deploy** stages.

```groovy
environment {
  IMAGE = 'docker.io/cloudwithvarjosh/cwvj-flask'   // use your namespace/repo
  TAG   = "${env.BUILD_NUMBER}"                     // easy, unique tag per run
}
```

*(You could also scope `environment {}` inside a single stage, but top-level makes them available wherever needed.)*

---

## Step 3: Full Jenkinsfile (simple, clear, production-ish)

```groovy
pipeline {
  agent any

  environment {
    IMAGE = 'docker.io/cloudwithvarjosh/cwvj-flask'   // change to your namespace/repo
    TAG   = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('checkout') {
      steps {
        git branch: 'main',
            credentialsId: 'github-pat',
            poll: false,
            url: 'https://github.com/CloudWithVarJosh/cwvj-private-repo.git'
      }
    }

    stage('build') {
      steps {
        sh 'docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .'
      }
    }

    stage('push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
          usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PWD')]) {
          sh 'echo "$DOCKERHUB_PWD" | docker login -u "$DOCKERHUB_USER" --password-stdin'
          sh 'docker push "$IMAGE:$TAG"'
          sh 'docker push "$IMAGE:latest"'
        }
      }
    }

    stage('deploy') {
      steps {
        sh 'docker pull "$IMAGE:$TAG"'
        sh 'docker rm -f cwvj-flask || true'
        sh 'docker run -d --name cwvj-flask -p 5000:5000 "$IMAGE:$TAG"'
      }
    }

    stage('test') {
      steps {
        sh 'sleep 2; curl -s http://localhost:5000 || true'
      }
    }
  }
}
```

*(We’ll add improvements like `post`, `when`, retries, and cleanup in the “Enhancements” section later.)*


---

# Improving our Day-5 flow with a Jenkinsfile

We’re doing the **same flow** as Day 5 (build → push → deploy → test), now via a **Jenkinsfile**. We’ll add four small improvements:

1. Use Pipeline Script from SCM.
2. Add **post actions**: what to do on success, on failure, and always.
3. Generate a **deploy-info.txt** (deployment details) and archive it.
4. **Clean the workspace** at the end.

---

## 1) Use Pipeline Script from SCM (so checkout happens automatically)

* Job → **Configure → Definition: Pipeline script from SCM**
  **SCM:** Git
  **Repository URL:** `https://github.com/CloudWithVarJosh/cwvj-private-repo.git` *(use your private repo)*
  **Credentials:** your GitHub PAT
  **Branches to build:** `main`

Put your **Jenkinsfile** in that repo.

> Keep the **Jenkinsfile in the same repo as the app code**—it versions with the code, works per-branch, and avoids drift.
Put reusable logic in a **Jenkins Shared Library** (separate repo) and call it from the Jenkinsfile.
Use a separate “pipeline repo” only for centralized templates/governance, not for everyday app pipelines.

---

## 2) Post actions

Add a `post {}` block at the end of the pipeline:

```groovy
post {
  success { echo "Build ${env.BUILD_NUMBER} succeeded" }
  failure { echo "Build ${env.BUILD_NUMBER} failed" }
  always  { echo "Build ${env.BUILD_NUMBER} finished" }
}
```

---

## 3) Generate and archive `deploy-info.txt`

Right after deploy, write a small file and **archive** it with the build:

```groovy
stage('deploy') {
  steps {
    sh 'docker pull "$IMAGE:$TAG"'
    sh 'docker rm -f cwvj-flask || true'
    sh 'docker run -d --name cwvj-flask -p 5000:5000 "$IMAGE:$TAG"'

    sh '''
      cat > deploy-info-$BUILD_NUMBER.txt <<EOF
build: $BUILD_NUMBER
image: $IMAGE:$TAG
commit: ${GIT_COMMIT:0:7}
branch: $GIT_BRANCH
time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
url: $BUILD_URL
EOF
    '''

    archiveArtifacts artifacts: "deploy-info-${BUILD_NUMBER}.txt", fingerprint: true
  }
}
```

---

## 4) Clean the workspace

Add a final cleanup stage:

```groovy
stage('cleanup') {
  steps { cleanWs() }
}
```

(If unsure a step exists, use the Snippet Generator at `http://localhost:8080/pipeline-syntax/`.)

---

# Consolidated Jenkinsfile (simple + improvements)

```groovy
pipeline {
  agent any

  environment {
    IMAGE = 'docker.io/cloudwithvarjosh/cwvj-flask'   // change to your namespace/repo
    TAG   = "${env.BUILD_NUMBER}"                     // simple, unique per run
  }

  stages {

    // Jenkins auto-checks out when using "Pipeline script from SCM"

    stage('build') {
      steps {
        sh 'docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .'
      }
    }

    stage('push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
          usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PWD')]) {
          sh 'echo "$DOCKERHUB_PWD" | docker login -u "$DOCKERHUB_USER" --password-stdin'
          sh 'docker push "$IMAGE:$TAG"'
          sh 'docker push "$IMAGE:latest"'
        }
      }
    }

    stage('deploy') {
      steps {
        sh 'docker pull "$IMAGE:$TAG"'
        sh 'docker rm -f cwvj-flask || true'
        sh 'docker run -d --name cwvj-flask -p 5000:5000 "$IMAGE:$TAG"'

        // write deploy info with build number in the filename
        sh '''
          cat > deploy-info-$BUILD_NUMBER.txt <<EOF
build: $BUILD_NUMBER
image: $IMAGE:$TAG
commit: ${GIT_COMMIT}
branch: $GIT_BRANCH
time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
url: $BUILD_URL
EOF
        '''

        // archive and fingerprint it
        archiveArtifacts artifacts: "deploy-info-${BUILD_NUMBER}.txt", fingerprint: true
      }
    }

    stage('test') {
      steps {
        sh 'sleep 2; curl -s http://localhost:5000 || true'
      }
    }

    stage('cleanup') {
      steps {
        cleanWs()
      }
    }
  }

  post {
    success { echo "Build ${env.BUILD_NUMBER} succeeded" }
    failure { echo "Build ${env.BUILD_NUMBER} failed" }
    always  { echo "Build ${env.BUILD_NUMBER} finished" }
  }
}
```

**That’s it.** Same Day-5 workflow, now as a Jenkinsfile, plus post actions, a deploy record you can download, and a clean workspace—while keeping the **image tag simple** (`build-number`).

---

## Conclusion

That’s Day 6. You took a working Freestyle flow and turned it into a clear, maintainable **Pipeline** with environment variables, secure credential use, post actions, deploy metadata, and cleanup. You now have the structure to grow: parameters, conditionals, parallel stages, and “Pipeline from SCM” for real projects. In the next sessions, we’ll iterate on this Jenkinsfile—shorten tags, add guards/tests, and move toward promotion patterns.

---

## References

* [Jenkins Pipeline (Overview)](https://www.jenkins.io/doc/book/pipeline/)
* [Declarative Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
* [Pipeline Syntax Snippet Generator](https://www.jenkins.io/doc/book/pipeline/getting-started/#snippet-generator)
* [Using Credentials in Jenkins Pipelines](https://www.jenkins.io/doc/book/using/using-credentials/)
* [Docker: `docker login` and image tagging](https://docs.docker.com/reference/cli/docker/)