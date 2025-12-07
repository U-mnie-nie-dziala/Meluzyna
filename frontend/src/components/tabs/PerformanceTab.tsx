import { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  AlertCircle,
  Award,
  Users,
  Newspaper,
} from 'lucide-react';
import { AnalysisData, Sector } from '../../types';


interface StatisticsDisplayProps {
  data: AnalysisData;
  sector: Sector;
}

function MetricCard({
  label,
  value,
  description,
  trend,
}: {
  label: string;
  value: string;
  description: string;
  trend: 'positive' | 'neutral' | 'negative';
}) {

  const trendColors = {
    positive: 'border-emerald-200 bg-emerald-50',
    neutral: 'border-slate-200 bg-slate-50',
    negative: 'border-red-200 bg-red-50',
  };

  return (
    <div className={`border rounded-lg p-5 ${trendColors[trend]}`}>
      <p className="text-sm font-semibold text-slate-700 mb-2">{label}</p>
      <p className="text-3xl font-bold text-slate-900 mb-2">{value}</p>
      <p className="text-xs text-slate-600 leading-relaxed">{description}</p>
    </div>
  );
}

function RiskMetricCard({
  label,
  value,
  optimal,
  status,
}: {
  label: string;
  value: string;
  optimal: string;
  status: 'good' | 'moderate' | 'high';
}) {
  const statusConfig = {
    good: { color: 'text-emerald-600', bg: 'bg-emerald-100', label: 'Optimal' },
    moderate: { color: 'text-amber-600', bg: 'bg-amber-100', label: 'Moderate' },
    high: { color: 'text-red-600', bg: 'bg-red-100', label: 'Elevated' },
  };

  const config = statusConfig[status];

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-slate-700">{label}</span>
        <span className={`text-xs font-semibold px-2 py-1 rounded ${config.bg} ${config.color}`}>
          {config.label}
        </span>
      </div>
      <p className="text-2xl font-bold text-slate-900 mb-1">{value}</p>
      <p className="text-xs text-slate-600">Optimal range: {optimal}</p>
    </div>
  );
}

export function PerformanceTab({ data }: { data: AnalysisData }) {
  return (
    <table className="min-w-full border-collapse border border-gray-300">
      <thead>
        <tr className="bg-gray-100">
          <th className="p-2 border border-gray-300">Nazwa</th>
          <th className="p-2 border border-gray-300">Wynik</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td className="p-2 border border-gray-300">Value A</td>
          <td className="p-2 border border-gray-300">Value B</td>
        </tr>
      </tbody>
    </table>


    );
} 