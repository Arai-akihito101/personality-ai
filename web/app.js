"use strict";
const el = (id) => document.getElementById(id);
let busy = false;
let loaded = false;

async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  };
  const response = await fetch(path, opts);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "通信エラー");
  return data;
}

function notice(message) {
  el("notice").textContent = message || "";
}

function setStatus(message) {
  el("status").textContent = message;
}

function appendMessage(role, content) {
  const container = document.createElement("div");
  container.className = "message " + (role === "user" ? "user" : "assistant");
  const who = document.createElement("div");
  who.className = "who";
  who.textContent = role === "user" ? "あなた" : "アオ";
  const body = document.createElement("div");
  body.className = "content";
  body.textContent = content;
  container.append(who, body);
  el("conversation").append(container);
  el("conversation").scrollTop = el("conversation").scrollHeight;
  return container;
}

function renderHistory(history) {
  el("conversation").replaceChildren();
  if (!history.length) {
    const intro = document.createElement("div");
    intro.className = "welcome";
    intro.textContent = "やあ。私はアオ。今日は何を話そうか。";
    el("conversation").append(intro);
  }
  history.forEach((m) => {
    if (m.role === "user" || m.role === "assistant") appendMessage(m.role, m.content);
  });
}

function renderMemories(memories) {
  const list = el("memories");
  list.replaceChildren();
  if (!memories.length) {
    const li = document.createElement("li");
    li.textContent = "まだ何も覚えていません";
    list.append(li);
  }
  memories.forEach((item, i) => {
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = item;
    const button = document.createElement("button");
    button.textContent = "×";
    button.title = "記憶を削除";
    button.setAttribute("aria-label", "記憶を削除: " + item);
    button.addEventListener("click", async () => {
      if (!confirm("この記憶を削除しますか？")) return;
      try {
        const data = await api("/api/forget", {index: i});
        renderMemories(data.memories);
        notice("");
      } catch (e) { notice(e.message); }
    });
    li.append(span, button);
    list.append(li);
  });
}

async function init() {
  try {
    const state = await api("/api/state");
    renderHistory(state.history);
    renderMemories(state.memories);
    el("persona").value = state.persona;
    el("model").textContent = "使用モデル: " + state.model;
    setStatus("会話できます");
    loaded = true;
  } catch (e) {
    setStatus("接続エラー");
    notice(e.message);
  }
}

el("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = el("message").value.trim();
  if (!message || busy || !loaded) return;
  busy = true;
  el("send").disabled = true;
  el("message").disabled = true;
  notice("");
  el("message").value = "";
  const preview = appendMessage("user", message);
  setStatus("考え中...");
  try {
    const data = await api("/api/chat", {message});
    appendMessage("assistant", data.answer);
    setStatus("会話できます");
  } catch (e) {
    preview.remove();
    el("message").value = message;
    setStatus("接続エラー");
    notice(e.message);
  } finally {
    busy = false;
    el("send").disabled = false;
    el("message").disabled = false;
    el("message").focus();
  }
});

el("message").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    el("chat-form").requestSubmit();
  }
});

el("memory-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const data = await api("/api/memory", {item: el("memory").value});
    renderMemories(data.memories);
    el("memory").value = "";
    notice("");
  } catch (err) { notice(err.message); }
});

el("save-persona").addEventListener("click", async () => {
  try {
    await api("/api/persona", {persona: el("persona").value});
    notice("");
    setStatus("性格を保存しました");
  } catch (e) { notice(e.message); }
});

el("reset").addEventListener("click", async () => {
  if (!confirm("会話履歴を消去しますか？ 登録済みの記憶と性格は残ります。")) return;
  try {
    await api("/api/reset", {});
    renderHistory([]);
    notice("");
  } catch (e) { notice(e.message); }
});

init();
