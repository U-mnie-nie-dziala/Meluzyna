import { Sector, AnalysisData } from '../types';

const sectorData: Record<Sector, Partial<AnalysisData>> = {
  technology: {
    marketCap: '$4.2T',
    revenue: '$1.8T',
    growth: 12.5,
    profitMargin: 22.3,
    roe: 18.7,
    debtToEquity: 1.2,
    peRatio: 28.4,
    dividendYield: 1.2,
    totalCompanies: 847,
    riskLevel: 'Medium',
    outlook: 'Positive',
  },
  healthcare: {
    marketCap: '$3.1T',
    revenue: '$1.2T',
    growth: 8.3,
    profitMargin: 18.5,
    roe: 15.2,
    debtToEquity: 1.8,
    peRatio: 22.1,
    dividendYield: 2.4,
    totalCompanies: 623,
    riskLevel: 'Low',
    outlook: 'Positive',
  },
  finance: {
    marketCap: '$5.8T',
    revenue: '$2.3T',
    growth: 6.7,
    profitMargin: 24.1,
    roe: 12.8,
    debtToEquity: 2.3,
    peRatio: 15.6,
    dividendYield: 3.1,
    totalCompanies: 1203,
    riskLevel: 'Medium',
    outlook: 'Neutral',
  },
  energy: {
    marketCap: '$2.4T',
    revenue: '$1.9T',
    growth: 15.2,
    profitMargin: 14.8,
    roe: 16.3,
    debtToEquity: 2.1,
    peRatio: 12.8,
    dividendYield: 4.2,
    totalCompanies: 412,
    riskLevel: 'High',
    outlook: 'Positive',
  },
  consumer: {
    marketCap: '$3.6T',
    revenue: '$2.1T',
    growth: 5.4,
    profitMargin: 11.2,
    roe: 13.5,
    debtToEquity: 1.6,
    peRatio: 19.3,
    dividendYield: 2.8,
    totalCompanies: 1547,
    riskLevel: 'Low',
    outlook: 'Neutral',
  },
  industrial: {
    marketCap: '$2.8T',
    revenue: '$1.5T',
    growth: 7.1,
    profitMargin: 13.6,
    roe: 14.2,
    debtToEquity: 1.9,
    peRatio: 18.7,
    dividendYield: 2.2,
    totalCompanies: 934,
    riskLevel: 'Medium',
    outlook: 'Positive',
  },
  realestate: {
    marketCap: '$1.9T',
    revenue: '$0.8T',
    growth: 4.2,
    profitMargin: 16.8,
    roe: 9.4,
    debtToEquity: 3.2,
    peRatio: 24.5,
    dividendYield: 3.8,
    totalCompanies: 567,
    riskLevel: 'Medium',
    outlook: 'Neutral',
  },
  utilities: {
    marketCap: '$1.5T',
    revenue: '$0.9T',
    growth: 3.8,
    profitMargin: 12.4,
    roe: 8.9,
    debtToEquity: 2.8,
    peRatio: 16.2,
    dividendYield: 3.5,
    totalCompanies: 289,
    riskLevel: 'Low',
    outlook: 'Neutral',
  },
};

