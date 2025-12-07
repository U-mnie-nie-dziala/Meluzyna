export async function fetchYoutubeHistogram(): Promise<AnalysisData> {
  const res = await fetch("http://127.0.0.1:8000/komentarz_youtube");

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
