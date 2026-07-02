import React, { useEffect, useState } from "react";
import { Plus, Upload, Download, Sparkles } from "lucide-react";
import {
  getRoads, getTrafficData, createTrafficData, uploadTrafficCsv,
  downloadTrafficCsv, getPrediction, trainModel,
} from "../api/client.js";
import { Badge } from "../components/Card.jsx";

const EMPTY_FORM = {
  road_id: "", vehicle_count: "", avg_speed: "", weather: "clear",
  record_date: new Date().toISOString().slice(0, 10),
  record_time: new Date().toTimeString().slice(0, 8),
  day_of_week: new Date().toLocaleDateString("en-US", { weekday: "long" }),
};

export default function TrafficData() {
  const [roads, setRoads] = useState([]);
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [predictions, setPredictions] = useState({});
  const [trainMsg, setTrainMsg] = useState("");

  const load = async () => {
    const [r, t] = await Promise.all([getRoads(), getTrafficData({ limit: 50 })]);
    setRoads(r.data);
    setRecords(t.data);
  };

  useEffect(() => { load(); }, []);

  const roadName = (id) => roads.find((r) => r.road_id === id)?.road_name || `Road #${id}`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createTrafficData({ ...form, road_id: parseInt(form.road_id) });
    setForm(EMPTY_FORM);
    setShowForm(false);
    load();
  };

  const handleCsvUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const res = await uploadTrafficCsv(file);
    alert(`Inserted ${res.data.inserted} rows. Errors: ${res.data.errors.length}`);
    load();
  };

  const handleDownload = async () => {
    const res = await downloadTrafficCsv();
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = "traffic_data_export.csv";
    a.click();
  };

  const handlePredict = async (trafficId) => {
    const res = await getPrediction(trafficId);
    setPredictions((p) => ({ ...p, [trafficId]: res.data }));
  };

  const handleTrain = async () => {
    setTrainMsg("Training...");
    const res = await trainModel();
    setTrainMsg(`Accuracy: ${(res.data.accuracy * 100).toFixed(2)}% | F1: ${(res.data.f1_score * 100).toFixed(2)}%`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Traffic Data</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">Manage sensor readings and run ML predictions</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button className="btn-secondary flex items-center gap-2" onClick={handleTrain}>
            <Sparkles size={16} /> Train ML Model
          </button>
          <label className="btn-secondary flex items-center gap-2 cursor-pointer">
            <Upload size={16} /> Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <button className="btn-secondary flex items-center gap-2" onClick={handleDownload}>
            <Download size={16} /> Download CSV
          </button>
          <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} /> Add Record
          </button>
        </div>
      </div>

      {trainMsg && (
        <div className="card text-sm text-primary-700 dark:text-primary-400 font-medium">
          Random Forest Training Result: {trainMsg}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="card grid grid-cols-1 md:grid-cols-4 gap-4">
          <select className="input-field" required value={form.road_id}
                  onChange={(e) => setForm({ ...form, road_id: e.target.value })}>
            <option value="">Select Road</option>
            {roads.map((r) => <option key={r.road_id} value={r.road_id}>{r.road_name}</option>)}
          </select>
          <input className="input-field" type="number" placeholder="Vehicle Count" required
                 value={form.vehicle_count} onChange={(e) => setForm({ ...form, vehicle_count: e.target.value })} />
          <input className="input-field" type="number" step="0.1" placeholder="Avg Speed (km/h)" required
                 value={form.avg_speed} onChange={(e) => setForm({ ...form, avg_speed: e.target.value })} />
          <select className="input-field" value={form.weather}
                  onChange={(e) => setForm({ ...form, weather: e.target.value })}>
            <option value="clear">Clear</option>
            <option value="rain">Rain</option>
            <option value="fog">Fog</option>
            <option value="storm">Storm</option>
          </select>
          <input className="input-field" type="date" required value={form.record_date}
                 onChange={(e) => setForm({ ...form, record_date: e.target.value })} />
          <input className="input-field" type="time" step="1" required value={form.record_time}
                 onChange={(e) => setForm({ ...form, record_time: e.target.value })} />
          <input className="input-field" placeholder="Day of Week" value={form.day_of_week}
                 onChange={(e) => setForm({ ...form, day_of_week: e.target.value })} />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">Save</button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="card overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
              <th className="py-2 pr-4">Road</th>
              <th className="py-2 pr-4">Vehicles</th>
              <th className="py-2 pr-4">Speed</th>
              <th className="py-2 pr-4">Weather</th>
              <th className="py-2 pr-4">Date / Time</th>
              <th className="py-2 pr-4">Congestion</th>
              <th className="py-2 pr-4">ML Prediction</th>
            </tr>
          </thead>
          <tbody>
            {records.map((t) => (
              <tr key={t.traffic_id} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4 font-medium text-slate-700 dark:text-slate-200">{roadName(t.road_id)}</td>
                <td className="py-2 pr-4">{t.vehicle_count}</td>
                <td className="py-2 pr-4">{t.avg_speed} km/h</td>
                <td className="py-2 pr-4 capitalize">{t.weather}</td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{t.record_date} {t.record_time}</td>
                <td className="py-2 pr-4">
                  {t.congestion_level ? <Badge level={t.congestion_level}>{t.congestion_level}</Badge> : "-"}
                </td>
                <td className="py-2 pr-4">
                  {predictions[t.traffic_id] ? (
                    <Badge level={predictions[t.traffic_id].predicted_level}>
                      {predictions[t.traffic_id].predicted_level} ({(predictions[t.traffic_id].confidence * 100).toFixed(0)}%)
                    </Badge>
                  ) : (
                    <button onClick={() => handlePredict(t.traffic_id)} className="text-primary-600 text-xs font-medium hover:underline">
                      Predict
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
