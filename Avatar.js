// ============================================================
//  components/Avatar.js — User avatar circle
// ============================================================

const AV_COLORS = ['#0EA5E9','#10B981','#F59E0B','#8B5CF6','#F43F5E','#06B6D4','#84CC16','#EC4899'];
const avColor  = (name) => AV_COLORS[(name || 'A').charCodeAt(0) % AV_COLORS.length];

function Av({ name, size = 'md', onClick }) {
  const sizes = { xs: 26, sm: 34, md: 46, lg: 68, xl: 88 };
  const fonts = { xs: 10, sm: 13, md: 16, lg: 24, xl: 30 };
  const px    = sizes[size] || 46;
  const fp    = fonts[size] || 16;

  return (
    <div
      onClick={onClick}
      style={{
        width: px, height: px, borderRadius: "50%",
        background: avColor(name || "?"),
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Syne', sans-serif", fontWeight: 800,
        color: "#fff", fontSize: fp, flexShrink: 0,
        cursor: onClick ? "pointer" : "default"
      }}
    >
      {(name || "?")[0].toUpperCase()}
    </div>
  );
}