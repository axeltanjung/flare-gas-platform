import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import FacilityDetail from './pages/FacilityDetail';
import AIInsights from './pages/AIInsights';
import Compliance from './pages/Compliance';
import Optimization from './pages/Optimization';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="facility/:id" element={<FacilityDetail />} />
        <Route path="insights" element={<AIInsights />} />
        <Route path="compliance" element={<Compliance />} />
        <Route path="optimization" element={<Optimization />} />
      </Route>
    </Routes>
  );
}
