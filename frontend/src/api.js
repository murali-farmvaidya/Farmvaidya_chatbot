const API = "http://localhost:8000";

export function login(email, password) {
  return fetch("http://localhost:8000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  }).then(res => res.json());
}

export const googleLogin = (token) =>
  fetch(`${API}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token })
  }).then(r => r.json());

export const newSession = (token) =>
  fetch(`${API}/sessions/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(r => r.json());

export const sendMsg = (sessionId, message) =>
  fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message })
  }).then(r => r.json());
