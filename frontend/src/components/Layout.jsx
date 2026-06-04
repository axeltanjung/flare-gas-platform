import { Outlet, NavLink } from 'react-router-dom';
import {
  BarChart3,
  Building2,
  Brain,
  ShieldCheck,
  Zap,
  Leaf,
} from 'lucide-react';

const navigation = [
  { name: 'ESG Overview', path: '/', icon: BarChart3 },
  { name: 'Facility Detail', path: '/facility/FAC-001', icon: Building2 },
  { name: 'AI Insights', path: '/insights', icon: Brain },
  { name: 'Compliance & Risk', path: '/compliance', icon: ShieldCheck },
  { name: 'Optimization', path: '/optimization', icon: Zap },
];

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 bg-carbon-900 border-r border-carbon-800 flex flex-col">
        <div className="p-6 border-b border-carbon-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-esg-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white">FlareGas AI</h1>
              <p className="text-xs text-carbon-400">ESG Intelligence</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? 'nav-link-active' : 'nav-link'
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-carbon-800">
          <div className="card !p-3">
            <p className="text-xs text-carbon-400">Platform Status</p>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 bg-esg-500 rounded-full animate-pulse" />
              <span className="text-xs text-esg-400">Models Active</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto bg-carbon-950">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
