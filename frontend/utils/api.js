// ============================================================
//  utils/api.js — All API calls to the Flask backend
// ============================================================

const BASE_URL = "http://localhost:5000/api";

// Get saved token from localStorage
const getToken = () => localStorage.getItem("tb_token");

// Build headers with Authorization
const headers = () => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${getToken()}`
});

// ── AUTH ───────────────────────────────────────────────────
const API = {

  register: async (data) => {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  login: async (data) => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  forgotPassword: async (email) => {
    const res = await fetch(`${BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    return res.json();
  },

  // ── USERS ────────────────────────────────────────────────
  getMe: async () => {
    const res = await fetch(`${BASE_URL}/users/me`, { headers: headers() });
    return res.json();
  },

  updateProfile: async (data) => {
    const res = await fetch(`${BASE_URL}/users/me`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  changePassword: async (old_password, new_password) => {
    const res = await fetch(`${BASE_URL}/users/me/password`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify({ old_password, new_password })
    });
    return res.json();
  },

  getUser: async (userId) => {
    const res = await fetch(`${BASE_URL}/users/${userId}`, { headers: headers() });
    return res.json();
  },

  // ── TRIPS ────────────────────────────────────────────────
  getTrips: async () => {
    const res = await fetch(`${BASE_URL}/trips/`, { headers: headers() });
    return res.json();
  },

  createTrip: async (data) => {
    const res = await fetch(`${BASE_URL}/trips/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  joinTrip: async (tripId) => {
    const res = await fetch(`${BASE_URL}/trips/${tripId}/join`, {
      method: "POST",
      headers: headers()
    });
    return res.json();
  },

  // ── MESSAGES ─────────────────────────────────────────────
  getMessages: async (tripId) => {
    const res = await fetch(`${BASE_URL}/messages/${tripId}`, { headers: headers() });
    return res.json();
  },

  sendMessage: async (tripId, text) => {
    const res = await fetch(`${BASE_URL}/messages/${tripId}`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ text })
    });
    return res.json();
  }
};