"use client";

import React from "react";

interface Skill {
    name: string;
    category: string;
    level: string;
    years_experience: number | null;
}

interface SkillsChartProps {
    skills: Skill[];
    strengths: string[];
    areasToImprove: string[];
}

const levelToPercent: Record<string, number> = {
    beginner: 25,
    intermediate: 50,
    advanced: 75,
    expert: 100,
};

const levelColors: Record<string, string> = {
    beginner: "#f59e0b",
    intermediate: "#06b6d4",
    advanced: "#6366f1",
    expert: "#10b981",
};

const categoryIcons: Record<string, string> = {
    technical: "⚡",
    soft: "🤝",
    language: "🌐",
    tool: "🔧",
};

export default function SkillsChart({
    skills,
    strengths,
    areasToImprove,
}: SkillsChartProps) {
    // Group skills by category
    const grouped = skills.reduce<Record<string, Skill[]>>((acc, skill) => {
        const cat = skill.category || "other";
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(skill);
        return acc;
    }, {});

    return (
        <div className="space-y-6">
            {/* Skills by Category */}
            {Object.entries(grouped).map(([category, catSkills]) => (
                <div key={category} className="glass-card p-5">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
                        <span>{categoryIcons[category] || "📋"}</span>
                        {category} skills
                    </h3>
                    <div className="space-y-3">
                        {catSkills.map((skill, i) => {
                            const pct = levelToPercent[skill.level] || 50;
                            const color = levelColors[skill.level] || "#6366f1";
                            return (
                                <div key={i} className="group">
                                    <div className="mb-1 flex items-center justify-between">
                                        <span className="text-sm font-medium text-[var(--foreground)]">
                                            {skill.name}
                                        </span>
                                        <span
                                            className="rounded-full px-2 py-0.5 text-xs font-medium"
                                            style={{
                                                background: `${color}22`,
                                                color: color,
                                            }}
                                        >
                                            {skill.level}
                                        </span>
                                    </div>
                                    <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--border)]">
                                        <div
                                            className="h-full rounded-full transition-all duration-700 ease-out"
                                            style={{
                                                width: `${pct}%`,
                                                background: `linear-gradient(90deg, ${color}, ${color}aa)`,
                                            }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}

            {/* Strengths & Areas to Improve */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {strengths.length > 0 && (
                    <div className="glass-card p-5">
                        <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--success)]">
                            💪 Strengths
                        </h3>
                        <ul className="space-y-2">
                            {strengths.map((s, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-[var(--foreground)]">
                                    <span className="mt-1 text-[var(--success)]">✓</span>
                                    {s}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                {areasToImprove.length > 0 && (
                    <div className="glass-card p-5">
                        <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--warning)]">
                            📈 Areas to Improve
                        </h3>
                        <ul className="space-y-2">
                            {areasToImprove.map((a, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-[var(--foreground)]">
                                    <span className="mt-1 text-[var(--warning)]">→</span>
                                    {a}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
