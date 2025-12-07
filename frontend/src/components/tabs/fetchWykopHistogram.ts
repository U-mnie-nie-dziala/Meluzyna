import { AnalysisData } from "./types";
import { API_BASE_URL } from "../../config";

export async function fetchWykopHistogram(sector: string): Promise<AnalysisData> {

  console.log(sector);
  const res = await fetch(`${API_BASE_URL}/post_wykop/${sector}`);

  if (!res.ok) {
    throw new Error("Failed to fetch post_wykop");
  }

  const json = await res.json();

  return {
    riskLevel: "Medium", // placeholder
    records: json.map((item: any) => ({
      id: item.id,
      tag_id: item.tag_id,
      post: item.post || item.komentarz, // Handle 'post' or 'komentarz' depending on backend
      emocje: Math.round(item.emocje ?? 0),
    })),
  };
}
