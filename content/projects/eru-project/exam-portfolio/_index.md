---
title: "Backend Process"
description: "Backend process"
date: 2026-04-07
weight: 10
hideChildList: true
layout: "story"
cascade:
  layout: "story"
---

Welcome to my backend exam portfolio for **eru**, a backend API developed during the third semester backend course.

This portfolio documents how the project evolved from an early idea into a deployed Java backend with authentication, content management, user interactions, AI-based elaboration, testing, and deployment.

The purpose of this document is not to present a perfect linear success story. Instead, it is meant to show how the system gradually grew as new technologies were introduced week by week, how architectural decisions were made, and how my understanding of backend development developed over time.

eru is a backend for a learning-focused content platform built around short educational posts such as facts, theories, and quotes. The goal of the project was to explore how a scrolling-style application could be used for something more meaningful than passive entertainment.

<div class="exam-portfolio-pagination">
  <a role="button" href="../what-is-eru/">The story behind eru</a>
  <a role="button" href="../frontend-process/">Go to Frontend Process</a>
</div>

## Chapter Overview

<div class="exam-portfolio-grid">

  <a class="exam-week-card" href="./planning-phase/">
    <p class="exam-week-card__eyebrow">01</p>
    <h3 class="exam-week-card__title">The Beginning</h3>
    <p class="exam-week-card__body">From the first project idea and early scope decisions to the initial domain sketch.</p>
  </a>

  <a class="exam-week-card" href="./jpa-basics/">
    <p class="exam-week-card__eyebrow">02</p>
    <h3 class="exam-week-card__title">Laying the Foundation</h3>
    <p class="exam-week-card__body">Setting up Hibernate, persistence, DAOs, and the first concrete building blocks of the backend.</p>
  </a>

  <a class="exam-week-card" href="./jpa-basics-and-relations/">
    <p class="exam-week-card__eyebrow">03</p>
    <h3 class="exam-week-card__title">Relationship Challenges</h3>
    <p class="exam-week-card__body">Figuring out how the entities should relate and modelling interactions in a way that made domain sense.</p>
  </a>

  <a class="exam-week-card" href="./data-integration/">
    <p class="exam-week-card__eyebrow">04</p>
    <h3 class="exam-week-card__title">Implementing OpenAI's API</h3>
    <p class="exam-week-card__body">Integrating AI elaboration through OpenAI and designing the request flow around it.</p>
  </a>

  <a class="exam-week-card" href="./rest-api/">
    <p class="exam-week-card__eyebrow">05</p>
    <h3 class="exam-week-card__title">eru = REST API</h3>
    <p class="exam-week-card__body">Building the HTTP layer, DTO boundaries, route structure, and a cleaner application setup.</p>
  </a>

  <a class="exam-week-card" href="./rest-and-test/">
    <p class="exam-week-card__eyebrow">06</p>
    <h3 class="exam-week-card__title">REST and Test</h3>
    <p class="exam-week-card__body">Testing the API from the outside with integration tests, JWT checks, and Rest Assured assertions.</p>
  </a>

  <a class="exam-week-card" href="./security/">
    <p class="exam-week-card__eyebrow">07</p>
    <h3 class="exam-week-card__title">Security</h3>
    <p class="exam-week-card__body">JWT, authorization, authenticated-user context, and integrating security cleanly into the architecture.</p>
  </a>

  <a class="exam-week-card" href="./deployment/">
    <p class="exam-week-card__eyebrow">08</p>
    <h3 class="exam-week-card__title">Deployment & The Beginning of the End</h3>
    <p class="exam-week-card__body">The full CI/CD pipeline, live deployment, and the DNS, HTTPS, database, and secret-handling issues that had to be solved along the way.</p>
  </a>

</div>
