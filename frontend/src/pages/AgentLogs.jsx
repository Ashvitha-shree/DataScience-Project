import React, { useEffect, useState } from "react";
import { Bot, Play } from "lucide-react";
import { getAgentLogs, getRoads, runAgent } from "../api/client.js";
import { Badge } from "../components/Card.jsx";

export default function AgentLogs() {
  const [logs, setLogs] = useState([]);
  const [roads, setRoads] = useState([]);
  const [selectedRoad, setSelectedRoad] = useState("");
  const [running, setRunning] = useState(false);

  const load = async () => {
    const [l, r] = await Promise.all([getAgentLogs(50), getRoads()]);
    setLogs(l.data);
    setRoads(r.data);
  };

  useEffect(() => { load(); }, []);

  const roadName = (id) => roads.find((r) => r.road_id === id)?.road_name || `Road #${id}`;

  const handleRunAgent = async () => {
    if (!selectedRoad) return;
    setRunning(true);
    try {
      await runAgent(parseInt(selectedRoad));
      load();
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <Bot size={24} /> Agentic AI - Traffic Decision Agent
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm max-w-2xl">
          The agent reads the latest prediction and incident data for a road, generates a commuter
          alert, recommends signal timing using simple rule-based reasoning, and logs its decision -
          no reinforcement learning, fully explainable.
        </p>
      </div>

      <div className="card flex gap-2 items-center flex-wrap">
        <select className="input-field max-w-xs" value={selectedRoad} onChange={(e) => setSelectedRoad(e.target.value)}>
          <option value="">Select a road to run the agent on...</option>
          {roads.map((r) => <option key={r.road_id} value={r.road_id}>{r.road_name}</option>)}
        </select>
        <button className="btn-primary flex items-center gap-2" onClick={handleRunAgent} disabled={running}>
          <Play size={16} /> {running ? "Running..." : "Run Agent Cycle"}
        </button>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
              <th className="py-2 pr-4">Road</th>
              <th className="py-2 pr-4">Decision</th>
              <th className="py-2 pr-4">Reason</th>
              <th className="py-2 pr-4">Urgency</th>
              <th className="py-2 pr-4">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.log_id} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4 font-medium text-slate-700 dark:text-slate-200">
                  {l.road_id ? roadName(l.road_id) : "-"}
                </td>
                <td className="py-2 pr-4">{l.decision}</td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{l.reason}</td>
                <td className="py-2 pr-4"><Badge level={l.urgency}>{l.urgency}</Badge></td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{new Date(l.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan={5} className="py-4 text-center text-slate-400">No agent decisions logged yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
