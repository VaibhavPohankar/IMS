import { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [selected, setSelected] = useState(null);

  // fetch incidents
  const fetchIncidents = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/incidents");
      const data = await res.json();
      setIncidents(data.incidents || data);
    } catch (err) {
      console.error("Error fetching incidents:", err);
    }
  };

  // auto refresh every 5 sec
  useEffect(() => {
    fetchIncidents();

    const interval = setInterval(() => {
      fetchIncidents();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // submit RCA
  const submitRCA = async () => {
    if (!selected) return;

    try {
      await fetch("http://127.0.0.1:8000/rca", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          work_item_id: selected.id,
          root_cause: "Cache overload",
          fix: "Increased memory",
          prevention: "Add alerts",
        }),
      });

      alert("RCA submitted");
    } catch (err) {
      console.error("Error submitting RCA:", err);
    }
  };

  // close incident
  const closeIncident = async () => {
    if (!selected) return;

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/close/${selected.id}`,
        {
          method: "POST",
        }
      );

      const data = await res.json();

      alert(JSON.stringify(data));
    } catch (err) {
      console.error("Error closing incident:", err);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>🚨 Incident Dashboard</h2>

      {/* Incident List */}
      {incidents.length === 0 && <p>No incidents yet...</p>}

      {incidents.map((i) => (
        <div
          key={i.id}
          onClick={() => setSelected(i)}
          style={{
            border: "1px solid black",
            padding: 10,
            margin: 5,
            cursor: "pointer",
            background: selected?.id === i.id ? "#eee" : "white",
          }}
        >
          <b>[{i.severity}]</b> {i.component_id} — {i.status}
        </div>
      ))}

      {/* Incident Detail */}
      {selected && (
        <div style={{ marginTop: 20 }}>
          <h3>Incident Detail</h3>

          <p><b>ID:</b> {selected.id}</p>
          <p><b>Component:</b> {selected.component_id}</p>
          <p><b>Status:</b> {selected.status}</p>

          <button onClick={submitRCA} style={{ marginRight: 10 }}>
            Submit RCA
          </button>

          <button onClick={closeIncident}>
            Close Incident
          </button>
        </div>
      )}
    </div>
  );
}

export default App;