import { useEffect, useState } from "react";

export default function Chat({ token, sessionId, setActiveSession }) {
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");

  // 🔹 Load history when session changes
  useEffect(() => {
    if (sessionId) {
      fetch(`http://localhost:8000/messages/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(r => {
          if (!r.ok) return [];
          return r.json();
        })
        .then(data => {
          if (Array.isArray(data)) {
            setMessages(data);
          } else {
            setMessages([]);
          }
        })
        .catch(() => setMessages([]));
    } else {
      // New chat
      setMessages([]);
    }
  }, [sessionId, token]);

  async function send() {
    if (!msg.trim()) return;

    let activeSid = sessionId;

    // 🔹 Create new session if none selected
    if (!activeSid) {
      const s = await fetch("http://localhost:8000/sessions/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json());

      activeSid = s.session_id;
      setActiveSession(activeSid); // 🔥 IMPORTANT
    }

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        session_id: activeSid,
        message: msg
      })
    }).then(r => r.json());

    setMessages(m => [
      ...m,
      { role: "user", content: msg },
      { role: "assistant", content: res.response || "No response" }
    ]);

    setMsg("");
  }

  return (
    <>
      <div style={{ height: "80vh", overflowY: "auto", border: "1px solid #ccc" }}>
        {messages.map((m, i) => (
          <p key={i}>
            <b>{m.role}:</b> {m.content}
          </p>
        ))}
      </div>

      <input
        value={msg}
        onChange={e => setMsg(e.target.value)}
        placeholder="Type message"
      />
      <button onClick={send}>Send</button>
    </>
  );
}
