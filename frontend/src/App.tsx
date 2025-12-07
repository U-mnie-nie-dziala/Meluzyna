import { useState } from 'react';
import { TrendingUp, BarChart3 } from 'lucide-react';
import SectorSelector from './components/SectorSelector';
import StatisticsDisplay from './components/StatisticsDisplay';
import { Sector, AnalysisData } from './types';
import { fetchSectorAnalysis } from './utils/analytics';

function App() {
  const [selectedSector, setSelectedSector] = useState<Sector | ''>('');
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!selectedSector) return;

    setIsAnalyzing(true);

    try {
      const data = await fetchSectorAnalysis(selectedSector);
      setAnalysisData(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2.5 rounded-lg">
              <BarChart3 className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Platforma Analityki Bankowej</h1>
              <p className="text-sm text-slate-600">Kompleksowa analiza i statystyki sektorowe</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-6">
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <SectorSelector
                selectedSector={selectedSector}
                onSectorChange={setSelectedSector}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={!selectedSector || isAnalyzing}
              className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700
                       disabled:bg-slate-300 disabled:cursor-not-allowed transition-all duration-200
                       flex items-center gap-2 shadow-sm hover:shadow-md"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  Analizuj
                </>
              )}
            </button>
          </div>
        </div>

        {analysisData && (
          <StatisticsDisplay data={analysisData} sector={selectedSector as Sector} />
        )}

        {!analysisData && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-16 text-center">
            <div className="max-w-md mx-auto">
              <div className="bg-slate-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Ready to Analyze</h3>
              <p className="text-slate-600">
                Select a sector from the dropdown above and click "Analyze" to view comprehensive financial statistics and insights.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
