import { useState, useEffect } from "react";
import Login from "./Login";
import Chat from "./Chat";
import Sidebar from "./Sidebar";
import Profile from "./Profile";

export default function App() {
  const [token, setToken] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [view, setView] = useState("chat"); // chat | profile

  useEffect(() => {
    const saved = localStorage.getItem("access_token");
    if (saved) setToken(saved);
  }, []);

  const handleLoginSuccess = (token) => {
    localStorage.setItem("access_token", token);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setActiveSession(null);
  };

  if (!token) return <Login onLoginSuccess={handleLoginSuccess} />;

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar
        token={token}
        activeSession={activeSession}
        setActiveSession={setActiveSession}
        onNewChat={() => {
          setActiveSession(null);
          setView("chat");
        }}
        onProfile={() => setView("profile")}
        onLogout={handleLogout}
      />

      <div style={{ flex: 1, padding: 10 }}>
        {view === "profile" ? (
          <Profile setView={setView} />
        ) : (
          <Chat
            token={token}
            sessionId={activeSession}
            setActiveSession={setActiveSession}
          />
        )}
      </div>
    </div>
  );
}
