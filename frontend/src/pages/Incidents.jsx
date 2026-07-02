import React, { useEffect, useState } from "react";
import { Send } from "lucide-react";
import { getIncidents, createIncident, getRoads } from "../api/client.js";
import { Badge } from "../components/Card.jsx";

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [roads, setRoads] = useState([]);
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    const [i, r] = await Promise.all([getIncidents(50), getRoads()]);
    setIncidents(i.data);
    setRoads(r.data);
  };

  useEffect(() => { load(); }, []);

  const roadName = (id) => roads.find((r) => r.road_id === id)?.road_name || "-";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    try {
      await createIncident({ raw_text: text, reported_by: "traffic_officer" });
      setText("");
      load();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Traffic Incident Analyzer (NLP)</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          Submit a free-text incident report. The NLP module (spaCy + keyword matching) automatically
          extracts road name, incident type, severity, and weather.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card flex gap-3">
        <input
          className="input-field flex-1"
          placeholder='e.g. "Accident near Anna Salai due to heavy rain."'
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" disabled={submitting} className="btn-primary flex items-center gap-2">
          <Send size={16} /> Submit
        </button>
      </form>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
              <th className="py-2 pr-4">Report Text</th>
              <th className="py-2 pr-4">Road</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Severity</th>
              <th className="py-2 pr-4">Weather</th>
              <th className="py-2 pr-4">Reported At</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((i) => (
              <tr key={i.incident_id} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4 max-w-xs text-slate-600 dark:text-slate-300">{i.raw_text}</td>
                <td className="py-2 pr-4">{i.road_id ? roadName(i.road_id) : "-"}</td>
                <td className="py-2 pr-4 capitalize">{i.incident_type}</td>
                <td className="py-2 pr-4"><Badge level={i.severity}>{i.severity}</Badge></td>
                <td className="py-2 pr-4 capitalize">{i.weather}</td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{new Date(i.reported_at).toLocaleString()}</td>
              </tr>
            ))}
            {incidents.length === 0 && (
              <tr><td colSpan={6} className="py-4 text-center text-slate-400">No incidents reported yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
