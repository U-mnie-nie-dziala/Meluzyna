export type Sector =
  | 'technology'
  | 'healthcare'
  | 'finance'
  | 'energy'
  | 'consumer'
  | 'industrial'
  | 'realestate'
  | 'utilities';

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
}
