import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Map, BarChart3, AlertTriangle, MessageSquareText,
  Bot, FileText, TrafficCone,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/roads", label: "Roads", icon: Map },
  { to: "/traffic", label: "Traffic Data", icon: BarChart3 },
  { to: "/incidents", label: "Incidents", icon: AlertTriangle },
  { to: "/alerts", label: "Alerts & Scenarios", icon: MessageSquareText },
  { to: "/agent", label: "Agent Decisions", icon: Bot },
  { to: "/reports", label: "Reports", icon: FileText },
];

export default function Sidebar({ open }) {
  return (
    <aside
      className={`${open ? "w-64" : "w-0"} transition-all duration-200 overflow-hidden
        bg-slate-900 text-slate-100 flex flex-col shrink-0`}
    >
      <div className="flex items-center gap-2 px-5 py-5 border-b border-slate-800">
        <TrafficCone className="text-primary-500" size={26} />
        <span className="font-bold text-lg whitespace-nowrap">Smart Traffic</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 text-xs text-slate-500 border-t border-slate-800">
        AI-Based Smart City Traffic Management System
      </div>
    </aside>
  );
}
