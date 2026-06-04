import { motion } from 'framer-motion';
import { TrendingDown, Flame, Wind, AlertTriangle, Factory } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const kpiData = [
  { label: 'Total CO₂e', value: '124.5K', unit: 'tonnes', change: '-8.3%', icon: Wind, positive: true },
  { label: 'Flare Volume', value: '892K', unit: 'm³/day', change: '-12.1%', icon: Flame, positive: true },
  { label: 'Emission Intensity', value: '3.42', unit: 'kg/bbl', change: '-5.7%', icon: TrendingDown, positive: true },
  { label: 'Risk Events', value: '23', unit: 'this month', change: '+2', icon: AlertTriangle, positive: false },
  { label: 'Active Facilities', value: '15', unit: 'monitored', change: '0', icon: Factory, positive: true },
];

const emissionTrend = Array.from({ length: 30 }, (_, i) => ({
  day: `Day ${i + 1}`,
  co2e: 4000 + Math.random() * 2000 - i * 30,
  flareVolume: 30000 + Math.random() * 10000 - i * 200,
}));

const facilityRanking = [
  { name: 'FAC-001', emissions: 18500, compliance: 92 },
  { name: 'FAC-003', emissions: 15200, compliance: 87 },
  { name: 'FAC-007', emissions: 14800, compliance: 95 },
  { name: 'FAC-012', emissions: 12100, compliance: 78 },
  { name: 'FAC-005', emissions: 11300, compliance: 91 },
];

const complianceDist = [
  { name: 'Compliant', value: 68, color: '#10b981' },
  { name: 'Warning', value: 22, color: '#f59e0b' },
  { name: 'Non-Compliant', value: 10, color: '#ef4444' },
];

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function Dashboard() {
  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">ESG Overview Dashboard</h1>
        <p className="text-carbon-400 mt-1">Real-time emission intelligence & flare gas monitoring</p>
      </div>

      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {kpiData.map((kpi) => (
          <div key={kpi.label} className="card-hover">
            <div className="flex items-center justify-between mb-3">
              <kpi.icon className="w-5 h-5 text-esg-400" />
              <span className={`text-xs font-medium ${kpi.positive ? 'text-esg-400' : 'text-red-400'}`}>
                {kpi.change}
              </span>
            </div>
            <p className="kpi-value text-white">{kpi.value}</p>
            <p className="kpi-label mt-1">{kpi.label}</p>
            <p className="text-xs text-carbon-500 mt-0.5">{kpi.unit}</p>
          </div>
        ))}
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Emission Trend (30 Days)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={emissionTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="co2e" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={2} name="CO₂e (tonnes)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Compliance Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={complianceDist} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value">
                {complianceDist.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {complianceDist.map((d) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-xs text-carbon-400">{d.name}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      <motion.div variants={item} className="card">
        <h3 className="text-lg font-semibold mb-4">Facility Emission Ranking</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={facilityRanking}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            <Bar dataKey="emissions" fill="#10b981" radius={[4, 4, 0, 0]} name="CO₂e (tonnes)" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </motion.div>
  );
}
