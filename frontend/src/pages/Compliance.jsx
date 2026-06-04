import { motion } from 'framer-motion';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

const facilityCompliance = [
  { facility: 'FAC-001', score: 94, status: 'compliant' },
  { facility: 'FAC-002', score: 88, status: 'compliant' },
  { facility: 'FAC-003', score: 72, status: 'warning' },
  { facility: 'FAC-004', score: 96, status: 'compliant' },
  { facility: 'FAC-005', score: 61, status: 'non_compliant' },
  { facility: 'FAC-006', score: 85, status: 'compliant' },
  { facility: 'FAC-007', score: 45, status: 'non_compliant' },
  { facility: 'FAC-008', score: 91, status: 'compliant' },
];

const riskTrend = Array.from({ length: 12 }, (_, i) => ({
  month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
  highRisk: Math.floor(Math.random() * 5 + (i > 8 ? 3 : 0)),
  mediumRisk: Math.floor(Math.random() * 10 + 5),
  violations: Math.floor(Math.random() * 3),
}));

const violations = [
  {
    regulation: 'EPA 40 CFR 60',
    threshold: '50,000 m³/day',
    observed: '67,200 m³/day',
    facility: 'FAC-007',
    severity: 'critical',
    date: '2024-01-14',
  },
  {
    regulation: 'EU ETS Phase IV',
    threshold: '20 kg CO₂e/bbl',
    observed: '24.3 kg CO₂e/bbl',
    facility: 'FAC-005',
    severity: 'high',
    date: '2024-01-12',
  },
  {
    regulation: 'OGMP 2.0',
    threshold: '5% methane slip',
    observed: '7.2% methane slip',
    facility: 'FAC-007',
    severity: 'high',
    date: '2024-01-10',
  },
  {
    regulation: 'World Bank Zero Flaring',
    threshold: 'Annual target',
    observed: 'On track (87%)',
    facility: 'ALL',
    severity: 'medium',
    date: '2024-01-08',
  },
];

export default function Compliance() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div>
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-esg-400" />
          <h1 className="text-2xl font-bold">Compliance & Risk Monitor</h1>
        </div>
        <p className="text-carbon-400 mt-1">Regulatory compliance tracking & emission threshold alerts</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Overall Score', value: '82.3%', icon: ShieldCheck, color: 'text-esg-400' },
          { label: 'Critical Violations', value: '2', icon: XCircle, color: 'text-red-400' },
          { label: 'Warnings', value: '5', icon: AlertTriangle, color: 'text-yellow-400' },
          { label: 'Compliant Facilities', value: '12/15', icon: CheckCircle, color: 'text-esg-400' },
        ].map((stat) => (
          <div key={stat.label} className="card">
            <stat.icon className={`w-5 h-5 ${stat.color} mb-2`} />
            <p className="text-xl font-bold">{stat.value}</p>
            <p className="text-xs text-carbon-400 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Facility Compliance Scores</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={facilityCompliance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="facility" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Bar dataKey="score" radius={[4, 4, 0, 0]} name="Compliance %">
                {facilityCompliance.map((entry, idx) => (
                  <motion.rect
                    key={idx}
                    fill={entry.score >= 90 ? '#10b981' : entry.score >= 70 ? '#f59e0b' : '#ef4444'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Risk Event Trend (Monthly)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="highRisk" stroke="#ef4444" strokeWidth={2} name="High Risk" />
              <Line type="monotone" dataKey="mediumRisk" stroke="#f59e0b" strokeWidth={2} name="Medium Risk" />
              <Line type="monotone" dataKey="violations" stroke="#8b5cf6" strokeWidth={2} name="Violations" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Regulatory Violations</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-carbon-700">
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Regulation</th>
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Threshold</th>
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Observed</th>
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Facility</th>
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Severity</th>
                <th className="text-left py-3 px-4 text-carbon-400 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {violations.map((v, idx) => (
                <tr key={idx} className="border-b border-carbon-800/50 hover:bg-carbon-800/30">
                  <td className="py-3 px-4 font-medium">{v.regulation}</td>
                  <td className="py-3 px-4 text-carbon-400">{v.threshold}</td>
                  <td className="py-3 px-4 text-red-400">{v.observed}</td>
                  <td className="py-3 px-4">{v.facility}</td>
                  <td className="py-3 px-4">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      v.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                      v.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {v.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-carbon-400">{v.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
