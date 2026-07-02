import React, { useEffect, useState } from "react";
import { Plus, Trash2, Edit2 } from "lucide-react";
import { getRoads, createRoad, updateRoad, deleteRoad } from "../api/client.js";
import MapView from "../components/MapView.jsx";

const EMPTY_FORM = {
  road_name: "", location: "", latitude: "", longitude: "", road_type: "arterial", signal_id: "",
};

export default function Roads() {
  const [roads, setRoads] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const loadRoads = async () => {
    const res = await getRoads();
    setRoads(res.data);
  };

  useEffect(() => { loadRoads(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      latitude: form.latitude ? parseFloat(form.latitude) : null,
      longitude: form.longitude ? parseFloat(form.longitude) : null,
    };
    if (editingId) {
      await updateRoad(editingId, payload);
    } else {
      await createRoad(payload);
    }
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowForm(false);
    loadRoads();
  };

  const handleEdit = (road) => {
    setForm({
      road_name: road.road_name, location: road.location || "",
      latitude: road.latitude || "", longitude: road.longitude || "",
      road_type: road.road_type, signal_id: road.signal_id || "",
    });
    setEditingId(road.road_id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (confirm("Delete this road? This will also delete its traffic data.")) {
      await deleteRoad(id);
      loadRoads();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Road Management</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">Add, edit, or remove monitored roads</p>
        </div>
        <button
          className="btn-primary flex items-center gap-2"
          onClick={() => { setForm(EMPTY_FORM); setEditingId(null); setShowForm(!showForm); }}
        >
          <Plus size={18} /> Add Road
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card grid grid-cols-1 md:grid-cols-3 gap-4">
          <input className="input-field" placeholder="Road Name" required
                 value={form.road_name} onChange={(e) => setForm({ ...form, road_name: e.target.value })} />
          <input className="input-field" placeholder="Location"
                 value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <select className="input-field" value={form.road_type}
                  onChange={(e) => setForm({ ...form, road_type: e.target.value })}>
            <option value="highway">Highway</option>
            <option value="arterial">Arterial</option>
            <option value="residential">Residential</option>
            <option value="collector">Collector</option>
          </select>
          <input className="input-field" placeholder="Latitude" type="number" step="any"
                 value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
          <input className="input-field" placeholder="Longitude" type="number" step="any"
                 value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
          <input className="input-field" placeholder="Signal ID"
                 value={form.signal_id} onChange={(e) => setForm({ ...form, signal_id: e.target.value })} />
          <div className="md:col-span-3 flex gap-2">
            <button type="submit" className="btn-primary">{editingId ? "Update Road" : "Save Road"}</button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="card">
        <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-3">Road Map</h2>
        <MapView roads={roads} />
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
              <th className="py-2 pr-4">Road Name</th>
              <th className="py-2 pr-4">Location</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Signal ID</th>
              <th className="py-2 pr-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {roads.map((r) => (
              <tr key={r.road_id} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4 font-medium text-slate-700 dark:text-slate-200">{r.road_name}</td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{r.location}</td>
                <td className="py-2 pr-4 capitalize text-slate-500 dark:text-slate-400">{r.road_type}</td>
                <td className="py-2 pr-4 text-slate-500 dark:text-slate-400">{r.signal_id}</td>
                <td className="py-2 pr-4 flex gap-2">
                  <button onClick={() => handleEdit(r)} className="text-primary-600 hover:text-primary-700">
                    <Edit2 size={16} />
                  </button>
                  <button onClick={() => handleDelete(r.road_id)} className="text-red-500 hover:text-red-600">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
