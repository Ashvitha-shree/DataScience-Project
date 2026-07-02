import React, { useEffect, useState } from "react";
import { Activity, AlertTriangle, MessageSquareText, Bot } from "lucide-react";
import { StatCard, Badge } from "../components/Card.jsx";
import { SpeedTrendChart, CongestionDoughnutChart } from "../components/TrafficChart.jsx";
import { getTrafficData, getIncidents, getAlerts, getAgentLogs } from "../api/client.js";

export default function Dashboard() {
  const [traffic, setTraffic] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [agentLogs, setAgentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [t, i, a, l] = await Promise.all([
          getTrafficData({ limit: 20 }), getIncidents(10), getAlerts(10), getAgentLogs(10),
        ]);
        setTraffic(t.data);
        setIncidents(i.data);
        setAlerts(a.data);
        setAgentLogs(l.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const congestionCounts = traffic.reduce(
    (acc, t) => {
      if (t.congestion_level) acc[t.congestion_level] = (acc[t.congestion_level] || 0) + 1;
      return acc;
    },
    { low: 0, medium: 0, high: 0 }
  );

  if (loading) return <div className="text-center py-12 text-slate-500">Loading dashboard...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">Live overview of city traffic conditions</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Traffic Records (recent)" value={traffic.length} icon={Activity} color="primary" />
        <StatCard title="Active Incidents" value={incidents.length} icon={AlertTriangle} color="amber" />
        <StatCard title="Alerts Generated" value={alerts.length} icon={MessageSquareText} color="red" />
        <StatCard title="Agent Decisions" value={agentLogs.length} icon={Bot} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Recent Average Speed Trend</h2>
          <SpeedTrendChart
            labels={traffic.slice().reverse().map((t) => t.record_time)}
            data={traffic.slice().reverse().map((t) => t.avg_speed)}
          />
        </div>
        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Congestion Breakdown</h2>
          <CongestionDoughnutChart {...congestionCounts} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Live Incident Feed</h2>
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {incidents.map((i) => (
              <li key={i.incident_id} className="text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-slate-700 dark:text-slate-200">{i.incident_type}</span>
                  <Badge level={i.severity}>{i.severity}</Badge>
                </div>
                <p className="text-slate-500 dark:text-slate-400 text-xs mt-1">{i.raw_text}</p>
              </li>
            ))}
            {incidents.length === 0 && <p className="text-sm text-slate-400">No incidents yet.</p>}
          </ul>
        </div>

        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Generated Alerts</h2>
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {alerts.map((a) => (
              <li key={a.alert_id} className="text-sm border-b border-slate-100 dark:border-slate-700 pb-2 text-slate-600 dark:text-slate-300">
                {a.alert_text}
              </li>
            ))}
            {alerts.length === 0 && <p className="text-sm text-slate-400">No alerts yet.</p>}
          </ul>
        </div>

        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Agent Decisions</h2>
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {agentLogs.map((l) => (
              <li key={l.log_id} className="text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-slate-700 dark:text-slate-200">{l.decision}</span>
                  <Badge level={l.urgency}>{l.urgency}</Badge>
                </div>
                <p className="text-slate-500 dark:text-slate-400 text-xs mt-1">{l.reason}</p>
              </li>
            ))}
            {agentLogs.length === 0 && <p className="text-sm text-slate-400">No agent decisions yet.</p>}
          </ul>
        </div>
      </div>
    </div>
  );
}
