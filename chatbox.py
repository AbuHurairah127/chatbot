import streamlit.components.v1 as components


def render_chatbox(api_url: str = "http://127.0.0.1:8000") -> None:
    """Render a floating chat UI fixed to the bottom-right of every page."""
    components.html(
        f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
      overflow: hidden;
    }}
  </style>
</head>
<body>
<script>
(function () {{
  const API_URL = {api_url!r};
  const doc = window.parent.document;
  const win = window.parent;

  if (doc.getElementById("floating-chat-root")) {{
    return;
  }}

  const style = doc.createElement("style");
  style.id = "floating-chat-style";
  style.textContent = `
    #floating-chat-root {{
      position: fixed !important;
      right: 20px !important;
      bottom: 20px !important;
      z-index: 999999 !important;
      font-family: "Segoe UI", Tahoma, sans-serif;
    }}
    #floating-chat-toggle {{
      width: 56px;
      height: 56px;
      border: none;
      border-radius: 50%;
      background: #111827;
      color: #fff;
      font-size: 22px;
      cursor: pointer;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }}
    #floating-chat-panel {{
      display: none;
      flex-direction: column;
      width: min(360px, calc(100vw - 40px));
      height: 460px;
      margin-bottom: 12px;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 16px;
      box-shadow: 0 18px 50px rgba(0,0,0,0.2);
      overflow: hidden;
    }}
    #floating-chat-panel.open {{
      display: flex;
    }}
    #floating-chat-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      background: #111827;
      color: #fff;
      font-weight: 600;
    }}
    #floating-chat-close {{
      border: none;
      background: transparent;
      color: #fff;
      font-size: 18px;
      cursor: pointer;
    }}
    #floating-chat-messages {{
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      background: #f8fafc;
    }}
    .chat-bubble {{
      max-width: 85%;
      margin: 0 0 10px 0;
      padding: 10px 12px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.4;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .chat-bubble.user {{
      margin-left: auto;
      background: #111827;
      color: #fff;
    }}
    .chat-bubble.assistant {{
      margin-right: auto;
      background: #fff;
      border: 1px solid #e5e7eb;
      color: #111827;
    }}
    .chat-bubble.system {{
      margin: 0 auto 10px auto;
      background: #eef2ff;
      color: #3730a3;
      font-size: 12px;
    }}
    #floating-chat-form {{
      display: flex;
      gap: 8px;
      padding: 10px;
      border-top: 1px solid #e5e7eb;
      background: #fff;
    }}
    #floating-chat-input {{
      flex: 1;
      resize: none;
      min-height: 44px;
      max-height: 90px;
      padding: 10px;
      border: 1px solid #d1d5db;
      border-radius: 10px;
      font: inherit;
    }}
    #floating-chat-send {{
      border: none;
      border-radius: 10px;
      padding: 0 14px;
      background: #111827;
      color: #fff;
      cursor: pointer;
      font-weight: 600;
    }}
    #floating-chat-send:disabled {{
      opacity: 0.6;
      cursor: not-allowed;
    }}
  `;
  doc.head.appendChild(style);

  const root = doc.createElement("div");
  root.id = "floating-chat-root";
  root.innerHTML = `
    <div id="floating-chat-panel">
      <div id="floating-chat-header">
        <span>AI Chat</span>
        <button id="floating-chat-close" type="button" aria-label="Close">×</button>
      </div>
      <div id="floating-chat-messages"></div>
      <form id="floating-chat-form">
        <textarea id="floating-chat-input" placeholder="Write your prompt..."></textarea>
        <button id="floating-chat-send" type="submit">Send</button>
      </form>
    </div>
    <button id="floating-chat-toggle" type="button" aria-label="Open chat">💬</button>
  `;
  doc.body.appendChild(root);

  const panel = doc.getElementById("floating-chat-panel");
  const toggle = doc.getElementById("floating-chat-toggle");
  const closeBtn = doc.getElementById("floating-chat-close");
  const form = doc.getElementById("floating-chat-form");
  const input = doc.getElementById("floating-chat-input");
  const sendBtn = doc.getElementById("floating-chat-send");
  const messages = doc.getElementById("floating-chat-messages");

  function addBubble(text, role) {{
    const bubble = doc.createElement("div");
    bubble.className = `chat-bubble ${{role}}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }}

  addBubble("Ask me anything. Your prompts are answered by the Groq agent.", "system");

  function setOpen(open) {{
    panel.classList.toggle("open", open);
    toggle.style.display = open ? "none" : "inline-flex";
  }}

  toggle.addEventListener("click", () => setOpen(true));
  closeBtn.addEventListener("click", () => setOpen(false));

  form.addEventListener("submit", async (event) => {{
    event.preventDefault();
    const prompt = (input.value || "").trim();
    if (!prompt) return;

    addBubble(prompt, "user");
    input.value = "";
    sendBtn.disabled = true;

    const thinking = doc.createElement("div");
    thinking.className = "chat-bubble assistant";
    thinking.textContent = "Thinking...";
    messages.appendChild(thinking);
    messages.scrollTop = messages.scrollHeight;

    try {{
      const response = await win.fetch(`${{API_URL}}/chat`, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ prompt }}),
      }});
      const data = await response.json();
      if (!response.ok) {{
        throw new Error(data.detail || "Chat request failed");
      }}
      thinking.textContent = data.reply || "(empty reply)";
    }} catch (error) {{
      thinking.textContent = `Error: ${{error.message || error}}`;
    }} finally {{
      sendBtn.disabled = false;
      input.focus();
      messages.scrollTop = messages.scrollHeight;
    }}
  }});

  input.addEventListener("keydown", (event) => {{
    if (event.key === "Enter" && !event.shiftKey) {{
      event.preventDefault();
      form.requestSubmit();
    }}
  }});
}})();
</script>
</body>
</html>
        """,
        height=0,
        width=0,
    )
