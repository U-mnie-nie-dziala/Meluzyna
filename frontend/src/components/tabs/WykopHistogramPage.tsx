import { useEffect, useState } from "react";
import { RiskTab } from "./RiskTab";
import { fetchYoutubeHistogram } from "./fetchYoutubeHistogram";
import { AnalysisData } from "./types";
import { fetchWykopHistogram } from "./fetchWykopHistogram";

export default function WykopHistogramPage({ sector }) {

  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    fetchWykopHistogram(sector)
      .then(setData)
      .catch((err) => console.error("Error:", err));
  }, []);

  if (!data) return <p>Loading histogram...</p>;

  return <RiskTab data={data} name={"Wykop"} />;
}
