# Day 5: Jenkins Project 1: Build, Push & Run a Flask App with Jenkins (DooD)

## Video reference for Day 5 is the following:

[![Watch the video](https://img.youtube.com/vi/UYlVTs_yK8U/maxresdefault.jpg)](https://www.youtube.com/watch?v=UYlVTs_yK8U&ab_channel=CloudWithVarJosh)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## Table of Contents

Here’s the updated **clickable Table of Contents** with colons in the step headings:

* [Introduction](#introduction)
* [Why we’re doing this](#why-were-doing-this)
* [What approach we’ll use (DooD)](#what-approach-well-use-dood)
  * [Step 1: Recreate Jenkins with the Docker socket mounted](#step-1-recreate-jenkins-with-the-docker-socket-mounted)
  * [Step 2: Allow the Jenkins user to talk to the socket (lab-simple)](#step-2-allow-the-jenkins-user-to-talk-to-the-socket-lab-simple)
  * [Step 3: Install the Docker CLI inside the Jenkins container](#step-3-install-the-docker-cli-inside-the-jenkins-container)
  * [Step 4: Verify from inside Jenkins](#step-4-verify-from-inside-jenkins)
* [Quick FAQ](#quick-faq)
* [Demo — Build, Push & Deploy a Flask App with Jenkins (DooD)](#demo--build-push--deploy-a-flask-app-with-jenkins-dood)

  * [0) Create a private GitHub repo](#0-create-a-private-github-repo)
  * [1) Create a GitHub Personal Access Token (PAT)](#1-create-a-github-personal-access-token-pat)
  * [2) Add credentials in Jenkins (GitHub & Docker Hub)](#2-add-credentials-in-jenkins-github--docker-hub)
  * [3) Create the Jenkins Freestyle job](#3-create-the-jenkins-freestyle-job)
  * [4) Run it end-to-end](#4-run-it-end-to-end)
* [Conclusion](#conclusion)
* [References](#references)

---

## Introduction

Welcome to **Day 5**! Today we’ll make Jenkins actually *ship* something. We’ll set up **Docker-outside-of-Docker (DooD)** so the Jenkins container can use the host’s Docker Engine, then build a tiny **Flask** app, **containerize** it, **push** the image to a **private Docker Hub repository**, and **deploy** it on the host for a quick smoke test. You’ll see the full CI loop end-to-end—**code → image → private registry → running container**—while keeping secrets safe with Jenkins Credentials.

---

## Why we’re doing this

Up to now we ran Jenkins in a container and built simple projects. As we move to **containerized apps**, our builds need to **build images and push them to a container registry**. That means Jenkins needs access to a tool that can create **OCI-compliant images**. We’ll use **Docker** for this.

### What approach we’ll use (DooD)

![DooD overview](/images/5a.png)

**Reading the diagram:**

* **Left (What we HAVE):** A Jenkins container exposed on **port 8080** with **no Docker access**.
* **Right (What we WANT — DooD):** The **Docker CLI lives inside the Jenkins container**, and a line labeled **`/var/run/docker.sock`** connects it to the **host Docker daemon**. No daemon runs inside Jenkins.

**Docker-outside-of-Docker (DooD) in one minute:**

* We **don’t** start a Docker daemon in the Jenkins container.
* We **mount the host socket** `-v /var/run/docker.sock:/var/run/docker.sock` and install **only the Docker CLI** in Jenkins.
* Commands run **inside Jenkins** (e.g., `docker build/push/run`) are executed by the **host’s Docker daemon** via that socket.
  *Result: fast, simple, perfect for a lab—handle with care because it grants powerful access to the host.*

> **Production note:** Prefer **Docker-enabled agents** or **daemonless builders** (e.g., **Kaniko**, **BuildKit**, **Buildx with remote driver**) instead of sharing the host socket.

---

## Step 1: Recreate Jenkins with the Docker socket mounted

We already persisted Jenkins state in a **named volume** (`jenkins_home`), so recreating the container won’t lose plugins, jobs, or config.

```bash
docker rm -f jenkins 2>/dev/null || true

docker run -d --name jenkins --restart unless-stopped \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e TZ=Asia/Kolkata \
  jenkins/jenkins:lts
```

**What this does:** the `-v /var/run/docker.sock:/var/run/docker.sock` line shares the **host’s Docker daemon** with the Jenkins container.

**What is `docker.sock`?**
On Linux, processes on the same machine can talk to each other using **Unix domain sockets** (files ending in `.sock`). These are special IPC endpoints that live on the filesystem and don’t use TCP/IP networking.
`/var/run/docker.sock` is the Unix socket where the **Docker daemon** listens for API requests. The **`docker` CLI** sends commands (build, run, push, etc.) through this socket to the daemon. If you mount this file into a container, commands inside that container control the **host’s Docker daemon**—powerful, so handle with care.

> By mounting `/var/run/docker.sock` into the Jenkins container, the **docker CLI inside the container** sends its commands to the **Docker daemon on the host** (Mac in my case). In other words, the container controls the host’s Docker engine—fast for labs, but powerful, so use with care.

---

## Step 2: Allow the Jenkins user to talk to the socket (lab-simple)

By default the socket is owned by `root:root` and not readable by others:

```bash
docker exec -it jenkins ls -l /var/run/docker.sock
# srw-rw---- 1 root root ... /var/run/docker.sock
```

**Lab-simple option:** make it world-read/write (quickest for demos):

```bash
docker exec -u root -it jenkins chmod 666 /var/run/docker.sock
```

> Note: This is convenient for a lab. For a safer setup, map the socket’s group and add `jenkins` to it. You can switch later.

Docker recreates its socket on every reboot or when the Docker daemon restarts, so any manual `chmod` changes are lost.
To make access persistent and safe, add the `jenkins` user to the host `docker` group so Jenkins can use the socket without repeated chmod.

---

## Step 3: Install the Docker **CLI** inside the Jenkins container

We’re installing **only the client**, not a daemon.

```bash
docker exec -u root -it jenkins bash -lc \
  'curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh'
```

---

## Step 4: Verify from inside Jenkins

```bash
docker exec -it jenkins bash -lc 'docker version && docker ps'
```

You should see:

* `Client: Docker Engine - Community` (CLI present)
* `Server: Docker Engine - Community` (talking to the host daemon)
* `docker ps` listing your **jenkins** container (because the CLI is using the host’s daemon)

---

### Quick FAQ

* **Are we “installing Docker in Jenkins”?**
  We install **the Docker CLI** in the Jenkins container. The **daemon** is the host’s; we access it via the mounted socket.
* **Why not run a daemon inside Jenkins (DinD)?**
  Needs `--privileged`, more moving parts, slower caches. Fine for labs, but DooD is simpler here.
* **Is the socket mount safe?**
  It grants broad control over the host daemon. OK for a personal lab; in real setups prefer Docker-enabled **agents**, or **daemonless** builders.
* **Will my Jenkins data persist across container recreates?**
  Yes—because `-v jenkins_home:/var/jenkins_home` stores state in a named volume.

---


# Demo — Build, Push & Deploy a Flask App with Jenkins (DooD)

### What we’ll do

![Alt text](/images/5b.png)

Create a tiny **Flask** app, **build a container image**, **push** it to a **private Docker Hub repo**, and **deploy** it on the Docker host using **DooD**.
**Why this matters:** it shows the full CI loop in one pass — **Code → Image → Private Registry → Running Container → Smoke Test**.

---

## 0) Create a **private GitHub repo**

Use **`https://github.com/CloudWithVarJosh/cwvj-private-repo.git`** as the example I’m using in the lecture. **You should use your own private repo** (on GitHub, GitLab, Bitbucket—any git host is fine).

All the files you need to upload for this demo (**`app.py`**, **`requirements.txt`**, **`Dockerfile`**, **`.dockerignore`**) are also available in the **GitHub repo for this lecture**.

Upload them (via the web UI for now) into **your** repo’s **root** (or a `python/` folder—just stay consistent with whatever path you reference in Jenkins).


**`app.py`**

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/")
def hello():
    return jsonify(
        message="✨ Welcome to Cloud with VarJosh ✨",
        tip="Built with Flask, shipped by Jenkins, running in Docker."
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**`requirements.txt`**

```
flask==3.0.3
```

**`Dockerfile`**

```dockerfile
# Small Python base image (Debian slim) to keep the final image light
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy only dependency list first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies (no pip download cache in the image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Document the port the app listens on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]

```

**`.dockerignore`**

```
__pycache__/
*.pyc
.git
```

---

## 1) Create a **GitHub Personal Access Token** (PAT)

* GitHub → **Settings → Developer settings → Personal access tokens**.
* **Fine-grained token:** grant **Contents: Read** on your private repo; or
  **Classic token:** scope **`repo`** (read is enough for checkout).
* **Copy the token now** (you’ll only see it once).

---

## 2) Add **credentials** in Jenkins (GitHub & Docker Hub)

#### A) GitHub PAT (for SCM checkout)

* Jenkins → **Manage Jenkins → Credentials → System → Global → Add Credentials**

  * **Kind:** *Username with password*
  * **Username:** your GitHub username
  * **Password:** your **PAT**
  * **ID:** `github-pat` (easy to remember)
  * Save.

#### B) Docker Hub (for push & private pull)

* Ensure you have a **private** repo on Docker Hub (e.g., `cloudwithvarjosh/cwvj-flask`).
* Jenkins → **Manage Jenkins → Credentials → System → Global → Add Credentials**

  * **Kind:** *Username with password*
  * **Username:** your Docker Hub username
  * **Password:** your Docker Hub password or token
  * **ID:** `dockerhub`
  * Save.

> Store secrets **once** in Jenkins Credentials and reference them—don’t paste them into **Execute shell**.
If you type a username/password or token directly in the shell step, it will show up in the **job config** and can leak in **console logs/history**—exactly what you don’t want.
Instead, add creds in **Manage Jenkins → Credentials**, then in the job enable **Build Environment → Use secret text(s) or file(s)** to inject variables like `DOCKERHUB_USER` / `DOCKERHUB_PWD`.
This keeps secrets out of scripts and logs while letting your shell commands use them safely.


---

## 3) Create the **Jenkins Freestyle job**

**Job name:** `flask-dood-demo` → **Freestyle project → OK**

### A) **Source Code Management → Git**

* **Repository URL:** `https://github.com/CloudWithVarJosh/cwvj-private-repo.git`
* **Credentials:** `github-pat`
* **Branches to build:** `*/main` (or your branch)

### B) **Build Environment → Use secret text(s) or file(s)**

We’ll inject Docker Hub creds as environment variables the shell can use:

* Tick **Use secret text(s) or file(s)** → **Add** → **Username and password (separated)**

  * **Credentials:** pick `dockerhub`
  * **Username variable:** `DOCKERHUB_USER`
  * **Password variable:** `DOCKERHUB_PWD`

### C) *(Optional) Parameters*

If you want a visible tag parameter:

* **This project is parameterized → Add Parameter → String Parameter**

  * **Name:** `TAG`
  * **Default value:** `${BUILD_NUMBER}`

### D) **Build Steps → Execute shell**

Paste this (kept beginner-simple, deploys with the exact tag):

```bash

# 1) Docker login (uses injected env vars)
echo "Logging in to Docker Hub..."
echo "$DOCKERHUB_PWD" | docker login -u "$DOCKERHUB_USER" --password-stdin

# 2) Image naming
IMAGE="docker.io/cloudwithvarjosh/cwvj-flask"
TAG="${BUILD_NUMBER}"

# 3) Build and push (exact tag + latest for convenience)
echo "Building image..."
docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .

echo "Pushing image..."
docker push "$IMAGE:$TAG"
docker push "$IMAGE:latest"

# 4) Deploy on the Docker host (DooD)
echo "Deploying..."
docker pull "$IMAGE:$TAG"
docker rm -f cwvj-flask || true
docker run -d --name cwvj-flask -p 5000:5000 "$IMAGE:$TAG"

# 5) Quick smoke check (optional)
sleep 2
echo "Hit http://localhost:5000 to see the app."
```

> Because the job runs **inside** your Jenkins container but talks to the **host** Docker daemon (via `/var/run/docker.sock`), the deployed container (`cwvj-flask`) will appear in your **host** `docker ps`.

### E) *(Optional, at the very end) Workspace cleanup*

After you’ve confirmed everything works, you can enable cleanup to save disk:

* **Post-build Actions → Delete workspace when build is done** *(Workspace Cleanup plugin)*, **or** add a final shell step:

  ```bash
  echo "Cleaning workspace..."
  rm -rf "$WORKSPACE"/* || true
  ```

---

## 4) Run it end-to-end

1. **Commit & push** the four files to your private GitHub repo.
2. In Jenkins, click **Build Now**.
3. Watch Console Output: you should see login → build → push → deploy.
4. Open `http://localhost:5000` in your browser (or):

   ```bash
   curl -s http://localhost:5000
   ```

   You should see the JSON message:

   ```
   {"message":"✨ Welcome to Cloud with VarJosh ✨", ...}
   ```

---


## Conclusion

By the end of this lesson, you’ll have a working Jenkins job that checks out a private repo, logs in to Docker Hub with masked credentials, builds a tagged image, pushes both a reproducible tag (e.g., `:BUILD_NUMBER`) and `:latest`, and runs the container on the host via DooD. You now understand where `docker.sock` fits, why we use the Docker **CLI** (not a daemon) inside the Jenkins container, and how to deploy reliably by pinning exact tags. Next, we’ll take these steps and move them into a **Pipeline (Jenkinsfile)** so builds are codified, reviewable, and reusable.

--- 
## References

* [Docker: `docker login` (including `--password-stdin`)](https://docs.docker.com/reference/cli/docker/login/)
* [Jenkins Credentials – Using credentials](https://www.jenkins.io/doc/book/using/using-credentials/)
* [Credentials Binding (Freestyle & masking in console)](https://plugins.jenkins.io/credentials-binding/)
* [Dockerfile reference (`HEALTHCHECK`, `COPY`, `RUN`)](https://docs.docker.com/reference/dockerfile/)
* [Flask Quickstart](https://flask.palletsprojects.com/en/latest/quickstart/)

---

