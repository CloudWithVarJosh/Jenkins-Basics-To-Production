# Jenkins Shared Library Tutorial: Real World CI/CD with Reusable Pipeline Steps

## Video reference for this lecture is the following:

[![Watch the video](https://img.youtube.com/vi/Eql35HIXS4A/maxresdefault.jpg)](https://www.youtube.com/watch?v=Eql35HIXS4A&ab_channel=CloudWithVarJosh)


---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

# **Table of Contents**

* [Introduction](#introduction)
* [Why Jenkins Shared Library?](#why-jenkins-shared-library)

  * [Challenges With the Traditional Approach](#challenges-with-the-traditional-approach)
* [Enter Jenkins Shared Library](#enter-jenkins-shared-library)

  * [Why This Is Powerful](#why-this-is-powerful)
* [Using a Shared Library in Jenkins](#using-a-shared-library-in-jenkins)
* [Shared Library Directory Structure](#shared-library-directory-structure)

  * [1. `vars/` (Most Important Directory)](#1-varsmost-important-directory)
  * [2. `src/`](#2-src)
  * [3. `resources/`](#3-resources)
* [Lab: Install Jenkins Controller on EC2](#lab-install-jenkins-controller-on-ec2)

  * [Prerequisites](#prerequisites)
  * [1 - Create the EC2 instance](#1---create-the-ec2-instance)
  * [2 - Connect to the instance and basic setup](#2---connect-to-the-instance-and-basic-setup)
  * [3 - Install Java 21 JDK](#3---install-java-21-jdk)
  * [4 - Add the Jenkins repository and install Jenkins](#4---add-the-jenkins-repository-and-install-jenkins)
  * [5 - Start and enable Jenkins](#5---start-and-enable-jenkins)
  * [6 - Access Jenkins UI and initial setup](#6---access-jenkins-ui-and-initial-setup)
  * [7 - Run pipeline workloads on the controller lab-mode](#7---run-pipeline-workloads-on-the-controller-lab-mode)
  * [8 - Install Docker Engine on the controller](#8---install-docker-engine-on-the-controller-for-lab-demos)
  * [9 - Allow Jenkins user to run Docker](#9---allow-jenkins-user-to-run-docker-lab-convenience-only)
* [Demo 1: Configure a very simple Shared Library](#demo-1-configure-a-very-simple-shared-library)

  * [Step 1: Create Repo and Minimal Layout](#step-1-create-repo--minimal-repo-layout)
  * [Step 2: Create Jenkins Shared Library](#step-2-create-jenkins-shared-library)
  * [Step 3: Write the Pipeline Script](#step-3-write-the-pipeline-script)
  * [Step 4: Run and Verify](#step-4-run--verify-execute-the-job-and-check-logs)
* [Demo 2: Private repos plus Jenkins Shared Library](#demo-2-private-repos--jenkins-shared-library)

  * [Step 1: Create private repositories](#step-1-create-private-repositories)
  * [Step 2: Create a GitHub PAT](#step-2-create-a-github-personal-access-token-pat-and-add-to-jenkins-credentials)
  * [Step 3: Prepare local project folders](#step-3-prepare-local-project-folders-and-files)
  * [Step 4: Initialize git and push repos](#step-4-initialize-git-and-push-each-repo-app1-app2-shared-library)
  * [Step 5: Create Pipeline jobs](#step-5-create-pipeline-jobs-in-jenkins-app1-job--app2-job)
  * [Step 6: Verify jobs without shared library](#step-6-verify-jobs-build-without-shared-library-quick-smoke-test)
  * [Step 7: Add private shared library](#step-7-add-private-shared-library-to-jenkins-global-pipeline-libraries)
  * [Step 8: Move build and deploy logic to library](#step-8-move-build--deploy-logic-to-the-shared-library-what-to-put-in-shared-library-private)
  * [Step 9: Update app Jenkinsfiles](#step-9-update-each-app-jenkinsfile-to-use-the-shared-library)
  * [Step 10: Run jobs and verify](#step-10-run-the-jobs-and-verify-final)
  * [Step 11: Demonstrate the power of the shared library](#step-11-demonstrate-the-power-of-the-shared-library)
* [Why centralising config matters](#why-centralising-config-matters)
* [Conclusion](#conclusion)
* [References](#references)

---

# **Introduction**

Modern organisations rarely work with a single application. Most engineering teams manage **multiple repositories**, each performing the **same build, test, security, and deployment steps** inside its Jenkinsfile. Even though these steps look identical, every team ends up **copying and pasting the same pipeline logic**, which leads to duplication and drift.

**Jenkins Shared Libraries** were created to solve this exact problem. Instead of repeating pipeline code across many services, you **centralise all common logic in one dedicated repository** and call it from any Jenkinsfile.
This lecture walks you from the **problem landscape**, into **why Shared Libraries matter**, and finally through **hands-on demos** that show how Shared Libraries give you consistency, simplicity, and true scalability in CI CD pipelines.

---

# Why Jenkins Shared Library?

Before we even use the term Shared Library, let’s understand the **problem landscape** that existed *before* this feature came into the picture.

![Alt text](/images/sl1.png)

When you work with multiple projects inside an organisation, you quickly realise that a large portion of your CI CD pipeline is **repetitive**.
Some examples:

* Logging into your container registry (ECR, Docker Hub, Artifactory)
* Running static code analysis tools (SonarQube)
* Running security scanners (Trivy, Snyk)
* Building source code using the same build tool (Maven, Gradle, npm)
* Running test suites
* Sending notifications (Slack, Teams, Email)

None of these are unique to a single microservice. They are routine steps that every team and every project must perform.

Now imagine your organisation runs **20 Java based microservices**.
Naturally, each repository will have its own **Jenkinsfile**.

This creates a challenge.

---

## Challenges With the Traditional Approach

Without shared libraries, each Jenkinsfile contains **duplicate logic**:

* SonarQube analysis step repeated 20 times
* Maven or Gradle build steps repeated 20 times
* Trivy container scan repeated 20 times
* Registry login repeated 20 times
* Notification steps repeated 20 times

This leads to:

### 1. Massive Duplication

Every project maintains its own copy of the same pipeline code.
If the logic is 20 lines long and you have 20 repos, that’s 400 lines to maintain.

### 2. Inconsistent Pipelines

Minor copy paste differences start creeping in.
One repo uses the latest scanner flags, another uses outdated flags.

### 3. High Maintenance Overhead

If something changes, such as:

* SonarQube URL changes
* Credentials ID is updated
* Trivy requires new arguments
* The organisation introduces a new compliance step

you now have to modify **20 separate Jenkinsfiles**.
This is slow, error prone and simply not scalable.

### 4. Difficult Onboarding

New developers or DevOps engineers struggle to understand why each project looks different even though the logic is the same.

---

# Enter Jenkins Shared Library

![Alt text](/images/sl2.png)

A Jenkins Shared Library solves all the above challenges by allowing you to **centralise your common pipeline code** in a separate GitHub repository.

Instead of repeating the same logic across 20 Jenkinsfiles, you:

1. Move the common logic into the Shared Library
2. Reference it from each Jenkinsfile
3. Call reusable functions wherever needed

Now, all 20 projects share the same behaviour, and any future change is made in **one place**.

---

## Why This Is Powerful

* **Write once, use everywhere**
  Define your common logic only once, and call it across all Jenkinsfiles.

* **Update in one location**
  If SonarQube, Trivy or any pipeline step needs modification, update the Shared Library once and every pipeline benefits instantly.

* **Cleaner Jenkinsfiles**
  Jenkinsfiles focus only on project specific logic, while reusable steps become simple function calls.

* **Easy programming analogy**
  A Shared Library works like defining functions in a programming language. You write them once and invoke them multiple times across different codebases.

---


# Using a Shared Library in Jenkins

When using a shared library, your Jenkinsfile typically requires only **two changes**:

### 1. Import the Shared Library

```groovy
@Library('my-shared-library') _
```

### 2. Call the functions from the library

```groovy
buildWithMaven()
runSonarAnalysis()
performTrivyScan()
```

This keeps the Jenkinsfile short, readable and maintainable.

---


# **Shared Library Directory Structure**

![Alt text](/images/sl3.png)

A Jenkins Shared Library follows a predictable structure in the root of the repository.
This structure tells Jenkins **where to look** for global steps, helper classes, and supporting files.

```
.
|__ src/
|__ vars/
|__ resources/
```

For Demo 2 (will come Later), your library looks like this:

```
shared-library-private/
├─ src/
├─ vars/
│  ├─ buildImage.groovy
│  └─ deployApp.groovy
└─ resources/
```

This layout is what allows both `app1` and `app2` to share the same build and deploy logic simply by importing the library in their Jenkinsfiles.

---

## **1. `vars/` (Most Important Directory)**

Anything placed inside vars/ is treated as a global variable and becomes directly callable from your Jenkinsfile.

**Key points:**

* Files must end with `.groovy`
* The **filename becomes the step name**
* Jenkins looks for a `call()` function inside each file
* Recommended naming style is **camelCase**
* Most DevOps teams rely heavily on this folder because it makes pipeline steps easy to use

**Diagram connection:**
This is where `buildImage.groovy` and `deployApp.groovy` live, and the diagram shows both apps calling those same functions.

**Example:**

`vars/buildWithMaven.groovy`

```groovy
def call() {
    sh 'mvn clean install'
}
```

Usage in Jenkinsfile:

```groovy
buildWithMaven()
```

---

## **2. `src/`**

This folder behaves like a typical Groovy or Java package structure.

Use it when:

* Logic becomes too complex for a simple `vars/*.groovy` file
* You want reusable **helper classes**
* You prefer organizing code in packages

**Example structure:**

```
src/org/devops/util/EmailHelper.groovy
```

These classes are not automatically exposed like `vars/` steps.
They are **imported into `vars/*.groovy` files or used internally** within the library.

**Diagram connection:**
The diagram does not dive into `src/` because Demo 2 uses only `vars/`, but this folder exists for more advanced use cases.

---

## **3. `resources/`**

Place non Groovy assets here:

* JSON templates
* YAML manifests
* Configuration files
* Shell scripts
* Any static text content

Jenkins loads these files using:

```groovy
libraryResource 'path/to/file'
```

This avoids embedding long templates inside Groovy code and keeps things cleaner.

**Diagram connection:**
This folder is shown as part of the library structure but intentionally not used in Demo 2 to keep things simple.

---

# Lab: Install Jenkins Controller on EC2

This VM will act **both as the controller and the runner for pipeline jobs** in this lab.
In production, pipeline workloads should run on dedicated agents, not the controller.

---

## Prerequisites

* An AWS account and ability to create EC2 instances.
* A local SSH key (`<your-key>.pem`) to connect to the instance.
* Basic familiarity with sudo on Ubuntu.

---

## 1 - Create the EC2 instance

* **AMI:** Ubuntu 24.04 LTS.
* **Instance type:** c7i-flex.large.
* **Root volume:** 20 GB or larger.

Security Group for the Jenkins controller VM:

* Allow **SSH (22)** from your IP.
* Allow **HTTP (8080)** from your IP for Jenkins UI.

---

## 2 - Connect to the instance and basic setup

From your workstation, lock down your private key and SSH in:

```bash
chmod 600 ~/path/to/<your-key>.pem
ssh -i ~/path/to/<your-key>.pem ubuntu@<jenkins-controller-public-ip>
```

On the instance, set hostname and timezone:

```bash
sudo hostnamectl set-hostname jenkins-controller  
exec bash  
sudo timedatectl set-timezone Asia/Kolkata  
timedatectl status
```

---

## 3 - Install Java 21 (JDK)

Jenkins LTS works well with Java 21. Install and verify:

```bash
sudo apt update
sudo apt install -y openjdk-21-jdk
java -version
javac -version
```

---

## 4 - Add the Jenkins repository and install Jenkins

Reference: https://www.jenkins.io/doc/book/installing/linux/

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | \
  sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | \
  sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins
```

---

### Set Jenkins JVM timezone (systemd override)

Make Jenkins UI timestamps match server timezone by setting `JAVA_OPTS`.

**Interactive:**

```bash
sudo systemctl edit jenkins
# add:
[Service]
Environment="JAVA_OPTS=-Duser.timezone=Asia/Kolkata"
# save and exit
```

**Non-interactive:**

```bash
sudo mkdir -p /etc/systemd/system/jenkins.service.d
cat <<'EOF' | sudo tee /etc/systemd/system/jenkins.service.d/override.conf > /dev/null
[Service]
Environment="JAVA_OPTS=-Duser.timezone=Asia/Kolkata"
EOF
```

After creating the override, reload systemd and restart Jenkins.

---

## 5 - Start and enable Jenkins

```bash
sudo systemctl daemon-reload
sudo systemctl enable jenkins
sudo systemctl status jenkins
```

---

## 6 - Access Jenkins UI and initial setup

Open in browser:

```
http://<jenkins-controller-public-ip>:8080
```

Get the initial admin password on the controller:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

In the UI:

* Install suggested plugins.
* Create the admin user.
* Complete initial setup and log in.

---

## 7 - Run pipeline workloads on the controller (lab mode)

* For this lab the controller will run build and deploy steps locally.
* If your pipelines run Docker, install Docker on the controller (instructions next).
* Note: running builds on the controller is fine for demos but not recommended for production.

---

## 8 - Install Docker Engine on the controller (for lab demos)

Use Docker official steps on Ubuntu hosts that will run containers. These commands are safe on a fresh VM.

```bash
# remove legacy packages if any (safe)
sudo apt remove docker docker-engine docker.io containerd runc -y

# refresh apt cache
sudo apt update

# install helper packages
sudo apt install -y ca-certificates curl gnupg

# prepare keyrings dir
sudo install -m 0755 -d /etc/apt/keyrings

# fetch Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

# add Docker apt repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# refresh and install Docker Engine and plugins
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## 9 - Allow Jenkins user to run Docker (lab convenience only)

Adding the `jenkins` user to the `docker` group is convenient for demos but has security implications in production.

```bash
sudo usermod -aG docker jenkins
# optionally add ubuntu user for admin demos
sudo usermod -aG docker ubuntu

# restart Jenkins so new group membership is picked up
sudo systemctl restart jenkins
```

Verify Docker from the jenkins user:

```bash
docker --version
sudo -u jenkins docker --version
```

---

## Lab notes and security reminders

* Adding the Jenkins user to the `docker` group grants container runtime privileges to Jenkins. This is fine for learning and demos but risky for production. Use dedicated agent hosts in production.
* Restrict port 8080 to your IP or a VPN. Do not open it publicly.
* Keep the Jenkins server patched and limit SSH access to trusted IPs.

---

# Demo 1: Configure a very simple Shared Library

**Goal**: show how to wire a shared library into a job and call one trivial step that only echoes a message. This proves the concept without introducing complexity.

---

## Step 1: Create Repo & Minimal repo layout

We will first create a **public** repository for the demo.
I am naming mine `shared-library-demo`.

```
shared-library-demo/  
├─ vars/  
│  └─ simpleEcho.groovy  
└─ README.md  
```

* Only `vars/` is used so viewers can see how a single global step maps into the `Jenkinsfile`.
* `simpleEcho.groovy` is intentionally tiny and safe.

> **Note:** I recommend you create your own public repo, because I will delete this public repo.


**About the `.groovy` extension and file contents**
Files inside `vars/` must use the `.groovy` extension. Jenkins treats `vars/*.groovy` as executable pipeline steps and loads them as Groovy code available to pipelines. The contents should be valid Groovy (commonly a `call(...)` method or a top-level closure) so the step can be invoked like a function from the `Jenkinsfile`. If you need static templates or other text files, put them under `resources/` and load them with `libraryResource`.

**`vars/simpleEcho.groovy`**

```groovy
// vars/simpleEcho.groovy
def call() {
  echo "Jenkins Shared Library Project with CWVJ"
}
```

* **What is `def call()` and why put it in `vars/*.groovy`?**
  When you create a file inside the `vars` folder, Jenkins expects one main function it can run when the step is called from a `Jenkinsfile`.
  That main function must be named `call`.

* **Filename → step mapping**
  The file `simpleEcho.groovy` becomes a global step named `simpleEcho()` in Jenkins.

* **Why this function is so simple**
  The function only echoes a short message. This is deliberate: it demonstrates the wiring from library to job without introducing secrets, external tools, or agent differences.

---

## Step 2: Create Jenkins Shared Library

* **Open** `Manage Jenkins` → `System` → `Global Pipeline Libraries`.
  This is where you register a reusable library that pipelines can import.

* **Name**: `my-first-shared-library`.
  This identifier is what you reference later in `@Library('...')`.

* **Default version**: `main`.
  The branch, tag, or commit Jenkins will use when a pipeline (via `Jenkinsfile`) does not request a specific version. For this demo pick `main`.

* **Load implicitly**: leave unchecked.
  Keep this unchecked so pipelines explicitly declare which libraries they use. This improves clarity for engineers reading the `Jenkinsfile`.

* **Allow default version to be overridden**: keep checked.
  This allows a pipeline to pin a different library version using `@Library('name@v1.2')`.

* **Include `@Library` changes in job recent changes**: keep checked.
  When checked, updates to the library are included in build changesets and can appear in pipeline change logs. You can override this per pipeline with `@Library(value="name@version", changelog=true|false)`.

* **Cache fetched versions on controller**: leave unchecked for the demo.
  For simple demos leave it off. In production enabling caching can speed retrieval.

* **Retrieval method**: select `SCM` → `Git` and enter the repository URL.
  Example repo for this demo: `https://github.com/CloudWithVarJosh/shared-library-demo.git`.

* **Save and verify**: after saving, confirm Jenkins can reach the repository and that the configured name matches what you will use in `@Library`.
  Check connectivity and validate that the repository is accessible from the Jenkins controller.


---


## Step 3: Write the Pipeline Script

Use this as the job's Pipeline script (not Pipeline script from SCM).

**Create the Jenkins job**

* In Jenkins, click **New Item** → enter `shared-library-job` → select **Pipeline** → click **OK**.
  Give the job a short description if you like.
* In the job configuration, scroll to **Pipeline** → **Definition** → choose **Pipeline script**.
  Paste the pipeline shown below into the **Script** box.
* Save the job.

```groovy
@Library('my-first-shared-library@main') _

pipeline {
  agent any

  stages {
    stage('Demo - call shared step') {
      steps {
        // Calls vars/simpleEcho.groovy
        simpleEcho()
      }
    }
  }
}
```

* **`@Library('my-first-shared-library@main') _`** tells Jenkins to **load** the shared library named `my-first-shared-library` using the `main` version for this script; the trailing underscore (`_`) is just a harmless placeholder so Groovy accepts the annotation syntactically and has no runtime effect. Place this line at the very **top** of the `Jenkinsfile`; if the library is configured to “load implicitly” you do not need it, but explicitly **importing** the library makes the pipeline easier to read and debug.

* **`pipeline { agent any ... }`** tells Jenkins to run the job on any available agent.

* **`stage('Demo - call shared step')`** groups the work so the UI shows a clear stage during the run.

* **`steps { simpleEcho() }`** calls the **`simpleEcho()`** global step from **`vars/simpleEcho.groovy`**. The step prints the demo message to the Jenkins console.

* This pipeline is intentionally **minimal**: **no post actions**, **no credentials**, and **no external tools**; it only proves the wiring between Jenkins and the shared library.

> Note: **Import** the shared library at the **top** of the `Jenkinsfile` (for example `@Library('my-first-shared-library@main') _`) so Jenkins loads it, then call steps by the filename without `.groovy` (for example **`simpleEcho()`**) inside your stages; different stages can call different **`vars/*.groovy`** steps (e.g., `stage A` calls `foo()`, `stage B` calls `bar()`), and Jenkins will invoke only each file’s **`call(...)`** entry point.


---

## Step 4: Run & Verify (Execute the job and check logs)

* Click **Build Now** on the `shared-library-job`.
  Wait for the new build to start and appear in **Build History**.

* Open the latest build and click **Console Output** to view the run log.
  Look for the stage header `Demo - call shared step` and the echo line:
  `Jenkins Shared Library Project with CWVJ`  (or your custom message if you passed one).

* Confirm the build completed successfully; look for `Finished: SUCCESS` near the end of the log.

---

# Demo 2: Private repos + Jenkins Shared Library

**What we are going to do?**
In this demo we will show a production-like flow where two private application repositories (`app1-private`, `app2-private`) use a private shared-library (`shared-library-private`) hosted on GitHub.
You will wire Jenkins to authenticate to private repos, register the shared library, and convert each app’s pipeline to call two reusable library steps: one to **build** the Docker image and one to **deploy** the container.
By the end you will prove that changing the build or deploy logic in a single shared-library file immediately affects both app pipelines without editing their `Jenkinsfile`s.

**Quick flow (high level):**

* Create three private Git repos (app1, app2, shared-library).
* Add a GitHub PAT to Jenkins so it can access private repos.
* Push app code and simple `Jenkinsfile`s to app repos.
* Configure Jenkins jobs to use **Pipeline script from SCM** for each app.
* Add the private shared-library to Jenkins Global Pipeline Libraries.
* Move `docker build` and `docker run` steps into `vars/buildImage.groovy` and `vars/deployApp.groovy`.
* Update app `Jenkinsfile`s to import the library and call `buildImage(...)` and `deployApp(...)`.
* Run both jobs and verify apps are running; then change one line in the shared library and re-run to demonstrate the single-change effect.

This demo focuses on clear, repeatable steps that show the practical value of a shared library in a private, production-like setup.


---

## Step 1: Create private repositories

Create three private GitHub repos:

* `app1-private`
* `app2-private`
* `shared-library-private`

These repos will hold your app code and the private shared library respectively.

---

## Step 2: Create a GitHub Personal Access Token (PAT) and add to Jenkins credentials

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Classic tokens**.
2. Create a Classic PAT with scope **repo** (this allows push).
   In production prefer least-privilege tokens or deploy keys.
3. Copy the token now — GitHub will not show it again.

Add the PAT to Jenkins:

* **Manage Jenkins → Credentials → System → Global credentials (unrestricted)** → **Add Credentials**.

  * Kind: **Username with password**
  * Username: your GitHub username (`YOUR_GH_USER`)
  * Password: your PAT (`<paste-token-here>`)
  * ID: `github-pat` (use this id in examples below)
  * Description: e.g. `GitHub PAT for private repos`

Purpose: Jenkins will use these credentials to checkout the private repos for the Pipeline jobs and to fetch the shared library.

---

## Step 3: Prepare local project folders and files

On your laptop create a `project-files` folder and inside it three subfolders: `app1`, `app2`, `shared-library`.
Place the code for each app in its folder. Minimum contents:

* `app1/` → `app1.py`, `Dockerfile`, `Jenkinsfile`
* `app2/` → `app2.py`, `Dockerfile`, `Jenkinsfile`
* `shared-library/` → `vars/buildImage.groovy`, `vars/deployApp.groovy`, `README.md` (we’ll add these below)

**Note:** We’ll first verify the apps work without the shared library, then wire the shared library in.

---

## Step 4: Initialize git and push each repo (app1, app2, shared-library)

> Use your PAT only in the one-time push command OR configure git credential helper. Never hardcode tokens in files.

Example for **app1** (replace `YOUR_GH_USER` and `YOUR_PAT_HERE`):

```bash
cd app1
git init
git add .
git commit -m "Initial commit with app1 code & Jenkinsfile"
git branch -M main
git remote add private-repo https://github.com/YOUR_GH_USER/app1-private.git
git remote set-url private-repo https://<YOUR_PAT_HERE>@github.com/<YOUR_GH_USER>/app1-private.git
git push private-repo main
```

Repeat for **app2** (use `app2-private` repo).

For the **shared library** push, point to `shared-library-private` (important — do **not** push shared-library into app1 repo):

```bash
cd shared-library
git init
git add .
git commit -m "Initial commit with shared library steps"
git branch -M main
git remote add private-repo https://github.com/YOUR_GH_USER/shared-library-private.git
git remote set-url private-repo https://<YOUR_PAT_HERE>@github.com/<YOUR_GH_USER>/shared-library-private.git
git push private-repo main
```

Security note: after pushing, remove the stored PAT from remote URL or use the credential helper so you are not keeping token in your repo config.

---

## Step 5: Create Pipeline jobs in Jenkins (app1-job + app2-job)

Create a Pipeline job for each app using **Pipeline script from SCM** so Jenkins checks out the app repo and runs its `Jenkinsfile`.

Example for **app1-job**:

* Name: `app1-job`
* Type: Pipeline
* Pipeline → Definition: **Pipeline script from SCM**

  * SCM: **Git**
  * Repository URL: `https://github.com/YOUR_GH_USER/app1-private.git`
  * Credentials: select `github-pat`
  * Branch: `*/main`
  * Script Path: `Jenkinsfile` (default)
* Save.

Repeat for **app2-job** pointing to `app2-private`.

---

## Step 6: Verify jobs build without shared library (quick smoke test)

* Click **Build Now** for `app1-job` and `app2-job`.
* Inspect **Console Output** for success and the `docker build` / `docker run` lines.
* On the Jenkins host run:

  ```bash
  docker images
  docker ps
  ```
* App endpoints (replace `JENKINS_HOST` with the host that runs the container):

  * `http://JENKINS_HOST:5000` for app1
  * `http://JENKINS_HOST:5050` for app2

Confirm both are reachable before moving to shared library wiring.

---

## Step 7: Add private shared library to Jenkins Global Pipeline Libraries

1. **Manage Jenkins → System → Global Pipeline Libraries** → **Add**.
2. Name: `my-first-shared-library` (or choose a logical name).
3. Default version: `main`.
4. Load implicitly: **leave unchecked** (recommended).
5. Allow default version to be overridden: **checked**.
6. Retrieval method: **SCM → Git**

   * Repository URL: `https://github.com/YOUR_GH_USER/shared-library-private.git`
   * Credentials: select `github-pat` (the PAT you created)
7. Save and verify Jenkins can fetch the repo.

This makes the private shared library available to pipelines that explicitly import it with `@Library(...)`.

---

## Step 8: Move build & deploy logic to the shared library (what to put in `shared-library-private`)

Create a `vars` folder in the shared library repo and add two simple files exactly as below.

**`vars/buildImage.groovy`**

```groovy
// vars/buildImage.groovy
def call() {
  sh 'docker build -t "$REPO:$TAG" .'
}
```

**`vars/deployApp.groovy`**

```groovy
// vars/deployApp.groovy
def call() {
    sh 'docker rm -f $REPO || true'
    sh 'docker run -d --name $REPO -p "$PORT:$PORT" "$REPO:$TAG"'
}
```

**Notes**

* These shared steps read pipeline environment variables directly using `env.*`.
* Jenkinsfiles that call these steps must set `REPO`, `TAG`, and `PORT` in their `environment` block.
* This style keeps Jenkinsfiles simple and is ideal for beginner-friendly demos.

Commit and push these two files to `shared-library-private` as shown earlier.

---

## Step 9: Update each app `Jenkinsfile` to use the shared library

Edit `Jenkinsfile` in `app1-private` to import and call the shared steps:

**`Jenkinsfile` (app1)**

```groovy
@Library('my-first-shared-library@main') _

pipeline {
  agent any

  environment {
    REPO = "app1-flask"
    TAG  = "${BUILD_NUMBER}"
    PORT = "5000"
  }

  stages {
    stage('Build') {
      steps {
        buildImage()
      }
    }

    stage('Deploy') {
      steps {
        deployApp()
      }
    }
  }
}
```

Make the analogous change in `app2` (use `REPO=app2-flask`, `PORT=5050`, container name `app2`).
Commit and push the updated `Jenkinsfile`s for both apps.

---

## Step 10: Run the jobs and verify (final)

* In Jenkins click **Build Now** for `app1-job` and `app2-job`.
* Open **Console Output** and confirm you see the shared library steps being executed (`docker build` then `docker run`).
* On the Jenkins host check `docker ps` and `docker images`.
* Confirm endpoints:

  * `http://JENKINS_HOST:5000` for app1
  * `http://JENKINS_HOST:5050` for app2

If something fails, check:

* Console Output top lines for library fetch or SCM errors.
* Jenkins **Global Pipeline Libraries** entry and credentials.
* That `vars/*.groovy` files are on the `main` branch of `shared-library-private`.

---

## Step 11: Demonstrate the power of the shared library

Now that both app1 and app2 are deployed using the shared library, let’s see why this design matters in real life.

Imagine this situation:
Your team lead walks up to you and says:

> After our patching activity on the Docker host, both app1 and app2 containers stopped and did not auto-start when the host came back. We want these apps to always start automatically after a reboot.
> Also, add a label in the Docker image that contains the owner’s email address.

Without a shared library, you would have to change **two separate Jenkinsfiles** (or twenty if you had twenty microservices).
With a shared library, you will update **only one file**, and both app1 and app2 will inherit the change automatically.

---

### First, verify the problem

Restart Docker on your Ubuntu VM:

```bash
sudo systemctl restart docker
```

Now check:

```bash
docker ps -a
```

You will notice that **app1** and **app2** containers are stopped and did not auto-start.

This is exactly the problem we want to solve.

---

## Apply the fix in the shared library

### 1. Add an image label in `buildImage.groovy`

Current command:

```groovy
sh "docker build -t ${repo}:${tag} ."
```

Replace with:

```groovy
sh "docker build --label maintainer=cloudwithvarjosh@gmail.com -t ${repo}:${tag} ."
```

### What does `--label` mean?

`--label key=value` allows you to attach metadata to the image.
This metadata is useful for:

* ownership tracking
* automation
* cleanup policies
* identifying who built the image

You can view labels later with:

```bash
docker inspect <image> | grep -A5 Labels
```

---

### 2. Add auto-restart behavior in `deployApp.groovy`

Current command:

```groovy
sh "docker run -d --name ${containerName} -p ${port}:${port} ${repo}:${tag}"
```

Replace with:

```groovy
sh "docker run -d --name ${containerName} --restart unless-stopped -p ${port}:${port} ${repo}:${tag}"
```

### What does `--restart unless-stopped` mean?

This flag tells Docker:

* automatically start the container when the docker daemon starts
* automatically start it after a host reboot
* keep it running unless you explicitly stop it

This is a very common production flag for workloads that must survive host restarts.

---

## Verification steps

### 1. Re-run the Jenkins jobs

Trigger a build for both:

* `app1-job`
* `app2-job`

This rebuilds the images with the new label and redeploys the containers with the restart policy.

---

### 2. Verify image labels

Pick an app image:

```bash
docker inspect app1-flask:latest | grep -A5 Labels
```

You should see:

```
"maintainer": "cloudwithvarjosh@gmail.com"
```

---

### 3. Verify restart policy

Run:

```bash
docker inspect app1 | grep RestartPolicy -A3
```

Expected:

```
"Name": "unless-stopped"
```

---

### 4. Restart Docker again

To test auto-start:

```bash
sudo systemctl restart docker
```

Then run:

```bash
docker ps
```

Both **app1** and **app2** containers should now be running automatically without manual intervention.

This is the exact benefit of using a shared library:
**one change, two apps updated instantly with zero modifications to their Jenkinsfiles.**

---

## Why centralising config matters

What you saw in the demo is intentionally simple. I kept `repo`, `tag`, and `port` inside each Jenkinsfile so nothing felt overwhelming. That choice helps beginners, but it also hides how powerful a shared library can become.

If you move these values into the shared library, a **single edit** can change how **every pipeline** behaves. Update the registry, adjust the tagging strategy, or modify port mappings in one file and the entire fleet of apps inherits the change automatically. No searching through multiple Jenkinsfiles and no risk of forgetting one service.

This really starts to shine in real CI setups where multiple apps rely on common tools like **SAST scanners (SonarQube, Semgrep)**, **DAST tools (OWASP ZAP, Burp Suite)**, **image scanners (Trivy, Grype)**, and **code quality platforms (SonarQube, CodeClimate)**. These tools are shared across many microservices, not one-to-one. When an endpoint changes, a new policy is introduced, or a credential rotates, you update **one place** in the shared library and **every pipeline stays consistent**. This reduces maintenance, improves reliability, and prevents subtle pipeline drift across teams.

---

# **Conclusion**

By now you’ve seen how a Shared Library becomes the **single source of truth** for your organisation’s CI CD logic. Instead of fixing twenty Jenkinsfiles, you **update one place**, and every service instantly benefits. This improves consistency, reduces maintenance overhead, and eliminates subtle pipeline differences across teams.

The demonstration made this real: adding a label or a restart policy required **only one change** in the library, and both app1 and app2 were updated automatically. This advantage multiplies in real-world environments where microservices depend on **shared tools like SonarQube, Trivy, Semgrep, OWASP ZAP, Maven, and Slack or email notifications**. Shared Libraries ensure every pipeline stays aligned, compliant, and easy to reason about.

In short: **write once, reuse everywhere**, and keep your Jenkins pipelines clean, predictable, and future-ready.

---

# **References**

* **Jenkins Pipeline Shared Libraries Documentation**
  [https://www.jenkins.io/doc/book/pipeline/shared-libraries/](https://www.jenkins.io/doc/book/pipeline/shared-libraries/)

* **Jenkins Pipeline Syntax Reference**
  [https://www.jenkins.io/doc/book/pipeline/syntax/](https://www.jenkins.io/doc/book/pipeline/syntax/)

* **`libraryResource` Function Reference (Jenkins)**
  [https://www.jenkins.io/doc/pipeline/steps/workflow-cps-global-lib/#libraryresource-unstable](https://www.jenkins.io/doc/pipeline/steps/workflow-cps-global-lib/#libraryresource-unstable)

* **Install Jenkins on Linux (Official Guide)**
  [https://www.jenkins.io/doc/book/installing/linux/](https://www.jenkins.io/doc/book/installing/linux/)

* **Groovy Language Reference**
  [https://groovy-lang.org/syntax.html](https://groovy-lang.org/syntax.html)

* **Dockerfile Reference (Labels, Build Options)**
  [https://docs.docker.com/reference/dockerfile/](https://docs.docker.com/reference/dockerfile/)

* **Docker Container Restart Policies (Official Docker Docs)**
  [https://docs.docker.com/config/containers/start-containers-automatically/](https://docs.docker.com/config/containers/start-containers-automatically/)

---








