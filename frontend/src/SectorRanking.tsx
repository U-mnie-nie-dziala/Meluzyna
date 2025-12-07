import { useEffect, useState } from 'react';
import './Ranking.css';

// AKTUALIZACJA: Dodano ceidg_score zgodnie z Twoim nowym backendem
export interface SectorRankingItem {
  section_code: string;
  section_name: string;
  market_score: number | null;
  gus_score: number | null;
  ceidg_score: number | null; // <--- NOWE POLE
  final_score: number;
}

const SectorRanking = () => {
  const [sectors, setSectors] = useState<SectorRankingItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_URL}/scores`);

        if (!response.ok) {
          throw new Error('Błąd pobierania danych');
        }

        const data = await response.json();

        // Filtrujemy "Pozostałe"
        const filteredData = data.filter((item: SectorRankingItem) =>
          item.section_name !== "Pozostałe"
        );

        setSectors(filteredData);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError("Nie udało się pobrać rankingu.");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500">Ładowanie rankingu...</div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="ranking-list pt-4">
      {sectors.map((sector, index) => {
        let rankClass = "rank-other";
        if (index === 0) rankClass = "rank-1";
        if (index === 1) rankClass = "rank-2";
        if (index === 2) rankClass = "rank-3";

        return (
          <div key={sector.section_code} className={`ranking-card ${rankClass}`}>
            <div className="rank-position">#{index + 1}</div>

            <div className="sector-info">
              <div className="sector-code">PKD: {sector.section_code}</div>
              <h3 className="sector-name">{sector.section_name}</h3>
            </div>

            <div className="scores-container">
              <div className="score-box final-score">
                <span className="score-label" style={{ color: '#bdc3c7' }}>Wynik</span>
                <div className="score-value">{sector.final_score.toFixed(1)}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SectorRanking;
