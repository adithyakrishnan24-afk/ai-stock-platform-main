const API_BASE = "https://ai-stock-platform-zpkg.onrender.com";

const input = document.getElementById("userMessage");
const chatBox = document.getElementById("chatBox");

input.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

async function sendMessage() {

  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, "user-msg");
  input.value = "";

  // Bot typing indicator
  const typing = appendMessage("Thinking...", "bot-msg");

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await res.json();

    typing.remove();
    appendMessage(data.reply, "bot-msg");

  } catch (err) {
    typing.remove();
    appendMessage("⚠️ Server error. Try again later.", "bot-msg");
  }
}

function appendMessage(text, className) {
  const div = document.createElement("div");
  div.className = className;
  div.innerHTML = text;

  chatBox.appendChild(div);

  // auto scroll
  chatBox.scrollTop = chatBox.scrollHeight;

  return div;
}