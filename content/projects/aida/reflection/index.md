---
title: "08 - Reflection"
date: 2026-10-14
weight: 8
tags: ["aida", "reflection", "naur"]
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
  <a class="exam-portfolio-nav__link" href="../figma-make-process/">06</a>
  <a class="exam-portfolio-nav__link" href="../security-and-ethics/">07</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../reflection/">08</a>
</div>

## Two ways of using AI

This semester I worked with AI in two very different ways. In Chip, my portfolio chatbot, AI is the product. A visitor asks a question, a knowledge base finds the right passages from my pages, and a language model writes the answer. In Supavisor, our group project, AI was part of the process. It helped us plan the system with grill-me, it helped me turn a whiteboard design into prompts for Figma Make, and it reviewed pull requests.

The places where I kept control have something in common. I did the thinking before the AI did the work. In Chip, I went through every setting I had taken from class and tested the ones I was unsure of: the number of chunks, the score threshold, hybrid search and the temperature. When Chip failed a question, I worked out with Claude's help whether the search or the model was to blame before I changed anything, and the fix that worked was one I could explain.

The same pattern shows up in Supavisor. In the grill-me session the agent asked, and the group decided. The design started on a whiteboard, and the prompts for Figma Make were built from a list of requirements I brought, which made them read like small specifications with clear limits. When I reviewed pull requests, I read the code myself before I asked Claude Code, so I was not reading the code through its findings. Nothing on this site went online before I had read and approved it.

## Lessons

There were also places where I lost control without noticing at first. `rag_sync.py` is the clearest example from Chip. I understood the idea before I understood all of the syntax, and the most important part of the script, the decision to skip, create or update a page, has no test. I can defend the idea and the decisions, but the code itself was written by Claude.

The Figma Make export is the clearest example from Supavisor. I understood the code in principle, but the styling ended up as one line of compiled CSS that an AI later split into modules. I could read it, but I could not say why it was organised the way it was, or predict what a change would do.

Next time I would connect Figma's **MCP** server to Claude Code in our frontend repository. MCP (Model Context Protocol) is a standard way to give an AI assistant direct access to an outside tool. Instead of exporting one file of almost 4,000 lines, I could share the link to the Figma Make project, let the agent fetch only the files for the screen we were working on, and ask it to rebuild that screen with our own components, plain JSX and a CSS module per page. A rule in the project's instruction file, such as replacing Tailwind classes with our own styling, would apply every time. Each screen would then arrive as a small change in our own structure, which is much easier to review and to own.

The same loss of control happened on a smaller scale in the grill-me session. Some decisions were made by quickly accepting the agent's recommendation, and in those cases the decision was ours while the thinking behind it came from the agent. The understanding itself also turned out to be fragile. Two members joined the group after the session and got the specification and the code without the process behind them. We never ran a test to check whether the understanding we thought we shared was actually there, and with no clear owner for each part of the system, it was spread across the group.

Next time, after a grill-me session, I would close the agent and check, as a group, whether we can explain our decisions without the documents, and I would do the same with anyone who joins later. I would also split the user stories into **swimlanes**, so each person owns a part of the system from end to end and the theory of that part lives somewhere specific. The rest of the changes are small. I would consider a key vault for secrets, and I would give Chip a warning about personal data and the site a short privacy note.

## Decisions and theory

My own rule of thumb from this semester is that coding agents work really well as long as you stay in control, and that you lose ownership when you get lazy. Looking back, that holds, but control turned out to mean two different things. I was usually in control of the decisions. Whether I held the theory behind them, in Naur's sense of being able to explain, justify and change what was built, depended on how much work I did after the AI had answered.

Where I did that work, as with Chip's settings and the test that followed, the system is mine. Where I accepted the output because it worked, as with the CSS and parts of the sync script, it runs, but I am not sure I own it. What made the difference was whether I stayed in the *driver's seat* after the AI had done its part.

<div class="exam-portfolio-pagination">
  <a role="button" href="../security-and-ethics/">Previous Chapter</a>
  <a role="button" href="../">Back To Overview</a>
</div>
