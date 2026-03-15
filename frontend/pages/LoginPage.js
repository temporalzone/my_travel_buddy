// ============================================================
//  pages/LoginPage.js — Login & Forgot Password
// ============================================================

const { useState } = React;

function LoginPage({ onLogin, onGoRegister }) {
  const [email, setEmail]   = useState("");
  const [pw, setPw]         = useState("");
  const [err, setErr]       = useState("");
  const [view, setView]     = useState("login"); // login | forgot
  const [ok, setOk]         = useState("");

  const handleLogin = async () => {
    setErr("");
    if (!email || !pw) { setErr("Please fill all fields."); return; }

    const res = await API.login({ email, password: pw });

    if (res.error) { setErr(res.error); return; }

    // Save token to localStorage
    localStorage.setItem("tb_token", res.token);
    onLogin(res.user);
  };

  const handleForgot = async () => {
    setErr(""); setOk("");
    if (!email) { setErr("Enter your email address."); return; }
    const res = await API.forgotPassword(email);
    if (res.error) { setErr(res.error); return; }
    setOk(res.message);
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "1fr 1fr" }}>

      {/* Left panel */}
      <div style={{ background: "linear-gradient(145deg,#0F172A,#1E293B)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "3rem", position: "relative", overflow: "hidden" }}>
        <div style={{ fontSize: "5rem", marginBottom: "1.5rem" }} className="float">🌍</div>
        <h1 style={{ fontFamily: "'Syne',sans-serif", fontSize: "2rem", fontWeight: 800, color: "#fff", textAlign: "center", lineHeight: 1.2, marginBottom: ".9rem" }}>
          Find Your Perfect Travel Companion
        </h1>
        <p style={{ color: "rgba(255,255,255,.55)", textAlign: "center", lineHeight: 1.7, fontSize: ".9rem" }}>
          Real trips. Real travelers. Real memories.
        </p>
      </div>

      {/* Right panel */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "3rem 2rem" }}>
        <div style={{ width: "100%", maxWidth: 410 }} className="fade-up">
          <Logo />
          <div style={{ marginTop: "1.75rem" }}>

            {view === "forgot" ? (
              <>
                <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.65rem", marginBottom: ".35rem" }}>Reset Password</h2>
                <p style={{ color: "var(--muted)", fontSize: ".86rem", marginBottom: "1.5rem" }}>Enter your email and we'll send a reset link.</p>
                {err && <div className="alert-err">{err}</div>}
                {ok  && <div className="alert-ok">{ok}</div>}
                <div className="field">
                  <label>Email Address</label>
                  <div className="field-wrap">
                    <span className="ico">📧</span>
                    <input type="email" placeholder="your@email.com" value={email} onChange={e => setEmail(e.target.value)} />
                  </div>
                </div>
                <button className="btn btn-primary" style={{ width: "100%", padding: ".78rem" }} onClick={handleForgot}>Send Reset Link</button>
                <p style={{ textAlign: "center", marginTop: "1rem", fontSize: ".83rem", color: "var(--muted)" }}>
                  <span style={{ color: "var(--teal)", fontWeight: 700, cursor: "pointer" }} onClick={() => { setView("login"); setErr(""); setOk(""); }}>← Back to Login</span>
                </p>
              </>
            ) : (
              <>
                <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.65rem", marginBottom: ".35rem" }}>Welcome back 👋</h2>
                <p style={{ color: "var(--muted)", fontSize: ".86rem", marginBottom: "1.5rem" }}>Sign in to your Travel Buddy account</p>
                {err && <div className="alert-err">{err}</div>}
                <div className="field">
                  <label>Email Address</label>
                  <div className="field-wrap">
                    <span className="ico">📧</span>
                    <input type="email" placeholder="your@email.com" value={email} onChange={e => setEmail(e.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>Password</label>
                  <div className="field-wrap">
                    <span className="ico">🔒</span>
                    <input type="password" placeholder="Your password" value={pw} onChange={e => setPw(e.target.value)} onKeyDown={e => e.key === "Enter" && handleLogin()} />
                  </div>
                </div>
                <div style={{ textAlign: "right", marginBottom: ".85rem" }}>
                  <span style={{ color: "var(--teal)", fontWeight: 700, cursor: "pointer", fontSize: ".82rem" }} onClick={() => { setView("forgot"); setErr(""); }}>Forgot password?</span>
                </div>
                <button className="btn btn-primary" style={{ width: "100%", padding: ".78rem" }} onClick={handleLogin}>Sign In →</button>
                <p style={{ textAlign: "center", marginTop: ".9rem", fontSize: ".86rem", color: "var(--muted)" }}>
                  Don't have an account?{" "}
                  <span style={{ color: "var(--teal)", fontWeight: 700, cursor: "pointer" }} onClick={onGoRegister}>Register free</span>
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}