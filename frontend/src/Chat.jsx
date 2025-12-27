import { useEffect, useState, useRef } from "react";
import { speechToText } from "./stt";

export default function Chat({ token, sessionId, setActiveSession, onMessageSent, refreshSessions, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [recording, setRecording] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [userName, setUserName] = useState("User");
  const [userEmail, setUserEmail] = useState("");
  const [latency, setLatency] = useState(null);
  const [revealingText, setRevealingText] = useState("");
  const [fullBotResponse, setFullBotResponse] = useState("");
  const [openMenuId, setOpenMenuId] = useState(null);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const messagesAreaRef = useRef(null);

  useEffect(() => {
    if (isAutoScrollEnabled && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, sending, revealingText, isAutoScrollEnabled]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!messagesAreaRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesAreaRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 100;
    setIsAutoScrollEnabled(isAtBottom);
  };

  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUserEmail(payload.email || "");
        setUserName(payload.email ? payload.email.split("@")[0] : "User");
      } catch {}
    }
  }, [token]);

  useEffect(() => {
    if (sessionId && sessionId !== "NEW") {
      fetch(`${import.meta.env.VITE_BACKEND_URL}/messages/${sessionId}`, {
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
      setMessages([]);
    }
  }, [sessionId, token]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/sessions/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(setSessions);
  }, [token, refreshSessions]);

  // Revealing text effect
  useEffect(() => {
    if (fullBotResponse && revealingText.length < fullBotResponse.length) {
      const timer = setTimeout(() => {
        setRevealingText(fullBotResponse.slice(0, revealingText.length + 1));
      }, 10);
      return () => clearTimeout(timer);
    }
  }, [revealingText, fullBotResponse]);

  // Format text with bold headers
  const formatText = (text) => {
    if (!text) return "";
    
    // Split by lines
    const lines = text.split('\n');
    const formatted = lines.map((line, idx) => {
      // Check if line contains bold markers ** or is a numbered point
      if (line.includes('**')) {
        // Replace **text** with <strong>text</strong>
        const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return `<div key="${idx}" style="margin-bottom: 8px;">${boldFormatted}</div>`;
      } else if (/^\d+\./.test(line.trim())) {
        // Numbered list item
        return `<div key="${idx}" style="margin-bottom: 8px; padding-left: 20px;">${line}</div>`;
      } else if (line.trim() === '') {
        return `<div key="${idx}" style="height: 8px;"></div>`;
      }
      return `<div key="${idx}" style="margin-bottom: 8px;">${line}</div>`;
    });
    
    return formatted.join('');
  };

  async function send() {
    if (!msg.trim() || sending) return;

    const userMessage = msg.trim();
    setMsg(""); // Clear input immediately
    
    // Add user message to display immediately
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    
    setSending(true);
    setLatency("0.00"); // Show latency immediately
    setRevealingText("");
    setFullBotResponse("");
    setIsAutoScrollEnabled(true);
    
    const startTime = Date.now();
    const latencyInterval = setInterval(() => {
      setLatency(((Date.now() - startTime) / 1000).toFixed(2));
    }, 100);

    try {
      let activeSid = sessionId;

      if (!activeSid || activeSid === "NEW") {
        const s = await fetch(`${import.meta.env.VITE_BACKEND_URL}/sessions/`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.json());

        activeSid = s.session_id;
        setActiveSession(activeSid);
      }

      await fetch(`${import.meta.env.VITE_BACKEND_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: activeSid,
          message: userMessage
        })
      });

      clearInterval(latencyInterval);
      const endTime = Date.now();
      setLatency(((endTime - startTime) / 1000).toFixed(2));

      const newMessages = await fetch(`${import.meta.env.VITE_BACKEND_URL}/messages/${activeSid}`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json());

      setMessages(newMessages);
      
      const lastBotMsg = newMessages.filter(m => m.role === "assistant").pop();
      if (lastBotMsg) {
        setFullBotResponse(lastBotMsg.content);
        setRevealingText("");
      }

      onMessageSent();
    } catch (error) {
      clearInterval(latencyInterval);
      setLatency(null);
    } finally {
      setSending(false);
    }
  }

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);

    chunksRef.current = [];
    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      if (audioBlob.size === 0) return;

      try {
        const text = await speechToText(audioBlob);
        if (text) {
          setMsg(text);
        }
      } catch (e) {
        console.error("STT failed:", e);
      }
      
      // Stop all audio tracks
      stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();
    setRecording(true);
  }

  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
  }

  async function deleteSession(id) {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/sessions/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });
    setSessions(s => s.filter(x => x.id !== id));
    setOpenMenuId(null);
    if (id === sessionId) {
      setActiveSession("NEW");
    }
  }

  const styles = {
    container: {
      display: "flex",
      height: "100vh",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
      background: "#f5f7f5"
    },
    sidebar: {
      width: showSidebar ? "280px" : "0",
      background: "white",
      borderRight: "1px solid #e0e0e0",
      display: "flex",
      flexDirection: "column",
      transition: "width 0.3s ease",
      overflow: "hidden"
    },
    sidebarHeader: {
      padding: "16px",
      borderBottom: "1px solid #e0e0e0",
      display: "flex",
      flexDirection: "column",
      gap: "8px"
    },
    newChatButton: {
      padding: "12px 16px",
      background: "white",
      border: "1px solid #e0e0e0",
      borderRadius: "8px",
      fontSize: "14px",
      fontWeight: 600,
      color: "#333",
      cursor: "pointer",
      transition: "all 0.2s ease",
      display: "flex",
      alignItems: "center",
      gap: "8px"
    },
    sessionsList: {
      flex: 1,
      overflowY: "auto",
      padding: "12px"
    },
    sessionItem: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px",
      borderRadius: "8px",
      marginBottom: "4px",
      cursor: "pointer",
      transition: "background 0.2s ease",
      background: "white",
      position: "relative"
    },
    sessionItemActive: {
      background: "#f0f0f0"
    },
    sessionText: {
      fontSize: "14px",
      color: "#333",
      flex: 1,
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis"
    },
    deleteButton: {
      background: "none",
      border: "none",
      color: "#666",
      cursor: "pointer",
      fontSize: "16px",
      padding: "4px 8px",
      borderRadius: "4px",
      transition: "all 0.2s ease"
    },
    sidebarFooter: {
      padding: "16px",
      borderTop: "1px solid #e0e0e0",
      display: "flex",
      flexDirection: "column",
      gap: "8px"
    },
    profileButton: {
      padding: "12px 16px",
      background: "white",
      border: "1px solid #e0e0e0",
      borderRadius: "8px",
      fontSize: "14px",
      fontWeight: 600,
      color: "#333",
      cursor: "pointer",
      transition: "all 0.2s ease",
      display: "flex",
      alignItems: "center",
      gap: "8px"
    },
    mainContent: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
      background: "#f5f7f5"
    },
    header: {
      background: "white",
      padding: "16px 24px",
      borderBottom: "1px solid #e0e0e0",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    },
    headerLeft: {
      display: "flex",
      alignItems: "center",
      gap: "16px"
    },
    menuIcon: {
      fontSize: "24px",
      cursor: "pointer",
      color: "#333"
    },
    messagesArea: {
      flex: 1,
      overflowY: "auto",
      padding: "32px 24px",
      background: "#f5f7f5"
    },
    welcomeContainer: {
      maxWidth: "900px",
      margin: "0 auto",
      textAlign: "left"
    },
    welcomeTitle: {
      fontSize: "48px",
      fontWeight: 700,
      color: "#1a1a1a",
      marginBottom: "16px",
      lineHeight: 1.2
    },
    welcomeSubtitle: {
      fontSize: "32px",
      fontWeight: 400,
      color: "#1a1a1a",
      marginBottom: "40px"
    },
    highlight: {
      color: "#00a67e"
    },
    suggestionChips: {
      display: "flex",
      gap: "12px",
      flexWrap: "wrap",
      marginTop: "32px"
    },
    chip: {
      padding: "12px 20px",
      background: "white",
      border: "1px solid #e0e0e0",
      borderRadius: "20px",
      fontSize: "14px",
      color: "#333",
      cursor: "pointer",
      transition: "all 0.2s ease"
    },
    messagesList: {
      maxWidth: "900px",
      margin: "0 auto"
    },
    messageBlock: {
      marginBottom: "32px"
    },
    userMessage: {
      display: "flex",
      justifyContent: "flex-end",
      marginBottom: "16px"
    },
    userBubble: {
      background: "#e8f5f1",
      padding: "14px 20px",
      borderRadius: "20px 20px 4px 20px",
      maxWidth: "70%",
      fontSize: "15px",
      color: "#1a1a1a",
      lineHeight: 1.5
    },
    botMessage: {
      marginBottom: "16px"
    },
    botText: {
      fontSize: "15px",
      color: "#1a1a1a",
      lineHeight: 1.7,
      marginBottom: "12px",
      whiteSpace: "pre-wrap"
    },
    thinkingIndicator: {
      display: "flex",
      alignItems: "center",
      gap: "12px",
      fontSize: "14px",
      color: "#666",
      marginBottom: "8px"
    },
    latencyBadge: {
      display: "inline-flex",
      alignItems: "center",
      gap: "6px",
      background: "#e8f5f1",
      color: "#00a67e",
      padding: "6px 14px",
      borderRadius: "12px",
      fontSize: "13px",
      fontWeight: 600,
      marginTop: "8px"
    },
    inputContainer: {
      padding: "20px 24px",
      background: "#f5f7f5",
      borderTop: "1px solid #e0e0e0"
    },
    inputWrapper: {
      maxWidth: "900px",
      margin: "0 auto",
      display: "flex",
      gap: "12px",
      alignItems: "flex-end"
    },
    inputBox: {
      flex: 1,
      display: "flex",
      alignItems: "flex-end",
      background: "white",
      borderRadius: "24px",
      border: "1px solid #e0e0e0",
      padding: "4px 4px 4px 20px",
      transition: "border 0.2s ease"
    },
    input: {
      flex: 1,
      border: "none",
      outline: "none",
      fontSize: "15px",
      padding: "12px 0",
      background: "transparent",
      color: "#333",
      resize: "none",
      minHeight: "24px",
      maxHeight: "120px"
    },
    micButton: {
      width: "40px",
      height: "40px",
      borderRadius: "50%",
      background: recording ? "#ef5350" : "transparent",
      border: "none",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: "pointer",
      fontSize: "20px",
      color: recording ? "white" : "#666",
      flexShrink: 0,
      transition: "all 0.2s ease",
      position: "relative"
    },
    recordingAnimation: {
      position: "absolute",
      width: "100%",
      height: "100%",
      borderRadius: "50%",
      border: "2px solid #ef5350",
      animation: "pulse-ring 1.5s ease-out infinite"
    },
    profileSidebar: {
      position: "fixed",
      right: 0,
      top: 0,
      width: "400px",
      height: "100vh",
      background: "white",
      boxShadow: "-2px 0 8px rgba(0,0,0,0.1)",
      transform: showProfile ? "translateX(0)" : "translateX(100%)",
      transition: "transform 0.3s ease",
      zIndex: 1001,
      display: "flex",
      flexDirection: "column"
    },
    profileHeader: {
      padding: "24px",
      borderBottom: "1px solid #e0e0e0",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center"
    },
    profileTitle: {
      fontSize: "18px",
      fontWeight: 700,
      color: "#333"
    },
    closeIcon: {
      fontSize: "24px",
      cursor: "pointer",
      color: "#666"
    },
    profileContent: {
      flex: 1,
      padding: "24px",
      display: "flex",
      flexDirection: "column"
    },
    profileAvatar: {
      width: "80px",
      height: "80px",
      borderRadius: "50%",
      margin: "0 auto 24px",
      background: "#ddd",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "32px",
      fontWeight: 700,
      color: "#666"
    },
    profileInfo: {
      marginBottom: "24px",
      flex: 1
    },
    profileLabel: {
      fontSize: "12px",
      color: "#666",
      fontWeight: 600,
      marginBottom: "8px"
    },
    profileValue: {
      fontSize: "15px",
      color: "#333",
      padding: "12px 16px",
      background: "#f5f5f5",
      borderRadius: "8px",
      marginBottom: "16px"
    },
    logoutButton: {
      width: "100%",
      padding: "14px",
      background: "#ef5350",
      border: "none",
      borderRadius: "8px",
      fontSize: "15px",
      fontWeight: 700,
      color: "white",
      cursor: "pointer",
      transition: "all 0.2s ease"
    }
  };

  return (
    <>
      <div style={styles.container}>
        {/* Sidebar */}
        <div style={styles.sidebar}>
          <div style={styles.sidebarHeader}>
            <button
              style={styles.newChatButton}
              onClick={() => {
                setActiveSession("NEW");
                setMessages([]);
              }}
              onMouseEnter={e => e.target.style.background = "#f0f0f0"}
              onMouseLeave={e => e.target.style.background = "white"}
            >
              ✏️ New Chat
            </button>
          </div>
          
          <div style={styles.sessionsList}>
            {sessions.map(s => (
              <div
                key={s.id}
                style={{
                  ...styles.sessionItem,
                  ...(s.id === sessionId ? styles.sessionItemActive : {})
                }}
                onClick={() => setActiveSession(s.id)}
                onMouseEnter={e => {
                  if (s.id !== sessionId) e.currentTarget.style.background = "#f5f5f5";
                }}
                onMouseLeave={e => {
                  if (s.id !== sessionId) e.currentTarget.style.background = "white";
                }}
              >
                <div style={styles.sessionText}>{s.title || "Chat"}</div>
                <button
                  style={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    if(window.confirm("Delete this chat?")) deleteSession(s.id);
                  }}
                  onMouseEnter={e => {
                    e.target.style.background = "#ffebee";
                    e.target.style.color = "#ef5350";
                  }}
                  onMouseLeave={e => {
                    e.target.style.background = "none";
                    e.target.style.color = "#666";
                  }}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>

          <div style={styles.sidebarFooter}>
            <button
              style={styles.profileButton}
              onClick={() => setShowProfile(true)}
              onMouseEnter={e => e.target.style.background = "#f0f0f0"}
              onMouseLeave={e => e.target.style.background = "white"}
            >
              <div style={{width: "24px", height: "24px", borderRadius: "50%", background: "#ddd", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "12px", fontWeight: 700}}>
                {userName[0]?.toUpperCase()}
              </div>
              {userName}
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div style={styles.mainContent}>
          {/* Header */}
          <div style={styles.header}>
            <div style={styles.headerLeft}>
              <div style={styles.menuIcon} onClick={() => setShowSidebar(!showSidebar)}>☰</div>
              <div style={{fontSize: "20px", fontWeight: 700, color: "#00916e"}}>farm vaidya</div>
            </div>
          </div>

          {/* Messages Area */}
          <div 
            style={styles.messagesArea} 
            ref={messagesAreaRef}
            onScroll={handleScroll}
          >
            {messages.length === 0 && !sending ? (
              <div style={styles.welcomeContainer}>
                <h1 style={styles.welcomeTitle}>
                  Hi {userName}, <span style={styles.highlight}>Bhuvi</span>, here!!
                </h1>
                <h2 style={styles.welcomeSubtitle}>
                  How can I assist you on your farming journey today?
                </h2>
                <div style={styles.suggestionChips}>
                  <div
                    style={styles.chip}
                    onClick={() => {
                      setMsg("Coconut Fertilizers");
                      setTimeout(send, 100);
                    }}
                    onMouseEnter={e => e.target.style.background = "#f0f0f0"}
                    onMouseLeave={e => e.target.style.background = "white"}
                  >
                    Coconut Fertilizers
                  </div>
                  <div
                    style={styles.chip}
                    onClick={() => {
                      setMsg("Rhinoceros beetle Management");
                      setTimeout(send, 100);
                    }}
                    onMouseEnter={e => e.target.style.background = "#f0f0f0"}
                    onMouseLeave={e => e.target.style.background = "white"}
                  >
                    Rhinoceros beetle Management
                  </div>
                  <div
                    style={styles.chip}
                    onClick={() => {
                      setMsg("Nut Drop Control");
                      setTimeout(send, 100);
                    }}
                    onMouseEnter={e => e.target.style.background = "#f0f0f0"}
                    onMouseLeave={e => e.target.style.background = "white"}
                  >
                    Nut Drop Control
                  </div>
                </div>
              </div>
            ) : (
              <div style={styles.messagesList}>
                {messages.map((m, i) => {
                  const isLastBotMessage = i === messages.length - 1 && m.role === "assistant" && fullBotResponse;
                  
                  return (
                    <div key={i} style={styles.messageBlock}>
                      {m.role === "user" ? (
                        <div style={styles.userMessage}>
                          <div style={styles.userBubble}>{m.content}</div>
                        </div>
                      ) : (
                        <div style={styles.botMessage}>
                          <div 
                            style={styles.botText}
                            dangerouslySetInnerHTML={{
                              __html: formatText(isLastBotMessage ? revealingText : m.content)
                            }}
                          />
                        </div>
                      )}
                    </div>
                  );
                })}

                {sending && (
                  <>
                    <div style={styles.thinkingIndicator}>
                      <div style={{animation: "pulse 1.5s ease-in-out infinite"}}>●</div>
                      <div>Thinking...</div>
                    </div>
                    {latency && (
                      <div style={styles.latencyBadge}>
                        <span style={{animation: "pulse 1s ease-in-out infinite"}}>⚡</span>
                        {latency}s
                      </div>
                    )}
                  </>
                )}
                
                {!sending && latency && messages.length > 0 && (
                  <div style={styles.latencyBadge}>
                    ⚡ Responded in {latency}s
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Container */}
          <div style={styles.inputContainer}>
            <div style={styles.inputWrapper}>
              <div style={styles.inputBox}>
                <textarea
                  style={styles.input}
                  value={msg}
                  onChange={e => setMsg(e.target.value)}
                  onKeyPress={e => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send();
                    }
                  }}
                  placeholder="Message Bhuvi"
                  rows={1}
                />
                <button
                  style={styles.micButton}
                  onClick={recording ? stopRecording : startRecording}
                  onMouseEnter={e => !recording && (e.target.style.background = "#f0f0f0")}
                  onMouseLeave={e => !recording && (e.target.style.background = "transparent")}
                >
                  {recording && <div style={styles.recordingAnimation}></div>}
                  {recording && <div style={{...styles.recordingAnimation, animationDelay: "0.5s"}}></div>}
                  🎤
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Sidebar */}
        <div style={styles.profileSidebar}>
          <div style={styles.profileHeader}>
            <div style={styles.profileTitle}>Profile</div>
            <div style={styles.closeIcon} onClick={() => setShowProfile(false)}>✕</div>
          </div>
          <div style={styles.profileContent}>
            <div style={styles.profileAvatar}>
              {userName[0]?.toUpperCase()}
            </div>

            <div style={styles.profileInfo}>
              <div style={styles.profileLabel}>Username</div>
              <div style={styles.profileValue}>{userName}</div>

              <div style={styles.profileLabel}>Email</div>
              <div style={styles.profileValue}>{userEmail}</div>
            </div>

            <button 
              style={styles.logoutButton} 
              onClick={onLogout}
              onMouseEnter={e => e.target.style.background = "#e53935"}
              onMouseLeave={e => e.target.style.background = "#ef5350"}
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
          }
          
          @keyframes pulse-ring {
            0% {
              transform: scale(1);
              opacity: 1;
            }
            100% {
              transform: scale(1.5);
              opacity: 0;
            }
          }
          
          strong {
            font-weight: 700;
            color: #1a1a1a;
          }
        `}
      </style>
    </>
  );
}