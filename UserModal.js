// ============================================================
//  components/UserModal.js — Popup to view another user's profile
// ============================================================

const { useState: useStateModal, useEffect: useEffectModal } = React;

function UserModal({ userId, onClose }) {
  const [user, setUser]       = useStateModal(null);
  const [loading, setLoading] = useStateModal(true);

  useEffectModal(() => {
    const load = async () => {
      setLoading(true);
      const data = await API.getUser(userId);
      if (!data.error) setUser(data);
      setLoading(false);
    };
    load();
  }, [userId]);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        {loading && (
          <div style={{ textAlign: "center", padding: "2rem", color: "var(--muted)" }}>Loading profile...</div>
        )}

        {!loading && user && (
          <>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "1.25rem" }}>
              <Av name={user.name} size="lg" />
              <h3 style={{ marginTop: ".85rem", marginBottom: ".22rem", fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.1rem", textAlign: "center" }}>{user.name}</h3>
              <p style={{ color: "var(--muted)", fontSize: ".8rem" }}>📍 {user.location || "Somewhere on Earth"}</p>
            </div>

            <div style={{ background: "var(--surface)", borderRadius: 10, padding: ".85rem", marginBottom: ".85rem", fontSize: ".84rem", lineHeight: 1.6, color: "var(--text)" }}>
              {user.bio || "No bio yet."}
            </div>

            {(user.interests || []).length > 0 && (
              <>
                <div style={{ fontSize: ".7rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: ".05em", color: "var(--muted)", marginBottom: ".4rem" }}>Interests</div>
                <div style={{ display: "flex", gap: ".3rem", flexWrap: "wrap", marginBottom: "1rem" }}>
                  {user.interests.map(i => <span key={i} className="tag tag-blue">{i}</span>)}
                </div>
              </>
            )}

            <button className="btn btn-outline" style={{ width: "100%" }} onClick={onClose}>Close</button>
          </>
        )}

        {!loading && !user && (
          <>
            <div style={{ textAlign: "center", padding: "1rem", color: "var(--muted)" }}>Could not load profile.</div>
            <button className="btn btn-outline" style={{ width: "100%" }} onClick={onClose}>Close</button>
          </>
        )}
      </div>
    </div>
  );
}