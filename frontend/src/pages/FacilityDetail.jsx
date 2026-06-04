import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Building2, Flame, Wind, AlertTriangle, Activity } from 'lucide-react';

const facilityHistory = Array.from({ length: 60 }, (_, i) => ({
  date: `2024-${String(Math.floor(i / 30) + 1).padStart(2, '0')}-${String((i % 30) + 1).padStart(2, '0')}`,
  flareVolume: 2000 + Math.random() * 3000 + (i > 40 ? Math.random() * 5000 : 0),
  co2e: 5 + Math.random() * 8 + (i > 40 ? Math.random() * 15 : 0),
  intensity: 2 + Math.random() * 3,
}));

const gasComposition = [
  { component: 'Methane (CH₄)', percentage: 82.3, color: '#10b981' },
  { component: 'Ethane (C₂H₆)', percentage: 8.7, color: '#06b6d4' },
  { component: 'Propane (C₃H₈)', percentage: 4.2, color: '#8b5cf6' },
  { component: 'CO₂', percentage: 2.8, color: '#f59e0b' },
  { component: 'N₂ + Others', percentage: 2.0, color: '#64748b' },
];

const operationalEvents = [
  { time: '2024-01-15 03:22', event: 'Emergency Relief', severity: 'high', impact: '+4,200 m³' },
  { time: '2024-01-12 14:00', event: 'Compressor Trip', severity: 'medium', impact: '+1,800 m³' },
  { time: '2024-01-10 06:15', event: 'Startup Event', severity: 'low', impact: '+950 m³' },
  { time: '2024-01-08 22:30', event: 'Maintenance Window', severity: 'low', impact: '-200 m³' },
  { time: '2024-01-05 11:00', event: 'Abnormal Operation', severity: 'high', impact: '+3,100 m³' },
];

export default function FacilityDetail() {
  const { id } = useParams();

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Building2 className="w-6 h-6 text-esg-400" />
            <h1 className="text-2xl font-bold">Facility {id || 'FAC-001'}</h1>
          </div>
          <p className="text-carbon-400 mt-1">Detailed emission analysis & operational timeline</p>
        </div>
        <span className="badge-low">Compliant</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Flare Volume', value: '182K m³', icon: Flame, color: 'text-orange-400' },
          { label: 'CO₂ Equivalent', value: '12.4K tonnes', icon: Wind, color: 'text-esg-400' },
          { label: 'Risk Events', value: '8', icon: AlertTriangle, color: 'text-yellow-400' },
          { label: 'Uptime', value: '97.3%', icon: Activity, color: 'text-blue-400' },
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
          <h3 className="text-lg font-semibold mb-4">Flare Gas Volume History</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={facilityHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="flareVolume" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.1} name="Volume (m³)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Emission Intensity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={facilityHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="intensity" stroke="#10b981" strokeWidth={2} dot={false} name="kg CO₂e/bbl" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Gas Composition Analysis</h3>
          <div className="space-y-3">
            {gasComposition.map((gas) => (
              <div key={gas.component} className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: gas.color }} />
                <span className="text-sm text-carbon-300 flex-1">{gas.component}</span>
                <div className="w-48 bg-carbon-700 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-500"
                    style={{ width: `${gas.percentage}%`, backgroundColor: gas.color }}
                  />
                </div>
                <span className="text-sm font-medium w-12 text-right">{gas.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Operational Events Timeline</h3>
          <div className="space-y-3">
            {operationalEvents.map((event, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-carbon-800/50 rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  event.severity === 'high' ? 'bg-red-500' :
                  event.severity === 'medium' ? 'bg-yellow-500' : 'bg-esg-500'
                }`} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{event.event}</span>
                    <span className={`text-xs font-mono ${
                      event.impact.startsWith('+') ? 'text-red-400' : 'text-esg-400'
                    }`}>{event.impact}</span>
                  </div>
                  <span className="text-xs text-carbon-500">{event.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
