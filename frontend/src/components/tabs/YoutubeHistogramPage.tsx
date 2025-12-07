import { useEffect, useState } from "react";
import { RiskTab } from "./RiskTab";
import { fetchYoutubeHistogram } from "./fetchYoutubeHistogram";
import { AnalysisData } from "./types";

export default function YoutubeHistogramPage() {
  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    fetchYoutubeHistogram()
      .then(setData)
      .catch((err) => console.error("Error:", err));
  }, []);

  if (!data) return <p>Loading histogram...</p>;

  return <RiskTab data={data} />;
}
