// src/components/StatisticsDisplay.tsx
import { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  AlertCircle,
  Award,
} from 'lucide-react';
import { AnalysisData, Sector } from '../types';
import SectorRanking from '../SectorRanking';
import ChartsTab from './ChartsTab';
import { RiskTab } from './tabs/RiskTab';
import { exampleRiskData } from './exampleHistogramData';
import YoutubeHistogramPage from './tabs/YoutubeHistogramPage';

interface StatisticsDisplayProps {
  data: AnalysisData;
  sector: Sector;
}



type Tab = 'overview' | 'performance' | 'media' | 'stock-market' | 'charts';

export default function StatisticsDisplay({ data, sector }: StatisticsDisplayProps) {
  const [activeTab, setActiveTab] = useState<Tab>('overview');



  const tabs = [
    { id: 'overview' as Tab, label: 'Przegląd', icon: BarChart3 },
    { id: 'performance' as Tab, label: 'Ranking Sektorów', icon: Activity },
    { id: 'media' as Tab, label: 'Media', icon: AlertCircle },
    { id: 'charts' as Tab, label: 'Wykresy', icon: TrendingUp },
    { id: 'stock-market' as Tab, label: 'Giełda', icon: AlertCircle },
  ];

  // ...

  {/* Tu jest Twój nowy ranking zamiast tabeli Value A/B */ }
  { activeTab === 'performance' && <SectorRanking /> }

  { activeTab === 'media' && <RiskTab data={data} /> }

  { activeTab === 'charts' && <ChartsTab sector={sector} /> }

  { activeTab === 'stock-market' && <StockMarket sector={sector} /> }

  const sectorName = sector.charAt(0).toUpperCase() + sector.slice(1);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
        <h2 className="text-xl font-bold text-slate-900">
          Analiza sektora {sectorName}
        </h2>
        <p className="text-sm text-slate-600 mt-1">
          Szczegółowe dane finansowe i kluczowe wnioski
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
                          ${activeTab === tab.id
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
        {/* Przekazujemy sector do OverviewTab dla CEIDG */}
        {activeTab === 'overview' && <OverviewTab data={data} sector={sector} />}

        {/* Tu jest Twój nowy ranking zamiast tabeli Value A/B */}
        {activeTab === 'performance' && <SectorRanking />}

        {activeTab === 'media' && <YoutubeHistogramPage />}

        {activeTab === 'charts' && <ChartsTab sector={sector} />}

        {activeTab === 'stock-market' && <StockMarket sector={sector} />}
      </div>
    </div>
  );
}

// ------------------------------------------------------------------
// PONIŻEJ SĄ FUNKCJE POMOCNICZE, KTÓRYCH BRAKOWAŁO I POWODOWAŁY BŁĄD
// ------------------------------------------------------------------

