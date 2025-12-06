import { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart3,
  Activity,
  AlertCircle,
  Award,
} from 'lucide-react';
import { AnalysisData, Sector } from '../types';

interface StatisticsDisplayProps {
  data: AnalysisData;
  sector: Sector;
}

type Tab = 'overview' | 'performance' | 'risk';

export default function StatisticsDisplay({ data, sector }: StatisticsDisplayProps) {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const tabs = [
    { id: 'overview' as Tab, label: 'Overview', icon: BarChart3 },
    { id: 'performance' as Tab, label: 'Performance', icon: Activity },
    { id: 'risk' as Tab, label: 'Risk Analysis', icon: AlertCircle },
    { id: 'stock-market' as Tab, label: 'Giełda', icon: AlertCircle },
  ];

  const sectorName = sector.charAt(0).toUpperCase() + sector.slice(1);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
        <h2 className="text-xl font-bold text-slate-900">
          {sectorName} Sector Analysis
        </h2>
        <p className="text-sm text-slate-600 mt-1">
          Comprehensive financial statistics and insights
        </p>
      </div>

      <div className="border-b border-slate-200">
        <div className="flex">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-4 font-semibold text-sm transition-all relative
                          ${
                            activeTab === tab.id
                              ? 'text-blue-600 bg-white'
                              : 'text-slate-600 bg-slate-50 hover:bg-slate-100'
                          }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </div>
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="p-6">
        {activeTab === 'overview' && <OverviewTab data={data} />}
        {activeTab === 'performance' && <PerformanceTab data={data} />}
        {activeTab === 'risk' && <RiskTab data={data} />}
        {activeTab === 'stock-market' && <StockMarket />}
      </div>
    </div>
  );
}


function StockMarket() {
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/markets/reports/latest");
        const data = await res.json();
        setLatest(data);
      } catch (error) {
        console.error("Error fetching latest report:", error);
      }
    };

    fetchLatest();
  }, []); 

  return (
    <div>
      <h1>Latest Market Report</h1>
      {latest ? (
        <pre>{JSON.stringify(latest, null, 2)}</pre>
      ) : (
        "Loading..."
      )}
    </div>
  );
}


function OverviewTab({ data }: { data: AnalysisData }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={DollarSign}
          label="Market Cap"
          value={data.marketCap}
          iconBg="bg-emerald-100"
          iconColor="text-emerald-600"
        />
        <StatCard
          icon={TrendingUp}
          label="Total Revenue"
          value={data.revenue}
          iconBg="bg-blue-100"
          iconColor="text-blue-600"
        />
        <StatCard
          icon={Activity}
          label="Growth Rate"
          value={`${data.growth > 0 ? '+' : ''}${data.growth}%`}
          trend={data.growth > 0 ? 'up' : 'down'}
          iconBg="bg-amber-100"
          iconColor="text-amber-600"
        />
        <StatCard
          icon={PieChart}
          label="Companies"
          value={data.totalCompanies.toString()}
          iconBg="bg-violet-100"
          iconColor="text-violet-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Financial Ratios</h3>
          <div className="space-y-3">
            <RatioRow label="Profit Margin" value={`${data.profitMargin}%`} />
            <RatioRow label="Return on Equity" value={`${data.roe}%`} />
            <RatioRow label="P/E Ratio" value={data.peRatio.toFixed(2)} />
            <RatioRow label="Dividend Yield" value={`${data.dividendYield}%`} />
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
            <Award className="w-4 h-4" />
            Top Performers
          </h3>
          <div className="space-y-3">
            {data.topPerformers.map((performer, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-slate-700 font-medium">{performer.name}</span>
                <span
                  className={`text-sm font-semibold ${
                    performer.performance > 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}
                >
                  {performer.performance > 0 ? '+' : ''}
                  {performer.performance}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PerformanceTab({ data }: { data: AnalysisData }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Revenue Growth"
          value={`${data.growth}%`}
          description="Year-over-year revenue growth rate"
          trend={data.growth > 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Profit Margin"
          value={`${data.profitMargin}%`}
          description="Net profit as percentage of revenue"
          trend={data.profitMargin > 15 ? 'positive' : 'neutral'}
        />
        <MetricCard
          label="Return on Equity"
          value={`${data.roe}%`}
          description="Profitability relative to shareholders' equity"
          trend={data.roe > 12 ? 'positive' : 'neutral'}
        />
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-start gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 mb-2">Sector Outlook</h3>
            <p className="text-sm text-slate-700 leading-relaxed">
              The sector demonstrates{' '}
              <span className="font-semibold">
                {data.outlook.toLowerCase()}
              </span>{' '}
              outlook with{' '}
              <span className="font-semibold">{data.growth > 0 ? 'positive' : 'negative'}</span>{' '}
              growth trajectory. Current market conditions indicate{' '}
              <span className="font-semibold">{data.riskLevel.toLowerCase()}</span> risk levels
              with strong fundamentals across key metrics.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function RiskTab({ data }: { data: AnalysisData }) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Low':
        return 'text-emerald-600 bg-emerald-100';
      case 'Medium':
        return 'text-amber-600 bg-amber-100';
      case 'High':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-slate-600 bg-slate-100';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between p-6 bg-slate-50 rounded-lg border border-slate-200">
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-1">Overall Risk Level</h3>
          <p className="text-2xl font-bold text-slate-900">{data.riskLevel}</p>
        </div>
        <div className={`px-4 py-2 rounded-lg font-semibold ${getRiskColor(data.riskLevel)}`}>
          {data.riskLevel} Risk
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RiskMetricCard
          label="Debt-to-Equity Ratio"
          value={data.debtToEquity.toFixed(2)}
          optimal="< 2.0"
          status={data.debtToEquity < 2 ? 'good' : data.debtToEquity < 3 ? 'moderate' : 'high'}
        />
        <RiskMetricCard
          label="P/E Ratio"
          value={data.peRatio.toFixed(2)}
          optimal="15-25"
          status={
            data.peRatio >= 15 && data.peRatio <= 25
              ? 'good'
              : data.peRatio < 15 || data.peRatio <= 35
              ? 'moderate'
              : 'high'
          }
        />
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-5">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-amber-900 mb-1">Risk Considerations</h4>
            <p className="text-sm text-amber-800 leading-relaxed">
              Monitor debt levels and valuation metrics closely. Diversification across multiple
              companies within the sector is recommended to mitigate individual company risks.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  trend,
  iconBg,
  iconColor,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  trend?: 'up' | 'down';
  iconBg: string;
  iconColor: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className={`${iconBg} p-2 rounded-lg`}>
          <Icon className={`w-5 h-5 ${iconColor}`} />
        </div>
        {trend && (
          <div className={trend === 'up' ? 'text-emerald-600' : 'text-red-600'}>
            {trend === 'up' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
          </div>
        )}
      </div>
      <p className="text-sm text-slate-600 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function RatioRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
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
