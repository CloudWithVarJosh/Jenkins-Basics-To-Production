# Complete DevSecOps CI/CD Pipeline | Multi-AZ Amazon EKS + Jenkins + Trivy + SonarQube + ECR + GitHub

---

## Video reference for this lecture is the following:

[![Watch the video](https://img.youtube.com/vi/9LXZm0Fryfw/maxresdefault.jpg)](https://www.youtube.com/watch?v=9LXZm0Fryfw&ab_channel=CloudWithVarJosh)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## **Table of Contents**

* [Introduction](#introduction)  
* [Pre-requisites for this lecture](#pre-requisites-for-this-lecture)  
  * [1. Modern SDLC Explained](#1-modern-sdlc-explained--build-automation--real-world-insights)  
  * [2. CI/CD Explained](#2-cicd-explained--how-pipelines-work--branching-strategies)  
  * [3. Maven Tutorial for DevOps](#3-maven-tutorial-for-devops--maven-beginner-tutorial)  
  * [4. SonarQube](#4-sonarqube)  
* [**Lab:** Install Jenkins Controller on EC2](#lab-install-jenkins-controller-on-ec2)  
  * [Create the EC2 instance](#1-create-the-ec2-instance)  
  * [Connect to the instance](#2-connect-to-the-instance)  
  * [Install Java 21](#3-install-java-21-jdk)  
  * [Install Jenkins](#4-add-jenkins-repository-and-install)  
  * [Start Jenkins](#5-start-and-enable-jenkins)  
  * [Access Jenkins UI](#6-access-jenkins-ui-and-unlock)  
* [**Lab:** Configure SSH-based Jenkins Agent](#lab-configure-ssh-based-jenkins-agent-on-ec2)  
  * [Create Jenkins Agent EC2](#1-create-the-ec2-instance-1)  
  * [Install Java on Agent](#3-install-java-21)  
  * [Create jenkins user](#4-create-a-dedicated-jenkins-user-non-root)  
  * [Add the Agent to Jenkins Controller](#lab-add-the-jenkins-agent-to-the-jenkins-controller)  
  * [Generate SSH keys](#1-generate-ssh-key-on-the-controller-jenkins-user)  
  * [Copy keys to Agent](#2-copy-the-public-key-to-the-agent)  
  * [Configure Agent in Jenkins UI](#3-configure-the-agent-in-jenkins-ui)  
* [**Lab:** Install SonarQube on EC2](#lab-install-sonarqube-on-ec2)  
    * [Create SonarQube EC2](#1-create-the-ec2-instance)  
    * [Install Java for SonarQube](#3-install-java-21-1)  
    * [Install PostgreSQL](#4-install-postgresql-and-create-db-for-sonarqube)  
    * [Configure kernel settings](#5-tune-kernel-settings-required-by-sonarqube)  
    * [Create sonar user](#6-create-a-dedicated-sonar-user)  
    * [Download SonarQube](#7-download-and-install-sonarqube)  
    * [Configure SonarQube Database](#8-configure-sonarqube-to-use-postgresql)  
    * [Create SonarQube systemd service](#9-create-a-systemd-service-for-sonarqube)  
    * [Access SonarQube UI](#10-access-the-sonarqube-ui)  
    * [Production notes](#11-production-notes-for-sonarqube)  
* [**Demo:** End-to-End Production DevSecOps Pipeline](#demo-end-to-end-production-devsecops-pipeline)  
  * [Stage 1: Git Checkout](#stage-1-git-checkout--jenkins-pipeline-job-setup)  
  * [Stage 2: Trivy FS Scan](#stage-2-trivy-fs-scan-filesystem-vulnerability-scan)  
  * [Stage 3: Build and Sonar](#stage-3-build-and-sonar-maven-build-sast-scan-coverage-enforcement)  
  * [Stage 4: ECR Login](#stage-4-ecr-login-authenticate-jenkins-agent-to-amazon-ecr)  
  * [Stage 5: Build Image](#stage-5-build-image-build-container-image)  
  * [Stage 6: Trivy Image Scan](#stage-6-trivy-image-scan-container-image-vulnerability-scan)  
  * [Stage 7: Push to ECR](#stage-7-push-to-ecr-push-built-image-to-amazon-ecr)  
  * [Stage 8: Create Kubernetes Manifests](#stage-8-create-kubernetes-manifests-deployment--service)  
  * [Stage 9: Deploy to Kubernetes](#stage-9-deploy-to-kubernetes-create-cluster-grant-access-deploy-app)  
* [Post Actions in Jenkins Pipeline](#post-actions-in-jenkins-pipeline)  
* [Trigger Pipeline on Git Push](#trigger-pipeline-on-git-push)  
* [How this pipeline can be improved](#how-this-pipeline-can-be-improved-production-enhancements)  
* [Conclusion](#conclusion)  
* [References](#references)  

---

# **Introduction**

In this lecture, we build an end-to-end **production-grade DevSecOps pipeline** that integrates secure coding, vulnerability scanning, container image hardening, artifact management, and automated Kubernetes deployment.
The goal is to show how real companies implement **secure CI/CD** using a combination of:

* Jenkins
* SonarQube (SAST + coverage)
* Trivy (SCA + image scanning)
* AWS ECR
* Amazon EKS
* Kubernetes YAML manifests
* IAM + RBAC for least-privilege deployments

By the end of this lesson, you will understand how each stage contributes to a hardened delivery pipeline — from scanning code on commit to deploying a signed, validated image on a topology-aware Kubernetes cluster.
This flow reflects **actual production implementations** used in modern enterprises.

---


## Pre-requisites for this lecture

To follow the DevSecOps and SonarQube flow end-to-end, these sessions will help a lot.
We conclude this lecture with a CI/CD pipeline that uses both Maven and SonarQube, so understanding these foundations makes the final pipeline much easier to follow.


#### 1. Modern SDLC Explained | Build Automation & Real-World Insights

* **YouTube Video:** [Modern SDLC Explained](https://youtu.be/imEHsgvJbYo)
* **GitHub Notes:** [Modern SDLC](https://github.com/CloudWithVarJosh/Jenkins-Basics-To-Production/tree/main/Day%2001)

**Why this helps:** Gives the big picture of how modern SDLC, build pipelines and environment promotion work.
You will understand where DevSecOps controls fit in the lifecycle and why we gate builds and deployments.

---

#### 2. CI/CD Explained | How Pipelines Work & Branching Strategies

* **YouTube Video:** [CI/CD Explained](https://www.youtube.com/watch?v=szPE1NKc614&ab_channel=CloudWithVarJosh)
* **GitHub Notes:** [CI/CD & Branching Strategies](https://github.com/CloudWithVarJosh/Jenkins-Basics-To-Production/tree/main/Day%2002)

**Why this helps:** Explains pipeline stages, promotions and branching strategies so you know at which stage to plug in SAST, SCA, and quality gates.
This makes the multibranch / PR mechanics and promotion rules in the demo easier to grasp.

---

#### 3. Maven Tutorial for DevOps | Maven Beginner Tutorial

* **YouTube Video:** [Maven Tutorial for DevOps](https://www.youtube.com/watch?v=3OKc5y_3wMM&ab_channel=CloudWithVarJosh)
* **GitHub Notes:** [Maven Lecture Notes](https://github.com/CloudWithVarJosh/YouTube-Standalone-Lectures/tree/main/Lectures/08-maven)

**Why this helps:** SonarQube is wired into the **Maven build lifecycle** in this lecture.
Knowing how Maven builds, runs tests, and produces coverage reports helps you understand exactly when Sonar analysis runs.

---

#### 4. SonarQube

* **YouTube Video:** [SonarQube for DevOps](https://www.youtube.com/watch?v=qyYsLVZDieU)
* **GitHub Notes:** [SonarQube Lecture Notes](https://github.com/CloudWithVarJosh/SonarQube-For-DevOps/blob/main/README.md)

**Why this helps:** Familiarity with SonarQube concepts (projects, tokens, quality gates, and analysis) makes it easier to configure CI integration and interpret SAST results during the pipeline.

---

## **Lab: Install Jenkins Controller on EC2**

This VM will act **only as the controller**.
All pipeline workloads will be executed on SSH-based Jenkins agents.

---

## **1. Create the EC2 instance**

* **AMI:** Ubuntu 24.04 LTS
* **Instance type:** c7i-flex.large

  > This instance type is eligible under AWS credits-based free tier
* **Root volume:** 20 GB or more

**Security Group (jenkins-controller VM):**

* Allow **SSH (22)** from your IP
* Allow **HTTP (8080)** from your IP (for Jenkins UI)

---

## **2. Connect to the instance**

```bash
ssh -i <your-key>.pem ubuntu@<jenkins-controller-public-ip>
```

Ensure your private key is restricted:

```bash
chmod 600 ~/.ssh/<your-private-key>
chown $(whoami):$(whoami) ~/.ssh/<your-private-key>
```

Set hostname:

```bash
sudo hostnamectl set-hostname jenkins-controller
exec bash
```

Set timezone:

```bash
sudo timedatectl set-timezone Asia/Kolkata
timedatectl status
```

---

## **3. Install Java 21 (JDK)**

Jenkins LTS works well with Java 21.

```bash
sudo apt update
sudo apt install -y openjdk-21-jdk
java -version
javac -version
```

---

## **4. Add Jenkins repository and install**

Reference: [https://www.jenkins.io/doc/book/installing/linux/](https://www.jenkins.io/doc/book/installing/linux/)

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

### **Set Jenkins JVM timezone (systemd-based installs)**

We set the JVM timezone so Jenkins UI timestamps match the server and agent local time.
If omitted, the JVM often runs in UTC and dashboard/console timestamps will be inconsistent.

**Interactive (edit with your preferred editor):**

```bash
sudo systemctl edit jenkins
# add the following lines in the editor and save:
[Service]
Environment="JAVA_OPTS=-Duser.timezone=Asia/Kolkata"
```

**Non-interactive (write override directly):**

```bash
sudo mkdir -p /etc/systemd/system/jenkins.service.d
cat <<'EOF' | sudo tee /etc/systemd/system/jenkins.service.d/override.conf > /dev/null
[Service]
Environment="JAVA_OPTS=-Duser.timezone=Asia/Kolkata"
EOF
```

---

## **5. Start and enable Jenkins**

```bash
sudo systemctl daemon-reload
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```

---


## **6. Access Jenkins UI and unlock**

Open in browser:

```
http://<jenkins-controller-public-ip>:8080
```

Get admin password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Then:

* Install suggested plugins
* Create admin user
* Log in to dashboard

---

## **Lab: Configure SSH-based Jenkins Agent on EC2**

This VM will execute all Jenkins jobs.
It will have JDK 21, Docker, and a non-root `jenkins` user.

---

### **1. Create the EC2 instance**

* **AMI:** Ubuntu 24.04 LTS
* **Instance type:** c7i-flex.large
* **Root volume:** 30 GB+ (Trivy scans need space)

**Security group (jenkins-agent VM):**

* Allow **SSH (22)** from the controller IP only
* Do not expose Jenkins UI (8080) on the agent

> Note: Jenkins controller connects to agents over SSH (port 22).
> Only open TCP 50000 on the controller if you use JNLP inbound agents; otherwise it is not required.

---

### **2. Connect to the instance**

```bash
ssh -i <your-key>.pem ubuntu@<jenkins-agent-public-ip>
```

Secure your SSH key:

```bash
chmod 600 ~/.ssh/<your-private-key>
chown $(whoami):$(whoami) ~/.ssh/<your-private-key>
```

Set hostname:

```bash
sudo hostnamectl set-hostname jenkins-agent
exec bash
```

Set timezone:

```bash
sudo timedatectl set-timezone Asia/Kolkata
timedatectl status
```

---

### **3. Install Java 21**

```bash
sudo apt update
sudo apt install -y openjdk-21-jdk
java -version
javac -version
```

---

### **4. Create a dedicated jenkins user (non-root)**

```bash
# Create a dedicated non-root 'jenkins' user with home directory and bash shell
sudo useradd -m -s /bin/bash jenkins
```

---


## **Lab: Add the jenkins-agent to the Jenkins Controller**

![Alt text](/images/me2.png)

SSH into controller:

```bash
ssh -i <your-key>.pem ubuntu@<jenkins-controller-public-ip>
```

---

### **1. Generate SSH key on the controller (Jenkins user)**

Jenkins service runs as `jenkins`, so we generate the key inside its home.

Use a **meaningful filename** and a **different comment**:

```bash
# You land in the home directory of jenkins user which is /var/lib/jenkins
sudo su - jenkins
ssh-keygen -t ed25519 -f /var/lib/jenkins/.ssh/jenkins-agent-key -C "jenkins-agent-access"
```

Explanation:

* **File:** `/var/lib/jenkins/.ssh/jenkins-agent-key`
* **Comment:** `jenkins-agent-access`
* They are intentionally different for clarity.

Show the public key:

```bash
cat /var/lib/jenkins/.ssh/jenkins-agent-key.pub
```

---


### **2. Copy the public key to the agent**

> Assume you already have SSH sessions open to **both** the controller and the agent.

#### **Manual copy (recommended for EC2)**

1. **On the controller (as jenkins), print the pubkey and copy it**

```bash
sudo su - jenkins
cat ~/.ssh/jenkins-agent-key.pub
```

Copy the single line starting with `ssh-ed25519`.

2. **On the agent (SSH session already open), switch to jenkins user**

```bash
sudo su - jenkins
mkdir -p ~/.ssh
vim ~/.ssh/authorized_keys
```
> This will prompt you to set the password for the `jenkins` user.
> Ubuntu service accounts are often created without a local password, so an interactive `sudo su - jenkins` may ask you to create one to allow a direct login.
> Note: switching users from root or via `sudo` does not require the target user’s password; to avoid setting a password use a root shell or `sudo -i -u jenkins` instead.

Paste the public key inside, save and exit.

3. **Set permissions (now that you’re already jenkins user)**

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

4. From the **controller**, test the connection

> Run this as the **jenkins** user so `~` expands to `/var/lib/jenkins`.

```bash
# switch to jenkins (loads jenkins HOME)
sudo su - jenkins

# test SSH using the private key from jenkins home
ssh -i /var/lib/jenkins/.ssh/jenkins-agent-key jenkins@<jenkins-agent-public-ip> hostname

# expected output:
# jenkins-agent

# when finished, exit the jenkins shell to return to your previous user
exit
```

**Why this matters**: running the command as `jenkins` ensures the private key path resolves to `/var/lib/jenkins/.ssh/jenkins-agent-key`. Running the same `ssh -i ~/.ssh/jenkins-agent-key ...` as another user (for example `ubuntu`) will look for `/home/ubuntu/.ssh/jenkins-agent-key` and fail.


---

### **3. Configure the agent in Jenkins UI**

1. Jenkins Dashboard → **Manage Jenkins → Nodes → New Node**

2. Name: `jenkins-agent`

3. Type: **Permanent Agent**

4. Configure:

   * **Number of executors:** `1` (or as needed)
   * **Remote root directory:** `/home/jenkins`  ← ensure this matches the agent's jenkins home.
   * **Labels:** `docker-maven-trivy`
   * **Usage:** Use this node as much as possible
   * **Launch method:** Launch agents via **SSH**

5. Enter connection details:

   * **Host:** `<jenkins-agent-PRIVATE-ip>`
   * **Credentials:** Add → **SSH Username with private key**

     * **Username:** `jenkins`
     * **Private key:** paste the private key contents from `/var/lib/jenkins/.ssh/jenkins-agent-key` (the file on the controller).
     * **Passphrase:** leave empty unless you set one.

6. Host Key Verification Strategy (choose one)

    * **Known hosts file Verification Strategy**
      Recommended for production. Jenkins uses its internal `known_hosts` file. Populate that file ahead of time (one-time `ssh` from controller or `ssh-keyscan`) so connections are trusted automatically.

    * **Manually provided key Verification Strategy**
      Very secure. You paste the agent’s host key fingerprint into Jenkins manually. Use this in regulated environments where you must verify keys out of band.

    * **Manually trusted key Verification Strategy**
      Convenient for small teams and controlled labs. Jenkins will accept the host key on first connection (TOFU) and save it as trusted. Use only when you can trust the network at the time of first connect.

    * **Non verifying Verification Strategy**
      Insecure. Jenkins will not verify host keys. Useful only in isolated test environments where security is not a concern.

      #### We choose `Known hosts file Verification Strategy`
      Use **Known hosts file Verification Strategy**. Manually populate Jenkins’ `known_hosts` once from the controller so future agent connections are trusted automatically.
      Run this as the `jenkins` user on the controller (it will prompt `yes` on first connect and append the host key):

      ```bash
      sudo -u jenkins ssh -i /var/lib/jenkins/.ssh/jenkins-agent-key jenkins@172.31.40.86 ls -la
      ```

      Alternative (non-interactive): fetch and append the agent host key without an interactive prompt:

      ```bash
      ssh-keyscan 172.31.40.86 | sudo -u jenkins tee -a /var/lib/jenkins/.ssh/known_hosts > /dev/null
      ```

      After either step, Jenkins will use its `known_hosts` file for secure, automated SSH verification.

7. Advanced (optional):

   * **SSH port:** change if agent SSH runs on a non-standard port (default 22).
   * **Connection timeout / retry:** increase if network latency is high.
   * **Remote FS root note:** If the agent user’s home differs from `/home/jenkins`, update Remote root directory accordingly.
   * **Tool locations / Java path:** only set if agent Java is nonstandard.

8. Save → Click **Launch agent**

**Expected result:**

```
Agent successfully connected and online
```

**Quick verification steps (if UI shows connected but you want to confirm):**

* On the agent page click **Log** and look for `Authentication successful` / `Agent successfully connected` lines.
* Create a tiny job restricting to this node (label) with a shell step:

```bash
echo "hello from agent"
hostname
whoami
```

Console should print the agent hostname and `jenkins`.

---

## Lab: Install SonarQube on EC2

For the lab, we will keep SonarQube and PostgreSQL on the **same VM**. This is ok for training, and close enough to a small production style deployment on VMs.

### 1. Create the EC2 instance

* AMI: Ubuntu 22.04 LTS
* Instance type: c7i-flex.large (SonarQube likes RAM)
  > **Note:** The instance type **c7i-flex.large** is eligible under the AWS **credits-based free tier**, so you will not incur charges as long as you remain within your credit balance.

* Root volume: 20 GB or more

**Security group (SonarQube VM)**

* Allow SSH (22) from your IP
* Allow HTTP (9000) from your IP and from the Jenkins VM


### 2. Connect to the instance

```bash
ssh -i <your-key>.pem ubuntu@<sonarqube-ec2-public-ip>
```
**Note:** Ensure your SSH private key is readable only by you.
Run:

```bash
chmod 600 ~/.ssh/<your-prvate-key>  
chown $(whoami):$(whoami) ~/.ssh/<your-prvate-key>  
```

**Suggested hostname:** `sonarqube`
This makes the server easy to identify in SSH sessions, monitoring dashboards, and DNS-based service discovery.

```bash
# Set hostname and reload your shell
sudo hostnamectl set-hostname sonarqube
exec bash
```

**Setting the correct timezone**
Set the machine timezone so logs and timestamps are consistent with your locality.
I'll use `Asia/Kolkata`; pick the timezone that matches your location.

```bash
# set timezone to Asia/Kolkata
sudo timedatectl set-timezone Asia/Kolkata

# verify
timedatectl status
# or
date
```

### 3. Install Java 21

SonarQube currently requires Java 21.

```bash
sudo apt-get update
sudo apt-get install -y openjdk-21-jre
java -version
```

You should see Java 21.

### 4. Install PostgreSQL and create DB for SonarQube

In SonarQube, the **database is critical**. It stores:

* All **projects, analyses and measures** (issues, coverage, duplications, ratings, technical debt).
* **Rules, quality profiles, quality gates**, user accounts, tokens and general configuration.

Because this data is so important, in production you will often see enterprises run SonarQube’s database on a **separate, self managed PostgreSQL VM** or use a **managed service such as Amazon RDS for PostgreSQL**, so that performance, backups and high availability can be handled independently from the SonarQube application VM.

For **development and small test setups**, you will sometimes see **H2** being used. H2 is an **embedded, in memory or file based relational database** that is very easy to start but not designed for heavy, multi user production use. It is fine for quick local trials, but for any serious team environment SonarQube recommends **PostgreSQL** instead.


```bash
# Install PostgreSQL and common extensions
sudo apt install -y postgresql postgresql-contrib

# Enable PostgreSQL to start automatically on boot
sudo systemctl enable postgresql

# Start the PostgreSQL service now
sudo systemctl start postgresql
```

**Create SonarQube database and user**

Below are the exact commands to create the database role and the `sonarqube` database, plus a quick connectivity test.
Run the SQL commands as the `postgres` superuser.

```bash
# open the PostgreSQL shell as the postgres superuser
sudo -u postgres psql
```

Inside `psql`, run:

```sql
-- create a login role for SonarQube with a password
CREATE ROLE sonar WITH LOGIN ENCRYPTED PASSWORD 'StrongPasswordHere';
-- Example: CREATE ROLE sonar WITH LOGIN ENCRYPTED PASSWORD 'sonar';

-- create the SonarQube database owned by that role
CREATE DATABASE sonarqube OWNER sonar;

-- grant privileges on the database to the sonar role
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO sonar;

-- exit psql
\q
```

Quick verification (run on the VM shell):

```bash
# list roles to confirm the 'sonar' role exists
sudo -u postgres psql -c "\du"

# list databases and owners to confirm the 'sonarqube' DB exists
sudo -u postgres psql -c "\l"

# test connecting exactly as SonarQube will (replace password if needed)
PGPASSWORD='StrongPasswordHere' psql -U sonar -h localhost -d sonarqube -c "\dt"
```

If the last command shows an empty relation list (no tables) and no authentication error, the database and user are configured correctly.
Update `sonar.jdbc.username`, `sonar.jdbc.password`, and `sonar.jdbc.url` in `/opt/sonarqube-current/conf/sonar.properties` to match these values and restart SonarQube.



### 5. Tune kernel settings required by SonarQube

SonarQube uses Elasticsearch internally and needs some kernel tweaks.

```bash
# Increase the maximum number of memory map areas (required by Elasticsearch)
echo 'vm.max_map_count=524288' | sudo tee -a /etc/sysctl.d/99-sonarqube.conf

# Increase the maximum number of file handles
echo 'fs.file-max=131072' | sudo tee -a /etc/sysctl.d/99-sonarqube.conf

# Apply the new sysctl settings
sudo sysctl --system
```

Set ulimits for the `sonar` user by adding to `/etc/security/limits.d/99-sonarqube.conf`:

```bash
# Allow many open files for the sonar user
echo 'sonar   -   nofile   131072' | sudo tee /etc/security/limits.d/99-sonarqube.conf

# Allow many processes for the sonar user
echo 'sonar   -   nproc    8192'   | sudo tee -a /etc/security/limits.d/99-sonarqube.conf
```

> **Note:** These kernel and ulimit tweaks give Elasticsearch (used by SonarQube) enough memory mappings and file descriptors to index code reliably.
> Apply them before starting SonarQube to avoid startup, indexing, or resource-limit failures.


### 6. Create a dedicated sonar user

```bash
# Create a dedicated 'sonar' user with its home directory at /opt/sonarqube
sudo useradd -m -d /opt/sonarqube -s /bin/bash sonar
```

### 7. Download and install SonarQube

Reference: https://www.sonarsource.com/products/sonarqube/downloads/

Check the LTS download URL from SonarQube site; as an example:

```bash
# switch to a temporary folder for downloads (keeps /tmp clean and avoids permission issues)
cd /tmp

# download the SonarQube community zip, follow redirects (-L) and write output to sonarqube.zip (-o)
curl -L -o sonarqube.zip "https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-25.11.0.114957.zip"

# install unzip non-interactively (-y auto-accepts prompts)
sudo apt-get update
sudo apt-get install -y unzip

# extract the downloaded archive into /tmp (unzip sonarqube.zip)
unzip sonarqube.zip

# move the extracted folder to a stable location for SonarQube deployment
sudo mv sonarqube-25.11.0.114957 /opt/sonarqube-current

# change ownership recursively (-R) so the sonar system user owns all files and directories
sudo chown -R sonar:sonar /opt/sonarqube-current
```


You can keep `/opt/sonarqube-current` as a symlink later when upgrading.

> In enterprise-grade implementations you would typically see the **Data Center Edition (DCE)** used because it provides application-level high availability.
**DCE** enables clustered SonarQube: multiple app nodes behind a load balancer, dedicated Elasticsearch search nodes, and a shared external database for resilience, scale and zero-downtime maintenance.


### 8. Configure SonarQube to use PostgreSQL

We are configuring SonarQube to connect to the PostgreSQL database you created.
**PostgreSQL default port is `5432`** — use it in the JDBC URL unless your DB uses a different port.

```bash
# edit the main SonarQube configuration file as the 'sonar' user
# (use your preferred editor: vim/nano)
sudo -u sonar vim /opt/sonarqube-current/conf/sonar.properties
```

Uncomment and set these lines (replace the password/host if needed):

```properties
# DB username for SonarQube (the DB user you created)
sonar.jdbc.username=sonar

# DB password for that user; keep this secret and match your DB setup
sonar.jdbc.password=StrongPasswordHere

# JDBC URL: jdbc:postgresql://<host>:<port>/<database>
# default PostgreSQL port is 5432 — using localhost because DB is on same VM
sonar.jdbc.url=jdbc:postgresql://localhost:5432/sonarqube
```

Notes and quick checks:

* If PostgreSQL runs on a different host, replace `localhost` with the DB host or IP and ensure the DB accepts remote connections (`listen_addresses` and `pg_hba.conf`).
* After saving, restart SonarQube so it picks up the new DB settings.
* If the SonarQube process cannot connect, check PostgreSQL is running and that the `sonar` user has access to the `sonarqube` database.


### 9. Create a systemd service for SonarQube

**What a systemd unit file is:** a small config that tells the OS how to start, stop, and manage a service, which user runs it, what it depends on, restart policy, and resource limits.

Create the unit file (edit as root):

```bash
sudo vim /etc/systemd/system/sonarqube.service
```

Paste this exact unit file (no inline comments inside the file):

```ini
[Unit]
Description=SonarQube service
After=network.target postgresql.service

[Service]
Type=forking
User=sonar
Group=sonar
ExecStart=/opt/sonarqube-current/bin/linux-x86-64/sonar.sh start
ExecStop=/opt/sonarqube-current/bin/linux-x86-64/sonar.sh stop
Restart=on-failure
LimitNOFILE=131072
LimitNPROC=8192

[Install]
WantedBy=multi-user.target
```

Reload systemd and start the service:

```bash
# reload systemd to pick up the new unit
sudo systemctl daemon-reload

# enable SonarQube to start on boot
sudo systemctl enable sonarqube

# start SonarQube now
sudo systemctl start sonarqube

# check current status; it should become active (running)
sudo systemctl status sonarqube
```

**Note: unit file directive explanations (keep these out of the unit file)**

* `Description` — human-friendly name for the service.
* `After` — start this service after the listed units are up (network and PostgreSQL here).
* `Type=forking` — the service forks to the background; systemd treats the original process as the starter.
* `User` / `Group` — the system account that runs the service (`sonar`) for least privilege.
* `ExecStart` — full path to the command that starts SonarQube. It must be executable.
* `ExecStop` — full path to the command that stops SonarQube cleanly.
* `Restart=on-failure` — automatically restart the service if it crashes or exits with an error.
* `LimitNOFILE` — raise the open-files limit; Elasticsearch needs many file descriptors.
* `LimitNPROC` — raise the allowed process count for the service user.
* `WantedBy=multi-user.target` — makes the service start during normal system boot.

**Operational tips:**

* If status is not `active (running)`, check live logs: `sudo journalctl -u sonarqube -f`.
* Confirm the `sonar` user owns `/opt/sonarqube-current` and that the `sonar` user has the ulimits set earlier.
* After editing the unit file, always run `sudo systemctl daemon-reload` to apply changes.

**Troubleshooting**
Check the SonarQube logs (look for ERROR / bootstrap failures)

```bash
# show recent sonar logs (general), web and elasticsearch logs
sudo tail -n 200 /opt/sonarqube-current/logs/sonar.log
sudo tail -n 200 /opt/sonarqube-current/logs/web.log
sudo tail -n 200 /opt/sonarqube-current/logs/es.log
```


### 10. Access the SonarQube UI

In your browser:

```text
http://<sonarqube-ec2-public-ip>:9000
```

Default login:

* Username: `admin`
* Password: `admin`

You will be asked to change the password.

From here you can:

* Explore **Quality Profiles**, **Quality Gates**, **Rules**
* Later, create a **project** and a **token** that Jenkins will use
* Configure `SONAR_HOST_URL` in Jenkins as `http://<sonarqube-ec2-public-ip>:9000`

### 11. Production notes for SonarQube

In many production deployments:

* SonarQube runs on **one or more VMs**, with PostgreSQL often on a separate DB server or managed service
* Resources are sized based on number of projects and users, often more CPU and RAM than in lab
* Access is via **HTTPS**, fronted by an ALB or Nginx
* Authentication integrates with **LDAP, SSO or OIDC**
* Backups are planned for both **database** and **configuration**
* Some teams move SonarQube to **Kubernetes**, but the VM pattern like this is still very common

---

# Demo: End-to-End Production DevSecOps Pipeline

## What are we going to do?

![Alt text](/images/me1.png)

In this demo, we build a **production-grade DevSecOps pipeline** using **Jenkins**, **Trivy**, **SonarQube**, **AWS ECR**, and **Amazon EKS**.
The pipeline enforces **multiple security gates** by **scanning source code**, **running unit tests**, **performing static analysis**, **scanning the container image**, and **deploying only when every stage passes**.
We follow **least-privilege access**, use **immutable image tags**, and **validate rollout health** before completing the deployment.

---

## **Stage 1: Git Checkout & Jenkins Pipeline Job Setup**

*(Reference: “Checkout private Git repo” box in the pipeline diagram)*

### **Objective**

Prepare source control and set up a Jenkins pipeline job that can securely checkout the private repository.
No build tools are required yet — only **Git** (already available on Ubuntu 24.04 and used via Jenkins Git plugin).

---

#### **0. Create a Private GitHub Repository**

Create the private repo that Jenkins will clone and push to.
This repo will hold our application code, the `pom.xml`, and later our Kubernetes manifests, Dockerfile and Jenkinsfile.


* Go to **GitHub → New Repository**
* Name it: **cwvj-private-repo**
* Visibility: **Private**
* This is the repo Jenkins will pull from and push build-related updates into.

---

#### **1. Create a GitHub Personal Access Token (PAT)**

This token allows Jenkins to authenticate to your private repo.

* Go to **GitHub → Settings → Developer settings → Personal access tokens**
* Create a **Classic PAT** with scope: `repo`
  Use this because the same token will be used for **push** operations.
  (In production, you would restrict the scope to minimal permissions.)
* **Copy the token** — GitHub will not show it again.

---


#### **2. Add the GitHub PAT into Jenkins credentials**

Path: **Manage Jenkins → Credentials → System → Global → Add Credentials**

* Kind: **Username with password**
* Username: your GitHub username
* Password: your PAT
* ID: **github-pat** (keep this exact ID for the pipeline)
* Save

**Purpose:**
Allows Jenkins to perform authenticated Git checkouts using the Git plugin.

---

#### **3. Prepare the project on your laptop / thin client**

We want a production-style flow: prepare your source locally, then push to a private repo.

Inside your folder (example: `java-maven`):

```bash
git init
git add .
git commit -m "Initial commit with project code"
git branch -M main
```
---

**First push using a temporary token (one-time only)**
Use a descriptive remote name so you know which remote is the private repo. You can use `origin` instead if you prefer.

```bash
# add a remote that points to your private repo
git remote add private-repo https://github.com/CloudWithVarJosh/cwvj-private-repo.git

# temporarily set the remote URL with the token so we can push securely
git remote set-url private-repo https://<TOKEN>@github.com/CloudWithVarJosh/cwvj-private-repo.git

# push the main branch
git push private-repo main
```

**Immediately remove the token from the remote URL**
This prevents the token from being stored in your local git config or shell history.

```bash
# restore the remote URL to the token-free form
git remote set-url private-repo https://github.com/CloudWithVarJosh/cwvj-private-repo.git

```


---
#### **4. Verify repository contents**

Ensure your private repo contains: `pom.xml`, `src` (Java code), and later you will add `Dockerfile`, `deploy-svc.yaml`, and `Jenkinsfile`.

---

#### **5. Create the Jenkins Pipeline job**

Path: **Jenkins → New Item → Pipeline**

* Name → `cwvj-devsecops-demo`
* Type → **Pipeline**
* Scroll to the “Pipeline” section

  * Definition: **Pipeline script from SCM**
  * SCM: **Git**
  * Repository URL:

    ```
    https://github.com/<your-username>/<your-private-repo>.git
    ```
  * Credentials → select **github-pat**
  * Branch → `*/main`
  * Script Path → `Jenkinsfile` (default)

Click **Save**.

---

#### **6. Run the first pipeline build**

Click **Build Now**.

Expected behavior:

* Jenkins uses the Git plugin.
* Jenkins authenticates via **github-pat**.
* Jenkins checks the specified branch for a `Jenkinsfile`.
* If a `Jenkinsfile` is found, the job will then checkout the workspace and proceed to the next stage.
* If a `Jenkinsfile` is missing, the job will fail immediately with `Unable to find Jenkinsfile` (this is expected for now).

---


## **Stage 2: Trivy FS Scan (Filesystem Vulnerability Scan)**

*(Reference: “Trivy FS Scan” box in the pipeline diagram)*

### **Objective**

Run a **filesystem-level vulnerability scan** on the source code directory using **Trivy**.
This stage ensures we catch **dependency CVEs, OS package issues, misconfigurations, and secrets** early, before building the image.

Trivy installs on the **Jenkins agent VM**, not on the controller.

---
### **Why run Trivy FS scan when we already run SonarQube SAST?**

**SonarQube SAST**
Scans **source code** for insecure patterns, code smells, bad practices, injection risks, and security hotspots.

**Trivy FS (SCA + more)**
Scans **runtime artifacts**; OS packages, JVM/dependency manifests, vendor libraries, Dockerfiles, and config files.
Performs **SCA (Software Composition Analysis)** to detect CVE-linked library vulnerabilities, plus misconfigurations and known secret patterns that SAST cannot find.

**Outcome:**
Using both provides **defence in depth** — SAST improves code quality and logic safety; Trivy secures third-party libraries and runtime components.

---

### **Add Stage 2 to the Jenkinsfile**

We create a `Jenkinsfile` inside your project folder (`jenkins-maven`) and define an early security gate.

```groovy
pipeline {
  agent { label 'docker-maven-trivy' }
  stages {
    stage('Trivy FS Scan') {
      steps {
        sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
      }
    }
  }
}
```

### **Explanation**

* `pipeline {}`
  Entire Jenkins Pipeline as code block.

* `agent { label 'docker-maven-trivy' }`
  Selects the Jenkins agent that has **Docker, Maven, and Trivy** installed.

* `stage('Trivy FS Scan')`
  Creates a dedicated security gate for filesystem vulnerability scanning.

* `sh 'trivy fs ...'`
  Runs Trivy against the **current workspace directory**.

  > Jobs are created on the Jenkins controller but run in a **temporary workspace on the agent**.

* `--exit-code 1`
  Acts as a security gate: forces the build to **fail the entire pipeline** when vulnerabilities meeting the threshold are found.

* `--severity HIGH,CRITICAL`
  Only blocks on **high-impact issues**, keeping the pipeline practical and reducing noise.


---

### **Install Trivy on the Jenkins Agent VM**

Your agent cannot execute Trivy commands unless Trivy is installed.
SSH into the agent:

```bash
ssh -i <your-key>.pem ubuntu@<jenkins-agent-public-ip>
```

Install Trivy using the Debian package (recommended):

```bash
# install wget
sudo apt-get install -y wget

# download specific Trivy release
wget https://github.com/aquasecurity/trivy/releases/download/v0.67.2/trivy_0.67.2_Linux-64bit.deb

# install the package
sudo dpkg -i trivy_0.67.2_Linux-64bit.deb

# verify installation
trivy --version
```

**Notes:**

* Keep Trivy updated for latest CVE definitions.
* Your Jenkins agent label is already configured to route jobs here.

---

### **Commit and Push the Jenkinsfile**

```bash
git add .
git commit -m "Jenkinsfile with Stage: 2"
git push origin main
```

---

### **Run the Pipeline**

Go to Jenkins → **Build Now**.
You will now see both:

* Stage 1 → Git Checkout
* Stage 2 → Trivy FS Scan

Both should pass successfully.

---

### **Example Trivy FS Report (Clean Run)**

```
Report Summary
┌─────────┬──────┬─────────────────┬─────────┐
│ Target  │ Type │ Vulnerabilities │ Secrets │
├─────────┼──────┼─────────────────┼─────────┤
│ pom.xml │ pom  │        0        │    -    │
└─────────┴──────┴─────────────────┴─────────┘
Legend:
- '-': Not scanned
- '0': Clean (no security findings detected)
```

> Trivy reports **no findings** because it scans dependencies, OS packages, and known secret patterns, not source-code logic or bad practices.
The issues in the Java file are **SAST/style/logic** problems (hardcoded string, wrong string compare, resource leak) and will be flagged by SonarQube, not Trivy.
Use both tools: **SonarQube for code issues** and **Trivy for CVEs and secret patterns**.

---

### Simulate a problem

If you want Trivy to find issues during the FS scan, introduce **intentional vulnerabilities**:

* **Add vulnerable dependency** — insert under `<dependencies>` in `pom.xml`:

```xml
<dependency>
  <groupId>org.apache.logging.log4j</groupId>
  <artifactId>log4j-core</artifactId>
  <version>2.14.0</version>
</dependency>
```

* **Add known-secret pattern** — create `secrets.txt` with:

```
AWS_SECRET_ACCESS_KEY=AKIAAAAAAAAAAAAAAAAA
```

Commit and push, run the pipeline, observe Trivy fail and show findings.
After testing, remove the vulnerable dependency and `secrets.txt`, then commit and push again.

---

## **Stage 3: Build and Sonar (Maven Build, SAST Scan, Coverage Enforcement)**

*(Reference: “Build and Sonar” box in the pipeline diagram)*

### **Objective**

Compile the application using **Maven**, run **unit tests**, collect **test coverage**, and perform **SAST analysis** using **SonarQube**.
This stage enforces **Quality Gates** so that the pipeline fails if the project does not meet required code coverage or security standards.

We use **JUnit**, **Surefire**, and **Jacoco** plugins to generate reports consumed by SonarQube.

Jenkins communicates with SonarQube over **private IP**, which is common in production deployments.

---

### **1. SSH into SonarQube Server**

```bash
ssh -i <your-key>.pem ubuntu@<sonarqube-public-ip>
```

This lets you configure the project, generate tokens, and create a Quality Gate.

---

### **2. Create a SonarQube Project**

SonarQube UI → **Projects → Create Project**

* Project display name → `cwvj-devsecops-demo`
* Project key → `cwvj-devsecops-demo`

This is the unique identifier used in the Maven command.

---

### **3. Create a Custom Quality Gate**

SonarQube → **Quality Gates → Create**

* Name → `cwvj-devsecops-demo-qg`
* Add Condition → Coverage

  * On: **Overall Code**
  * Operator: **is greater than**
  * Value: **80**

Add your project (`cwvj-devsecops-demo`) to this Quality Gate.

Purpose:
Fail the pipeline if overall coverage drops below 80 percent.
This makes build failure predictable during the demo.

---

### **4. Generate a SonarQube Token for Jenkins**

SonarQube → Administration → Security → Users → **Create User**.

* Machine account name → `jenkins-sonar` or `sonar-user`.
* Assign minimal required group/permissions (avoid full admin unless needed).

Under **Generate Tokens**, create a token named `jenkins-token`.
**Why:** create this token so the **Jenkins agent can authenticate to SonarQube** and upload analysis results during the pipeline.

**Copy the token immediately** — you will only see it once.

---

### **5. Add Token to Jenkins Credentials**

Jenkins → **Manage Jenkins → Credentials → System → Global → Add Credentials**.

* Kind: **Secret Text**
* Secret: `<sonarqube-token>`
* ID: **sonarqube-token**
  **Why:** so the **Jenkins agent can authenticate to SonarQube** and upload analysis results during the pipeline.

Use **Pipeline Syntax** → **withCredentials** to bind the token into a variable at runtime:

* Sample Step → withCredentials: Bind credentials to variables → Select **Secret text** → Variable name `SONAR_TOKEN` (keep it relevant) → Credentials: choose the `sonarqube-token` you created → Generate pipeline script.

Example generated block to use in the Build & Sonar stage:

```groovy
withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
    // some block
}
```

You will use this `withCredentials` block around the Maven Sonar command so the pipeline passes the token securely to SonarQube.

> **Note on security:** using `withCredentials` (Secret Text / `string`) is the correct way to provide tokens to the pipeline; Jenkins’ Credentials Binding plugin will **mask/redact** the secret in console output and logs when it is used via the binding.


---

### **6. Add Maven Tool in Jenkins**

Jenkins → Manage Jenkins → Global Tool Configuration → Maven

* Name → `maven3`
* Check **Install automatically**
* Select Apache Maven version (for online environments)

You **can** manually install Maven on the `jenkins-agent`, but Jenkins also supports automatic installation via the Global Tool Configuration plugin (convenient for demos and online agents).
If your environment is **offline** or has restricted internet access, **preinstall Maven on the agent** and point the tool configuration to that local path.

---

## **Pipeline with Stage 3 Included**

```groovy
pipeline {
  agent { label 'docker-maven-trivy' }
  tools {
    maven 'maven3'
  }
  environment {
    SONAR_IP = '172.31.21.44'
  }
  stages {
    stage('Trivy FS Scan') {
      steps {
        sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
      }
    }
    stage('Build & Sonar') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token-new', variable: 'SONAR_TOKEN')]) {
          sh 'mvn clean verify sonar:sonar \
  -Dsonar.projectKey=cwvj-devsecops-demo \
  -Dsonar.host.url="http://${SONAR_IP}:9000" \
  -Dsonar.token="${SONAR_TOKEN}" \
  -Dsonar.qualitygate.wait=true'
        }
      }
    }
  }
}
```

---

### **Explanation (Stage 3 specific blocks)**

#### **tools { maven 'maven3' }**

* Tells Jenkins to provision Maven (version configured earlier).
* Jenkins automatically injects `mvn` into PATH for this build.

---

#### **environment { SONAR_IP = '172.31.21.44' }**

* Stores the private IP of the SonarQube server.
* Could also be defined **inside the stage block**, but defined globally so all variables stay in one place for learning clarity.
> **Note (production):** use **DNS names** (eg. `sonar.internal.company.local`) instead of IPs; DNS enables certificate validation, easier rotation, and environment portability.


---

### **Build & Sonar Stage**

```groovy
stage('Build & Sonar') {
  steps {
    withCredentials([string(credentialsId: 'sonarqube-token-new', variable: 'SONAR_TOKEN')]) {
      sh 'mvn clean verify sonar:sonar \
-Dsonar.projectKey=cwvj-devsecops-demo \
-Dsonar.host.url="http://${SONAR_IP}:9000" \
-Dsonar.token="${SONAR_TOKEN}" \
-Dsonar.qualitygate.wait=true'
    }
  }
}
```

#### **withCredentials**

* Securely injects the Sonar token into the environment as `SONAR_TOKEN`.
* Ensures token never appears in logs or pipeline history.

#### **mvn clean verify sonar:sonar**

Breakdown:

* `clean` → removes old build artefacts
* `verify` → runs compile, test, surefire, jacoco coverage
* `sonar:sonar` → runs SonarQube SAST, uploads coverage, and triggers Quality Gate evaluation

Sonar parameters:

* `-Dsonar.projectKey` → points to our project
* `-Dsonar.host.url` → SonarQube server URL
* `-Dsonar.token` → auth token for CI
* `-Dsonar.qualitygate.wait=true`

  * Pipeline **waits** for SonarQube to evaluate quality gates
  * Build **fails** immediately if coverage or SAST rules violate the gate

---

### **Run the Pipeline**

Click **Build Now**.

The pipeline will fail at Stage 3 because:

* We configured a strict Quality Gate requiring **80 percent coverage**.
* Our demo project does not have enough unit tests to satisfy this requirement.

In production, this is where **developers fix test coverage** or improve code quality.

---

### **For Demo Purposes Only**

To continue the pipeline, lower coverage threshold:

Change the Quality Gate condition from `80` to `1`

**Do not ever do this in production.** Quality gates exist to protect system integrity.

---

## **Stage 4: ECR Login (Authenticate Jenkins Agent to Amazon ECR)**

*(Reference: “ECR Login” box in the pipeline diagram)*

### **Objective**

Authenticate the Jenkins agent to your **Amazon ECR** private registry so the pipeline can push Docker images.
We install **AWS CLI**, configure correct **IAM permissions** for the agent, create the ECR repository, and then perform a secure login using `aws ecr get-login-password`.

---

## **Prerequisite: Install AWS CLI & Docker Engine on Jenkins Agent**

We require `aws-cli` in the agent to run AWS-specific commands.
SSH into the **jenkins-agent VM**:

### **1) Install AWS CLI v2 (system-wide)**

```bash
# download aws cli v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip

# Install unzip
sudo apt install unzip

# unzip installer
unzip awscliv2.zip

# install system-wide so all users (including jenkins) can access it
sudo ./aws/install
```

Verify installation:

```bash
aws --version
sudo -u jenkins aws --version
```

---

### **2) Install Docker Engine on Jenkins Agent (official steps, minimal comments)**

Reference: [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)

```bash
# remove old docker packages if present (safe to run)  
sudo apt remove docker docker-engine docker.io containerd runc -y  

# refresh apt cache (always do this first)  
sudo apt update  

# install required helper packages for Docker repo setup  
sudo apt install -y ca-certificates curl gnupg  

# create apt keyrings dir with correct perms  
sudo install -m 0755 -d /etc/apt/keyrings  

# fetch Docker GPG key and store in keyrings (safe, read-only)  
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg  

# ensure Docker keyring is world-readable so apt can use it  
sudo chmod a+r /etc/apt/keyrings/docker.gpg  

# add Docker apt repository for the current Ubuntu codename  
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null  

# refresh package lists to include Docker repo  
sudo apt update  

# install Docker Engine, CLI, containerd and plugins  
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash
# add the 'jenkins' system user to docker group so builds can run docker without sudo  
sudo usermod -aG docker jenkins  

# optional: also add ubuntu user if admins will demo from ubuntu user account  
sudo usermod -aG docker ubuntu
```

```bash
# verify Docker CLI works as current user (local quick check)  
docker --version  

# verify Docker CLI works when run as the jenkins user (non-root check)  
sudo -u jenkins docker --version
```

**Notes:**

* After `usermod -aG docker jenkins` the `jenkins` session must re-login or the agent reconnects for group membership to apply.
* For production, secure Docker remote API; do not expose `/var/run/docker.sock` to untrusted containers.

---

## **Prerequisite: Grant Jenkins Agent Access to Amazon ECR**

Since the Jenkins agent is running on an **EC2 instance**, the best practice is to use an **IAM Role**, not long-lived AWS access keys.

### **Create IAM Role for Jenkins Agent**

AWS Console → **IAM → Roles → Create Role**

* Select **AWS Service**
* Use case → **EC2**
* Attach policy → **AmazonEC2ContainerRegistryPowerUser**
* Name the role → `jenkins-agent-role`

### **Attach the Role to the Jenkins Agent EC2 Instance**

AWS Console → **EC2 → Instances → jenkins-agent → Actions → Security → Modify IAM Role**

* Select → `jenkins-agent-role`
* Save

This grants the agent permission to authenticate to ECR, pull/push images, and perform registry actions.

---

### **Create the ECR Repository**

AWS Console → **Amazon ECR → Private Registry → Create Repository**

* Name → `cwvj-devsecops-demo`
* Image tag settings → **Immutable**

  * Benefits: prevents accidental overwrites, improves auditability, and keeps deployment history clean.
* Immutable tag exclusions → `latest`

  * Allows pushing the `latest` tag repeatedly during demos.
* Keep other settings default → **Create**

From the repo → **View push commands** gives the login snippet:

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 386275436648.dkr.ecr.ap-south-1.amazonaws.com
```

---

### **Pipeline with ECR Login (Stage 4)**

```groovy
pipeline {
  agent { label 'docker-maven-trivy' }
  tools {
    maven 'maven3'
  }
  environment {
    SONAR_IP = '172.31.21.44'
    ECR_REGISTRY = '386275436648.dkr.ecr.ap-south-1.amazonaws.com'
  }
  stages {
    stage('Trivy FS Scan') {
      steps {
        sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
      }
    }
    stage('Build & Sonar') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token-new', variable: 'SONAR_TOKEN')]) {
          sh 'mvn clean verify sonar:sonar \
  -Dsonar.projectKey=cwvj-devsecops-demo \
  -Dsonar.host.url="http://${SONAR_IP}:9000" \
  -Dsonar.token="${SONAR_TOKEN}" \
  -Dsonar.qualitygate.wait=true'
        }
      }
    }
    stage('ECR Login') {
      steps {
        sh 'aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_REGISTRY'
      }
    }
  }
}
```

---

### **Explanation**

* `environment { ECR_REGISTRY = '386275436648.dkr.ecr.ap-south-1.amazonaws.com' }`
  Stores the private ECR registry hostname so we avoid repeating long URLs inside stages.

* `aws ecr get-login-password --region ap-south-1`
  Fetches a **short-lived authentication token** for Docker login.

* `| docker login --username AWS --password-stdin $ECR_REGISTRY`
  Pipes the ECR token directly into Docker for a secure, non-interactive login.

* Combined login command
  Ensures the Jenkins agent authenticates safely without exposing credentials and without requiring AWS access keys.
  This method works seamlessly because the EC2 instance uses an IAM role (`jenkins-agent-role`) with ECR permissions.

---

### **Run the Pipeline**

Click **Build Now**.

If AWS CLI is installed, IAM role is attached correctly, and repository exists, the **ECR Login** stage will complete successfully.
If login fails, verify:

* IAM role is attached
* IAM policy includes `AmazonEC2ContainerRegistryPowerUser`
* AWS CLI is accessible to both root and Jenkins user
* ECR_REGISTRY value matches your repository

---

## **Stage 5: Build Image (Build Container Image)**

*(Reference: “Build Image” box in the pipeline diagram)*

### **Objective**

Install **Docker Engine** on the Jenkins agent, ensure the `jenkins` user can run Docker, and build a Docker image that will be pushed to ECR in a later stage.
We add an `IMAGE_REPO` environment variable for consistent image naming across stages.

---

## Create Dockerfile

Create `Dockerfile` in the `java-maven` project root with the following contents:

```dockerfile
FROM eclipse-temurin:21  
WORKDIR /app  
COPY target/cwvj-devsecops-demo-1.0.0-SNAPSHOT.jar app.jar  
EXPOSE 8080  
ENTRYPOINT ["java", "-jar", "app.jar"]  
```

---

### **Crisp explanation**

* `FROM eclipse-temurin:21`
  Uses Eclipse Temurin Java 21 runtime as a small, maintained base image.

* `WORKDIR /app`
  Sets the working directory inside the image to `/app`.

* `COPY target/cwvj-devsecops-demo-1.0.0-SNAPSHOT.jar app.jar`
  Copies the built JAR from your Maven `target` folder into the image as `app.jar`.

* `EXPOSE 8080`
  Documents that the container listens on port 8080 at runtime.

* `ENTRYPOINT ["java", "-jar", "app.jar"]`
  Runs the JAR when the container starts — this is the application entrypoint.

---

### **Commit and push**

From the `java-maven` folder:

```bash
git add .  
git commit -m "added Dockerfile"  
git push private-repo main  
```

---

## **Pipeline with Build Image Stage (IMAGE_REPO added)**

```groovy
pipeline {
  agent { label 'docker-maven-trivy' }
  tools {
    maven 'maven3'
  }
  environment {
    SONAR_IP = '172.31.21.44'
    ECR_REGISTRY = '386275436648.dkr.ecr.ap-south-1.amazonaws.com'
    IMAGE_REPO = "${ECR_REGISTRY}/cwvj-devsecops-demo"
  }
  stages {
    stage('Trivy FS Scan') {
      steps {
        sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
      }
    }
    stage('Build & Sonar') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token-new', variable: 'SONAR_TOKEN')]) {
          sh 'mvn clean verify sonar:sonar \
  -Dsonar.projectKey=cwvj-devsecops-demo \
  -Dsonar.host.url="http://${SONAR_IP}:9000" \
  -Dsonar.token="${SONAR_TOKEN}" \
  -Dsonar.qualitygate.wait=true'
        }
      }
    }
    stage('ECR Login') {
      steps {
        sh 'aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_REGISTRY'
      }
    }
    stage('Build Image') {
      steps {
        sh 'export DOCKER_BUILDKIT=0 && docker build --platform linux/amd64 -t "$IMAGE_REPO:$BUILD_NUMBER" -t "$IMAGE_REPO:latest" .'
      }
    }
  }
}
```

---

### **Explanation**

* `environment { IMAGE_REPO = "${ECR_REGISTRY}/cwvj-devsecops-demo" }`
  Defines the image repository variable used for tagging and pushing images across stages.

* `stage('Build Image')`
  Dedicated stage that constructs the container image from the pipeline workspace.

* `sh 'export DOCKER_BUILDKIT=0 && docker build --platform linux/amd64 -t "$IMAGE_REPO:$BUILD_NUMBER" -t "$IMAGE_REPO:latest" .'`
  Runs the build command inside the agent shell.


* `export DOCKER_BUILDKIT=0`
  Disables Docker’s newer BuildKit engine so builds run in the classic, predictable mode.
  Prevents unexpected behaviour when agents have older Docker versions or mixed BuildKit support.
  Ensures we get the same build output regardless of agent configuration.

* `--platform linux/amd64`
Ensures the image is built for the **amd64** architecture.
This matches your **EKS worker nodes**, which run **x86_64** (Docker treats x86_64 and amd64 as the same).
Prevents accidental multi-arch builds or arm64 builds that would fail to run on your cluster.
Also ensures compatibility with the **base image** in the Dockerfile (`FROM eclipse-temurin:21`), which is also amd64 by default.

  **In short:** the architecture of both the **EKS nodes** and the **base image** must align, and `--platform linux/amd64` guarantees that alignment.

* `-t "$IMAGE_REPO:$BUILD_NUMBER"`
  Tags the image with the Jenkins `BUILD_NUMBER` for immutable, traceable deployments.

* `-t "$IMAGE_REPO:latest"`
  Also tags the image as `latest` for demo convenience (repo configured to exclude `latest` from immutability).

* `.` (build context)
  Uses the repository root as the Docker build context; ensure a `.dockerignore` is present to keep context small.

---

### **Run the Stage**

Click **Build Now**.
If Docker is installed and Jenkins user has group membership, the Build Image stage will construct and tag the image successfully.
If it fails, check:

* Docker service is active (`sudo systemctl status docker`).
* `jenkins` user is in `docker` group and agent session picked up the change.
* Build context is small and `.dockerignore` is present.

---


## **Stage 6: Trivy Image Scan (Container Image Vulnerability Scan)**

*(Reference: “Trivy Image Scan” box in the pipeline diagram)*

### **Objective**

Scan the **built container image** for vulnerabilities before pushing or deploying it.
This ensures the actual runtime artefact (the Docker image running inside your Kubernetes pods) is secure and free from high or critical CVEs.

Image scanning is a mandatory security gate in any production DevSecOps pipeline.

---

## **Why Trivy Image Scan is Important**

Trivy Image Scan analyzes the **final container image**, including:

* OS packages inside the base image (Ubuntu, Alpine, Distroless, etc)
* Language-level dependencies bundled inside the image
* System libraries and utilities present only at runtime
* Vulnerable binaries or layers introduced by the base image

This is critical because **developers rarely control the base image**, yet most vulnerabilities come from it.

---

## **How Trivy Image Scan differs from previous scans**

### **1. Trivy FS Scan (SCA on source folder)**

* Scans your *project source code folder*
* Detects dependency vulnerabilities in `pom.xml`, configs, and vendor packages
* Does **not** inspect the final container image

### **2. SonarQube SAST + Coverage**

* Checks your **custom application code**
* Finds insecure patterns, code smells, bugs, and quality issues
* Measures unit test coverage
* Does **not** detect OS-level CVEs or container vulnerabilities

### **3. Trivy Image Scan (this stage)**

* Scans the **fully built image** stored in Docker local cache
* Finds vulnerabilities in base image layers and OS packages
* Detects issues that **do not exist in source code** and appear only after building
* Ensures production runtime artefact is safe to deploy

**In short:**
Source-level scans protect your code.
Image scans protect your container runtime.
Both are required for a secure pipeline.

---

## **Pipeline with Trivy Image Scan Stage**

```groovy
stage('Trivy Image Scan') {
  steps {
    sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL "$IMAGE_REPO:$BUILD_NUMBER"'
  }
}
```

---

### **Explanation**

* `stage('Trivy Image Scan')`
  Creates a dedicated security gate to scan the built Docker image before deployment.

* `trivy image ... "$IMAGE_REPO:$BUILD_NUMBER"`
  Scans the **exact image** we just built in the previous stage.
  Uses the immutable tag (`$BUILD_NUMBER`) to avoid scanning the wrong version.

* `--exit-code 1`
  Makes the pipeline **fail** if High or Critical vulnerabilities are found.

* `--severity HIGH,CRITICAL`
  Focuses on severe issues that must be fixed before any deployment.

---

### **Outcome**

This stage validates that the container image is production-safe.
If vulnerabilities are found:

* The pipeline fails
* You do **not** push the image
* You do **not** deploy it to EKS

This enforces a strong security boundary and ensures only secure container artefacts move forward.

---


## **Stage 7: Push to ECR (Push Built Image to Amazon ECR)**

*(Reference: “Push to ECR” box in the pipeline diagram)*

### **Objective**

Push the built and tagged Docker image to the Amazon ECR repository so it becomes available for deployment.
We push both the immutable build-tag (`$BUILD_NUMBER`) and the convenience `latest` tag.

---

### **Pipeline Snippet**

```groovy
stage('Push to ECR') {
  steps {
    sh 'docker push "$IMAGE_REPO:$BUILD_NUMBER"'
    sh 'docker push "$IMAGE_REPO:latest"'
  }
}
```

---

### **Why this stage matters**

* Pushes the exact artifact that was scanned and validated in prior stages.
* The `$BUILD_NUMBER` tag provides an immutable, traceable image for rollbacks.
* The `latest` tag is useful for iterative testing and demos (excluded from immutability in repo settings).

---

### **Explanation**

* `stage('Push to ECR')`
  Dedicated stage that uploads the local image to the remote ECR registry.

* `docker push "$IMAGE_REPO:$BUILD_NUMBER"`
  Pushes the build-specific image. This is the canonical image to promote to environments.

* `docker push "$IMAGE_REPO:latest"`
  Pushes the `latest` tag for convenience; repo was configured to exclude `latest` from immutability.

* Preconditions for success

  * ECR Login stage completed successfully.
  * `IMAGE_REPO` is correctly defined (`<account>.dkr.ecr.<region>.amazonaws.com/<repo>`).
  * Jenkins agent IAM role has ECR push permissions.
  * Docker daemon is running and the image with the specified tags exists locally.

---

### **Verify**

1. Open AWS Console → **Amazon ECR** → select repository `cwvj-devsecops-demo`.
2. Click **Images** (or **View push commands** → **View images**) and confirm two tags exist:

   * `<BUILD_NUMBER>` (e.g., `42`)
   * `latest`
3. Confirm image digest and pushed timestamp for traceability.

If a tag is missing, check pipeline logs for errors and ensure the image was built and tagged locally before push.

---

## **Stage 8: Create Kubernetes Manifests (Deployment + Service)**

*(Reference: “Create manifest” box in the pipeline diagram)*

### **Objective**

Create Kubernetes manifests for the application: a Deployment with **2 replicas** and a NodePort Service.
Add `topologySpreadConstraints` so pods are distributed across availability zones.
Commit the manifests to the repo so the pipeline can update them later.

---

### **Deployment (deploy-svc.yaml)**

```yaml
apiVersion: apps/v1  
kind: Deployment  
metadata:  
  name: cwvj-devsecops-demo  
  namespace: cwvj-devsecops
  labels:  
    app: cwvj-devsecops-demo  
spec:  
  replicas: 2  
  selector:  
    matchLabels:  
      app: cwvj-devsecops-demo  
  template:  
    metadata:  
      labels:  
        app: cwvj-devsecops-demo  
    spec:  
      topologySpreadConstraints:  
        - maxSkew: 1  
          topologyKey: topology.kubernetes.io/zone  
          whenUnsatisfiable: DoNotSchedule  
          labelSelector:  
            matchLabels:  
              app: cwvj-devsecops-demo  
      containers:  
        - name: cwvj-devsecops-demo  
          image: 386275436648.dkr.ecr.ap-south-1.amazonaws.com/cwvj-devsecops-demo:latest  
          ports:  
            - containerPort: 8080  
```

---

### **Service (deploy-svc.yaml — same file or separate)**

```yaml
apiVersion: v1  
kind: Service  
metadata:  
  name: cwvj-devsecops-demo-svc  
  namespace: cwvj-devsecops
  labels:  
    app: cwvj-devsecops-demo  
spec:  
  type: NodePort  
  selector:  
    app: cwvj-devsecops-demo  
  ports:  
    - port: 80  
      targetPort: 8080  
      protocol: TCP  
      nodePort: 31000  
```

---

### **topologySpreadConstraints — explanation**

* Purpose: evenly distribute pods across a topology domain (here, AZs) to improve availability and reduce blast radius.

* `maxSkew: 1`
  Maximum allowed difference in pod counts between topology domains. With 2 replicas, `maxSkew: 1` enforces an even 1–1 spread.

* `topologyKey: topology.kubernetes.io/zone`
  The node label used as the distribution axis. This tells the scheduler to spread pods across Availability Zones.

* `whenUnsatisfiable: DoNotSchedule`
  If placing a pod would violate the constraint, the scheduler will not place it. This enforces strict separation.

* `labelSelector.matchLabels`
  Limits the spread rule to pods with `app: cwvj-devsecops-demo` so other workloads are unaffected.


---

### **Pipeline Snippet**

```groovy
    stage('Update Deployment') {
      steps {
        sh 'sed -i "s|image:.*|image: $IMAGE_REPO:$BUILD_NUMBER|g" deploy-svc.yaml'
      }
    }
```

### **`sed` command — step-by-step explanation**

Command used later in pipeline:

```bash
sed -i "s|image:.*|image: $IMAGE_REPO:$BUILD_NUMBER|g" deploy-svc.yaml
```

1. `sed -i`
   Edit the file **in-place** so changes are written directly to `deploy-svc.yaml`.

2. `s|image:.*|image: $IMAGE_REPO:$BUILD_NUMBER|g`

   * `s` — `sed` substitute command.
   * `|` — delimiter chosen to avoid escaping slashes in the image URL.
   * `image:.*` — regex matching any `image:` line and everything after it on that line.
   * `image: $IMAGE_REPO:$BUILD_NUMBER` — replacement text; shell expands `$IMAGE_REPO` and `$BUILD_NUMBER` before `sed` runs.
   * `g` — global flag; replaces all matches in the file (safe if multiple `image:` entries exist).

3. `deploy-svc.yaml`
   The target manifest file to update.

**Net effect:** replaces every `image:` line with the exact build image `${IMAGE_REPO}:${BUILD_NUMBER}`, ensuring Kubernetes will pull the image produced by this pipeline run.

---

### **Commit the manifests**

```bash
git add .  
git commit -m "uploaded deployment and svc manifest"  
git push private-repo main  
```

---

## **Stage 9: Deploy to Kubernetes (Create cluster, grant access, deploy app)**

*(Reference: “Deploy to Kubernetes” box in the pipeline diagram)*

### **Objective**

Provision an EKS cluster (if not already present), give the Jenkins agent the minimum IAM + Kubernetes RBAC it needs, install `kubectl` on the agent, and deploy the `deploy-svc.yaml` manifest into the `cwvj-devsecops` namespace.
This stage is careful about sequencing: cluster first → node distribution → agent tools → IAM permissions → aws-auth mapping → RBAC → deployment.

> Reminder: **git push** your manifests before clicking Build Now so the pipeline has the latest files.

---

### **Pipeline Snippet**

```groovy
stage('Deploy to Kubernetes') {
  steps {
    sh '''#!/bin/bash -l
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name cwvj-devsecops-eks \
  --kubeconfig /home/jenkins/.kube/config

kubectl create ns cwvj-devsecops
kubectl apply -f deploy-svc.yaml

kubectl rollout status -n cwvj-devsecops deployment/cwvj-devsecops-demo --timeout=60s || {
  kubectl rollout undo -n cwvj-devsecops deployment/cwvj-devsecops-demo || true
  exit 1
}
'''
  }
}
```

---

### **What this stage does (high level)**

* Ensures Jenkins agent can talk to the EKS cluster via updated kubeconfig.
* Creates the demo namespace and applies the Deployment+Service manifests.
* Waits for the deployment to roll out; on failure it undoes the rollout and fails the stage.
* Enforces least-privilege: we only grant the Jenkins agent the RBAC verbs it needs (deployments, replicasets, pods, services, namespaces).

---

### **Pre-steps (what you must do first — sequence)**

1. **Create EKS cluster** using `eksctl` and the provided config.
2. **Verify node AZ distribution** with `kubectl get nodes --show-labels`.
3. **Install `kubectl` on jenkins-agent** (version should match EKS control plane).
4. **Attach inline EKS DescribeCluster policy** to `jenkins-agent-role`.
5. **Edit `aws-auth` configmap** to map the IAM role to a Kubernetes username.
6. **Create ClusterRole and ClusterRoleBinding** granting limited permissions.
7. **Commit and push** `deploy-svc.yaml` and RBAC manifests to the repo.

---

### **Create the EKS cluster — config with one-line comments**

Create `eks-config.yaml` and add these 1-line comments for clarity:

![Alt text](/images/me3.png)

#### Install Required Tools

Ensure the following tools are installed on your local machine or cloud jump-host:

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [eksctl](https://eksctl.io/installation/)

```yaml
apiVersion: eksctl.io/v1alpha5            # eksctl cluster config API version
kind: ClusterConfig                      # resource kind for eksctl
metadata:                                # cluster metadata block
  name: cwvj-devsecops-eks               # EKS cluster name
  region: ap-south-1                     # AWS region for the cluster
  version: "1.32"                        # Kubernetes control plane version
  tags:                                  # tags to help identify resources
    owner: cloudwithvarjosh               # tag owner
    environment: training                 # tag environment
    project: cwvj-devsecops-demo         # tag project
    purpose: youtube-labs                # tag purpose
availabilityZones:                        # AZs for node placement
  - ap-south-1a                           # AZ 1
  - ap-south-1b                           # AZ 2
iam:                                      # IAM/OIDC settings
  withOIDC: true                         # enable IAM OIDC provider for IRSA
managedNodeGroups:                        # defines managed node groups
  - name: cwvj-ng-public                  # node group name
    instanceType: t3.small                # EC2 instance type for workers
    minSize: 2                            # minimum nodes in node group
    maxSize: 2                            # maximum nodes in node group
    desiredCapacity: 1                    # desired node count at creation
    volumeSize: 20                        # root disk size (GiB)
    privateNetworking: false              # nodes get public networking
    ssh:                                  # SSH configuration
      allow: true                         # allow SSH access to nodes
      publicKeyName: cwvj-sj-mumbai       # EC2 key pair name for SSH
    iam:                                  # per-node-group IAM settings
      withAddonPolicies:                  # enable addon policies
        autoScaler: true                  # allow cluster autoscaler usage
        ebs: true                         # allow EBS volume usage
        albIngress: true                  # allow ALB ingress addon
        externalDNS: true                 # allow ExternalDNS addon
    labels:                               # node labels for scheduling
      owner: cloudwithvarjosh             # node label owner
      app: devsecops-demo                 # node label app
    tags:                                 # node-level tags
      node-type: public-worker            # custom tag
      managed-by: eksctl                  # managed by eksctl
```

Create the cluster:

```bash
eksctl create cluster -f eks-config.yaml
```

Verify node AZ distribution:

```bash
kubectl get nodes --show-labels | grep topology.kubernetes.io/zone
```

---

### **Install kubectl on the jenkins-agent**

```bash
# download kubectl binary for EKS version 1.32
curl -LO https://dl.k8s.io/release/v1.32.0/bin/linux/amd64/kubectl

# make it executable
chmod +x kubectl

# move it to /usr/local/bin so ALL users get it in PATH
sudo mv kubectl /usr/local/bin/
```

Verify:

```bash
kubectl version --client
sudo -u jenkins kubectl version --client
```

---

### **Modify `jenkins-agent-role` to allow kubeconfig update**

Attach an inline policy to the `jenkins-agent-role` that permits `eks:DescribeCluster` for the cluster:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster"
      ],
      "Resource": "arn:aws:eks:ap-south-1:386275436648:cluster/cwvj-devsecops-eks"
    }
  ]
}
```

Apply via IAM console: **Roles → jenkins-agent-role → Add inline policy**.

---

### **Why edit `aws-auth` and how**

The **aws-auth ConfigMap** controls how AWS IAM roles are mapped to Kubernetes users and groups.
EKS uses this mapping to determine **who can authenticate** to the cluster before RBAC decides **what they can do**.

Before adding our Jenkins role, let’s understand the **existing** ConfigMap created automatically by `eksctl`:

```yaml
apiVersion: v1
data:
  mapRoles: |
    - rolearn: arn:aws:iam::386275436648:role/eksctl-cwvj-devsecops-eks-nodegrou-NodeInstanceRole-J3Szf4uMWv1R
      groups:
      - system:bootstrappers
      - system:nodes
      username: system:node:{{EC2PrivateDNSName}}
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
```

---

### **Understanding the existing aws-auth entry**

This entry represents the **Node Instance Role** used by worker nodes.

* `system:bootstrappers`
  Allows nodes to **join the cluster** securely during bootstrapping.

* `system:nodes`
  Grants nodes permission to read/write node objects, report status, attach volumes, register with the scheduler, etc.
  This is a **powerful group** — nodes need it for cluster operations but humans should *never* be placed here.

* `username: system:node:{{EC2PrivateDNSName}}`
  Each worker node is represented as a Kubernetes user based on its private DNS name.

These permissions are **intended only for Kubernetes Nodes**, not CI/CD systems or humans.
Giving Jenkins these permissions would allow it to:

✔ Act like a node
✔ Update its own status
✔ Read/write secrets via node privileges
✔ Perform node-level actions across namespaces

This violates least privilege and is **dangerous**.

---

### **Why we do NOT add Jenkins to system:masters or node groups**

* `system:masters` → **full cluster admin**, unrestricted power
  (manage nodes, secrets, CRDs, everything).
* `system:nodes` or `system:bootstrappers` → **privileged node identity**, meant only for kubelets.

Granting Jenkins these groups would effectively give it rights equal to cluster-admin or node identity, which is unnecessary and insecure.

Pipeline deployments should **never** run with cluster-admin privileges.

---

### **Why we use only `system:authenticated`**

We map our Jenkins IAM role into:

```yaml
groups:
  - system:authenticated
```

This group means:

* “You are a known, authenticated user.”
* But you **do not** have any permissions by default.
* RBAC will decide exactly what Jenkins is allowed to do.

This enforces **strict least privilege**:

* Authentication → via aws-auth
* Authorization → granted later via a ClusterRole + ClusterRoleBinding we created

This separation keeps the cluster secure and predictable.

---

### **Add Jenkins IAM role to aws-auth**

Now that we understand the existing mapping, we add:

```yaml
mapRoles: |
  - rolearn: arn:aws:iam::386275436648:role/jenkins-agent-role
    username: jenkins-agent-role
    groups:
      - system:authenticated
```

Edit the ConfigMap (from the admin machine):

```bash
kubectl -n kube-system edit configmap aws-auth
```

---

### **Verify mapping**

```bash
kubectl describe configmap aws-auth -n kube-system
```

You should now see **two entries**:

1. NodeInstanceRole (bootstrappers + nodes)
2. jenkins-agent-role (system:authenticated)

---

### **Grant precise RBAC (least privilege)**

Create `clusterrole` and `clusterrolebinding` so the `jenkins-agent-role` (mapped username) can manage deployments, replicasets, services, pods, and namespaces — nothing more.

`clusterrole-binding.yaml` (two manifests combined):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: jenkins-deployer-role
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch", "delete"]
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch", "create", "delete", "patch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jenkins-deployer-binding
subjects:
  - kind: User
    name: jenkins-agent-role   # must match username in aws-auth
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: jenkins-deployer-role
  apiGroup: rbac.authorization.k8s.io
```

Apply (from cluster admin machine):

```bash
kubectl apply -f clusterrole-binding.yaml
```

**Verify:** try kubectl commands from the jenkins-agent (pods/deployments/services/namespaces should work; nodes list should fail).

---

### **Line-by-line explanation of the pipeline shell block**

This is the block you asked to be explained line-by-line:

```bash
#!/bin/bash -l
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name cwvj-devsecops-eks \
  --kubeconfig /home/jenkins/.kube/config

kubectl create ns cwvj-devsecops
kubectl apply -f deploy-svc.yaml

kubectl rollout status -n cwvj-devsecops deployment/cwvj-devsecops-demo --timeout=60s || {
  kubectl rollout undo -n cwvj-devsecops deployment/cwvj-devsecops-demo || true
  exit 1
}
```


1. `aws eks update-kubeconfig \`
   Begins the `aws` CLI command that populates a kubeconfig for the specified EKS cluster. This allows `kubectl` to talk to the cluster using IAM-based auth.

2. `  --region ap-south-1 \`
   Specifies the AWS region where the EKS cluster is located.

3. `  --name cwvj-devsecops-eks \`
   The name of the EKS cluster whose kubeconfig will be generated/updated.

4. `  --kubeconfig /home/jenkins/.kube/config`
   Writes the kubeconfig to the Jenkins user’s kubeconfig path so subsequent `kubectl` commands run as Jenkins will use it.

5. `kubectl create ns cwvj-devsecops`
   Creates the namespace `cwvj-devsecops` if it does not exist. `kubectl apply` would also create it if you included a namespace manifest, but this explicit create is simple and idempotent.

6. `kubectl apply -f deploy-svc.yaml`
   Applies the Deployment + Service manifest to the cluster in the current context (kubeconfig). This creates/updates the application resources.

7. `kubectl rollout status -n cwvj-devsecops deployment/cwvj-devsecops-demo --timeout=60s`
   Waits up to 60 seconds for the rollout to complete. This returns success when the deployment reaches the desired state.

8. `|| {`
    If the previous `rollout status` command fails (timeout or unhealthy pods), execute the commands inside the braces as a failure recovery block.

9. `  kubectl rollout undo -n cwvj-devsecops deployment/cwvj-devsecops-demo || true`
    Tries to roll back to the previous deployment revision. The `|| true` ensures that even if rollback fails, the script continues to the next line (so we can exit with a non-zero code afterwards).

10. `  exit 1`
    Exits the script with a non-zero exit code so Jenkins marks the stage as failed. This prevents bad deployments from being considered successful.

11. `}`
    Closes the failure handling block.

---

### **Verification steps**

After pipeline run (or manually):

* `kubectl get ns` → confirm `cwvj-devsecops` exists.
* `kubectl get deploy -n cwvj-devsecops` → check deployment presence.
* `kubectl rollout status -n cwvj-devsecops deployment/cwvj-devsecops-demo` → confirm stable rollout.
* `kubectl get pods -n cwvj-devsecops -o wide` → verify pods distribution across nodes/AZs.
* Test service access: `kubectl get svc cwvj-devsecops-svc -n cwvj-devsecops` and hit the `NodePort` if allowed.

---

### **Notes, gotchas & best-practices**

* Ensure Jenkins agent has AWS CLI, `kubectl`, and proper PATH.
* `aws eks update-kubeconfig` requires `eks:DescribeCluster` permission on the role.
* `aws-auth` mapping gives authentication; RBAC ClusterRoleBinding gives authorization. Keep bindings minimal.
* Rolling update timeout may need tuning for cold starts or image pulls.
* For production, use IRSA, service accounts, or kubeconfigs sealed as secrets — avoid using broad permissions.
* Always `git push` manifests before triggering pipeline to ensure pipeline uses the latest files.

---

## **Post Actions in Jenkins Pipeline**

At the end of the Jenkinsfile, we add a `post` block that defines actions Jenkins must perform **after the entire pipeline finishes**, regardless of which stage succeeded or failed.

This block is placed **outside the `stages {}` block** because it applies to the *pipeline as a whole*, not to any individual stage.
If it is placed inside `stages`, Jenkins will throw an error.

---

### **Pipeline Snippet**

```groovy
post {
  success { echo "Build ${env.BUILD_NUMBER} succeeded" }
  failure { echo "Build ${env.BUILD_NUMBER} failed" }
  always  { echo "Build ${env.BUILD_NUMBER} finished" }
}
```

---

### **Explanation**

* `post { ... }`
  A global section that defines actions Jenkins runs after the pipeline completes — regardless of what happened inside the stages.

* `success { ... }`
  Runs only when the **entire pipeline** succeeds.
  Common usage: send deployment notifications, push artifacts, tag builds as stable.

* `failure { ... }`
  Runs when **any stage fails**.
  Production usage: send alerts, page on-call teams, create Jira tickets, log failure metrics.

* `always { ... }`
  Runs **every time**, even if the pipeline was aborted, unstable, or failed.
  Production usage: workspace cleanup, log archival, closing external sessions, Slack notifications, cleaning Docker images, deleting temp files.

---

### **Why these belong outside `stages`**

The `stages {}` block defines the sequence of pipeline steps.
The `post {}` block defines **global lifecycle actions** for the *entire pipeline run*.
Putting it inside `stages` would make Jenkins assume it's another stage, which is invalid.

Correct structure:

```groovy
pipeline {
  agent any

  stages {
    stage('Build') { ... }
    stage('Deploy') { ... }
  }

  post {
    success { ... }
    failure { ... }
    always  { ... }
  }
}
```
---


## Trigger pipeline on Git **push**

**Recommended approach: Multibranch Pipeline + GitHub webhook**

1. Create Jenkins Multibranch Pipeline job pointing at your repo.

   * Jenkins will auto-scan branches and read `Jenkinsfile`.

2. Add Jenkins credentials for GitHub (username/token) in Jenkins Credentials.

   * Use a machine token, not a personal password.

3. Add a GitHub webhook in the repo → Settings → Webhooks.

   * Payload URL: `https://<JENKINS_HOST>/github-webhook/`
   * Content type: `application/json`
   * Secret: add a strong secret and store it in Jenkins job config (optional but recommended).
   * Events: select `Push` (and `Pull request` if you want PR builds).

4. Configure job branch filters and build strategies in Multibranch settings.

   * Exclude `dependabot` and `docs` branches if desired.

5. Test the webhook from GitHub UI → send `Push` test payload.

   * Check Jenkins job indexing and build logs for trigger confirmation.

**Alternative (simple): Poll SCM**

* Configure the job with `Poll SCM` cron (e.g., `H/5 * * * *`) as a fallback when webhooks are blocked.

**Security / production tips**

* Use webhook secret and enable secret validation in Jenkins.
* Use fine-grained GitHub tokens and least privilege.
* Prefer Multibranch for clean branch/PR isolation and auto-discovery.

---

### **Real-world usage by outcome:**

**Success:**

* Notifications: Slack, Teams, Email for successful builds.
* Git ops: tag commits or comment on PRs when builds pass.
* Reports: publish JUnit, coverage, and security summaries.

**Failure:**

* Notifications: alert developers or on-call immediately.
* Rollbacks: trigger rollback pipelines or mark deployment failed.
* Debug data: upload logs or diagnostic bundles for triage.

**Always:**

* Cleanup: remove temp files, old artifacts, Docker images.
* Observability: push metrics/logs to CloudWatch, Datadog, Prometheus, ELK.
* Housekeeping: archive artifacts and close active sessions.

---

## **How this pipeline can be improved (Production Enhancements)**

The pipeline you built is intentionally simple so you can learn every moving part clearly.
In real DevSecOps environments, teams extend this workflow to introduce stronger automation, GitOps, better deploy strategies, and enterprise security.
Below are the *most important upgrades*.

---

### **1. Kubernetes Ingress / Gateway API instead of NodePort (Highly recommended)**

In this demo, we used a simple NodePort due to its simplicity.
In production, teams use **Ingress controllers** or the **Gateway API** for TLS termination, host-path routing, and managed load balancers.
I already have a complete lecture demonstrating AWS Load Balancer Controller, TLS certificates, and routing patterns. Deploy your app using that flow to experience real-world ingress.
**Video:** [https://www.youtube.com/watch?v=ngyegIE_5FM&list=PLmPit9IIdzwSv2zwizysG6OwWUACpQFN0&index=3&t=1s](https://www.youtube.com/watch?v=ngyegIE_5FM&list=PLmPit9IIdzwSv2zwizysG6OwWUACpQFN0&index=3&t=1s)  
**GitHub Notes:** [https://github.com/CloudWithVarJosh/YouTube-Standalone-Lectures/tree/main/Lectures/03-ing-eks](https://github.com/CloudWithVarJosh/YouTube-Standalone-Lectures/tree/main/Lectures/03-ing-eks)  

---

### **2. Multibranch Pipelines (Critical for real CI/CD)**

Real teams don’t push to main directly.
A multibranch pipeline auto-discovers branches and PRs, runs CI on each, and only merges when checks pass.
I already have a deep-dive lecture on this using a practical project.
**Video:** [https://www.youtube.com/watch?v=Eq-HHLtSJM4&list=PLmPit9IIdzwSiYCKOtXUGNwytXXiJ8Rv8&index=7](https://www.youtube.com/watch?v=Eq-HHLtSJM4&list=PLmPit9IIdzwSiYCKOtXUGNwytXXiJ8Rv8&index=7). 
**GitHub Notes:** [https://github.com/CloudWithVarJosh/Jenkins-Basics-To-Production/tree/main/Day%2007](https://github.com/CloudWithVarJosh/Jenkins-Basics-To-Production/tree/main/Day%2007). 
I kept this demo single-branch for simplicity.

---

### **3. GitOps with ArgoCD (True production pattern)**

ArgoCD implements a **pull-based deployment** model where Kubernetes syncs itself from Git.
This ensures Git becomes the **single source of truth**, provides automated sync, drift detection, and instant rollbacks.
Not included here because ArgoCD has not yet been taught on my channel, but this is one of the most important next steps after mastering Jenkins pipelines.

---

### **4. Use DNS names instead of IPs (Always in production)**

We used raw IPs to reference Jenkins agent and SonarQube.
In production, always use **DNS (Route53 private zones, internal LB names, service discovery)** for reliability, identity, and certificate validation.
DNS gives portability — IP rotation or autoscaling never breaks your pipeline.

---

### **5. Use image digests instead of tags (Enterprise best practice)**

Enterprises pull images using immutable SHA256 digests, not tags.
A digest guarantees the exact scanned, approved artifact is what gets deployed — preventing tag drift or accidental overwrites.
You can easily add digest retrieval after pushing the image to ECR.

---

### **6. Signed images + policy enforcement**

Modern clusters enforce that only signed images can run (Cosign, Notary v2).
Pair this with Gatekeeper or Kyverno for runtime policies — ensuring only compliant, trusted containers reach production.
This protects your cluster from tampered or unverified images.

---

### **7. Centralised secrets management**

Instead of Jenkins credentials, enterprises integrate Vault or AWS Secrets Manager.
These tools provide short-lived secrets, automatic rotation, and strong encryption.
No secrets ever appear in logs or environment variables.

---

### **8. Observability integration**

Teams add CloudWatch, Grafana, Prometheus, or Datadog pipelines to track build → deploy → runtime behaviour.
This makes rollbacks easy and helps correlate performance issues with specific builds.
Add build-number annotations to deployments for traceability.

---

### **9. Policy-as-Code and compliance scans**

Insert Conftest, Checkov, or OPA checks to validate Kubernetes manifests and Terraform before deployment.
This ensures all resources comply with security standards and organisational policies — especially important in regulated environments.

---

### **10. Helm or Kustomize to manage Kubernetes manifests**

Instead of raw YAML, enterprises package deployments using **Helm charts** or **Kustomize** overlays.
This makes deployments modular, repeatable, and environment-aware, while keeping configuration clean.
Jenkins can easily template Helm values and deploy through chart releases.

---

### **11. Argo Rollouts / Blue-Green / Canary deployments**

Once you stabilise the basic pipeline, enhance deployments using progressive delivery.
Argo Rollouts, Flagger, or NGINX canary strategies enable partial rollouts, traffic shifting, and automatic rollback on failure.
This significantly reduces deployment risk.

---

### **12. Automated cleanups & cost optimisation**

Add steps to auto-delete unused images, clean Docker cache, remove old workspaces, and rotate ECR tags.
Enterprises heavily optimise CI/CD runtimes for speed and cost.

---

# **Conclusion**

We successfully implemented a complete DevSecOps pipeline that enforces **security at every layer**:

* Source-level security through SonarQube SAST and unit test coverage
* Dependency and filesystem scanning with Trivy FS
* Container image scanning with Trivy Image
* Immutable, versioned image storage in Amazon ECR
* Least-privilege EKS access for Jenkins through IAM + RBAC
* Topology-aware Kubernetes deployments with clean rollouts and automated rollback
* Pipeline-level post actions for success, failure, and always-run tasks

This pipeline demonstrates how real teams balance automation, security, and reliability.
Instead of only building and shipping containers, we ensure that **every artifact is scanned, validated, and deployed in a controlled, secure, and observable manner**.

You now have a reproducible template that mirrors production DevSecOps patterns and can be extended with features like admission controllers, GitOps, multi-stage environments, and progressive delivery strategies.

---

# **References**

Below are authoritative links and documentation used throughout this lecture:

### **Jenkins**

* Declarative Pipeline Syntax: [https://www.jenkins.io/doc/book/pipeline/syntax/](https://www.jenkins.io/doc/book/pipeline/syntax/)
* Post actions documentation: [https://www.jenkins.io/doc/book/pipeline/syntax/#post](https://www.jenkins.io/doc/book/pipeline/syntax/#post)

### **SonarQube**

* SonarQube Scanner for Maven: [https://docs.sonarsource.com/sonarqube](https://docs.sonarsource.com/sonarqube)
* Quality Gates: [https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/)

### **Trivy**

* Official Trivy Documentation: [https://aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy)
* Installation & Usage: [https://trivy.dev](https://trivy.dev)

### **Amazon ECR**

* Amazon ECR Authentication: [https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_Authorization.html](https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_Authorization.html)

### **Amazon EKS**

* aws-auth ConfigMap: [https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html](https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html)
* IAM for EKS access: [https://docs.aws.amazon.com/eks/latest/userguide/security-iam.html](https://docs.aws.amazon.com/eks/latest/userguide/security-iam.html)
* EKSCTL cluster creation: [https://eksctl.io/usage/creating-and-managing-clusters/](https://eksctl.io/usage/creating-and-managing-clusters/)

### **Kubernetes**

* Topology Spread Constraints: [https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/](https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/)
* RBAC Authorization: [https://kubernetes.io/docs/reference/access-authn-authz/rbac/](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
* Deployments: [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---
