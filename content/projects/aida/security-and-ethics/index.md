---
title: "07 - Security and ethics"
date: 2026-10-14
weight: 7
tags: ["aida", "security", "ethics", "chip"]
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
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../security-and-ethics/">07</a>
  <a class="exam-portfolio-nav__link" href="../reflection/">08</a>
</div>

## An agent or a spy?

A coding agent can read a repository, run commands in a terminal, edit files, make commits and send what it reads to a model on someone else's server. The most likely risk is that the agent makes an ordinary mistake, such as including a `.env` file in a summary, running a command that prints environment variables, or committing a secret.

While I built this portfolio, Claude had access to a few chosen folders on my Mac. It was told never to read the values in a `.env` file, it could not delete anything without my approval, and it could not push to GitHub, so every push was mine. Those limits helped, but the rule about `.env` is only a rule. The file is still on a machine where an AI is working, and the safest assumption is that anything on that machine can be read. It is hard to trust an external AI completely, whatever it promises.

## Where the keys live

Chip needs two kinds of keys. The Dify Knowledge API key, which the sync script uses, sits in a `.env` file on my Mac that is excluded from git. In GitHub Actions the same key is stored as a **repository secret**, so it never appears in the code or the logs. The OpenAI key that Chip's model runs on has a hard spending limit of 5 dollars, so a leaked key or a visitor spamming the chat can never cost more than that.

In Supavisor, the deployed server reads its database connection and settings from environment variables, and developers keep their local values in a config file that git ignores. Early on, though, a small config file with database settings, including a password, was committed and then deleted two days later. Deleting a file does not remove it from git history, so anyone with access to the repository can still read the old version. The only real fix is to change the password.

If I set it up again, I would consider a **key vault**, a central service that stores secrets and controls who can read them. A vault per application and per environment keeps development and production keys apart, and access can be protected with two-factor authentication. A vault does not stop an agent from reading a secret that is already on the same machine, but it gives an overview of which keys exist and who uses them.

## Nothing to leak

A chatbot can only reveal what it has access to. Chip's only tool is a search in the knowledge base, which contains my public portfolio pages and nothing else. The API keys live in the settings of Dify and OpenAI, outside anything Chip can read. When I tried to make Chip print its system prompt and asked it for its keys, it declined both times.

That would change if Chip got a tool that could read files or call other services. The safe pattern is the same as for coding agents. A tool should only get the access it needs, so a search over public documents is preferable to a general function that reads any file.

## What happens to a visitor's question

A question typed into Chip does not stay on my site. It goes to Dify, which runs on Microsoft Azure in the US and keeps the conversation in the app's logs. It goes to OpenAI, which turns it into an embedding and writes the answer, and which keeps API data for up to 30 days for **abuse monitoring** but does not use it for training. It also goes to Jina, whose reranker sorts the passages.

Chip does not ask for any **personal data**, but nothing stops a visitor from typing a name or an email, and under GDPR that is personal data whether I asked for it or not. I think Chip should warn people not to share personal information, and the site should have a short privacy note explaining where the questions go.

Since 2 August 2026, the EU **AI Act** requires a chatbot to tell people that they are talking to an AI. Chip's opening message says that it is an AI assistant, that it answers from the pages on this site and that it can get things wrong, and the sources are listed under every answer so a visitor can check them. Copyright is simpler. The knowledge base only contains text I wrote myself, so Chip can only quote material I am allowed to share.

## Chip the Cheap

OpenAI charges per **token**, a small piece of a word. For `gpt-4o-mini` the price is 0.15 dollars per million tokens in and 0.60 dollars per million tokens out, and every answer sends the system prompt, up to eight passages from my pages and the whole conversation so far. So far, Chip has cost 0.02 dollars. The low cost comes from choosing a small model that is good enough for the task, and from a sync script that only sends new or changed pages to Dify.

<div class="exam-portfolio-pagination">
  <a role="button" href="../figma-make-process/">Previous Chapter</a>
  <a role="button" href="../reflection/">Next Chapter</a>
</div>
