// ============================================================
//  pages/RegisterPage.js — New user registration
// ============================================================

const { useState: useStateReg } = React;

function RegisterPage({ onLogin, onGoLogin }) {
  const [f, setF]   = useStateReg({ name: "", email: "", pw: "", pw2: "", location: "", bio: "" });
  const [err, setErr] = useStateReg("");
  const s = (k, v) => setF(p => ({ ...p, [k]: v }));

  const handleRegister = async () => {
    setErr("");
    if (!f.name || !f.email || !f.pw || !f.pw2) { setErr("Please fill all required fields."); return; }
    if (!f.email.includes("@"))                  { setErr("Enter a valid email address."); return; }
    if (f.pw.length < 6)                         { setErr("Password must be at least 6 characters."); return; }
    if (f.pw !== f.pw2)                          { setErr("Passwords do not match."); return; }

    const res = await API.register({
      name: f.name, email: f.email, password: f.pw,
      location: f.location, bio: f.bio
    });

    if (res.error) { setErr(res.error); return; }

    localStorage.setItem("tb_token", res.token);
    onLogin(res.user);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem", background: "var(--surface)" }}>
      <div style={{ width: "100%", maxWidth: 480, background: "#fff", borderRadius: 20, padding: "2rem", border: "1px solid var(--border)" }} className="fade-up">
        <Logo />
        <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.65rem", margin: "1.5rem 0 .35rem" }}>Create Account 🚀</h2>
        <p style={{ color: "var(--muted)", fontSize: ".86rem", marginBottom: "1.5rem" }}>Join thousands of travelers today — no fake data!</p>

        {err && <div className="alert-err">{err}</div>}

        <div className="field">
          <label>Full Name *</label>
          <div className="field-wrap"><span className="ico">👤</span><input placeholder="Your full name" value={f.name} onChange={e => s("name", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>Email Address *</label>
          <div className="field-wrap"><span className="ico">📧</span><input type="email" placeholder="your@email.com" value={f.email} onChange={e => s("email", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>Password *</label>
          <div className="field-wrap"><span className="ico">🔒</span><input type="password" placeholder="Min. 6 characters" value={f.pw} onChange={e => s("pw", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>Confirm Password *</label>
          <div className="field-wrap"><span className="ico">🔒</span><input type="password" placeholder="Repeat password" value={f.pw2} onChange={e => s("pw2", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>Location (optional)</label>
          <div className="field-wrap"><span className="ico">📍</span><input placeholder="City, Country" value={f.location} onChange={e => s("location", e.target.value)} /></div>
        </div>
        <div className="field">
          <label>Bio (optional)</label>
          <textarea style={{ width: "100%", padding: ".65rem .95rem", border: "1.5px solid var(--border)", borderRadius: 10, fontFamily: "'Nunito',sans-serif", fontSize: ".9rem", outline: "none", resize: "vertical", minHeight: 76 }} placeholder="Tell fellow travelers about yourself..." value={f.bio} onChange={e => s("bio", e.target.value)} />
        </div>

        <button className="btn btn-primary" style={{ width: "100%", padding: ".78rem" }} onClick={handleRegister}>Create Account →</button>
        <p style={{ textAlign: "center", marginTop: ".9rem", fontSize: ".86rem", color: "var(--muted)" }}>
          Already have an account?{" "}
          <span style={{ color: "var(--teal)", fontWeight: 700, cursor: "pointer" }} onClick={onGoLogin}>Sign in</span>
        </p>
      </div>
    </div>
  );
}