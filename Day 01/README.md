# Modern SDLC Explained | Build Automation & Real-World Insights

## Table of Contents

- [Introduction](#introduction)  
- [The Software Development Life Cycle (SDLC)](#the-software-development-life-cycle-sdlc)  
  - [Phases of SDLC (Modern, Agile/DevOps)](#phases-of-sdlc-modern-agiledevops)  
- [Waterfall vs Agile/DevOps](#waterfall-vs-agiledevops)  
  - [Waterfall vs Agile/DevOps – Key Differences](#waterfall-vs-agiledevops--key-differences)  
- [Role of Git in Modern SDLC](#role-of-git-in-modern-sdlc)  
- [From SDLC to Build Automation](#from-sdlc-to-build-automation)  
- [Compiled vs. Interpreted Languages](#compiled-vs-interpreted-languages). 
  - [Java Artifact Formats](#java-artifact-formats)  
- [Build Processes in the Real World (DevOps/SRE Lens)](#build-processes-in-the-real-world-devopssre-lens)  
  - [Compiled Languages – Two-Step Build](#compiled-languages--two-step-build). 
    - [Containerized Workloads: Compiled Languages](#containerized-workloads-compiled-languages)  
    - [Non-Containerized Workloads: Compiled Languages](#non-containerized-workloads-compiled-languages)  
  - [Interpreted Languages – One-Step Build](#interpreted-languages--one-step-build)  
    - [Non-Containerized Workloads](#non-containerized-workloads)  
    - [Containerized Workloads](#containerized-workloads)  
- [Why Build Automation Matters](#why-build-automation-matters)  
- [Conclusion](#conclusion)  
- [References](#references)  

---

## Introduction

* Explore the phases of the **SDLC**, from requirements to feedback.
* Contrast **Waterfall vs Agile/DevOps**, and why iterative, automated delivery is now standard.
* Learn the difference between **compiled vs interpreted languages**, and what artifacts, runtimes, and dependencies really mean.
* Break down how build processes work in both **containerized and non-containerized workloads**.
* Understand **why build automation matters** and how it prevents “works on my machine” issues.

👉 By the end of this lecture, you’ll have a strong foundation to appreciate **why CI/CD exists** and how tools like Jenkins fit into the bigger picture.

---

## The Software Development Life Cycle (SDLC)

Every software product — whether a simple website or a large-scale banking system — goes through a structured journey called the **Software Development Life Cycle (SDLC)**.


### Phases of SDLC (Modern, Agile/DevOps)

![Alt text](/images/1a.png)

The Software Development Life Cycle defines how ideas move from requirements to running software.
In modern Agile/DevOps, this flow is **iterative, automated, and feedback-driven** rather than a rigid one-way process.


**1. Requirement Gathering** – Define what the system must achieve.

   * *Example:* A bank requests a mobile loan app; analysts capture user workflows, SLAs, audit requirements, and data-privacy constraints.
   * *Production note:* Strong requirements include both:

     * **Functional requirements:** what the system should do (e.g., apply for a loan, approve/reject requests, send notifications).
     * **Non-functional requirements:** how the system should behave (e.g., 99.9% availability, RPO = 15 min, response time <200 ms, GDPR compliance).
     * **Security & compliance needs:** capture standards upfront (PCI DSS, GDPR, ISO 27001, RBI/MAS guidelines) so architecture choices align with regulations.
     * **Environments & workflow expectations:** define that there will be dev, staging, and production environments, and that teams will follow a branching strategy in source control (the *specific approach* is designed in the next phase).

   Capturing these upfront avoids rework and ensures DevOps/SRE can plan for **reliability, compliance, and scalability** from day one.

**2. Design** – Decide how the system should function and interact.

   * *Example:* The team chooses a microservices approach for authentication, loan processing, and payments. APIs and data models are defined, along with retry and failure-handling strategies.
   * *Production note:* Effective design covers both functional and non-functional aspects:

     * **Source control strategy:** define branching models (trunk-based, GitFlow, release branches) early, ensuring teams follow consistent collaboration and merge practices.
     * **Branching policies:** enforce peer reviews, approvals, and CI checks before merges; decide rules for hotfix branches and release stabilization.
     * **Testability & observability:** design services with health endpoints, structured logs, metrics, and distributed tracing.
     * **Environment strategy:** plan for dev, staging, and production parity to reduce “works on my machine” issues.
     * **Scalability & resilience:** build for horizontal scaling, graceful degradation, and fallback mechanisms.
     * **Security boundaries:** define access controls, encryption standards, and compliance zones (e.g., PCI, HIPAA).

**3. Development** – Implement features and functionality as per design.

   * *Example:* Developers work on short-lived Git branches, raise pull requests for **peer code reviews**, run **local unit tests**, and resolve lint/type errors before merging.
   * *Production note:* Modern teams adopt practices that reduce risk and accelerate delivery:

     * **Shift-left security:** catch issues early by running checks during development, not after deployment. This includes **SAST (Static Application Security Testing)** and **SCA (Software Composition Analysis)** to scan source code and open-source dependencies for vulnerabilities.
     * **Trunk-based workflows:** developers commit small, frequent changes to the main branch (“trunk”) instead of maintaining long-lived feature branches. This reduces merge conflicts and keeps integration fast and continuous.
     * **Feature flags/toggles:** release new code behind runtime switches, so unfinished or risky features can be deployed to production without being visible to all users. Teams can gradually enable them for small groups (canary) or quickly disable if issues occur.
     * **Automated checks:** enforce style, quality, and security rules through pre-commit hooks and CI jobs, ensuring consistency before code merges.

**4. Build** – Compile code, resolve dependencies, and create deployable artifacts.
* *Example:* Java applications are built with **Maven/Gradle** into JAR/WAR files; Node.js uses `npm/yarn`; Python pins dependencies with `pip` and lockfiles. Teams may also containerize apps into **Docker images** for portability.
* *Production note:* Reliable builds are the backbone of CI/CD pipelines:

    * **Reproducibility:** enforce lockfiles, pinned versions, and deterministic build scripts.
    * **Artifact storage:** publish outputs to registries (Nexus, Artifactory, container registries) for traceability and rollbacks.
    * **Immutability:** once built, artifacts should not be modified; deploy the same artifact across dev, staging, and prod.
    * **Supply-chain security:** generate SBOMs (Software Bill of Materials), sign artifacts, and scan images for vulnerabilities to prevent compromised dependencies from reaching production.

**5. Testing (Continuous)** – Validation happens throughout, not just once.

* **Unit tests:** smallest logic checks (e.g., loan interest calculation).
* **Integration tests:** modules/services together (e.g., loan ↔ payment).
* **Functional/End-to-end:** full workflow (apply loan → approve → notify).

*Production note:* In modern pipelines, testing extends into staging and production-like environments with multiple safety nets:

* **Smoke tests:** quick deploy checks (homepage loads, APIs return 200).
* **Contract tests:** ensure microservices agree on request/response formats.
* **Performance/load tests:** simulate peak traffic, validate SLAs under stress.
* **Security testing (shift-left & continuous):**

  * **SAST (Static Application Security Testing):** scan source code, compiled artifacts, or even Dockerfile/image layers for insecure patterns and CVEs.

    * *Tools:* SonarQube, Checkmarx, Bandit, Trivy (image layer scanning).
  * **SCA (Software Composition Analysis):** identify vulnerable open-source libraries and base images.

    * *Tools:* Snyk, Anchore, Clair, JFrog Xray.
  * **DAST (Dynamic Application Security Testing):** probe running containers/services for runtime flaws (e.g., XSS, SQL injection, auth bypass).

    * *Tools:* OWASP ZAP, Burp Suite, Nikto.
  * **Runtime/container security (DAST extended):** detect malicious behavior or misconfigurations in live containers.

    * *Tools:* Falco, Aqua Security, Prisma Cloud, Sysdig Secure.
  * **Pen tests (periodic):** human-driven attack simulations, often run before major releases.

**6. Deployment** – Promote software safely across environments.

   * *Example:* Code flows from **Dev → Staging → Prod**. Staging mirrors production for realistic validation, and promotion requires automated checks or manual approvals depending on organizational policy.
   * *Production note:* Modern deployments emphasize safety, speed, and reversibility:

     * **Progressive delivery:** use blue-green or canary releases to minimize blast radius and validate changes with a small user set first.
     * **Infrastructure as Code (IaC):** manage deployments with declarative tools (e.g., Terraform, Helm, Ansible) for consistency and repeatability.
     * **Configuration promotion:** ensure config moves with the build (no “works in staging but fails in prod” surprises).
     * **Rollback & roll-forward playbooks:** automate recovery steps to quickly revert or advance if issues are detected post-deploy.
     * **Post-deploy validations:** run smoke tests, monitoring hooks, and health checks immediately after release to catch regressions early.


**7. Operate & Maintain** – Ensure reliability, security, and efficiency after go-live.

  * *Example:* Patch a loan calculation bug, scale horizontally during festive traffic spikes, rotate secrets and renew TLS certificates.
  * *Production note:* Daily operations involve more than just bug fixes:

    * **Monitoring & alerting:** track metrics, logs, and traces; define SLOs/SLIs; integrate with on-call systems.
    * **Backups & disaster recovery (DR):** ensure data recoverability, run periodic restore drills, validate RPO/RTO targets.
    * **Patch & upgrade cycles:** apply OS/runtime updates, upgrade libraries, rotate keys, and deprecate insecure versions.
    * **Capacity & cost optimization:** right-size infrastructure, use autoscaling, and monitor cloud spend.
    * **Incident response:** follow playbooks, perform blameless postmortems, and feed improvements back into pipelines.

**8. Feedback & Improve (Continuous)** – Learn from signals and evolve the system.

  * *Example:* Collect user feedback through surveys or analytics, monitor feature adoption, review weekly error budgets, and run blameless postmortems. Translate these into backlog items for future sprints.
  * *Production note:* This phase is about **continuous evolution**, not just keeping the lights on:

    * **User feedback loops:** prioritize features and UX fixes based on customer input and usage analytics.
    * **Weekly/iterative improvement cycles:** schedule retrospectives, review incidents, and agree on reliability/efficiency improvements.
    * **Reliability improvements:** recurring issues or SLO breaches feed directly into engineering backlogs.
    * **Security learnings:** vulnerability scans, pen tests, and incident reports inform stronger baselines.
    * **Pipeline and process tuning:** refine CI/CD flows, alerts, and test coverage to reduce noise and improve confidence.


> **Backbone: Source Control (Git)** – All code lives in a Git repo (GitHub/GitLab/Bitbucket). Teams collaborate via branches, pull requests, and reviews; only authorized collaborators can push or merge. CI pipelines are triggered automatically on repo events (push/PR). Version control ensures traceability, auditability, and rollback when needed.

> **Continuous by Design** – Testing, security, and automation are embedded at every stage: unit tests run locally, CI pipelines validate on push/PR, integration tests in staging, smoke tests post-deploy, and monitoring in production. Security is shift-left (SAST/SCA during dev, DAST/container scans during build/deploy), making the pipeline resilient end to end.

---


### Waterfall vs Agile/DevOps

* **Waterfall model** – A traditional, **linear approach** where work flows downward like a waterfall.

  * Each phase (Requirements → Design → Development → Testing → Deployment) must be completed **before the next begins**.
  * Feedback is **delayed** — bugs or design gaps are often discovered only at the end, when fixing them is expensive and slow.
  * Example: A bank builds a new system over 12 months; only at the end of the year do testers (and customers) see the first working product.

* **Agile + DevOps approach** – A **modern, iterative approach** where work is broken into small increments.

  * Developers push **small, frequent changes** rather than big releases.
  * Testing, security, and deployment are **automated** so teams get feedback early (in minutes or hours, not months).
  * Example: Netflix or Amazon push **hundreds of updates daily** — often invisible to end users — making delivery faster, safer, and more resilient.


### Waterfall vs Agile/DevOps – Key Differences

| **Aspect**             | **Waterfall**                              | **Agile/DevOps**                                   |
| ---------------------- | ------------------------------------------ | -------------------------------------------------- |
| **Process Flow**       | Linear, sequential (phase after phase)     | Iterative, continuous, overlapping activities      |
| **Delivery**           | Big-bang release at the end                | Small, frequent, incremental releases              |
| **Feedback**           | Comes late (after testing/deployment)      | Continuous (tests, automation, monitoring)         |
| **Flexibility**        | Rigid; hard to adapt once requirements set | Adaptive; requirements and priorities can evolve   |
| **Risk**               | High — issues found late are costly        | Lower — early detection through automation         |
| **Team Collaboration** | Siloed (handoffs between teams)            | Cross-functional (dev + ops + QA working together) |
| **Examples**           | Year-long banking system project           | Netflix/Amazon deploying updates daily             |


---

### Role of Git in Modern SDLC

In today’s Agile/DevOps workflows, **source code is always stored in a Git repository** (GitHub, GitLab, Bitbucket).

* Developers are added as **collaborators** and push code into branches.
* Changes are reviewed (pull/merge requests) and merged into the main branch.
* From there, automation tools (like Jenkins) can **pull the code**, run builds/tests, and promote it across environments.

This way, Git acts as the **single source of truth** — every change is tracked, versioned, and automatically linked to the build and release process.

---

### From SDLC to Build Automation

In the SDLC we saw that **Build** is one of the critical phases. But why do we even need a build stage? 🤔
The answer depends on the type of programming language being used — **compiled vs. interpreted**.

---


### Compiled vs. Interpreted Languages

![Alt text](/images/1b.png)

#### **Compiled Languages**

* **Source code is translated *before execution*** – a compiler converts human-readable source into either:

  * **Machine code** (e.g., C, C++, Go → `.exe`, ELF binary).
  * **Bytecode** (e.g., Java → `.class/.jar`, C# → `.dll`) which requires a runtime (JVM, .NET CLR).

* **Requires a build stage (compiler + tools)** – compilers (`gcc`, `g++`, `javac`, `go build`) handle translation; build tools (Maven, Gradle, Make, Bazel) orchestrate dependencies, packaging, and tests.
* **Faster execution (runs directly on CPU)** – since the code is already compiled into machine language, there’s no translation at runtime. This makes compiled programs suitable for performance-sensitive workloads (databases, operating systems, trading platforms).
* **Portability**

  * **Non-containerized:** Less portable — binaries are tied to the OS and CPU architecture (e.g., Linux x86\_64 binary won’t run on Windows ARM without recompilation). You also need the correct runtime/middleware (e.g., JVM, .NET CLR).
  * **Containerized:** More portable — once the artifact (e.g., `.jar`, `.exe`) is baked into a container image with its runtime and dependencies, the image can run consistently across environments (as long as a compatible container runtime exists).
* **Code is hidden (not directly visible)** – when you install an app on your laptop, mobile device, or even use a container image, you typically only see the compiled binary. The original source code is not shipped, which provides a layer of intellectual property protection.
* **Examples:** Java (compiled to bytecode, then run on the JVM), C/C++, Go, Rust.

---

#### Java Artifact Formats


When working with **Java applications**, you’ll often encounter different **artifact formats**. As DevOps/SRE engineers, it’s important to understand these at a **high level**, since they directly affect **how applications are deployed and what middleware/runtime is required**.

The most common formats are **`.jar`**, **`.war`**, and **`.ear`**, each serving a different purpose — from standalone apps to web apps to full enterprise systems. There’s also a fourth type, the raw **`.class`** file (bytecode produced by `javac`), which is typically an **intermediate step** and only used in advanced scenarios, not something you usually deploy directly.


| **Artifact**                         | **What it Contains**                                         | **Needs Runtime?** | **Needs Middleware?**           | **Where it Runs**                                 | **Real-world Example**             |
| ------------------------------------ | ------------------------------------------------------------ | ------------------ | ------------------------------- | ------------------------------------------------- | ---------------------------------- |
| **`.jar`** (Java ARchive)            | Compiled `.class` files + metadata + libraries               | ✅ JVM              | ❌ Not required                  | Directly with `java -jar app.jar` or as a library | Spring Boot microservice           |
| **`.war`** (Web Application Archive) | Web components (servlets, JSPs, HTML, static files, configs) | ✅ JVM              | ✅ Yes (Servlet container)       | **App servers** like Tomcat, JBoss, WebLogic      | Legacy HR portal on Tomcat         |
| **`.ear`** (Enterprise Archive)      | Multiple modules: `.war` + `.jar` (EJBs, services)           | ✅ JVM              | ✅ Yes (Full Java EE app server) | WebLogic, JBoss EAP, WebSphere, GlassFish         | Banking/insurance enterprise suite |

---

#### **Interpreted Languages**

* **Source code is executed by an interpreter at runtime** – no binary is generated beforehand; instead, the interpreter (like Python, Node.js, PHP runtime) reads and executes the code line by line.
* **Generally no explicit build step** – developers can write and run scripts directly, though packaging/dependency management is still needed for production.
* **Slower execution (line-by-line interpretation)** – since translation happens during runtime, interpreted languages usually have a performance penalty compared to compiled ones.
* **Portability**
  * **Non-containerized:** Portable *only if* the correct interpreter and dependencies are installed on the host. A Python script may run on Linux, Windows, or macOS — but only if the right Python version + required libraries (`pip install`) are present.
  * **Containerized:** Highly portable — the base image (e.g., `python:3.11-slim`, `node:20-alpine`) ensures the interpreter and dependencies are pre-packaged. The same image will run consistently across dev, staging, and production.
* **Code is visible (shared as scripts)** – when you distribute a Python, JavaScript, or Ruby program, you’re often sharing the raw source code (e.g., `.py`, `.js`, `.rb` files). Anyone with access can read or modify it unless you obfuscate or package it. In containerized workloads, images built with interpreted languages typically **embed the source code inside the image**, making it directly visible unless extra steps (obfuscation, bytecode compilation, packaging) are taken.
* **Examples:** Python, JavaScript (Node.js), PHP, Ruby, Perl.

> ⚡ *Note:* Modern engines (like V8 for Node.js) use **JIT compilation** to speed up execution. This blurs the line, but source code is still required at runtime, so JavaScript is generally treated as an interpreted language.

---

### Build Processes in the Real World (DevOps/SRE Lens)

![Alt text](/images/1c.png)

As DevOps/SRE engineers, you’ll mostly be deploying **containerized workloads**. These workloads are built on top of applications written in either **compiled** or **interpreted** languages. To understand how containers (or even non-containerized apps) are prepared for production, it’s important to know **what exactly gets packaged and shipped**.

Before diving into compiled vs. interpreted builds, let’s clarify some **key terms** that appear in every build process:

* **Artifact** → the tangible build output that results from a build step.
  *Examples:* `.jar`, `.war` (Java), `.exe` (Windows apps), `a.out` (C), Go binary.

* **Runtime** → the execution environment required for running your app.

  * For compiled languages: **JVM** (Java), **.NET CLR** (C#), **libc/glibc** (C/C++).
  * For interpreted languages: the **interpreter itself** (Python, Node.js, Ruby).
    👉 Think of runtime as the “engine” — it provides the instructions or system calls your program needs.

* **Middleware** → additional layer between runtime/OS and your application that provides extra services your code relies on.

  * Examples: **Tomcat, JBoss, WebLogic** (for Java `.war`/`.ear` apps).
  * Why “middleware”? Because it sits *in the middle* — your app doesn’t implement HTTP request handling, connection pooling, or transaction management; the middleware does it for you.

* **Dependencies** → external libraries, frameworks, or modules needed for your app’s logic.
  *Examples:* Spring Boot (Java), Flask/Django (Python), Express (Node.js).

👉 Together, these three — **artifact, runtime, and dependencies** — form the **backbone** of any workload. How they’re prepared and combined differs between **compiled** and **interpreted** languages, and between **containerized** and **non-containerized** environments.

**Note on End-User Installations**
When end-users install applications on their laptops or servers, the **installer package** typically includes everything needed — binaries, runtimes, and required dependencies — so the app runs out of the box. In cases where dependencies might conflict or cannot be bundled (e.g., licensing, system-level requirements), the application owner will **explicitly document prerequisites**.

* Example: *“This application requires Java 17 or above”* — here, the installer assumes the correct JVM is already present on the system.

👉 This ensures consistency: either the installer bundles the full runtime stack, or the owner specifies **exact versions** the user must install before running the app.

---

### Compiled Languages – Two-Step Build

Compiled languages always require a **compilation step** before deployment. Source code is translated into machine-readable artifacts (`.jar`, `.war`, `.exe`, binaries), which are then deployed either onto **VMs/servers** or **container images**.

---

#### Containerized Workloads: Compiled Languages

![Alt text](/images/1d.png)

* **Step 1: Application Build**

  * Source code is compiled into an artifact using compilers (`javac`, `gcc`, `go build`) orchestrated by build tools (Maven, Gradle, Make).
  * Output formats: `.jar`, `.war`, `.exe`, or single binary.

    | **Language** | **Compiler**          | **Common Build Tools**       | **Artifact Format**          |
    | ------------ | --------------------- | ---------------------------- | ---------------------------- |
    | **Java**     | `javac`               | Maven, Gradle                | `.class`, `.jar`, `.war`     |
    | **C**        | `gcc`, `clang`        | make, CMake                  | Executable (`a.out`, `.exe`) |
    | **C++**      | `g++`, `clang++`      | CMake, Bazel                 | Executable / `.so`, `.dll`   |
    | **Go**       | `go build` (built-in) | Go modules (built-in), Bazel | Single binary executable     |


* **Step 2: Container Image Build**

  * A Dockerfile copies the artifact into a base runtime image:

    ```dockerfile
    FROM openjdk:17-jdk-slim
    COPY app.jar
    ```
  * The resulting image is **slim, immutable, and production-ready** — containing only what’s needed to run (artifact + minimal runtime).
  * Benefits: smaller attack surface, secure and reproducible deployments.
  * Additional enterprise practices: **artifact signing, SBOMs (Software Bill of Materials), image scanning**.

---

#### Non-Containerized Workloads: Compiled Languages

![Alt text](/images/1e.png)

* **Step 1: Application Build**

  * Just like in containers, compilers + build tools produce an artifact (`.jar`, `.war`, `.exe`, binary).

* **Step 2: Deployment onto VM/Server**

  * The artifact is deployed directly to a host or application server.
  * **Dependencies must already exist** on the VM:

    * **Runtimes** → JVM (for Java), .NET CLR (for C#), libc/glibc (for C/C++).
    * **Middleware** → Application servers like Tomcat or JBoss (for `.war` deployments).
  * Risks: **configuration drift** — different environments may have mismatched versions of runtimes or middleware.
  * Ops teams often standardize runtimes and use automation tools (Ansible, Puppet, Chef) to enforce consistency.

---

#### Key Takeaway

* **Compiled languages → 2-step process**:

  * **Build application artifact → Deploy artifact** (into container image or directly on VM).
* **Containerized builds** ensure slim, immutable images with predictable behavior.
* **Non-containerized builds** depend heavily on the target VM’s runtime/middleware setup, which is prone to drift if not managed carefully.

---

### Interpreted Languages – One-Step Build

Unlike compiled languages, interpreted languages don’t have a separate “compile → artifact” stage. The **source code itself is executed directly by the interpreter (which acts as the runtime)**. But a *build step still exists* — not for compilation, but for **assembling a consistent execution environment** (runtime + dependencies + code).

---

#### Non-Containerized Workloads

![Alt text](/images/1g.png)

* **Source code runs directly on the host** through the interpreter (e.g., `python script.py`, `node app.js`, `ruby server.rb`).
* The **runtime/interpreter must already exist** on the VM/server (Python, Node.js, Ruby, etc.).
* **Dependencies** are installed and version-locked using package managers:

  * Python → `pip install -r requirements.txt`
  * Node.js → `npm install`
  * Ruby → `gem install`
* To avoid conflicts between projects, **per-project isolation tools** are used:

  * **venv (Python Virtual Environment):** Creates a project-specific folder with its own Python binary + libraries. Example: Project A runs Django 3.2, Project B runs Django 4.0 — both coexist safely.
  * **nvm (Node Version Manager):** Allows multiple Node.js versions. Example: One app runs Node.js 14, another runs Node.js 20; switch seamlessly per project.
  * **rbenv (Ruby Environment):** Manages multiple Ruby versions side by side (e.g., Ruby 2.7 vs 3.2).

⚠️ Without proper isolation, apps may break across laptops, QA servers, or production due to mismatched runtimes or dependency versions.

---

#### Containerized Workloads
![Alt text](/images/1f.png)
* The **runtime comes from a base image** — e.g., `python:3.11-slim`, `node:20-alpine`, `ruby:3.2`.
* A **Dockerfile** defines the build process:

  ```dockerfile
  FROM python:3.11-slim
  COPY source .
  RUN pip install -r requirements.txt
  ```
* Step 1: **Image Build** → packages source code + dependencies + runtime into a container image.
* Step 2: **Deploy Containers** → that image is run consistently across dev, staging, and production.
* This guarantees **consistency** (no “works on my machine” issues), but note:

  * Code is visible inside the image.
  * Enterprises may apply **obfuscation, packaging, or runtime controls** to reduce source code exposure.

---

#### Key Takeaways

* **Build ≠ compilation** in interpreted languages.
* Instead, build = **preparing the execution environment** (runtime + dependencies + code).
* **Non-containerized:** Relies on interpreters + package managers + isolation tools.
* **Containerized:** Encapsulates runtime, dependencies, and code into an immutable container image.
* Tradeoff: Containers simplify reproducibility but still expose the source code.


---

### Why Build Automation Matters

Writing code is only half the job. To actually run in production, applications need to be **prepared into a deployable form** — whether that’s a compiled artifact (`.jar`, `.exe`, Go binary) or an interpreted app with its dependencies packaged (`pip`, `npm`, `gem`).

If this step is done **manually**, every developer may use different commands, dependency versions, or environments. That leads to unpredictable results — the classic *“works on my machine”* problem. In production, these mismatches cause outages, bugs, or inconsistent behavior.

👉 **Automation fixes this** by making builds **reproducible, traceable, and environment-agnostic**. A properly automated build process ensures:

* The same steps run everywhere (dev, staging, prod).
* Artifacts and dependencies are version-locked.
* Results are predictable and safe to promote.

---
