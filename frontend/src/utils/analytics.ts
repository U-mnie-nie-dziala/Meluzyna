import { Sector, AnalysisData } from '../types';

// Removed hardcoded mock data (sectorData, topPerformersData) to ensure strictly "No Data" is shown when backend fails or lacks data.

export function generateAnalysis(sector: Sector): AnalysisData {
  // Return explicit "No Data" / Sentinel state
  return {
    marketCap: 'Brak danych',
    revenue: 'Brak danych',
    growth: 0,
    profitMargin: 0,
    roe: 0,
    debtToEquity: 0,
    peRatio: 0,
    dividendYield: 0,
    totalCompanies: 0,
    topPerformers: [],
    riskLevel: 'Medium',
    outlook: 'N/A',
    demographics: -1,         // Sentinel for "No Data"
    growthSpeed: -1,          // Sentinel for "No Data"
    mediaSentiment: -1,       // Sentinel for "No Data"
    stockMarketSentiment: -1, // Sentinel for "No Data"
    combinedScore: -1,        // Sentinel for "No Data"
  };
}

export async function fetchSectorAnalysis(sector: Sector): Promise<AnalysisData> {
  try {
    // Dual fetch using soft-handling (return null if failed)
    const [detailsData, scoresData] = await Promise.all([
      fetch(`http://127.0.0.1:8001/markets/scores/${sector}`).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`http://127.0.0.1:8001/scores/${sector}`).then(r => r.ok ? r.json() : null).catch(() => null)
    ]);

    // If both failed, we really have nothing -> Return explicit "No Data" state
    if (!detailsData && !scoresData) {
      console.warn("Both endpoints failed data fetch. Returning No Data state.");
      return generateAnalysis(sector);
    }

    // Default object for details if missing
    const defDetails = {
      total_cap_pln: 0,
      median_margin: 0,
      median_roe: 0,
      median_pe: 0,
      median_divident_yield: 0,
      companies_count: 0,
      safety_score: 50,
      rating: 'N/A'
    };

    // Default object for scores if missing
    const defScores = {
      gus_score: null,
      market_score: null,
      ceidg_score: null,
      social_score: null,
      final_score: null
    };

    const d = detailsData || defDetails;
    const s = scoresData || defScores;

    console.log("Analytics details:", d);
    console.log("Analytics scores:", s);

    return {
      marketCap: d.total_cap_pln ? new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN', notation: 'compact' }).format(d.total_cap_pln) : 'Brak danych',
      revenue: 'Brak danych',
      growth: 0,
      profitMargin: Number(d.median_margin || 0),
      roe: Number(d.median_roe || 0),
      debtToEquity: 0,
      peRatio: Number(d.median_pe || 0),
      dividendYield: Number(d.median_divident_yield || 0),
      totalCompanies: d.companies_count || 0,
      topPerformers: [],
      riskLevel: d.safety_score > 70 ? 'Low' : d.safety_score > 40 ? 'Medium' : 'High',
      outlook: d.rating === 'AAA' || d.rating === 'AA' ? 'Positive' : d.rating === 'CCC' ? 'Negative' : 'Neutral',

      // New mapped metrics - using -1 sentinel if data is missing, NO MOCKS
      demographics: -1,
      growthSpeed: s.gus_score !== null ? s.gus_score : -1,
      mediaSentiment: s.social_score !== null ? s.social_score : -1,
      stockMarketSentiment: s.market_score !== null ? s.market_score : -1,
      combinedScore: (s.final_score !== null && s.final_score !== 0) ? s.final_score : -1,
    };
  } catch (error) {
    console.error("Error fetching sector analysis:", error);
    return generateAnalysis(sector);
  }
}
