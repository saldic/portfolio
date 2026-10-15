// Chip's own chat window sends questions here. The Worker passes them on to
// the Dify app with the secret API key and streams the answer back, so the
// key never reaches the browser. It only passes on the answer text, the
// names of the pages the answer came from and the conversation id, nothing
// else from Dify, and it caps how many questions can be asked a minute.
// Every other request is served from the static site.

const MAX_QUESTION = 600; // characters

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/chat") return env.ASSETS.fetch(request);

    const origin = request.headers.get("Origin") || "";
    const allowed = [url.origin, ...String(env.ALLOWED_ORIGINS || "").split(",").map((o) => o.trim()).filter(Boolean)];
    const cors = allowed.includes(origin) ? { "Access-Control-Allow-Origin": origin, Vary: "Origin" } : {};

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: { ...cors, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Content-Type" },
      });
    }
    if (request.method !== "POST") return json({ error: "Method not allowed." }, 405, cors);
    if (!allowed.includes(origin)) return json({ error: "This site may not use Chip." }, 403, cors);
    if (!env.DIFY_API_KEY) return json({ error: "Chip is not set up yet." }, 500, cors);

    // Every question costs tokens, so each visitor gets a few questions a
    // minute, and everyone together a few more. Cloudflare counts per data
    // centre, so the caps are rough but stop anyone from running up the bill.
    const visitor = request.headers.get("CF-Connecting-IP") || "unknown";
    const [mine, everyone] = await Promise.all([
      env.CHIP_VISITOR_LIMIT ? env.CHIP_VISITOR_LIMIT.limit({ key: `chip:${visitor}` }) : { success: true },
      env.CHIP_TOTAL_LIMIT ? env.CHIP_TOTAL_LIMIT.limit({ key: "chip:all" }) : { success: true },
    ]);
    if (!mine.success) return json({ error: "That's a lot of questions at once. Give Chip a minute and try again." }, 429, cors);
    if (!everyone.success) return json({ error: "Chip is busy right now. Try again in a minute." }, 429, cors);

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "The request could not be read." }, 400, cors);
    }
    const question = typeof body.question === "string" ? body.question.trim() : "";
    if (!question) return json({ error: "Ask Chip a question first." }, 400, cors);
    if (question.length > MAX_QUESTION) return json({ error: `Keep the question under ${MAX_QUESTION} characters.` }, 400, cors);
    const conversationId = typeof body.conversationId === "string" ? body.conversationId.slice(0, 100) : "";
    const user = typeof body.user === "string" && body.user ? body.user.slice(0, 100) : "visitor";

    const base = String(env.DIFY_BASE_URL || "https://api.dify.ai/v1").replace(/\/+$/, "");
    const dify = await fetch(`${base}/chat-messages`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.DIFY_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ inputs: {}, query: question, response_mode: "streaming", conversation_id: conversationId, user }),
    });
    if (!dify.ok || !dify.body) {
      console.log(`Dify answered ${dify.status}: ${await dify.text().catch(() => "")}`);
      return json({ error: "Chip could not answer right now. Try again in a moment." }, 502, cors);
    }

    return new Response(relay(dify.body), {
      headers: { ...cors, "Content-Type": "text/event-stream", "Cache-Control": "no-store" },
    });
  },
};

// Reads Dify's stream of events and writes a smaller one of our own:
// {type: "answer", text}, then {type: "done", conversationId, sources} or
// {type: "error"}.
export function relay(stream) {
  const { readable, writable } = new TransformStream();
  const writer = writable.getWriter();
  const encoder = new TextEncoder();
  const send = (event) => writer.write(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));

  (async () => {
    const reader = stream.pipeThrough(new TextDecoderStream()).getReader();
    let buffer = "";
    let finished = false;
    const handle = async (event) => {
      if ((event.event === "message" || event.event === "agent_message") && event.answer) {
        await send({ type: "answer", text: event.answer });
      } else if (event.event === "message_end") {
        const names = (event.metadata?.retriever_resources || []).map((r) => r.document_name).filter(Boolean);
        await send({ type: "done", conversationId: event.conversation_id || "", sources: [...new Set(names)] });
        finished = true;
      } else if (event.event === "error") {
        console.log(`Dify stream error: ${event.message || ""}`);
        await send({ type: "error" });
        finished = true;
      }
    };
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += value;
        let end;
        while ((end = buffer.indexOf("\n\n")) >= 0) {
          const block = buffer.slice(0, end);
          buffer = buffer.slice(end + 2);
          for (const line of block.split("\n")) {
            if (!line.startsWith("data:")) continue;
            let event;
            try {
              event = JSON.parse(line.slice(5));
            } catch {
              continue;
            }
            await handle(event);
          }
        }
      }
      if (!finished) await send({ type: "error" });
    } catch (error) {
      console.log(`Relay failed: ${error}`);
      await send({ type: "error" }).catch(() => {});
    } finally {
      await writer.close().catch(() => {});
    }
  })();

  return readable;
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), { status, headers: { ...headers, "Content-Type": "application/json" } });
}
