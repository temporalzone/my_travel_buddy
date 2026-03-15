// ============================================================
//  components/Toast.js — Notification popup
// ============================================================

const { useEffect } = React;

function Toast({ msg, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 3000);
    return () => clearTimeout(t);
  }, []);

  return <div className="toast">{msg}</div>;
}