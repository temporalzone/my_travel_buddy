// ============================================================
//  components/TripCard.js — Trip card used on Dashboard & Explore
// ============================================================

const GRADS = [
  'linear-gradient(135deg,#0EA5E9,#6366F1)',
  'linear-gradient(135deg,#10B981,#0EA5E9)',
  'linear-gradient(135deg,#F59E0B,#EF4444)',
  'linear-gradient(135deg,#8B5CF6,#EC4899)',
  'linear-gradient(135deg,#06B6D4,#10B981)',
];
const tripGrad = (id) => GRADS[id.charCodeAt(0) % GRADS.length];
const TAG_COLORS = ["tag-blue","tag-green","tag-amber","tag-violet","tag-rose"];

function TripCard({ trip, user, onJoin, onOpen, joined }) {
  const isHost = trip.hostId === user.id;
  const grad   = tripGrad(trip.id);

  return (
    <div className="card" style={{ transition: "transform .18s, box-shadow .18s", cursor: "pointer" }}
      onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-3px)"; e.currentTarget.style.boxShadow = "0 8px 28px rgba(0,0,0,.07)"; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}
      onClick={() => joined && onOpen(trip.id)}
    >
      {/* Thumbnail */}
      <div style={{ height: 118, background: grad, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "3rem", position: "relative" }}>
        <span>{trip.emoji}</span>
        <span style={{ position: "absolute", top: ".6rem", left: ".6rem", background: "rgba(0,0,0,.35)", backdropFilter: "blur(4px)", color: "#fff", fontSize: ".65rem", fontWeight: 700, padding: ".2rem .55rem", borderRadius: 100 }}>{trip.style}</span>
        <span style={{ position: "absolute", top: ".6rem", right: ".6rem", background: "rgba(255,255,255,.92)", color: "#0F172A", fontSize: ".65rem", fontWeight: 700, padding: ".2rem .55rem", borderRadius: 100 }}>{trip.seats > 0 ? `${trip.seats} seat${trip.seats !== 1 ? "s" : ""} left` : "Full"}</span>
      </div>

      {/* Body */}
      <div style={{ padding: "1rem" }}>
        <div style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".92rem", marginBottom: ".25rem" }}>{trip.title}</div>
        <div style={{ fontSize: ".74rem", color: "var(--muted)", marginBottom: ".65rem", display: "flex", gap: ".6rem", flexWrap: "wrap" }}>
          <span>📍 {trip.dest}</span><span>📅 {trip.dates}</span><span>💰 {trip.budget}</span>
        </div>

        {/* Member avatars */}
        <div style={{ display: "flex", marginBottom: ".7rem" }}>
          {(trip.memberIds || []).slice(0, 4).map((mid, i) => (
            <div key={mid} style={{ width: 24, height: 24, borderRadius: "50%", border: "2px solid #fff", marginLeft: i === 0 ? 0 : -4, background: avColor(mid), display: "flex", alignItems: "center", justifyContent: "center", fontSize: ".55rem", fontWeight: 800, color: "#fff", zIndex: 10 - i }}>
              {mid[0].toUpperCase()}
            </div>
          ))}
        </div>

        {/* Tags */}
        <div style={{ display: "flex", gap: ".3rem", flexWrap: "wrap", marginBottom: ".85rem" }}>
          {(trip.tags || []).map((tg, i) => <span key={tg} className={`tag ${TAG_COLORS[i % 5]}`}>{tg}</span>)}
        </div>

        {/* Action button */}
        <div style={{ display: "flex", gap: ".45rem", alignItems: "center" }}>
          {joined ? (
            <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={e => { e.stopPropagation(); onOpen(trip.id); }}>💬 Open Chat</button>
          ) : trip.seats > 0 ? (
            <button className="btn btn-emerald btn-sm" style={{ flex: 1 }} onClick={e => { e.stopPropagation(); onJoin(trip.id); }}>✈️ Join Trip</button>
          ) : (
            <button className="btn btn-sm" style={{ flex: 1, background: "var(--surface)", color: "var(--muted)", cursor: "not-allowed" }} disabled>Trip Full</button>
          )}
          {isHost && <span style={{ fontSize: ".68rem", color: "var(--amber)", fontWeight: 700 }}>👑 Yours</span>}
        </div>
      </div>
    </div>
  );
}