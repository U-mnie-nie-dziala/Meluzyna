export type Sector = string;

export interface AnalysisData {
  marketCap: string;
  revenue: string;
  growth: number;
  profitMargin: number;
  roe: number;
  debtToEquity: number;
  peRatio: number;
  dividendYield: number;
  totalCompanies: number;
  topPerformers: Array<{
    name: string;
    performance: number;
  }>;
  riskLevel: 'Low' | 'Medium' | 'High';
  outlook: 'Positive' | 'Neutral' | 'Negative';

  // New metrics (0-100)
  demographics: number;
  growthSpeed: number;
  mediaSentiment: number;
  stockMarketSentiment: number;
}
