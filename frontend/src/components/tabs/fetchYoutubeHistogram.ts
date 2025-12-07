import { AnalysisData } from "./types";
import { API_BASE_URL } from "../../config";

export async function fetchYoutubeHistogram(sector: string): Promise<AnalysisData> {

  console.log(sector);

  const res = await fetch(`${API_BASE_URL}/komentarz_youtube/${sector}`);

  if (!res.ok) {
    throw new Error("Failed to fetch komentarz_youtube");
  }

  const json = await res.json();

  return {
    riskLevel: "Medium", // placeholder
    records: json.map((item: any) => ({
      id: item.id,
      tag_id: item.tag_id,
      post: item.komentarz,
      emocje: Math.round(item.emocje ?? 0),
    })),
  };
}
