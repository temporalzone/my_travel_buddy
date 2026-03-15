// ============================================================
//  pages/ProfilePage.js — View & edit user profile
// ============================================================

const { useState: useStateProfile } = React;

function ProfilePage({ user, onUpdate, onLogout, showToast }) {
  const [editing, setEditing] = useStateProfile(false);
  const [f, setF] = useStateProfile({
    name:      user.name,
    email:     user.email,
    location:  user.location || "",
    bio:       user.bio || "",
    interests: (user.interests || []).join(", ")
  });
  const [pw, setPw]     = useStateProfile({ old: "", n1: "", n2: "" });
  const [pwErr, setPwErr] = useStateProfile("");
  const [pwOk,  setPwOk]  = useStateProfile("");
  const s  = (k, v) => setF(p => ({ ...p, [k]: v }));
  const sp = (k, v) => setPw(p => ({ ...p, [k]: v }));

  const saveProfile = async () => {
    if (!f.name.trim() || !f.email.trim()) { showToast("Name and email are required."); return; }
    const res = await API.updateProfile({
      name:      f.name.trim(),
      email:     f.email.trim(),
      location:  f.location.trim(),
      bio:       f.bio.trim(),
      interests: f.interests.split(",").map(i => i.trim()).filter(Boolean)
    });
    if (res.error) { showToast(res.error); return; }
    onUpdate({ ...user, name: f.name.trim(), email: f.email.trim(), location: f.location.trim(), bio: f.bio.trim(), interests: f.interests.split(",").map(i => i.trim()).filter(Boolean) });
    setEditing(false);
    showToast("✅ Profile updated!");
  };

  const changePassword = async () => {
    setPwErr(""); setPwOk("");
    if (!pw.old || !pw.n1 || !pw.n2)  { setPwErr("Fill all password fields."); return; }
    if (pw.n1.length < 6)             { setPwErr("New password must be at least 6 characters."); return; }
    if (pw.n1 !== pw.n2)              { setPwErr("New passwords do not match."); return; }
    const res = await API.changePassword(pw.old, pw.n1);
    if (res.error) { setPwErr(res.error); return; }
    setPwOk("Password changed successfully!");
    setPw({ old: "", n1: "", n2: "" });
  };

  const joined = user.joined_at ? new Date(user.joined_at).toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" }) : "Recently";

  return (
    <div style={{ maxWidth: 620 }} className="fade-up">

      {/* Profile Hero */}
      <div style={{ background: "linear-gradient(135deg,#0F172A,#1E3A5F)", borderRadius: 18, padding: "2rem", display: "flex", alignItems: "center", gap: "1.5rem", marginBottom: "1.1rem", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", right: "1.75rem", top: "50%", transform: "translateY(-50%)", fontSize: "5rem", opacity: .06 }}>🌍</div>
        <Av name={user.name} size="xl" />
        <div>
          <h2 style={{ fontFamily: "'Syne',sans-serif", fontSize: "1.35rem", fontWeight: 800, color: "#fff" }}>{user.name}</h2>
          <p style={{ color: "rgba(255,255,255,.5)", fontSize: ".82rem", marginTop: ".2rem" }}>📧 {user.email}</p>
          <p style={{ color: "rgba(255,255,255,.5)", fontSize: ".82rem" }}>📍 {user.location}</p>
          <p style={{ color: "rgba(255,255,255,.5)", fontSize: ".82rem" }}>🗓️ Joined {joined}</p>
          <div style={{ display: "flex", gap: ".35rem", marginTop: ".6rem", flexWrap: "wrap" }}>
            {(user.interests || []).map(i => (
              <span key={i} style={{ background: "rgba(255,255,255,.14)", color: "#fff", fontSize: ".7rem", padding: ".15rem .55rem", borderRadius: 100 }}>{i}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Personal Info */}
      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "1.35rem", marginBottom: ".9rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
          <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".88rem" }}>👤 Personal Info</h4>
          {!editing && <button className="btn btn-outline btn-sm" onClick={() => setEditing(true)}>Edit Profile</button>}
        </div>

        {editing ? (
          <>
            <div className="field"><label>Full Name</label><div className="field-wrap"><span className="ico">👤</span><input value={f.name} onChange={e => s("name", e.target.value)} /></div></div>
            <div className="field"><label>Email</label><div className="field-wrap"><span className="ico">📧</span><input value={f.email} onChange={e => s("email", e.target.value)} /></div></div>
            <div className="field"><label>Location</label><div className="field-wrap"><span className="ico">📍</span><input value={f.location} onChange={e => s("location", e.target.value)} /></div></div>
            <div className="field">
              <label>Bio</label>
              <textarea style={{ width: "100%", padding: ".65rem .95rem", border: "1.5px solid var(--border)", borderRadius: 10, fontFamily: "'Nunito',sans-serif", fontSize: ".88rem", outline: "none", resize: "vertical", minHeight: 76 }} value={f.bio} onChange={e => s("bio", e.target.value)} />
            </div>
            <div className="field"><label>Interests (comma separated)</label><div className="field-wrap"><span className="ico">🏷️</span><input placeholder="e.g. Hiking, Photography, Food" value={f.interests} onChange={e => s("interests", e.target.value)} /></div></div>
            <div style={{ display: "flex", gap: ".55rem" }}>
              <button className="btn btn-primary btn-sm" onClick={saveProfile}>Save Changes</button>
              <button className="btn btn-outline btn-sm" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </>
        ) : (
          [["👤 Name", user.name], ["📧 Email", user.email], ["📍 Location", user.location || "Not set"], ["✏️ Bio", user.bio || "Not set"]].map(([l, v]) => (
            <div key={l} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: ".42rem 0", borderBottom: "1px solid var(--border)", fontSize: ".85rem" }}>
              <span style={{ fontWeight: 700, color: "var(--text)" }}>{l}</span>
              <span style={{ color: "var(--muted)", textAlign: "right", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{v}</span>
            </div>
          ))
        )}
      </div>

      {/* Change Password */}
      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "1.35rem", marginBottom: ".9rem" }}>
        <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".88rem", marginBottom: "1rem" }}>🔒 Change Password</h4>
        {pwErr && <div className="alert-err">{pwErr}</div>}
        {pwOk  && <div className="alert-ok">{pwOk}</div>}
        <div className="field"><label>Current Password</label><div className="field-wrap"><span className="ico">🔒</span><input type="password" placeholder="Your current password" value={pw.old} onChange={e => sp("old", e.target.value)} /></div></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div className="field"><label>New Password</label><div className="field-wrap"><span className="ico">🔑</span><input type="password" placeholder="Min. 6 characters" value={pw.n1} onChange={e => sp("n1", e.target.value)} /></div></div>
          <div className="field"><label>Confirm New</label><div className="field-wrap"><span className="ico">🔑</span><input type="password" placeholder="Repeat new password" value={pw.n2} onChange={e => sp("n2", e.target.value)} /></div></div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={changePassword}>Update Password</button>
      </div>

      {/* Logout */}
      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "1.35rem" }}>
        <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".88rem", marginBottom: ".75rem" }}>⚠️ Account</h4>
        <p style={{ fontSize: ".82rem", color: "var(--muted)", marginBottom: ".9rem" }}>Logging out will end your session. Your data stays saved on the server.</p>
        <button className="btn btn-danger btn-sm" onClick={onLogout}>🚪 Logout</button>
      </div>
    </div>
  );
}