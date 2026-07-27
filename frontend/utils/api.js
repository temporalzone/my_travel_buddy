// ============================================================
//  utils/api.js — All API calls to the Flask backend
// ============================================================

const BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://localhost:5000/api'
  : 'https://my-travel-buddy-kn22.onrender.com/api';

// Get saved token from localStorage
const getToken = () => localStorage.getItem("tb_token");

// Build headers with Authorization
const headers = () => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${getToken()}`
});

// Safe JSON parsing (so fetch errors don’t fail silently)
const safeJson = async (res) => {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return { error: text || "Unexpected server response" };
  }
};

// ── AUTH ───────────────────────────────────────────────────
const API = {

  register: async (data) => {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return safeJson(res);
  },

  login: async (data) => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return safeJson(res);
  },

  forgotPassword: async (email) => {
    const res = await fetch(`${BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    return safeJson(res);
  },

  resetPassword: async (data) => {
    const res = await fetch(`${BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return safeJson(res);
  },

  // ── USERS ────────────────────────────────────────────────
  getMe: async () => {
    const res = await fetch(`${BASE_URL}/users/me`, { headers: headers() });
    return safeJson(res);
  },

  updateProfile: async (data) => {
    const res = await fetch(`${BASE_URL}/users/me`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify(data)
    });
    return safeJson(res);
  },

  changePassword: async (old_password, new_password) => {
    const res = await fetch(`${BASE_URL}/users/me/password`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify({ old_password, new_password })
    });
    return safeJson(res);
  },

  getUser: async (userId) => {
    const res = await fetch(`${BASE_URL}/users/${userId}`, { headers: headers() });
    return safeJson(res);
  },

  // ── TRIPS ────────────────────────────────────────────────
  getTrips: async () => {
    const res = await fetch(`${BASE_URL}/trips/`, { headers: headers() });
    return safeJson(res);
  },

  createTrip: async (data) => {
    const res = await fetch(`${BASE_URL}/trips/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(data)
    });
    return safeJson(res);
  },

  joinTrip: async (tripId) => {
    const res = await fetch(`${BASE_URL}/trips/${tripId}/join`, {
      method: "POST",
      headers: headers()
    });
    return safeJson(res);
  },

  // ── MESSAGES ─────────────────────────────────────────────
  getMessages: async (tripId) => {
    const res = await fetch(`${BASE_URL}/messages/${tripId}`, { headers: headers() });
    return safeJson(res);
  },

  sendMessage: async (tripId, text) => {
    const res = await fetch(`${BASE_URL}/messages/${tripId}`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ text })
    });
    return safeJson(res);
  }
};
