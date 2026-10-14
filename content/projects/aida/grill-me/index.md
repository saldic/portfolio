---
title: "05 - Grill-me"
date: 2026-10-14
weight: 5
tags: ["aida", "supavisor", "sdd", "grill-me"]
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../anatomy-of-chip/">01</a>
  <a class="exam-portfolio-nav__link" href="../keeping-chip-up-to-date/">02</a>
  <a class="exam-portfolio-nav__link" href="../interrogating-chip/">03</a>
  <a class="exam-portfolio-nav__link" href="../delegating-the-code-not-the-theory/">04</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../grill-me/">05</a>
  <a class="exam-portfolio-nav__link" href="../figma-make-process/">06</a>
  <a class="exam-portfolio-nav__link" href="../security-and-ethics/">07</a>
</div>

## From interview to specification

Supavisor began with an interview. Almost all team members were present while a coding agent ran the **grill-me** skill. The skill works through a design as a decision tree: in each round it asks every question that can be answered at that point, proposes an answer to each, and waits for the group to decide before moving on. It stops when no open decisions remain.

The result was `spec.md`, committed after the session together with a prioritised product backlog (P0 to P4). The specification contains a problem statement, 73 user stories, implementation decisions, testing decisions and a list of what is **out of scope**.

## Strengths and weaknesses of grill-me

The main strength of grill-me was that it moved the hard questions to the start. Questions we had not thought about ourselves came up before any code existed, when the cost of change was at its lowest. Grill-me turned the implicit assumptions an agent would otherwise make silently into questions, each with a recommended answer. That made the choices visible, but it also meant that an assumption could still slip through if we simply accepted the recommendation.

The recommended answers also made the questions easy to discuss, because everyone had something concrete to agree or disagree with, and a disagreement at that stage shows that people's mental models of the system differ while it is still cheap to fix. What came out of the session went straight into the specification and from there into a prioritised product backlog, so it became the starting point for how we planned the sprints. 

The weaknesses are easier to see in hindsight. The session itself was not saved, so there is no record of which answers came from us and which were the agent's recommendations that we accepted. A recommendation that is accepted without discussion ends up in the specification looking exactly like a decision. Every decision was ours in the sense that we said yes to it, but some of them we made by quickly accepting the agent's suggestion. The specification also lacks **acceptance criteria** for the individual stories. Each story states a need and a purpose, but the document does not define when a story is done, so that had to be written by hand in each GitHub issue.

Finally, the shared understanding the session produced existed mainly in the heads of the people in the room. That became a problem when two new members joined the group well after the session. We had to explain the product to them, but we could not be sure that our explanation matched what had been decided, or that they would get the whole picture, because what they had missed was the process. They had the specification and the code to work from, and the theory behind them had to come from us.

## The Naur test

One way to check whether a grill-me session has built a shared understanding is the **Naur test**. The team closes the agent and answers questions such as which decisions were made and why, which decision the team is least sure of, and what the agent must not change without asking. If the answers require looking in the documents, the understanding has not yet been built.

We never ran it. In Naur's terms, the theory of a program lives in the people who build it, and the test is a way of checking that it is actually there. Without it, we assumed that the session had given everyone who attended it the same understanding. Our way of working made that assumption harder to keep. We picked stories from the sprint backlog freely, so no part of the system had a clear owner, and the understanding from the session was spread across the group with nobody holding it together.

Looking back, we were in control of the decisions during the session. In Naur's sense, being in control of a program means holding the theory behind it, and that is the part we never made sure of.

<div class="exam-portfolio-pagination">
  <a role="button" href="../delegating-the-code-not-the-theory/">Previous Chapter</a>
  <a role="button" href="../figma-make-process/">Next Chapter</a>
</div>
