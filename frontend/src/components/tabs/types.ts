export type RecordItem = {
  id: number;
  tag_id: number;
  post: string;
  emocje: number;
};

export type AnalysisData = {
  riskLevel?: string;   
  records: RecordItem[];
};