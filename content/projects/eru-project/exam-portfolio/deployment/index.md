---
title: "08 - Deployment & The Beginning of the End"
description: "Deployment and the beginning of the end phase of the eru exam portfolio."
date: 2026-04-07
weight: 8
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../planning-phase/">01</a>
  <a class="exam-portfolio-nav__link" href="../jpa-basics/">02</a>
  <a class="exam-portfolio-nav__link" href="../jpa-basics-and-relations/">03</a>
  <a class="exam-portfolio-nav__link" href="../data-integration/">04</a>
  <a class="exam-portfolio-nav__link" href="../rest-api/">05</a>
  <a class="exam-portfolio-nav__link" href="../rest-and-test/">06</a>
  <a class="exam-portfolio-nav__link" href="../security/">07</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../deployment/">08</a>
</div>

## Overview

The beginning of the end is here, and eru can finally come to life through the **full pipeline**.

The deployment is officially **live** on https://eru-api.dk/api/v1/routes

## The Pipeline Picture

Let me introduce you to the **full CI/CD pipeline process** using GitHub Actions and Docker

![Full CI/CD pipeline for eru](/images/fullpipeline.png)

So looking at this picture, how did the deployment actually work?

1. The developer (me) writes code locally.
2. I then push the code to GitHub
3. The code is stored in the GitHub repository, which also contains the *Dockerfile* (which defines how the Java application is packaged into a Docker container and how that container should run) and the GitHub Actions *workflow* (which automates publishing the application image when stuff gets pushed to main).
4. A push to the *main* branch triggers GitHub Actions
5. GitHub Actions builds the project, runs the tests, and prepares the deployment process, unless the test/s fails.
6. GitHub Actions then builds and pushes a Docker image of the application.
7. That new Docker image is then pushed to Docker Hub (all of this is connected to my Docker Hub username `cphds`), as `cphds/eru:latest`
8. The server later performs a Docker image pull from Docker Hub instead of receiving code directly from GitHub
9. Watchtower, running on the DigitalOcean server, monitors the image and checks wether the `:latest` tag has changed
10. When a newer image is available, Watchtower pulls the updated image and replaces the running container, thereby deploying the new version of the Javalin API
11. Caddy acts as a reverse proxy in front of the running container and exposes the API securely over HTTPS on the project domain

Seems easy right? **It wasn't.**

## docker-compose.yml

Existing on the droplet is a docker-compose.yml, which is the blueprint for the deployment setup, and it looks somewhat like this. Which is also where Caddy and Watchtower is configured.

```yaml
version: '3'

services:

  db:
    image: postgres:16.2
    container_name: db
    restart: unless-stopped
    networks:
      - backend
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data:/var/lib/postgresql/data/
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 10s

networks:
  backend:
    name: backend
```

## Challenges I Encountered During Deployment

Deployment turned out to be one of the **most educational** and at the same time the **most exhausting** parts of the project. Even though the application itself was working locally, several issues appeared once I tried to run it as a **real deployed system**.

1. One of the first problems was that the domain `eru-api.dk` did not resolve correctly, which meant the API was not reachable from outside the server. Because of that, Caddy could not obtain an HTTPS certificate, and repeated failed certificate attempts eventually triggered Let’s Encrypt rate limiting. This meant I had to stop retrying and wait for the next valid issuance window instead of trying to brute-force the setup.

2. Another issue was that PostgreSQL was running, but the actual `eru` database did not exist yet inside the container. As a result, the application failed during startup because it could not connect to the expected database. I also ran into a Docker-related issue where Watchtower initially failed because of a Docker API version mismatch between the Watchtower container and the Docker daemon on the server.

3. Deployment also exposed configuration and security problems in the project itself. One of my Docker files contained a hardcoded database password that had been tracked in Git, which meant I had to treat that secret as compromised and clean up the configuration. Once the API was publicly accessible, I also realised that some route permissions were too loose for a real deployment. For example, the AI endpoint was initially open to everyone, and regular authenticated users had too much power over content management.

## How I Solved Them

1. I solved the deployment issues **step by step** by working from infrastructure inward. The domain problem was fixed by pointing `eru-api.dk` to the DigitalOcean droplet correctly through DNS. After that, I allowed DNS propagation to complete and retried the HTTPS setup through Caddy. When Let’s Encrypt rate limiting occurred, I simply waited for the retry window instead of continuing to force certificate requests.

2. To fix the application startup issue, I created the missing `eru` database directly inside the running PostgreSQL container and then restarted the API container. The Watchtower issue was solved by explicitly setting a compatible Docker API version in the Watchtower configuration so it could communicate with the server’s Docker daemon correctly.

3. For the configuration cleanup, I removed the **hardcoded password** from the tracked Docker setup, replaced it with **environment variables**, and added a cleaner `.env.example` file. I then tightened the authorization model so that the AI endpoint now requires an **authenticated user**, while content creation, updating, and deletion are restricted to **admins** instead of regular users.

## My Final Thoughts

This has been a journey like no other, it has been quite the **learning curve**, and im now looking forward to get creative with the frontend implementation, and to finally let loose my inner artist and to give eru some colour.

Deployment can be a bit tricky sometimes, but from every mistake you make, you have one less mistake *to* make!

<div class="exam-portfolio-pagination">
  <a role="button" href="../security/">Previous Chapter</a>
  <a role="button" href="../">Back To Overview</a>
</div>
