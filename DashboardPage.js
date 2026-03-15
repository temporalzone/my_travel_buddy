// ============================================================
//  pages/DashboardPage.js
// ============================================================

function DashboardPage({ user, trips, onJoin, onOpen, setPage }) {
  const myTrips   = trips.filter(t => t.memberIds.includes(user.id));
  const openTrips = trips.filter(t => !t.memberIds.includes(user.id) && t.seats > 0);

  return (
    <div className="fade-up">
      <div style={{ background: "linear-gradient(135deg,#0F172A,#1E3A5F)", borderRadius: 18, padding: "1.75rem 2rem", color: "#fff", marginBottom: "1.6rem", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", right: "1.75rem", top: "50%", transform: "translateY(-50%)", fontSize: "5rem", opacity: .06 }}>✈</div>
        <h2 style={{ fontFamily: "'Syne',sans-serif", fontSize: "1.4rem", fontWeight: 800, marginBottom: ".35rem" }}>Hey {user.name.split(" ")[0]}! 👋</h2>
        <p style={{ opacity: .6, fontSize: ".86rem" }}>{openTrips.length > 0 ? `${openTrips.length} trip${openTrips.length !== 1 ? "s are" : " is"} looking for companions.` : "Be the first to create a trip!"}</p>
        <div style={{ display: "flex", gap: ".65rem", marginTop: "1rem" }}>
          <button className="btn btn-emerald btn-sm" onClick={() => setPage("create")}>+ Create a Trip</button>
          <button className="btn btn-ghost btn-sm" onClick={() => setPage("explore")}>Explore Trips →</button>
        </div>
      </div>

      {myTrips.length > 0 && <>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1rem" }}>✈️ My Trips</h3>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(275px,1fr))", gap: "1.1rem", marginBottom: "1.75rem" }}>
          {myTrips.map(t => <TripCard key={t.id} trip={t} user={user} onOpen={onOpen} joined />)}
        </div>
      </>}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1rem" }}>🌍 Discover Trips</h3>
        {openTrips.length > 0 && <button className="btn btn-outline btn-sm" onClick={() => setPage("explore")}>View All</button>}
      </div>

      {openTrips.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(275px,1fr))", gap: "1.1rem" }}>
          {openTrips.slice(0, 3).map(t => <TripCard key={t.id} trip={t} user={user} onJoin={onJoin} onOpen={onOpen} />)}
        </div>
      ) : (
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "3rem", textAlign: "center" }}>
          <div style={{ fontSize: "2.5rem", marginBottom: ".75rem" }}>🗺️</div>
          <h3 style={{ fontFamily: "'Syne',sans-serif", marginBottom: ".5rem" }}>No trips yet</h3>
          <p style={{ color: "var(--muted)", fontSize: ".88rem", marginBottom: "1.25rem" }}>Be the first adventurer! Create a trip and let others join.</p>
          <button className="btn btn-primary" onClick={() => setPage("create")}>Create First Trip</button>
        </div>
      )}
    </div>
  );
}