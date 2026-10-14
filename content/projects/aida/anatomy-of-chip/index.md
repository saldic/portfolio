---
title: "01 - Anatomy of Chip"
date: 2026-10-13
weight: 1
tags: ["aida", "chip", "rag", "dify"]
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../anatomy-of-chip/">01</a>
  <a class="exam-portfolio-nav__link" href="../keeping-chip-up-to-date/">02</a>
  <a class="exam-portfolio-nav__link" href="../interrogating-chip/">03</a>
  <a class="exam-portfolio-nav__link" href="../delegating-the-code-not-the-theory/">04</a>
  <a class="exam-portfolio-nav__link" href="../grill-me/">05</a>
  <a class="exam-portfolio-nav__link" href="../figma-make-process/">06</a>
  <a class="exam-portfolio-nav__link" href="../security-and-ethics/">07</a>
</div>

## Chip the RAG-bot

RAG stands for retrieval-augmented generation. Before the language model writes anything, the system finds the passages from my own pages that best match the question, and the model answers from those. A general model knows nothing about my projects, so without RAG it would make up something that sounds right.

My pages are Markdown files in the portfolio. When I push to GitHub, GitHub Actions builds the site with Hugo and publishes it. The same push starts a second workflow that runs the sync script. It sends new and changed pages to Dify, where they are split into chunks and embedded.

When a visitor asks a question in the chat bubble, Dify runs Chip's chatflow. Chip runs on Dify Cloud, so it works on the live site.

{{< mermaid >}}
flowchart TB
  subgraph before["Python script syncs the pages to Dify on every push"]
    direction LR
    P["My pages<br/>Markdown in content/"] --> C["Chunks + embeddings<br/>text-embedding-3-small"] --> K[("Chip Knowledge<br/>chunks stored as vectors")]
  end
  subgraph ask["When Chip receives a question"]
    direction LR
    Q["Question<br/>from the chat bubble"] --> E["Embed the question<br/>with the same model"] --> V["Vector search<br/>finds the closest chunks"] --> R["Reranker · Chip's extra step<br/>reads question + chunk together,<br/>keeps the best 8"]
  end
  subgraph answer["Writing the answer"]
    direction LR
    PR["Prompt<br/>system prompt + question<br/>+ the 8 chunks"] --> L["LLM<br/>gpt-4o-mini writes"] --> A["Answer<br/>with sources underneath"]
  end
  before --> ask
  ask --> answer
  classDef hi stroke-width:3px
  class R hi
{{< /mermaid >}}

In Dify, Chip's chatflow has four steps: user input, knowledge retrieval, the LLM and the answer.

## Finding the right chunks

The knowledge base, *Chip Knowledge*, holds my portfolio pages as 15 documents, and a sync script keeps it up to date. Dify splits each page into **chunks**, smaller passages that can match a specific question. I left the chunk size on Dify's automatic setting.

Each chunk is turned into an **embedding** with OpenAI's `text-embedding-3-small`. An embedding is a long list of numbers that represents what the text is about, so texts that mean similar things get similar numbers. "Which database does Supavisor use?" ends up close to a chunk about PostgreSQL, even though the words are different. **Vector search** finds the chunks closest to the question.

The candidates then go to a **reranker**, `jina-reranker-v3`. The embedding compares the question and the chunk separately, while the reranker reads them together and scores how well the chunk answers the question. The eight best chunks go on to the model. It used to be four, but testing showed that wasn't enough.

There is no **score threshold**. When I tested one, the relevant chunks scored the same as the noise, so no value removed only the noise. I also tried **hybrid search**, which adds keyword search to vector search, and it didn't change the result.

The knowledge base and the chatflow each have their own retrieval settings. Reranking is off in the knowledge base and on in the chatflow, and the chatflow decides. The knowledge base's Top K still limits how many candidates come out at all, so it's set to 8 in both places.

The sync script also puts the page's title, section and tags at the top of each document. They come from the front matter, which is removed before upload, so without them a chunk wouldn't know which page it came from.

## The model and the prompt

The chunks are put into the system prompt, and OpenAI's `gpt-4o-mini` writes the answer. I started with `gemma3:4b`, a small open model running through Ollama. But Ollama has to run on my own computer, my laptop has 8 GB of RAM, and it made no sense for it to act as a server all the time.

This is the system prompt. `{{#context#}}` is where Dify inserts the chunks.

> You are Chip, an AI assistant on Dino Saldic's portfolio website. Visitors ask you about Dino and his projects. Refer to Dino in the third person.
>
> Use the following portfolio context to answer the user's question:
>
> CONTEXT: {{#context#}}
>
> Answer the user's question based on this context.
>
> Only use information from the CONTEXT. Do not use general knowledge, even if you recognise a term. If the context does not explain something, say that you cannot find it in the portfolio.
>
> Answer in the same language as the user.

Two parts of the prompt are new. The first line used to say:

> You are an AI assistant for my online portfolio.

Chip took "my" literally and talked to visitors as if they were me. Now it says:

> You are Chip, an AI assistant on Dino Saldic's portfolio website.

The line about general knowledge is also new. When I asked what AIDA is, Chip explained the marketing model AIDA (Attention, Interest, Desire, Action), which isn't mentioned anywhere on my site. The old prompt said to answer from the context, but it didn't forbid the model from filling gaps with what it already knew. The prompt still has no rules for off-topic questions and no protection against someone telling it to ignore its instructions.

## Memory, temperature and the answer

Conversation memory is on, with no limit, so a follow-up like "tell me more about that" works. The cost is that every earlier message is sent to the model again.

**Temperature** controls how much the model varies its answers. It was 0.7 when I ran the Chip test, and at that level Chip would sometimes round off an answer with a phrase that wasn't on the page. I lowered it to 0.4, because I'd rather have a quick, precise answer.

The model runs on my own OpenAI API key with a hard spending limit of 5 dollars, so a visitor spamming the chat can't cost me more than that.

The answer is shown as it is, with the sources listed underneath, and nothing checks it on the way out. That's fine for a chat bubble a person reads. If another system depended on Chip's answers, it would need structured output and validation.

## On the page

Before a visitor writes anything, Chip says:

> Hi, I'm Chip, an AI assistant. I answer questions about Dino's portfolio using the pages on this site. I can get things wrong, so check anything important on the pages themselves.

The EU AI Act requires chatbots to tell people they're talking to an AI from 2 August 2026. Chip didn't, until I moved it to the live site.

Most of Chip's settings came from what we used in class, and at first I hadn't thought much about them. Going through them gave me a list of things to test: the number of chunks, the score threshold, hybrid search, the temperature and the missing AI disclosure. Some I changed, and some I tested and kept.

<div class="exam-portfolio-pagination">
  <a role="button" href="../">Back To Overview</a>
  <a role="button" href="../keeping-chip-up-to-date/">Next Chapter</a>
</div>
