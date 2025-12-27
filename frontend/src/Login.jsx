import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { login, googleLogin } from "./api";

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogin() {
    setError("");
    setIsLoading(true);
    
    try {
      let res;

      if (isSignup) {
        res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name })
        }).then(r => r.json());
      } else {
        res = await login(email, password);
      }

      if (!res.access_token) {
        setError(isSignup ? "Signup failed" : "Invalid credentials");
        return;
      }

      localStorage.setItem("access_token", res.access_token);
      onLoginSuccess(res.access_token);
    } catch (e) {
      setError(isSignup ? "Signup failed" : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleGoogleLogin(token) {
    setIsLoading(true);
    try {
      const res = await googleLogin(token);

      if (!res.access_token) {
        setError("Google login failed");
        return;
      }
      localStorage.setItem("access_token", res.access_token);
      onLoginSuccess(res.access_token);
    } catch (e) {
      setError("Google login failed");
    } finally {
      setIsLoading(false);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div style={styles.container}>
      {/* Left Side - Form */}
      <div style={styles.leftPanel}>
        <div style={styles.formContainer}>
          {/* Logo */}
          <div style={styles.logoContainer}>
            <img 
              src="/logo.png" 
              alt="FarmVaidya Logo" 
              style={styles.logoImage}
            />
            
          </div>

          {/* Title */}
          <h1 style={styles.title}>
            {isSignup ? "Signup" : "Login"} to Cultivate<br />Success
          </h1>

          {/* Form */}
          <div style={styles.formFields}>
            {isSignup ? (
              <>
                {/* Signup Form */}
                <div style={styles.inputWrapper}>
                  <svg style={styles.inputIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Name"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={styles.input}
                  />
                </div>

                <div style={styles.inputWrapper}>
                  <svg style={styles.inputIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={styles.input}
                  />
                </div>

                <div style={styles.inputWrapperSimple}>
                  <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={styles.inputSimple}
                  />
                </div>
              </>
            ) : (
              <>
                {/* Login Form */}
                <div>
                  <label style={styles.label}>Email</label>
                  <input
                    type="text"
                    placeholder="Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={styles.inputSimple}
                  />
                </div>

                <div style={styles.inputWrapperSimple}>
                  <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={styles.inputSimple}
                  />
                </div>
              </>
            )}

            {/* Error Message */}
            {error && (
              <div style={styles.errorBox}>
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleLogin}
              disabled={isLoading}
              style={{...styles.submitButton, ...(isLoading ? styles.submitButtonDisabled : {})}}
            >
              {isLoading ? (
                <div style={styles.loadingContainer}>
                  <div style={styles.spinner}></div>
                  <span>Processing...</span>
                </div>
              ) : (
                <span>{isSignup ? "Signup" : "Login"}</span>
              )}
            </button>

            {/* Google Login */}
            <div style={styles.googleContainer}>
              <GoogleLogin
                onSuccess={async (cred) => {
                  const token = cred?.credential;
                  if (!token) {
                    setError("Google token missing");
                    return;
                  }
                  await handleGoogleLogin(token);
                }}
                onError={() => setError("Google Login Failed")}
                theme="outline"
                size="large"
                width="100%"
                text={isSignup ? "signup_with" : "signin_with"}
              />
            </div>

            {/* Toggle Login/Signup */}
            <div style={styles.toggleContainer}>
              <button
                onClick={() => {
                  setIsSignup(!isSignup);
                  setError("");
                  setEmail("");
                  setPassword("");
                  setName("");
                }}
                style={styles.toggleButton}
              >
                {isSignup ? "Already have an account? Login" : "Don't have an account? Signup"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Background Image with Voice Agent */}
      <div style={styles.rightPanel}>
        {/* Background Image */}
        <img 
          src="/login.png" 
          alt="Coconut Farm with Farmer" 
          style={styles.backgroundImage}
        />
        
        {/* Voice Agent Chat Bubbles */}
        <div style={styles.chatContainer}>
          {/* User Message Bubble */}
          <div style={{...styles.chatBubble, ...styles.chatBubbleAnimate}}>
            <p style={styles.chatText}>Coconut fertilizer schedule</p>
          </div>
          
          {/* AI Response Bubble */}
          <div style={{...styles.responseBubble, ...styles.responseBubbleAnimate}}>
            <div style={styles.avatarCircle}>
              <svg style={styles.avatarIcon} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
              </svg>
            </div>
            <div style={styles.responseContent}>
              <div style={styles.waveContainer}>
                <div style={{...styles.waveBar, animationDelay: '0s'}}></div>
                <div style={{...styles.waveBar, animationDelay: '0.2s'}}></div>
                <div style={{...styles.waveBar, animationDelay: '0.4s'}}></div>
                <div style={{...styles.waveBar, animationDelay: '0.6s'}}></div>
              </div>
              <p style={styles.responseText}>Generating response....</p>
            </div>
          </div>
        </div>

        <style>{`
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes wave {
            0%, 100% {
              transform: scaleY(1);
            }
            50% {
              transform: scaleY(1.5);
            }
          }

          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  leftPanel: {
    width: '100%',
    maxWidth: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    backgroundColor: 'white',
  },
  formContainer: {
    width: '100%',
    maxWidth: '450px',
  },
  logoContainer: {
    marginBottom: '40px',
  },
  logoImage: {
    height: '60px',
    marginBottom: '12px',
  },
  tagline: {
    fontSize: '14px',
    color: '#6B7280',
    margin: 0,
  },
  title: {
    fontSize: '40px',
    fontWeight: 'bold',
    marginBottom: '40px',
    lineHeight: '1.2',
    color: '#111827',
  },
  formFields: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  inputWrapper: {
    position: 'relative',
    width: '100%',
  },
  inputWrapperSimple: {
    width: '100%',
  },
  input: {
    width: '100%',
    padding: '14px 14px 14px 48px',
    border: '2px solid #E5E7EB',
    borderRadius: '12px',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  },
  inputSimple: {
    width: '100%',
    padding: '14px',
    border: '2px solid #E5E7EB',
    borderRadius: '12px',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '14px 40px 14px 48px',
    border: '2px solid #E5E7EB',
    borderRadius: '12px',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s',
    backgroundColor: 'white',
    color: '#374151',
    appearance: 'none',
    boxSizing: 'border-box',
    cursor: 'pointer',
  },
  inputIcon: {
    position: 'absolute',
    left: '16px',
    top: '50%',
    transform: 'translateY(-50%)',
    width: '20px',
    height: '20px',
    color: '#9CA3AF',
    pointerEvents: 'none',
  },
  selectArrow: {
    position: 'absolute',
    right: '16px',
    top: '50%',
    transform: 'translateY(-50%)',
    width: '20px',
    height: '20px',
    color: '#9CA3AF',
    pointerEvents: 'none',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
    marginBottom: '8px',
  },
  errorBox: {
    backgroundColor: '#FEF2F2',
    border: '1px solid #FCA5A5',
    color: '#DC2626',
    padding: '12px 16px',
    borderRadius: '12px',
    fontSize: '14px',
  },
  submitButton: {
    width: '100%',
    backgroundColor: '#059669',
    color: 'white',
    padding: '16px',
    borderRadius: '12px',
    fontSize: '16px',
    fontWeight: '600',
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  submitButtonDisabled: {
    backgroundColor: '#9CA3AF',
    cursor: 'not-allowed',
  },
  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  spinner: {
    width: '20px',
    height: '20px',
    border: '3px solid rgba(255,255,255,0.3)',
    borderTop: '3px solid white',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  googleContainer: {
    display: 'flex',
    justifyContent: 'center',
    width: '100%',
  },
  toggleContainer: {
    textAlign: 'center',
    paddingTop: '8px',
  },
  toggleButton: {
    fontSize: '14px',
    color: '#6B7280',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'none',
    transition: 'color 0.2s',
  },
  rightPanel: {
    width: '50%',
    position: 'relative',
    overflow: 'hidden',
  },
  backgroundImage: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'linear-gradient(135deg, #4ADE80 0%, #16A34A 100%)',
  },
  chatContainer: {
    position: 'absolute',
    bottom: '120px',
    right: '48px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    zIndex: 10,
  },
  chatBubble: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '12px 24px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
    maxWidth: '320px',
  },
  chatBubbleAnimate: {
    animation: 'fadeIn 0.5s ease-in',
  },
  chatText: {
    color: '#1F2937',
    fontSize: '14px',
    fontWeight: '500',
    margin: 0,
  },
  responseBubble: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '16px 24px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
    maxWidth: '320px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  responseBubbleAnimate: {
    animation: 'fadeIn 0.5s ease-in 0.3s both',
  },
  avatarCircle: {
    width: '32px',
    height: '32px',
    backgroundColor: '#10B981',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  avatarIcon: {
    width: '16px',
    height: '16px',
    color: 'white',
  },
  responseContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  waveContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  waveBar: {
    width: '4px',
    height: '12px',
    backgroundColor: '#F59E0B',
    borderRadius: '2px',
    animation: 'wave 1s ease-in-out infinite',
  },
  responseText: {
    color: '#6B7280',
    fontSize: '14px',
    margin: 0,
  },
};