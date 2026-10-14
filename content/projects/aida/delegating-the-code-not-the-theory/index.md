---
title: "04 - Delegating the code, not the theory"
date: 2026-10-13
weight: 4
tags: ["aida", "naur", "reflection"]
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../anatomy-of-chip/">01</a>
  <a class="exam-portfolio-nav__link" href="../keeping-chip-up-to-date/">02</a>
  <a class="exam-portfolio-nav__link" href="../interrogating-chip/">03</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../delegating-the-code-not-the-theory/">04</a>
  <a class="exam-portfolio-nav__link" href="../grill-me/">05</a>
</div>

## Who's driving?

Since AI became part of software development, it is harder to keep both hands on the wheel. If you let your guard down and accept whatever the model suggests, you slowly stop making the decisions yourself. You lose ownership of the product one suggestion at a time, and you don't really notice it happening. At some point you find yourself in the passenger seat, without knowing how you got there or who picked the route.

The **theory of the program**, according to Peter Naur, is what is lost. The code is still there, but you no longer understand why it looks the way it does.

This semester the most useful thing AI did for my group was ask questions. Before any of us wrote a line of code, we ran a **'grill-me'** session as the first step of our **spec-driven development**. We came out of it with a spec of **73 user stories** and a shared understanding of what we were building. The spec was then broken down into prioritised tickets, and some of those tickets became briefs for a coding agent.

> That shared understanding is what Naur means by theory, and in this case the AI helped us build it.

So for me, the interesting question is how to use AI without losing that understanding.

## Before the course

Before this semester I used AI quite casually. I told it what to do, and if the result worked, I didn't think much more about it. Afterwards I was often left wondering why it had chosen that particular method, or solved the problem that particular way. The code was in my repository, but I couldn't always explain why it was written like that. Looking back, I wasn't really the one driving.

I've since learned that the result depends on how clear my instructions are. There's a difference between **asking** an AI something and **giving it a task**. When I ask, I still do the work myself and the AI is an assistant. When I give it a task, the agent does the work, and the rules and the spec I give it are what keep it from guessing. Without them, the result mostly comes down to probabilities I have much less control over.

## Grill-me

'Grill-me' worked the other way round. The AI asked the questions, and it kept going until  it reached questions we probably wouldn't have thought about until it was too late to change them easily. We answered yes or no, or told it to do something else. That made our own picture of the system clearer.

Without grill-me, an agent usually fills in open decisions with a default and writes it into the plan, and it's hard to tell that guess apart from an actual choice. Grill-me helped us build that shared understanding, which mattered more than getting a perfect spec. It's the most useful way I've used AI so far, and I stayed in the driver's seat the whole way.

<div class="exam-portfolio-pagination">
  <a role="button" href="../interrogating-chip/">Previous Chapter</a>
  <a role="button" href="../grill-me/">Next Chapter</a>
</div>
