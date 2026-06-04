import { motion } from 'framer-motion';
import { Brain, TrendingUp, TrendingDown, Lightbulb } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
} from 'recharts';

const shapFeatures = [
  { feature: 'gas_flow_rate', importance: 0.234, direction: 'positive' },
  { feature: 'gas_pressure', importance: 0.187, direction: 'positive' },
  { feature: 'compressor_load', importance: 0.142, direction: 'positive' },
  { feature: 'combustion_temperature', importance: 0.098, direction: 'negative' },
  { feature: 'methane_ratio', importance: 0.087, direction: 'positive' },
  { feature: 'valve_opening_pct', importance: 0.072, direction: 'negative' },
  { feature: 'upstream_pressure', importance: 0.065, direction: 'positive' },
  { feature: 'emergency_event', importance: 0.058, direction: 'positive' },
  { feature: 'wind_speed', importance: 0.032, direction: 'negative' },
  { feature: 'ambient_temp', importance: 0.025, direction: 'negative' },
];

const radarData = [
  { subject: 'Gas Flow', A: 89, fullMark: 100 },
  { subject: 'Pressure', A: 76, fullMark: 100 },
  { subject: 'Compressor', A: 65, fullMark: 100 },
  { subject: 'Temperature', A: 52, fullMark: 100 },
  { subject: 'Methane', A: 48, fullMark: 100 },
  { subject: 'Valve Control', A: 38, fullMark: 100 },
];

const operationalInsights = [
  {
    title: 'High Gas Flow Rate Correlation',
    description: 'Gas flow rate is the primary driver of emissions, accounting for 23.4% of prediction variance. Facilities with flow rates > 400 m³/h show 3.2x higher emission levels.',
    impact: 'high',
    actionable: true,
  },
  {
    title: 'Compressor Load Inefficiency',
    description: 'Compressor loads above 80% correlate with 45% increase in flare events. Scheduling maintenance during low-demand periods can reduce unnecessary flaring.',
    impact: 'medium',
    actionable: true,
  },
  {
    title: 'Temperature-Combustion Optimization',
    description: 'Higher combustion temperatures (>900°C) improve destruction efficiency. Current average of 850°C leaves 2% uncombusted methane.',
    impact: 'medium',
    actionable: true,
  },
  {
    title: 'Wind Speed Dispersion Effect',
    description: 'Wind speeds > 15 m/s reduce ground-level concentrations but increase incomplete combustion risk by 8%.',
    impact: 'low',
    actionable: false,
  },
];

export default function AIInsights() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div>
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-esg-400" />
          <h1 className="text-2xl font-bold">AI Insights & Explainability</h1>
        </div>
        <p className="text-carbon-400 mt-1">SHAP-based emission driver analysis & operational intelligence</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Feature Importance (SHAP Values)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={shapFeatures} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" stroke="#64748b" tick={{ fontSize: 11 }} width={140} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              <Bar dataKey="importance" radius={[0, 4, 4, 0]} name="SHAP Importance">
                {shapFeatures.map((entry, idx) => (
                  <motion.rect
                    key={idx}
                    fill={entry.direction === 'positive' ? '#10b981' : '#06b6d4'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Driver Impact Radar</h3>
          <ResponsiveContainer width="100%" height={350}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Radar name="Impact" dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.2} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          Operational Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {operationalInsights.map((insight, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="p-4 bg-carbon-800/50 rounded-lg border border-carbon-700/50"
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  insight.impact === 'high' ? 'bg-red-500/20 text-red-400' :
                  insight.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-carbon-600/30 text-carbon-400'
                }`}>
                  {insight.impact} impact
                </span>
                {insight.actionable && (
                  <span className="text-xs bg-esg-500/20 text-esg-400 px-2 py-0.5 rounded-full">
                    Actionable
                  </span>
                )}
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">{insight.title}</h4>
              <p className="text-xs text-carbon-400 leading-relaxed">{insight.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
