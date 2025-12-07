import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { AlertCircle } from "lucide-react";
import { AnalysisData, RecordItem } from "./types";
import { fetchYoutubeHistogram } from "./fetchYoutubeHistogram";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);




export function RiskTab({ data }: { data: AnalysisData }) {
  const buildHistogram = (records: RecordItem[]) => {
    const counts = Array(101).fill(0);

    records.forEach((item) => {
      if (item.emocje >= 0 && item.emocje <= 100) {
        counts[item.emocje] += 1;
      }
    });

    return {
      labels: Array.from({ length: 101 }, (_, i) => i.toString()),
      values: counts,
    };
  };

  const histogram = buildHistogram(data.records);

  const histogramData = {
    labels: histogram.labels,
    datasets: [
      {
        label: "Liczba komentarzy",
        data: histogram.values,
        backgroundColor: "#38bdf8",
      },
    ],
  };

  return (
    <div className="space-y-6">

      <div className="p-6 bg-white border border-slate-200 rounded-lg shadow-sm">
        <h3 className="text-md font-semibold text-slate-800 mb-4">
          Histogram nastrojów komentarzy na Youtube w danym sektorze (0–100)
        </h3>
        <Bar data={histogramData} />
      </div>
    </div>
  );
}
