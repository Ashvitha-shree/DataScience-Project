import React from "react";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, ArcElement, Title, Tooltip, Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend
);

const baseOptions = {
  responsive: true,
  plugins: { legend: { labels: { color: "#64748b" } } },
  scales: {
    x: { ticks: { color: "#64748b" }, grid: { color: "rgba(100,116,139,0.1)" } },
    y: { ticks: { color: "#64748b" }, grid: { color: "rgba(100,116,139,0.1)" } },
  },
};

export function SpeedTrendChart({ labels, data }) {
  return (
    <Line
      data={{
        labels,
        datasets: [{
          label: "Average Speed (km/h)",
          data,
          borderColor: "#2563eb",
          backgroundColor: "rgba(37,99,235,0.15)",
          tension: 0.35,
          fill: true,
        }],
      }}
      options={baseOptions}
    />
  );
}

export function CongestionBarChart({ labels, data }) {
  return (
    <Bar
      data={{
        labels,
        datasets: [{
          label: "Vehicle Count",
          data,
          backgroundColor: "#0ea5e9",
          borderRadius: 6,
        }],
      }}
      options={baseOptions}
    />
  );
}

export function CongestionDoughnutChart({ low, medium, high }) {
  return (
    <Doughnut
      data={{
        labels: ["Low", "Medium", "High"],
        datasets: [{
          data: [low, medium, high],
          backgroundColor: ["#22c55e", "#f59e0b", "#ef4444"],
          borderWidth: 0,
        }],
      }}
      options={{ plugins: { legend: { position: "bottom", labels: { color: "#64748b" } } } }}
    />
  );
}
