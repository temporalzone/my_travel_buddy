// ============================================================
//  App.js — Root component — controls all pages & state
// ============================================================

const { useState: useStateApp, useEffect: useEffectApp } = React;

function App() {
  const [user,       setUser]       = useStateApp(null);
  const [trips,      setTrips]      = useStateApp([]);
  const [allUsers,   setAllUsers]   = useStateApp([]);
  const [page,       setPage]       = useStateApp("dashboard");
  const [authView,   setAuthView]   = useStateApp("login");   // login | register
  const [openTripId, setOpenTripId] = useStateApp(null);
  const [viewUserId, setViewUserId] = useStateApp(null);
  const [toast,      setToast]      = useStateApp(null);

  const showToast = msg => { setToast(null); setTimeout(() => setToast(msg), 10); };

  // ── On app load: check if user is already logged in ──
  useEffectApp(() => {
    const token = localStorage.getItem("tb_token");
    if (!token) return;

    API.getMe().then(data => {
      if (data.error) {
        localStorage.removeItem("tb_token"); // token expired
        return;
      }
      setUser(data);
    });
  }, []);

  // ── Load all trips whenever user logs in ──
  useEffectApp(() => {
    if (!user) return;
    loadTrips();
  }, [user]);

  const loadTrips = async () => {
    const data = await API.getTrips();
    if (Array.isArray(data)) setTrips(data);
  };

  const handleLogin = (u) => {
    setUser(u);
    setPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("tb_token");
    setUser(null);
    setTrips([]);
    setPage("dashboard");
    setAuthView("login");
  };

  const handleUpdateUser = (updated) => {
    setUser(updated);
  };

  const handleJoinTrip = async (tripId) => {
    const res = await API.joinTrip(tripId);
    if (res.error) { showToast(res.error); return; }
    showToast("🎉 You joined the trip! Opening group chat...");
    await loadTrips(); // refresh trips list
    setOpenTripId(tripId);
    setPage("chat");
  };

  const handleOpenChat = (tripId) => {
    setOpenTripId(tripId);
    setPage("chat");
  };

  const handleTripCreated = async () => {
    showToast("🚀 Trip created! Others can now find and join it.");
    await loadTrips();
    setPage("dashboard");
  };

  // ── If not logged in, show auth screens ──
  if (!user) {
    return (
      <>
        {authView === "login"
          ? <LoginPage    onLogin={handleLogin}   onGoRegister={() => setAuthView("register")} />
          : <RegisterPage onLogin={handleLogin}   onGoLogin={()    => setAuthView("login")} />
        }
      </>
    );
  }

  const openTripObj = trips.find(t => t.id === openTripId);
  const myTrips     = trips.filter(t => (t.memberIds || []).includes(user.id));

  const PAGE_TITLES = {
    dashboard: "Dashboard",
    explore:   "Explore Trips",
    create:    "Create Trip",
    profile:   "My Profile",
    chat:      openTripObj ? `${openTripObj.emoji} ${openTripObj.title}` : "Trip Chat"
  };

  return (
    <div className="app-shell">

      {/* ── SIDEBAR ── */}
      <div className="sidebar">
        <Logo />

        <div style={{ marginBottom: "1.25rem" }}>
          <div className="sb-lbl">Menu</div>
          {[
            { id: "dashboard", ico: "🏠", lbl: "Dashboard" },
            { id: "explore",   ico: "🌍", lbl: "Explore Trips" },
            { id: "create",    ico: "✈️", lbl: "Create Trip" },
            { id: "profile",   ico: "👤", lbl: "My Profile" },
          ].map(n => (
            <div key={n.id} className={`nav-item ${page === n.id ? "on" : ""}`} onClick={() => setPage(n.id)}>
              <span className="ni">{n.ico}</span>{n.lbl}
            </div>
          ))}
        </div>

        {myTrips.length > 0 && (
          <div style={{ marginBottom: "1.25rem" }}>
            <div className="sb-lbl">My Trips</div>
            {myTrips.map(t => (
              <div key={t.id} className={`nav-item ${page === "chat" && openTripId === t.id ? "on" : ""}`} onClick={() => handleOpenChat(t.id)} title={t.title} style={{ overflow: "hidden" }}>
                <span className="ni">{t.emoji}</span>
                <span style={{ fontSize: ".8rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.title}</span>
              </div>
            ))}
          </div>
        )}

        <div className="sb-footer">
          <div className="user-pill" onClick={() => setPage("profile")}>
            <Av name={user.name} size="sm" />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: ".86rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{user.name}</div>
              <div style={{ fontSize: ".7rem", color: "var(--muted)" }}>Traveler ✈️</div>
            </div>
            <span style={{ fontSize: ".7rem", color: "var(--muted)" }}>→</span>
          </div>
        </div>
      </div>

      {/* ── MAIN CONTENT ── */}
      <div>
        <div className="topbar">
          <h1>{PAGE_TITLES[page] || ""}</h1>
          <div style={{ display: "flex", alignItems: "center", gap: ".65rem" }}>
            <button className="btn btn-primary btn-sm" onClick={() => setPage("create")}>+ New Trip</button>
            <Av name={user.name} size="sm" onClick={() => setPage("profile")} />
          </div>
        </div>

        <div className="main">
          {page === "dashboard" && <DashboardPage  user={user} trips={trips} onJoin={handleJoinTrip} onOpen={handleOpenChat} setPage={setPage} />}
          {page === "explore"   && <ExplorePage    trips={trips} user={user} onJoin={handleJoinTrip} onOpen={handleOpenChat} />}
          {page === "create"    && <CreateTripPage user={user} onCreated={handleTripCreated} setPage={setPage} />}
          {page === "profile"   && <ProfilePage    user={user} onUpdate={handleUpdateUser} onLogout={handleLogout} showToast={showToast} />}
          {page === "chat" && openTripObj && (
            <ChatPage
              trip={openTripObj}
              user={user}
              allUsers={allUsers}
              onBack={() => setPage("dashboard")}
              onViewUser={id => setViewUserId(id)}
            />
          )}
        </div>
      </div>

      {/* ── MODALS & TOAST ── */}
      {viewUserId && <UserModal userId={viewUserId} onClose={() => setViewUserId(null)} />}
      {toast      && <Toast msg={toast} onDone={() => setToast(null)} />}

    </div>
  );
}

// Mount React app into #root
ReactDOM.createRoot(document.getElementById("root")).render(<App />);