// ============================================================
//  pages/ExplorePage.js — Browse & search all trips
// ============================================================

const { useState: useStateExplore } = React;

function ExplorePage({ trips, user, onJoin, onOpen }) {
  const [q,   setQ]   = useStateExplore("");
  const [fil, setFil] = useStateExplore("All");

  const FILTERS = ["All","Adventure","Culture","Relaxation","Backpacking","Photography","Food & Nightlife"];

  const list = trips.filter(t => {
    const matchQ   = t.title.toLowerCase().includes(q.toLowerCase()) || t.dest.toLowerCase().includes(q.toLowerCase());
    const matchFil = fil === "All" || t.style === fil || (t.tags || []).some(g => g.toLowerCase().includes(fil.toLowerCase()));
    return matchQ && matchFil;
  });

  return (
    <div className="fade-up">
      <div style={{ marginBottom: "1.25rem" }}>
        <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.25rem", marginBottom: ".35rem" }}>🌍 Explore All Trips</h2>
        <p style={{ color: "var(--muted)", fontSize: ".85rem" }}>Find your perfect adventure and meet amazing travel companions.</p>
      </div>

      {/* Search bar */}
      <div style={{ position: "relative", marginBottom: "1rem" }}>
        <span style={{ position: "absolute", left: ".85rem", top: "50%", transform: "translateY(-50%)", color: "var(--muted)", fontSize: ".9rem" }}>🔍</span>
        <input
          style={{ width: "100%", padding: ".62rem 1rem .62rem 2.5rem", border: "1.5px solid var(--border)", borderRadius: 10, fontFamily: "'Nunito',sans-serif", fontSize: ".86rem", outline: "none", background: "#fff" }}
          placeholder="Search by destination or trip name..."
          value={q}
          onChange={e => setQ(e.target.value)}
        />
      </div>

      {/* Filter chips */}
      <div style={{ display: "flex", gap: ".35rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
        {FILTERS.map(fi => (
          <button
            key={fi}
            onClick={() => setFil(fi)}
            style={{
              padding: ".36rem .82rem", borderRadius: 100,
              border: `1.5px solid ${fil === fi ? "var(--teal)" : "var(--border)"}`,
              background: fil === fi ? "var(--teal)" : "#fff",
              color: fil === fi ? "#fff" : "var(--muted)",
              fontFamily: "'Nunito',sans-serif", fontWeight: 700,
              fontSize: ".76rem", cursor: "pointer", transition: "all .18s"
            }}
          >{fi}</button>
        ))}
      </div>

      {/* Trip grid */}
      {list.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(275px,1fr))", gap: "1.1rem" }}>
          {list.map(t => {
            const joined = t.memberIds.includes(user.id);
            return <TripCard key={t.id} trip={t} user={user} onJoin={onJoin} onOpen={onOpen} joined={joined} />;
          })}
        </div>
      ) : (
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "3rem", textAlign: "center" }}>
          <div style={{ fontSize: "2.5rem", marginBottom: ".75rem" }}>🔍</div>
          <h3 style={{ fontFamily: "'Syne',sans-serif", marginBottom: ".5rem" }}>No trips found</h3>
          <p style={{ color: "var(--muted)", fontSize: ".88rem" }}>
            {q ? `No trips match "${q}". Try a different search.` : "No trips available right now. Be the first to create one!"}
          </p>
        </div>
      )}
    </div>
  );
}