const topPerformersData: Record<Sector, Array<{ name: string; performance: number }>> = {
  technology: [
    { name: 'TechCorp International', performance: 24.5 },
    { name: 'Digital Solutions Inc.', performance: 18.7 },
    { name: 'Cloud Systems Ltd.', performance: 15.3 },
  ],
  healthcare: [
    { name: 'MediPharm Group', performance: 16.2 },
    { name: 'BioHealth Systems', performance: 12.8 },
    { name: 'Wellness Corp', performance: 11.4 },
  ],
  finance: [
    { name: 'Global Banking Corp', performance: 14.3 },
    { name: 'Investment Holdings Ltd', performance: 10.7 },
    { name: 'Finance Capital Group', performance: 9.2 },
  ],
  energy: [
    { name: 'Energy Dynamics Inc.', performance: 28.5 },
    { name: 'Renewable Power Co.', performance: 22.1 },
    { name: 'Oil & Gas Partners', performance: 19.6 },
  ],
  consumer: [
    { name: 'Consumer Brands Inc.', performance: 11.8 },
    { name: 'Retail Solutions Co.', performance: 9.4 },
    { name: 'Food & Beverage Group', performance: 8.1 },
  ],
  industrial: [
    { name: 'Manufacturing Global', performance: 13.5 },
    { name: 'Heavy Industries Ltd.', performance: 11.2 },
    { name: 'Engineering Systems', performance: 10.8 },
  ],
  realestate: [
    { name: 'Property Holdings Inc.', performance: 9.7 },
    { name: 'Real Estate Trust', performance: 8.3 },
    { name: 'Commercial Properties', performance: 7.4 },
  ],
  utilities: [
    { name: 'Power & Water Corp', performance: 8.9 },
    { name: 'Electric Services Inc.', performance: 7.2 },
    { name: 'Utility Networks Ltd.', performance: 6.5 },
  ],
};

// ... existing code ...

// ... existing arrays ...

export function generateAnalysis(sector: Sector): AnalysisData {
  const baseData = sectorData[sector] || {
    marketCap: 'N/A',
    revenue: 'N/A',
    growth: 0,
    profitMargin: 0,
    roe: 0,
    debtToEquity: 0,
    peRatio: 0,
    dividendYield: 0,
    totalCompanies: 0,
    riskLevel: 'Medium',
    outlook: 'Neutral',
    demographics: 50,
    growthSpeed: 50,
    mediaSentiment: 50,
    stockMarketSentiment: 50,
  };
  const topPerformers = topPerformersData[sector] || [];

  return {
    marketCap: baseData.marketCap!,
    revenue: baseData.revenue!,
    growth: baseData.growth!,
    profitMargin: baseData.profitMargin!,
    roe: baseData.roe!,
    debtToEquity: baseData.debtToEquity!,
    peRatio: baseData.peRatio!,
    dividendYield: baseData.dividendYield!,
    totalCompanies: baseData.totalCompanies!,
    topPerformers,
    riskLevel: baseData.riskLevel!,
    outlook: baseData.outlook!,
    demographics: baseData.demographics || Math.floor(Math.random() * 100),
    growthSpeed: baseData.growthSpeed || Math.floor(Math.random() * 100),
    mediaSentiment: baseData.mediaSentiment || Math.floor(Math.random() * 100),
    stockMarketSentiment: baseData.stockMarketSentiment || Math.floor(Math.random() * 100),
  };
}

export async function fetchSectorAnalysis(sector: Sector): Promise<AnalysisData> {
  try {
    const response = await fetch(`http://127.0.0.1:8000/markets/scores/${sector}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Map backend data to frontend AnalysisData
    // Backend: SectionSchema
    // Frontend: AnalysisData

    return {
      marketCap: new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN', notation: 'compact' }).format(data.total_cap_pln),
      revenue: 'N/A', // Not in DB
      growth: 0, // Not in DB
      profitMargin: Number(data.median_margin), // Assuming raw value needs formatting? Backend is float.
      roe: Number(data.median_roe),
      debtToEquity: 0, // Not in DB
      peRatio: Number(data.median_pe),
      dividendYield: Number(data.median_divident_yield),
      totalCompanies: data.companies_count,
      topPerformers: [], // Not in DB
      riskLevel: data.safety_score > 70 ? 'Low' : data.safety_score > 40 ? 'Medium' : 'High',
      outlook: data.rating === 'AAA' || data.rating === 'AA' ? 'Positive' : data.rating === 'CCC' ? 'Negative' : 'Neutral', // Simple mapping
      demographics: Math.floor(Math.random() * 100), // Mock
      growthSpeed: Math.floor(Math.random() * 100), // Mock
      mediaSentiment: Math.floor(Math.random() * 100), // Mock
      stockMarketSentiment: Math.floor(Math.random() * 100), // Mock
    };
  } catch (error) {
    console.error("Error fetching sector analysis:", error);
    // Fallback to local data if fetch fails (safe failover)
    return generateAnalysis(sector);
  }
}

