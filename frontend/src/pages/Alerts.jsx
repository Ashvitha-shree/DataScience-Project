import React, { useEffect, useState } from "react";
import { Sparkles, MessageSquareText } from "lucide-react";
import { getAlerts, getIncidents, generateAlert, getScenario, getScenarioTypes } from "../api/client.js";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState("");
  const [scenarioTypes, setScenarioTypes] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState("");
  const [scenario, setScenario] = useState(null);
  const [loadingScenario, setLoadingScenario] = useState(false);

  const load = async () => {
    const [a, i, st] = await Promise.all([getAlerts(50), getIncidents(50), getScenarioTypes()]);
    setAlerts(a.data);
    setIncidents(i.data);
    setScenarioTypes(st.data.scenario_types);
  };

  useEffect(() => { load(); }, []);

  const handleGenerateAlert = async () => {
    if (!selectedIncident) return;
    await generateAlert(parseInt(selectedIncident));
    load();
  };

  const handleGenerateScenario = async () => {
    setLoadingScenario(true);
    try {
      const res = await getScenario(selectedScenario || undefined);
      setScenario(res.data);
    } finally {
      setLoadingScenario(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Alerts (SLM) & Scenarios (GenAI)</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          FLAN-T5 Small generates concise commuter alerts from incidents; the Generative AI module
          creates realistic what-if traffic scenarios for planning and testing.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-2">
            <MessageSquareText size={18} /> Generate Commuter Alert
          </h2>
          <div className="flex gap-2 mb-4">
            <select className="input-field" value={selectedIncident} onChange={(e) => setSelectedIncident(e.target.value)}>
              <option value="">Select an incident...</option>
              {incidents.map((i) => (
                <option key={i.incident_id} value={i.incident_id}>
                  #{i.incident_id} - {i.incident_type} ({i.severity}) - {i.raw_text.slice(0, 40)}...
                </option>
              ))}
            </select>
            <button className="btn-primary whitespace-nowrap" onClick={handleGenerateAlert}>Generate</button>
          </div>
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {alerts.map((a) => (
              <li key={a.alert_id} className="text-sm border-b border-slate-100 dark:border-slate-700 pb-2 text-slate-600 dark:text-slate-300">
                {a.alert_text}
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-2">
            <Sparkles size={18} /> Generative AI Scenario Generator
          </h2>
          <div className="flex gap-2 mb-4">
            <select className="input-field" value={selectedScenario} onChange={(e) => setSelectedScenario(e.target.value)}>
              <option value="">Random scenario type</option>
              {scenarioTypes.map((t) => (
                <option key={t} value={t}>{t.replace("_", " ")}</option>
              ))}
            </select>
            <button className="btn-primary whitespace-nowrap" onClick={handleGenerateScenario} disabled={loadingScenario}>
              {loadingScenario ? "Generating..." : "Generate"}
            </button>
          </div>
          {scenario && (
            <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
              <div className="text-xs uppercase font-semibold text-primary-600 mb-1">
                {scenario.scenario_type.replace("_", " ")}
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-200 mb-3">{scenario.description}</p>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Recommended Actions:</div>
              <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-300 space-y-1">
                {scenario.recommended_actions.map((a, idx) => <li key={idx}>{a}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
