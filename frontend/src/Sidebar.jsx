import { useEffect, useState } from "react";

export default function Sidebar({
  token,
  activeSession,
  setActiveSession,
  refreshSessions,
  onNewChat,
  onProfile,
  onLogout
}) {
  const [sessions, setSessions] = useState([]);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/sessions/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(setSessions);
  }, [token, refreshSessions]);

  async function deleteSession(id) {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/sessions/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });
    setSessions(s => s.filter(x => x.id !== id));
    setOpenMenuId(null);
  }

  const styles = {
    container: {
      position: "relative",
      display: "flex"
    },
    sidebar: {
      width: isCollapsed ? "0" : "280px",
      background: "linear-gradient(180deg, #1b5e20 0%, #2e7d32 100%)",
      padding: isCollapsed ? "0" : "24px 16px",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
      boxShadow: "2px 0 12px rgba(0, 0, 0, 0.1)",
      overflowY: "auto",
      overflowX: "hidden",
      transition: "all 0.3s ease"
    },
    toggleButton: {
      position: "absolute",
      top: "20px",
      left: isCollapsed ? "10px" : "290px",
      background: "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)",
      border: "none",
      borderRadius: "50%",
      width: "36px",
      height: "36px",
      color: "white",
      fontSize: "18px",
      cursor: "pointer",
      boxShadow: "0 2px 8px rgba(0, 0, 0, 0.2)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transition: "all 0.3s ease",
      zIndex: 10
    },
    button: {
      padding: "12px 18px",
      background: "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)",
      color: "white",
      border: "none",
      borderRadius: "12px",
      fontSize: "14px",
      fontWeight: 600,
      cursor: "pointer",
      transition: "all 0.3s ease",
      boxShadow: "0 2px 8px rgba(0, 0, 0, 0.2)",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      justifyContent: "center",
      opacity: isCollapsed ? 0 : 1,
      pointerEvents: isCollapsed ? "none" : "auto"
    },
    logoutButton: {
      padding: "12px 18px",
      background: "linear-gradient(135deg, #ef5350 0%, #e53935 100%)",
      color: "white",
      border: "none",
      borderRadius: "12px",
      fontSize: "14px",
      fontWeight: 600,
      cursor: "pointer",
      transition: "all 0.3s ease",
      boxShadow: "0 2px 8px rgba(0, 0, 0, 0.2)",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      justifyContent: "center",
      opacity: isCollapsed ? 0 : 1,
      pointerEvents: isCollapsed ? "none" : "auto"
    },
    divider: {
      height: "2px",
      background: "linear-gradient(90deg, transparent 0%, #4caf50 50%, transparent 100%)",
      margin: "8px 0",
      opacity: isCollapsed ? 0 : 0.5
    },
    sessionsList: {
      display: "flex",
      flexDirection: "column",
      gap: "8px",
      marginTop: "12px",
      flex: 1,
      overflowY: "auto",
      opacity: isCollapsed ? 0 : 1
    },
    sessionItem: {
      display: "flex",
      alignItems: "center",
      gap: "8px",
      padding: "10px 14px",
      background: "rgba(255, 255, 255, 0.1)",
      borderRadius: "10px",
      transition: "all 0.3s ease",
      border: "1px solid rgba(255, 255, 255, 0.2)",
      position: "relative"
    },
    activeSessionItem: {
      background: "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)",
      border: "1px solid rgba(255, 255, 255, 0.5)",
      boxShadow: "0 2px 8px rgba(102, 187, 106, 0.4)"
    },
    sessionButton: {
      flex: 1,
      background: "none",
      border: "none",
      color: "white",
      fontSize: "14px",
      fontWeight: 500,
      cursor: "pointer",
      textAlign: "left",
      padding: "4px 0",
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis"
    },
    menuButton: {
      background: "none",
      border: "none",
      color: "white",
      width: "28px",
      height: "28px",
      cursor: "pointer",
      fontSize: "16px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transition: "all 0.2s ease",
      borderRadius: "6px"
    },
    dropdownMenu: {
      position: "absolute",
      top: "100%",
      right: "0",
      marginTop: "4px",
      background: "white",
      borderRadius: "8px",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
      zIndex: 100,
      minWidth: "120px",
      overflow: "hidden"
    },
    menuItem: {
      padding: "10px 16px",
      background: "white",
      border: "none",
      width: "100%",
      textAlign: "left",
      cursor: "pointer",
      fontSize: "14px",
      color: "#333",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      transition: "all 0.2s ease"
    },
    sessionsTitle: {
      color: "#c8e6c9",
      fontSize: "12px",
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: "1px",
      marginTop: "16px",
      marginBottom: "8px",
      opacity: isCollapsed ? 0 : 1
    }
  };

  return (
    <div style={styles.container}>
      <button 
        style={styles.toggleButton}
        onClick={() => setIsCollapsed(!isCollapsed)}
        onMouseEnter={e => e.target.style.transform = "scale(1.1)"}
        onMouseLeave={e => e.target.style.transform = "scale(1)"}
        title={isCollapsed ? "Show Sidebar" : "Hide Sidebar"}
      >
        {isCollapsed ? "☰" : "◀"}
      </button>

      <div style={styles.sidebar}>
        <button 
          style={styles.button}
          onClick={onNewChat}
          onMouseEnter={e => e.target.style.transform = "translateY(-2px)"}
          onMouseLeave={e => e.target.style.transform = "translateY(0)"}
        >
          ➕ New Chat
        </button>
        
        <button 
          style={styles.button}
          onClick={onProfile}
          onMouseEnter={e => e.target.style.transform = "translateY(-2px)"}
          onMouseLeave={e => e.target.style.transform = "translateY(0)"}
        >
          👤 Profile
        </button>
        
        <button 
          style={styles.logoutButton}
          onClick={onLogout}
          onMouseEnter={e => e.target.style.transform = "translateY(-2px)"}
          onMouseLeave={e => e.target.style.transform = "translateY(0)"}
        >
          🚪 Logout
        </button>

        <div style={styles.divider}></div>

        <div style={styles.sessionsTitle}>Chat History</div>

        <div style={styles.sessionsList}>
          {sessions.map(s => (
            <div 
              key={s.id} 
              style={{
                ...styles.sessionItem,
                ...(s.id === activeSession ? styles.activeSessionItem : {})
              }}
              onMouseEnter={e => {
                if (s.id !== activeSession) {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.15)";
                }
              }}
              onMouseLeave={e => {
                if (s.id !== activeSession) {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
                }
              }}
            >
              <button
                style={styles.sessionButton}
                onClick={() => setActiveSession(s.id)}
              >
                {s.title || "Chat"}
              </button>
              <button 
                style={styles.menuButton}
                onClick={() => setOpenMenuId(openMenuId === s.id ? null : s.id)}
                onMouseEnter={e => {
                  e.target.style.background = "rgba(255, 255, 255, 0.2)";
                }}
                onMouseLeave={e => {
                  e.target.style.background = "none";
                }}
              >
                ⋮
              </button>
              
              {openMenuId === s.id && (
                <div style={styles.dropdownMenu}>
                  <button 
                    style={styles.menuItem}
                    onClick={() => deleteSession(s.id)}
                    onMouseEnter={e => {
                      e.target.style.background = "#ffebee";
                      e.target.style.color = "#c62828";
                    }}
                    onMouseLeave={e => {
                      e.target.style.background = "white";
                      e.target.style.color = "#333";
                    }}
                  >
                    🗑️ Delete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        <style>
          {`
            div[style*="overflowY"]::-webkit-scrollbar {
              width: 6px;
            }
            div[style*="overflowY"]::-webkit-scrollbar-track {
              background: rgba(255, 255, 255, 0.1);
              border-radius: 3px;
            }
            div[style*="overflowY"]::-webkit-scrollbar-thumb {
              background: rgba(255, 255, 255, 0.3);
              border-radius: 3px;
            }
            div[style*="overflowY"]::-webkit-scrollbar-thumb:hover {
              background: rgba(255, 255, 255, 0.5);
            }
          `}
        </style>
      </div>
    </div>
  );
}