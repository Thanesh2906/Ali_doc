import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  ZAxis
} from "recharts";
import { api } from "../api/client";

const COLORS = ["#2ECC71", "#F1C40F", "#E67E22", "#E74C3C"];

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState({
    risk_distribution: [],
    risk_trend: [],
    mc_vs_risk: [],
    department_heatmap: [],
    top_high_risk_employees: []
  });

  useEffect(() => {
    api
      .get("/admin/dashboard-metrics", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` }
      })
      .then((res) => setMetrics(res.data));
  }, []);

  return (
    <div className="dashboard-grid">
      <section>
        <h3>Workforce Risk Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={metrics.risk_distribution} dataKey="count" nameKey="risk_band" outerRadius={90}>
              {metrics.risk_distribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h3>Risk Trend Over Time</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={metrics.risk_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Line dataKey="avg_risk" stroke="#3498DB" />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h3>MC Days vs Risk Correlation</h3>
        <ResponsiveContainer width="100%" height={250}>
          <ScatterChart>
            <CartesianGrid />
            <XAxis dataKey="mc_days" name="MC Days" />
            <YAxis dataKey="risk" name="Risk" />
            <ZAxis range={[40]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={metrics.mc_vs_risk} fill="#16A085" />
          </ScatterChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h3>Department Risk Heatmap</h3>
        <div className="heatmap">
          {metrics.department_heatmap.map((item) => (
            <div
              key={`${item.department_name}-${item.risk_band}`}
              className="heat-cell"
              style={{ background: `rgba(231, 76, 60, ${Math.min(item.value / 100, 1)})` }}
            >
              <strong>{item.department_name}</strong>
              <span>{item.risk_band}: {item.value}%</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3>Top 10 High-Risk Employees</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={metrics.top_high_risk_employees}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="employee_id" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="high_claim_risk" fill="#9B59B6" />
          </BarChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}
