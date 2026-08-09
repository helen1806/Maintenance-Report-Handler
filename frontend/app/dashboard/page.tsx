"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function Dashboard() {
    const [patterns, setPatterns] = useState([]);
    const [scores, setScores] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch data from our new FastAPI Intelligence Endpoints
        Promise.all([
            fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/intelligence/analytics/patterns`).then(res => res.json()),
            fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/intelligence/analytics/reliability`).then(res => res.json())
        ]).then(([patternData, scoreData]) => {
            setPatterns(patternData.patterns);
            setScores(scoreData.scores);
            setLoading(false);
        });
    }, []);

    if (loading) {
        return <div className="flex h-screen items-center justify-center text-xl font-semibold">Loading Intelligence Data...</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="mb-8 border-b pb-4">
                <h1 className="text-4xl font-bold text-gray-900 tracking-tight">Engineering Command Center</h1>
                <p className="text-gray-500 mt-2">Real-time asset reliability and failure pattern discovery powered by Neo4j.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Reliability Scores Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
                        📊 Asset Reliability Scores
                    </h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={scores}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="asset" tick={{ fill: '#6b7280' }} />
                                <YAxis domain={[0, 100]} tick={{ fill: '#6b7280' }} />
                                <Tooltip cursor={{ fill: '#f3f4f6' }} contentStyle={{ borderRadius: '8px' }} />
                                <Legend />
                                <Bar dataKey="reliability_score" fill="#3b82f6" name="Reliability Score (%)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Pattern Discovery Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
                        🔍 Common Failure Patterns
                    </h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={patterns} layout="vertical" margin={{ left: 50 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" tick={{ fill: '#6b7280' }} />
                                <YAxis dataKey="failure_mode" type="category" tick={{ fontSize: 12, fill: '#374151' }} />
                                <Tooltip cursor={{ fill: '#f3f4f6' }} contentStyle={{ borderRadius: '8px' }} />
                                <Legend />
                                <Bar dataKey="frequency" fill="#ef4444" name="Occurrences" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>
        </div>
    );
}
