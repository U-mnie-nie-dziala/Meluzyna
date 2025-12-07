import { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  AlertCircle,
  Award,
} from 'lucide-react';
import { AnalysisData, Sector } from '../../types';

interface StatisticsDisplayProps {
  data: AnalysisData;
  sector: Sector;
}

type Tab = 'overview' | 'performance' | 'risk';

export function OverviewTab({ data }: { data: AnalysisData }) {

  // Determine color for large score
  const isNoData = data.combinedScore === -1;

  let scoreColor = '';
  let scoreBg = '';

  if (isNoData) {
    scoreColor = 'text-slate-400';
    scoreBg = 'bg-slate-50 border-slate-200';
  } else {
    scoreColor = data.combinedScore >= 60 ? 'text-emerald-600' : data.combinedScore >= 40 ? 'text-yellow-600' : 'text-red-600';
    scoreBg = data.combinedScore >= 60 ? 'bg-emerald-50 border-emerald-200' : data.combinedScore >= 40 ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200';
  }

  // Icon logic for Combined Score: Same behavior as ScoreCards (Result-based)
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
              {isNoData ? 'Brak danych' : '/ 100 Points'}
            </span>
          </div>
          <CombinedIcon className={`w-12 h-12 ${scoreColor}`} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard
          label="Demografia firm CEIDG"
          value={data.demographics}
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