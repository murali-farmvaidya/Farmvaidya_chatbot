import { useEffect, useState } from "react";

export default function Chat({ token, sessionId, setActiveSession, onMessageSent }) {
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);

  // 🔹 Load history when session changes
  useEffect(() => {
    if (sessionId && sessionId !== "NEW") {
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
    } else if (sessionId === "NEW") {
      // New chat
      setMessages([]);
    }
  }, [sessionId, token]);

  async function send() {
    if (!msg.trim() || sending) return;

    setSending(true);

    try {
      let activeSid = sessionId;

      if (!activeSid || activeSid === "NEW") {
        const s = await fetch("http://localhost:8000/sessions/", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.json());

        activeSid = s.session_id;
        setActiveSession(activeSid);
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

      await fetch(`http://localhost:8000/messages/${activeSid}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(setMessages);

      onMessageSent();

      setMsg("");
    } finally {
      setSending(false);
    }
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
      <button onClick={send} disabled={sending}>
        {sending ? "Sending..." : "Send"}
      </button>
    </>
  );
}
