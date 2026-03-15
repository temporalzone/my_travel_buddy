// ============================================================
//  components/Logo.js — Reusable Logo component
// ============================================================

function Logo({ size = 1 }) {
  return (
    <div className="logo-wrap" style={{ display: "flex", alignItems: "center", gap: 9, cursor: "pointer", userSelect: "none" }}>
      <svg width={30 * size} height={30 * size} viewBox="0 0 30 30" fill="none">
        <circle cx="15" cy="15" r="15" fill="#0EA5E9"/>
        <circle cx="15" cy="15" r="9" fill="none" stroke="white" strokeWidth="1.3"/>
        <ellipse cx="15" cy="15" rx="4.2" ry="9" fill="none" stroke="white" strokeWidth="1.3"/>
        <line x1="6" y1="15" x2="24" y2="15" stroke="white" strokeWidth="1.3"/>
        <polygon points="21,8.5 25,11 21,9.5" fill="#F59E0B"/>
        <circle cx="21" cy="8.5" r="1.8" fill="#F59E0B"/>
      </svg>
      <span style={{
        fontFamily: "'Syne', sans-serif",
        fontWeight: 800,
        fontSize: `${1.3 * size}rem`,
        color: "#0F172A"
      }}>
        Travel<span style={{ color: "#0EA5E9" }}>Buddy</span>
      </span>
    </div>
  );
}