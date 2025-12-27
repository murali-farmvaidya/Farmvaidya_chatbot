export default function Profile({ setView }) {
  const token = localStorage.getItem("access_token");

  let email = "Unknown";
  let name = "User";
  let initial = "U";

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      email = payload.email;
      name = email.split("@")[0];
      initial = email[0].toUpperCase();
    } catch {}
  }

  const styles = {
    container: {
      minHeight: "100vh",
      background: "linear-gradient(135deg, #f8fdf9 0%, #ffffff 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "32px"
    },
    card: {
      background: "white",
      borderRadius: "24px",
      boxShadow: "0 8px 32px rgba(76, 175, 80, 0.15)",
      padding: "48px 40px",
      width: "100%",
      maxWidth: "500px",
      border: "2px solid #e8f5e9"
    },
    header: {
      textAlign: "center",
      marginBottom: "40px"
    },
    avatarContainer: {
      display: "flex",
      justifyContent: "center",
      marginBottom: "24px"
    },
    avatar: {
      width: "120px",
      height: "120px",
      borderRadius: "50%",
      background: "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "white",
      fontSize: "48px",
      fontWeight: 700,
      boxShadow: "0 8px 24px rgba(76, 175, 80, 0.4)",
      border: "4px solid white"
    },
    title: {
      fontSize: "28px",
      fontWeight: 700,
      color: "#1b5e20",
      marginBottom: "8px"
    },
    subtitle: {
      fontSize: "14px",
      color: "#81c784",
      textTransform: "uppercase",
      letterSpacing: "1px",
      fontWeight: 600
    },
    infoSection: {
      marginBottom: "32px"
    },
    infoItem: {
      background: "linear-gradient(135deg, #f8fdf9 0%, #f1f8f4 100%)",
      padding: "20px 24px",
      borderRadius: "16px",
      marginBottom: "16px",
      border: "2px solid #e8f5e9",
      transition: "all 0.3s ease"
    },
    label: {
      fontSize: "12px",
      fontWeight: 700,
      color: "#81c784",
      textTransform: "uppercase",
      letterSpacing: "1px",
      marginBottom: "8px"
    },
    value: {
      fontSize: "16px",
      fontWeight: 600,
      color: "#2e7d32"
    },
    buttonContainer: {
      display: "flex",
      gap: "12px",
      marginTop: "32px"
    },
    button: {
      flex: 1,
      padding: "14px",
      background: "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)",
      color: "white",
      border: "none",
      borderRadius: "12px",
      fontSize: "14px",
      fontWeight: 700,
      cursor: "pointer",
      transition: "all 0.3s ease",
      boxShadow: "0 4px 12px rgba(76, 175, 80, 0.3)"
    },
    badge: {
      display: "inline-block",
      background: "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)",
      color: "#2e7d32",
      padding: "6px 14px",
      borderRadius: "20px",
      fontSize: "12px",
      fontWeight: 700,
      marginTop: "8px",
      border: "1px solid #a5d6a7"
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.avatarContainer}>
            <div style={styles.avatar}>{initial}</div>
          </div>
          <h3 style={styles.title}>{name}</h3>
          <p style={styles.subtitle}>User Profile</p>
        </div>

        <div style={styles.infoSection}>
          <div 
            style={styles.infoItem}
            onMouseEnter={e => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.2)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div style={styles.label}>Full Name</div>
            <div style={styles.value}>{name}</div>
            <div style={styles.badge}>✓ Verified</div>
          </div>

          <div 
            style={styles.infoItem}
            onMouseEnter={e => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.2)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div style={styles.label}>Email Address</div>
            <div style={styles.value}>{email}</div>
          </div>

          <div 
            style={styles.infoItem}
            onMouseEnter={e => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.2)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div style={styles.label}>Account Type</div>
            <div style={styles.value}>Premium Farmer 🌾</div>
          </div>
        </div>

        <div style={styles.buttonContainer}>
          <button 
            style={styles.button}
            onClick={() => setView("chat")}
            onMouseEnter={e => {
              e.target.style.transform = "translateY(-2px)";
              e.target.style.boxShadow = "0 6px 20px rgba(76, 175, 80, 0.4)";
            }}
            onMouseLeave={e => {
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.3)";
            }}
          >
            ⬅ Back to Chat
          </button>
        </div>
      </div>
    </div>
  );
}