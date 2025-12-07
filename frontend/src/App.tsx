import { useState } from 'react';
import { TrendingUp, BarChart3, LayoutDashboard } from 'lucide-react';
import SectorSelector from './components/SectorSelector';
import StatisticsDisplay from './components/StatisticsDisplay';
import SectorRanking from './SectorRanking'; // <--- Importujemy Twój nowy komponent
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 pb-12">
      <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Meluzyna Analytics</h1>
              <p className="text-xs text-slate-600">Platforma analizy ryzyka sektorowego</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* --- SEKCJA 1: Panel Kontrolny i Analiza Szczegółowa --- */}
        <section className="mb-12">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Analiza Indywidualna
            </h2>
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
                    Przetwarzanie...
                  </>
                ) : (
                  <>
                    <BarChart3 className="w-5 h-5" />
                    Analizuj Sektor
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Wyniki Analizy lub Placeholder */}
          {analysisData ? (
            <StatisticsDisplay data={analysisData} sector={selectedSector as Sector} />
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center border-dashed">
              <div className="max-w-md mx-auto">
                <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-8 h-8 text-slate-300" />
                </div>
                <h3 className="text-lg font-medium text-slate-900 mb-1">Gotowy do analizy</h3>
                <p className="text-slate-500 text-sm">
                  Wybierz sektor z listy powyżej, aby zobaczyć szczegółowe wskaźniki finansowe i ocenę ryzyka.
                </p>
              </div>
            </div>
          )}
        </section>


      </main>
    </div>
  );
}

export default App;
