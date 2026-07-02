import React from "react";

export function StatCard({ title, value, icon: Icon, color = "primary" }) {
  const colorMap = {
    primary: "bg-primary-50 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400",
    green: "bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    amber: "bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
    red: "bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400",
  };
  return (
    <div className="card flex items-center justify-between">
      <div>
        <div className="text-sm text-slate-500 dark:text-slate-400">{title}</div>
        <div className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-1">{value}</div>
      </div>
      {Icon && (
        <div className={`p-3 rounded-xl ${colorMap[color]}`}>
          <Icon size={22} />
        </div>
      )}
    </div>
  );
}

export function Badge({ children, level }) {
  const colors = {
    low: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
    medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
    high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
    critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  };
  return <span className={`badge ${colors[level] || colors.low}`}>{children}</span>;
}
