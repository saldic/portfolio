---
title: "06 - The Figma Make process"
date: 2026-10-14
weight: 6
tags: ["aida", "supavisor", "figma", "claude"]
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../anatomy-of-chip/">01</a>
  <a class="exam-portfolio-nav__link" href="../keeping-chip-up-to-date/">02</a>
  <a class="exam-portfolio-nav__link" href="../interrogating-chip/">03</a>
  <a class="exam-portfolio-nav__link" href="../delegating-the-code-not-the-theory/">04</a>
  <a class="exam-portfolio-nav__link" href="../grill-me/">05</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../figma-make-process/">06</a>
  <a class="exam-portfolio-nav__link" href="../security-and-ethics/">07</a>
</div>

## Spec-driven design

In Supavisor, AI was mostly part of how we planned and designed the system. Both followed a **spec-driven** approach, which means that decisions were written down as requirements before anything was built, and the AI worked from those requirements. The specification came out of a grill-me session, and I used it to get an overview of which components the design needed. The AI that turned the design into screens was **Figma Make**, Figma's AI tool that turns a text prompt into an interactive prototype you can click through, with real code behind it.

## From whiteboard to prompt

Before I used any AI for the design, I drew the screens on a physical whiteboard and discussed the UI and UX with our product owner and the rest of the group. The final decisions were mine, and I could explain every one of them. I then brought Claude a full list of requirements from the whiteboard and our specification, covering the screens, the navigation, the toolbar, what the schedule should show and what must not change. Claude turned that list into prompts for Figma Make.

## The Figma Export from Hell

The prototype looked the way we had drawn it, but the code behind it did not fit our project. Figma Make wrote it in TypeScript (TSX) and styled it with **Tailwind CSS**, where the styling is written as class names directly in the markup. Our frontend used plain JavaScript (JSX) and ordinary CSS, so I had Claude refactor the export into JSX.

After that, the whole app was still a single file. `App.jsx` was 3,894 lines long, with 1,088 `className` attributes and demo data such as `mockAssignments`. The styling sat in an `index.css` that was one line of 62,714 characters, the compiled output of Tailwind. It worked as a prototype, but none of it was connected to our backend. When another group member and I converted it into our real frontend, an AI split the styling into a CSS module for each page.

## Lack of overview
I understood the code in principle. What I lacked was an overview. I could not say why the styling was organised the way it was, or predict what a change in one place would do somewhere else. I could read it, but I am not sure I owned it.

<div class="exam-portfolio-pagination">
  <a role="button" href="../grill-me/">Previous Chapter</a>
  <a role="button" href="../security-and-ethics/">Next Chapter</a>
</div>
