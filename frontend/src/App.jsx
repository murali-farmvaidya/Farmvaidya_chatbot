import { useState, useEffect } from "react";
import Login from "./Login";
import Chat from "./Chat";

export default function App() {
  const [token, setToken] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [refreshSessions, setRefreshSessions] = useState(0);

  useEffect(() => {
    const savedToken = localStorage.getItem("access_token");
    const lastSession = localStorage.getItem("active_session");

    if (savedToken) setToken(savedToken);
    if (lastSession) setActiveSession(lastSession);
  }, []);

  useEffect(() => {
    if (activeSession) {
      localStorage.setItem("active_session", activeSession);
    }
  }, [activeSession]);

  const handleLoginSuccess = (token) => {
    localStorage.setItem("access_token", token);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("active_session");
    setToken(null);
    setActiveSession(null);
  };

  if (!token) return <Login onLoginSuccess={handleLoginSuccess} />;

  return (
    <Chat
      token={token}
      sessionId={activeSession}
      setActiveSession={setActiveSession}
      onMessageSent={() => setRefreshSessions(x => x + 1)}
      refreshSessions={refreshSessions}
      onLogout={handleLogout}
    />
  );
}