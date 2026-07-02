import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext.jsx";

import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Roads from "./pages/Roads.jsx";
import TrafficData from "./pages/TrafficData.jsx";
import Incidents from "./pages/Incidents.jsx";
import Alerts from "./pages/Alerts.jsx";
import AgentLogs from "./pages/AgentLogs.jsx";
import Reports from "./pages/Reports.jsx";
import Layout from "./components/Layout.jsx";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="roads" element={<Roads />} />
        <Route path="traffic" element={<TrafficData />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="agent" element={<AgentLogs />} />
        <Route path="reports" element={<Reports />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
