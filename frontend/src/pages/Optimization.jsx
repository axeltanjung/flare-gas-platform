import { motion } from 'framer-motion';
import { Zap, ArrowDown, Wrench, Clock, Target } from 'lucide-react';

const optimizations = [
  {
    category: 'Compressor Scheduling',
    suggestion: 'Shift compressor maintenance windows to periods of lower gas throughput (02:00-06:00). Analysis shows 34% reduction in emergency flaring during off-peak maintenance.',
    estimatedReduction: 18.5,
    priority: 'HIGH',
    metric: 'Flare Volume',
    icon: Clock,
    savings: '~12,400 tonnes CO₂e/year',
  },
  {
    category: 'Valve Control Optimization',
    suggestion: 'Implement predictive valve opening strategy based on upstream pressure trends. Current reactive approach causes 15% excess flaring during pressure spikes.',
    estimatedReduction: 12.3,
    priority: 'HIGH',
    metric: 'Emission Intensity',
    icon: Wrench,
    savings: '~8,200 tonnes CO₂e/year',
  },
  {
    category: 'Gas Recovery System',
    suggestion: 'Install vapor recovery units at FAC-005 and FAC-007. Cost-benefit analysis shows ROI within 14 months based on carbon credit value and energy recovery.',
    estimatedReduction: 35.0,
    priority: 'CRITICAL',
    metric: 'Total Emissions',
    icon: Target,
    savings: '~28,000 tonnes CO₂e/year',
  },
  {
    category: 'Combustion Efficiency',
    suggestion: 'Increase pilot gas flow by 8% and install wind shields on flare stacks FS-03 and FS-05. Current combustion efficiency of 96.2% can reach 98.5%.',
    estimatedReduction: 8.7,
    priority: 'MEDIUM',
    metric: 'Methane Slip',
    icon: Zap,
    savings: '~4,800 tonnes CO₂e/year',
  },
  {
    category: 'Startup/Shutdown Protocol',
    suggestion: 'Implement staged startup protocol with 30-minute ramp periods. Current abrupt startups generate 2.4x normal flare volumes during first hour.',
    estimatedReduction: 6.2,
    priority: 'MEDIUM',
    metric: 'Peak Emissions',
    icon: Clock,
    savings: '~3,100 tonnes CO₂e/year',
  },
];

const scenarios = [
  {
    name: 'Baseline (Current)',
    annualCO2e: 124500,
    intensity: 3.42,
    compliance: 82,
  },
  {
    name: 'Moderate Optimization',
    annualCO2e: 98200,
    intensity: 2.71,
    compliance: 91,
  },
  {
    name: 'Aggressive Reduction',
    annualCO2e: 72800,
    intensity: 2.01,
    compliance: 97,
  },
  {
    name: 'Zero Routine Flaring',
    annualCO2e: 45100,
    intensity: 1.24,
    compliance: 99,
  },
];

export default function Optimization() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div>
        <div className="flex items-center gap-3">
          <Zap className="w-6 h-6 text-esg-400" />
          <h1 className="text-2xl font-bold">Optimization Recommendations</h1>
        </div>
        <p className="text-carbon-400 mt-1">AI-driven operational adjustments for emission reduction</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Emission Reduction Scenarios</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {scenarios.map((scenario, idx) => (
            <motion.div
              key={scenario.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.1 }}
              className={`p-4 rounded-lg border ${
                idx === 0 ? 'border-carbon-700 bg-carbon-800/30' :
                idx === 3 ? 'border-esg-500/50 bg-esg-900/20' :
                'border-carbon-700/50 bg-carbon-800/20'
              }`}
            >
              <p className="text-xs text-carbon-400 font-medium uppercase">{scenario.name}</p>
              <p className="text-2xl font-bold mt-2">{(scenario.annualCO2e / 1000).toFixed(1)}K</p>
              <p className="text-xs text-carbon-500">tonnes CO₂e/year</p>
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-carbon-400">Intensity</span>
                  <span>{scenario.intensity} kg/bbl</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-carbon-400">Compliance</span>
                  <span className={scenario.compliance >= 95 ? 'text-esg-400' : ''}>{scenario.compliance}%</span>
                </div>
              </div>
              {idx > 0 && (
                <div className="mt-3 flex items-center gap-1 text-esg-400">
                  <ArrowDown className="w-3 h-3" />
                  <span className="text-xs font-medium">
                    {Math.round((1 - scenario.annualCO2e / scenarios[0].annualCO2e) * 100)}% reduction
                  </span>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Recommended Actions</h3>
        {optimizations.map((opt, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="card-hover"
          >
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                opt.priority === 'CRITICAL' ? 'bg-red-500/20' :
                opt.priority === 'HIGH' ? 'bg-orange-500/20' : 'bg-yellow-500/20'
              }`}>
                <opt.icon className={`w-5 h-5 ${
                  opt.priority === 'CRITICAL' ? 'text-red-400' :
                  opt.priority === 'HIGH' ? 'text-orange-400' : 'text-yellow-400'
                }`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">{opt.category}</h4>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    opt.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                    opt.priority === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {opt.priority}
                  </span>
                </div>
                <p className="text-sm text-carbon-400 mt-1">{opt.suggestion}</p>
                <div className="flex items-center gap-6 mt-3">
                  <div className="flex items-center gap-1.5">
                    <ArrowDown className="w-4 h-4 text-esg-400" />
                    <span className="text-sm text-esg-400 font-medium">{opt.estimatedReduction}% reduction</span>
                  </div>
                  <span className="text-xs text-carbon-500">Metric: {opt.metric}</span>
                  <span className="text-xs text-esg-500 font-medium">{opt.savings}</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
