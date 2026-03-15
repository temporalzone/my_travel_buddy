// ============================================================
//  pages/CreateTripPage.js — Create a new trip
// ============================================================

const { useState: useStateCreate } = React;

function CreateTripPage({ user, onCreated, setPage }) {
  const EMOJIS = ["🌴","🗼","🏔️","🕌","🌊","🏯","🎭","🦁","🏝️","🌋","🎪","🏕️"];
  const [f, setF] = useStateCreate({ title: "", dest: "", emoji: "🌴", dates: "", duration: "", budget: "Mid-range", style: "Adventure", seats: "4", tags: "" });
  const [err, setErr]   = useStateCreate("");
  const [loading, setLoading] = useStateCreate(false);
  const s = (k, v) => setF(p => ({ ...p, [k]: v }));

  const handleCreate = async () => {
    setErr("");
    if (!f.title.trim()) { setErr("Please enter a trip title."); return; }
    if (!f.dest.trim())  { setErr("Please enter a destination."); return; }
    if (!f.dates.trim()) { setErr("Please enter the dates."); return; }

    setLoading(true);

    const res = await API.createTrip({
      title:    f.title.trim(),
      dest:     f.dest.trim(),
      emoji:    f.emoji,
      dates:    f.dates.trim(),
      duration: f.duration.trim() || "TBD",
      budget:   f.budget,
      style:    f.style,
      seats:    parseInt(f.seats) || 4,
      tags:     f.tags.split(",").map(t => t.trim()).filter(Boolean).slice(0, 4)
    });

    setLoading(false);

    if (res.error) { setErr(res.error); return; }

    onCreated(); // refresh trips list and go to dashboard
  };

  return (
    <div className="fade-up" style={{ maxWidth: 620 }}>
      <div style={{ marginBottom: "1.25rem" }}>
        <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.25rem", marginBottom: ".35rem" }}>✈️ Create a New Trip</h2>
        <p style={{ color: "var(--muted)", fontSize: ".85rem" }}>Share your travel plans and find real companions to join you.</p>
      </div>

      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "1.75rem" }}>
        {err && <div className="alert-err">{err}</div>}

        {/* Emoji picker */}
        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", fontSize: ".75rem", fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".04em", marginBottom: ".45rem" }}>Pick an Emoji</label>
          <div style={{ display: "flex", gap: ".4rem", flexWrap: "wrap" }}>
            {EMOJIS.map(e => (
              <button key={e} onClick={() => s("emoji", e)} style={{
                width: 36, height: 36, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.15rem", cursor: "pointer", transition: "all .18s",
                border: `1.5px solid ${f.emoji === e ? "var(--teal)" : "var(--border)"}`,
                background: f.emoji === e ? "#EFF6FF" : "#fff"
              }}>{e}</button>
            ))}
          </div>
        </div>

        <div className="field"><label>Trip Title *</label><div className="field-wrap"><span className="ico">✏️</span><input placeholder="e.g. Bali Adventure 2025" value={f.title} onChange={e => s("title", e.target.value)} /></div></div>
        <div className="field"><label>Destination *</label><div className="field-wrap"><span className="ico">📍</span><input placeholder="e.g. Bali, Indonesia" value={f.dest} onChange={e => s("dest", e.target.value)} /></div></div>
        <div className="field"><label>Dates *</label><div className="field-wrap"><span className="ico">📅</span><input placeholder="e.g. Apr 10–20, 2025" value={f.dates} onChange={e => s("dates", e.target.value)} /></div></div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div className="field"><label>Duration</label><div className="field-wrap"><span className="ico">⏱️</span><input placeholder="e.g. 10 days" value={f.duration} onChange={e => s("duration", e.target.value)} /></div></div>
          <div className="field"><label>Total Seats (incl. you)</label><div className="field-wrap"><span className="ico">👥</span><input type="number" min="2" max="20" value={f.seats} onChange={e => s("seats", e.target.value)} /></div></div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div className="field">
            <label>Budget</label>
            <select style={{ width: "100%", padding: ".68rem 1rem", border: "1.5px solid var(--border)", borderRadius: 10, fontFamily: "'Nunito',sans-serif", fontSize: ".9rem", outline: "none" }} value={f.budget} onChange={e => s("budget", e.target.value)}>
              {["Budget","Mid-range","Comfortable","Luxury"].map(b => <option key={b}>{b}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Travel Style</label>
            <select style={{ width: "100%", padding: ".68rem 1rem", border: "1.5px solid var(--border)", borderRadius: 10, fontFamily: "'Nunito',sans-serif", fontSize: ".9rem", outline: "none" }} value={f.style} onChange={e => s("style", e.target.value)}>
              {["Adventure","Culture","Relaxation","Backpacking","Photography","Food & Nightlife"].map(st => <option key={st}>{st}</option>)}
            </select>
          </div>
        </div>

        <div className="field"><label>Tags (comma separated, max 4)</label><div className="field-wrap"><span className="ico">🏷️</span><input placeholder="e.g. Beach, Surfing, Sunset" value={f.tags} onChange={e => s("tags", e.target.value)} /></div></div>

        <div style={{ display: "flex", gap: ".65rem" }}>
          <button className="btn btn-primary" style={{ flex: 1, padding: ".75rem" }} onClick={handleCreate} disabled={loading}>
            {loading ? "Creating..." : "🚀 Launch Trip"}
          </button>
          <button className="btn btn-outline" onClick={() => setPage("dashboard")}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
