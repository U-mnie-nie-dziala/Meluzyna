import { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import { Sector } from '../types';

import { API_BASE_URL } from '../config';

interface ChartsTabProps {
    sector: Sector;
}

interface HistoryPoint {
    date: string;
    wykop: number | null;
    youtube: number | null;
    ceidg: number | null;
    gus: number | null;
}

export default function ChartsTab({ sector }: ChartsTabProps) {
    const [data, setData] = useState<HistoryPoint[]>([]);
    const [days, setDays] = useState(90);
    const [loading, setLoading] = useState(true);

    // Toggle visible lines
    const [showWykop, setShowWykop] = useState(true);
    const [showYoutube, setShowYoutube] = useState(true);
    const [showCeidg, setShowCeidg] = useState(true);
    const [showGus, setShowGus] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`${API_BASE_URL}/charts/history/${sector}?days=${days}`)
            .then(res => {
                if (!res.ok) throw new Error("Failed to fetch history");
                return res.json();
            })
            .then(d => {
                setData(d);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setData([]);
                setLoading(false);
            });
    }, [sector, days]);

    if (loading) return <div className="p-8 text-center text-slate-500">Ładowanie wykresów...</div>;

    return (
        <div className="space-y-6">
            {/* Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-200">
                <div className="flex gap-2">
                    {[30, 90, 180, 365].map(d => (
                        <button
                            key={d}
                            onClick={() => setDays(d)}
                            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors
                ${days === d ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-300 hover:bg-slate-50'}`}
                        >
                            {d} Dni
                        </button>
                    ))}
                </div>

                <div className="flex flex-wrap gap-3">
                    <Toggle label="Wykop" color="#ea580c" active={showWykop} onClick={() => setShowWykop(!showWykop)} />
                    <Toggle label="Youtube" color="#dc2626" active={showYoutube} onClick={() => setShowYoutube(!showYoutube)} />
                    <Toggle label="CEIDG" color="#059669" active={showCeidg} onClick={() => setShowCeidg(!showCeidg)} />
                    <Toggle label="GUS" color="#2563eb" active={showGus} onClick={() => setShowGus(!showGus)} />
                </div>
            </div>

            {/* Chart */}
            <div className="bg-white p-4 rounded-lg border border-slate-200 h-[400px]">
                {data.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis
                                dataKey="date"
                                tick={{ fontSize: 12 }}
                                tickFormatter={(val) => new Date(val).toLocaleDateString()}
                            />
                            <YAxis />
                            <Tooltip
                                labelFormatter={(val) => new Date(val).toLocaleDateString()}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            <Legend />

                            {showWykop && (
                                <Line
                                    type="monotone"
                                    dataKey="wykop"
                                    name="Wykop (Sentyment)"
                                    stroke="#ea580c"
                                    strokeWidth={2}
                                    dot={false}
                                    connectNulls
                                />
                            )}
                            {showYoutube && (
                                <Line
                                    type="monotone"
                                    dataKey="youtube"
                                    name="Youtube (Sentyment)"
                                    stroke="#dc2626"
                                    strokeWidth={2}
                                    dot={false}
                                    connectNulls
                                />
                            )}
                            {showCeidg && (
                                <Line
                                    type="monotone"
                                    dataKey="ceidg"
                                    name="CEIDG (Wskaźnik)"
                                    stroke="#059669"
                                    strokeWidth={2}
                                    dot={false}
                                    connectNulls
                                />
                            )}
                            {showGus && (
                                <Line
                                    type="monotone"
                                    dataKey="gus"
                                    name="GUS (Wskaźnik)"
                                    stroke="#2563eb"
                                    strokeWidth={2}
                                    dot={false}
                                    connectNulls
                                />
                            )}
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-slate-400 italic">
                        Brak danych historycznych dla wybranego okresu.
                    </div>
                )}
            </div>
        </div>
    );
}

function Toggle({ label, color, active, onClick }: { label: string, color: string, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-all
        ${active ? 'bg-white shadow-sm' : 'bg-slate-100 opacity-60 grayscale'}`}
            style={{ borderColor: active ? color : 'transparent' }}
        >
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span style={{ color: active ? 'inherit' : '#64748b' }}>{label}</span>
        </button>
    );
}
