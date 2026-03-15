// ============================================================
//  pages/ChatPage.js — Group chat for a trip
// ============================================================

const { useState: useStateChat, useEffect: useEffectChat, useRef: useRefChat } = React;

function ChatPage({ trip, user, allUsers, onBack, onViewUser }) {
  const [msgs, setMsgs] = useStateChat([]);
  const [inp,  setInp]  = useStateChat("");
  const [loading, setLoading] = useStateChat(true);
  const btm = useRefChat(null);

  // Load messages from Flask API when page opens
  useEffectChat(() => {
    const loadMsgs = async () => {
      setLoading(true);
      const data = await API.getMessages(trip.id);
      if (Array.isArray(data)) setMsgs(data);
      setLoading(false);
    };
    loadMsgs();

    // Poll for new messages every 3 seconds (simple real-time simulation)
    const interval = setInterval(loadMsgs, 3000);
    return () => clearInterval(interval);
  }, [trip.id]);

  // Auto scroll to bottom when new message arrives
  useEffectChat(() => {
    btm.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  const send = async () => {
    if (!inp.trim()) return;
    const optimistic = { id: "tmp", text: inp.trim(), time: new Date().toTimeString().slice(0, 5), userId: user.id, userName: user.name };
    setMsgs(m => [...m, optimistic]);
    setInp("");

    // Send to Flask backend
    await API.sendMessage(trip.id, optimistic.text);
  };

  const members = (trip.memberIds || []).map(id => allUsers.find(u => u.id === id)).filter(Boolean);

  return (
    <div style={{ height: "calc(100vh - 5.5rem)" }}>

      {/* Back + trip info header */}
      <div style={{ display: "flex", alignItems: "center", gap: ".9rem", marginBottom: ".9rem" }}>
        <button className="btn btn-outline btn-sm" onClick={onBack}>← Back</button>
        <div>
          <h2 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "1.1rem" }}>{trip.emoji} {trip.title}</h2>
          <p style={{ fontSize: ".74rem", color: "var(--muted)" }}>📍 {trip.dest} · 📅 {trip.dates} · {members.length} member{members.length !== 1 ? "s" : ""}</p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1.1rem", height: "calc(100vh - 9rem)" }}>

        {/* CHAT PANEL */}
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", display: "flex", flexDirection: "column", overflow: "hidden" }}>

          {/* Chat header */}
          <div style={{ padding: ".85rem 1.1rem", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".88rem" }}>💬 Group Chat</span>
            <span style={{ fontSize: ".72rem", color: "var(--muted)" }}>{members.length} member{members.length !== 1 ? "s" : ""}</span>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: "auto", padding: ".85rem", display: "flex", flexDirection: "column", gap: ".6rem" }}>
            <div style={{ textAlign: "center", fontSize: ".72rem", color: "var(--muted)", padding: ".65rem", background: "var(--surface)", borderRadius: 8 }}>
              {trip.emoji} {trip.title} group chat — say hello!
            </div>

            {loading && <div style={{ textAlign: "center", color: "var(--muted)", fontSize: ".82rem", padding: "1rem" }}>Loading messages...</div>}

            {!loading && msgs.length === 0 && (
              <div style={{ textAlign: "center", padding: "2rem", color: "var(--muted)" }}>
                <div style={{ fontSize: "2rem", marginBottom: ".5rem" }}>👋</div>
                <p style={{ fontSize: ".82rem" }}>No messages yet. Start the conversation!</p>
              </div>
            )}

            {msgs.map(m => {
              const mine   = m.userId === user.id;
              const sender = allUsers.find(u => u.id === m.userId);
              return (
                <div key={m.id} style={{ display: "flex", gap: ".5rem", alignItems: "flex-end", flexDirection: mine ? "row-reverse" : "row" }}>
                  {!mine && <Av name={sender?.name || "?"} size="xs" onClick={() => onViewUser(m.userId)} />}
                  <div>
                    {!mine && (
                      <div style={{ fontSize: ".7rem", color: "var(--muted)", marginBottom: ".18rem", cursor: "pointer" }} onClick={() => onViewUser(m.userId)}>
                        {m.userName || sender?.name}
                      </div>
                    )}
                    <div style={{
                      maxWidth: "72%", padding: ".58rem .9rem", borderRadius: 16,
                      fontSize: ".84rem", lineHeight: 1.5, wordBreak: "break-word",
                      background: mine ? "var(--teal)" : "var(--surface)",
                      color: mine ? "#fff" : "var(--text)",
                      borderBottomRightRadius: mine ? 3 : 16,
                      borderBottomLeftRadius: mine ? 16 : 3
                    }}>
                      {m.text}
                    </div>
                    <div style={{ fontSize: ".64rem", color: "var(--muted)", marginTop: ".18rem", textAlign: mine ? "right" : "left" }}>{m.time}</div>
                  </div>
                </div>
              );
            })}
            <div ref={btm} />
          </div>

          {/* Input row */}
          <div style={{ padding: ".6rem", borderTop: "1px solid var(--border)", display: "flex", gap: ".45rem", alignItems: "center" }}>
            <input
              style={{ flex: 1, padding: ".55rem .9rem", border: "1.5px solid var(--border)", borderRadius: 100, fontFamily: "'Nunito',sans-serif", fontSize: ".84rem", outline: "none" }}
              placeholder="Type a message… press Enter to send"
              value={inp}
              onChange={e => setInp(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            />
            <button className="btn btn-primary btn-sm" onClick={send}>Send</button>
          </div>
        </div>

        {/* MEMBERS PANEL */}
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid var(--border)", padding: "1.1rem", overflowY: "auto" }}>
          <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: ".88rem", marginBottom: ".85rem" }}>
            👥 Members ({members.length})
          </h4>
          {members.map(m => (
            <div
              key={m.id}
              onClick={() => onViewUser(m.id)}
              style={{ display: "flex", alignItems: "center", gap: ".65rem", padding: ".55rem .4rem", borderRadius: 9, cursor: "pointer", transition: "background .15s", marginBottom: ".15rem" }}
              onMouseEnter={e => e.currentTarget.style.background = "var(--surface)"}
              onMouseLeave={e => e.currentTarget.style.background = "transparent"}
            >
              <Av name={m.name} size="sm" />
              <div>
                <div style={{ fontWeight: 700, fontSize: ".82rem" }}>
                  {m.name}
                  {m.id === trip.hostId && (
                    <span style={{ marginLeft: ".4rem", fontSize: ".66rem", background: "rgba(245,158,11,.15)", color: "#92400E", padding: ".1rem .4rem", borderRadius: 100 }}>Host</span>
                  )}
                </div>
                <div style={{ fontSize: ".7rem", color: "var(--muted)" }}>📍 {m.location || "Somewhere"}</div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: ".85rem", fontSize: ".75rem", color: "var(--muted)", background: "var(--surface)", borderRadius: 9, padding: ".65rem", lineHeight: 1.5 }}>
            Tap a member to view their profile.
          </div>
        </div>

      </div>
    </div>
  );
}