function StockMarket({ sector }: { sector: Sector }) {
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8001/markets/scores/${sector}`);
        if (res.ok) {
          const data = await res.json();
          setLatest(data);
        }
      } catch (error) {
        console.error("Error fetching sector score:", error);
      }
    };

    if (sector) {
      fetchLatest();
    }
  }, [sector]);

  return (
    <div>
      <h3 className="text-lg font-bold mb-4">Dane Giełdowe ({sector})</h3>
      {latest ? (
        <pre className="bg-slate-50 p-4 rounded-lg text-sm overflow-auto">
          {JSON.stringify(latest, null, 2)}
        </pre>
      ) : (
        "Ładowanie..."
      )}
    </div>
  );
}

function OverviewTab({ data, sector }: { data: AnalysisData, sector: Sector }) {
  const isNoData = data.combinedScore === -1;

  // --- NOWE LOGIKA DLA CEIDG ---
  const [ceidgScore, setCeidgScore] = useState<number | null>(null);

  useEffect(() => {
    const fetchCeidg = async () => {
      setCeidgScore(null);
      try {
        const response = await fetch(`http://127.0.0.1:8001/ceidg/scores/${sector}`);
        if (response.ok) {
          const result = await response.json();
          // Sprawdzamy czy to obiekt czy liczba
          const scoreValue = result.score || result.wskaznik || result.final_score || result.safety_score;

          if (scoreValue !== undefined) {
            setCeidgScore(Number(scoreValue));
          } else if (typeof result === 'number') {
            setCeidgScore(result);
          }
        }
      } catch (e) {
        console.error("Błąd pobierania CEIDG", e);
        setCeidgScore(null);
      }
    }

    if (sector) {
      fetchCeidg();
    }
  }, [sector]);
  // -----------------------------

  let scoreColor = '';
  let scoreBg = '';

  if (isNoData) {
    scoreColor = 'text-slate-400';
    scoreBg = 'bg-slate-50 border-slate-200';
  } else {
    scoreColor = data.combinedScore >= 60 ? 'text-emerald-600' : data.combinedScore >= 40 ? 'text-yellow-600' : 'text-red-600';
    scoreBg = data.combinedScore >= 60 ? 'bg-emerald-50 border-emerald-200' : data.combinedScore >= 40 ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200';
  }

  let CombinedIcon = AlertCircle;
  if (!isNoData) {
    if (data.combinedScore >= 60) CombinedIcon = TrendingUp;
    else if (data.combinedScore >= 40) CombinedIcon = Activity;
    else CombinedIcon = TrendingDown;
  }

  return (
    <div className="space-y-6">
      {/* Large Combined Score Indicator */}
      <div className={`rounded-2xl p-6 border-2 flex items-center justify-between ${scoreBg}`}>
        <div>
          <h3 className="text-lg font-bold text-slate-800 mb-1">Syntetyczny Wskaźnik Sektora</h3>
          <p className="text-slate-600 text-sm max-w-md">
            Zbiorczy wskaźnik łączący ocenę bezpieczeństwa giełdowego, opinie mediów, demografię firm i wskaźniki ekonomiczne GUS.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className={`block text-5xl font-black ${scoreColor}`}>
              {isNoData ? '--' : data.combinedScore}
            </span>
            <span className="text-sm font-semibold text-slate-500 uppercase tracking-wider">
              {isNoData ? 'Brak danych' : '/ 100 pkt'}
            </span>
          </div>
          <CombinedIcon className={`w-12 h-12 ${scoreColor}`} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Dane z CEIDG */}
        <ScoreCard
          label="Demografia firm CEIDG"
          value={ceidgScore !== null ? ceidgScore : -1}
        />

        <ScoreCard
          label="Tempo wzrostu GUS"
          value={data.growthSpeed}
        />
        <ScoreCard
          label="Media"
          value={data.mediaSentiment}
        />
        <ScoreCard
          label="Giełda"
          value={data.stockMarketSentiment}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Wskaźniki Finansowe</h3>
          <div className="space-y-3">
            <RatioRow label="Marża Zysku" value={`${data.profitMargin}%`} />
            <RatioRow label="ROE" value={`${data.roe}%`} />
            <RatioRow label="Wskaźnik C/Z (P/E)" value={data.peRatio.toFixed(2)} />
            <RatioRow label="Stopa Dywidendy" value={`${data.dividendYield}%`} />
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
            <Award className="w-4 h-4" />
            Liderzy Sektora
          </h3>
          <div className="space-y-3">
            {data.topPerformers.map((performer, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-slate-700 font-medium">{performer.name}</span>
                <span
                  className={`text-sm font-semibold ${performer.performance > 0 ? 'text-emerald-600' : 'text-red-600'
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



function RiskMetricCard({ label, value, optimal, status }: { label: string, value: string, optimal: string, status: 'good' | 'moderate' | 'high' }) {
  const getStatusColor = () => {
    if (status === 'good') return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (status === 'moderate') return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  }

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor()}`}>
      <p className="text-xs font-semibold opacity-80 uppercase mb-1">{label}</p>
      <div className="flex justify-between items-end">
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs opacity-80">Optymalnie: {optimal}</p>
      </div>
    </div>
  )
}

function ScoreCard({ label, value }: { label: string; value: number }) {
  const isNoData = value === -1;

  const getColorClass = (val: number) => {
    if (isNoData) return 'text-slate-400';
    if (val >= 60) return 'text-emerald-500';
    if (val >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getBgClass = (val: number) => {
    if (isNoData) return 'bg-slate-50 border-slate-200';
    if (val >= 60) return 'bg-emerald-50 border-emerald-100';
    if (val >= 40) return 'bg-yellow-50 border-yellow-100';
    return 'bg-red-50 border-red-100';
  };

  const getTrendIcon = (val: number) => {
    if (isNoData) return <AlertCircle className="w-8 h-8 text-slate-300" />;
    if (val >= 60) return <TrendingUp className="w-8 h-8" />;
    if (val >= 40) return <Activity className="w-8 h-8" />;
    return <TrendingDown className="w-8 h-8" />;
  };

  const colorClass = getColorClass(value);
  const bgClass = getBgClass(value);

  return (
    <div className={`border rounded-lg p-5 hover:shadow-md transition-all ${bgClass}`}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-lg font-bold text-slate-700">{label}</p>
        <div className={colorClass}>
          {getTrendIcon(value)}
        </div>
      </div>

      <div className="flex items-end gap-2">
        {isNoData ? (
          <p className="text-xl font-bold text-slate-400">Brak danych</p>
        ) : (
          <p className={`text-2xl font-bold ${colorClass}`}>{value.toFixed(1)}/100</p>
        )}
      </div>

      {!isNoData && (
        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${valToTailwind(value)}`}
            style={{ width: `${value}%` }}
          />
        </div>
      )}
    </div>
  );
}

function valToTailwind(val: number) {
  if (val >= 60) return 'bg-emerald-500';
  if (val >= 40) return 'bg-yellow-500';
  return 'bg-red-500';
}

function RatioRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}
