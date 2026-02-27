"use client";

import React, { useState } from "react";

interface Opportunity {
    type: string;
    title: string;
    provider: string;
    url: string;
    description: string;
    required_skills: string[];
    match_score: number;
    reason: string;
}

interface RecommendationCardProps {
    opportunities: Opportunity[];
    title: string;
    icon: string;
    accentColor: string;
}

export default function RecommendationCard({
    opportunities,
    title,
    icon,
    accentColor,
}: RecommendationCardProps) {
    const [expanded, setExpanded] = useState<number | null>(null);

    if (!opportunities || opportunities.length === 0) return null;

    return (
        <div className="glass-card overflow-hidden">
            {/* Header */}
            <div
                className="flex items-center gap-3 border-b border-[var(--border)] px-6 py-4"
                style={{ borderLeftWidth: "3px", borderLeftColor: accentColor }}
            >
                <span className="text-xl">{icon}</span>
                <h3 className="text-base font-semibold text-[var(--foreground)]">{title}</h3>
                <span
                    className="ml-auto rounded-full px-2.5 py-0.5 text-xs font-medium"
                    style={{ background: `${accentColor}22`, color: accentColor }}
                >
                    {opportunities.length} found
                </span>
            </div>

            {/* Items */}
            <div className="divide-y divide-[var(--border)]">
                {opportunities.slice(0, 5).map((opp, i) => {
                    const scorePercent = Math.round((opp.match_score || 0) * 100);
                    const isExpanded = expanded === i;

                    return (
                        <div
                            key={i}
                            className="cursor-pointer px-6 py-4 transition-colors hover:bg-[var(--card-hover)]"
                            onClick={() => setExpanded(isExpanded ? null : i)}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="min-w-0 flex-1">
                                    <h4 className="truncate text-sm font-semibold text-[var(--foreground)]">
                                        {opp.title}
                                    </h4>
                                    <p className="mt-0.5 text-xs text-[var(--muted)]">
                                        {opp.provider}
                                    </p>
                                </div>
                                {/* Score badge */}
                                <div
                                    className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold"
                                    style={{
                                        background: `${accentColor}18`,
                                        color: accentColor,
                                        border: `2px solid ${accentColor}44`,
                                    }}
                                >
                                    {scorePercent}%
                                </div>
                            </div>

                            {/* Expanded detail */}
                            {isExpanded && (
                                <div className="mt-3 animate-fade-in space-y-2">
                                    <p className="text-sm text-[var(--foreground)] opacity-80">
                                        {opp.description}
                                    </p>
                                    {opp.reason && (
                                        <p className="text-xs italic text-[var(--muted)]">
                                            💡 {opp.reason}
                                        </p>
                                    )}
                                    {opp.required_skills?.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5">
                                            {opp.required_skills.map((skill, si) => (
                                                <span
                                                    key={si}
                                                    className="rounded-md bg-[var(--border)] px-2 py-0.5 text-xs text-[var(--foreground)]"
                                                >
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                    {opp.url && opp.url !== "#" && (
                                        <a
                                            href={opp.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="mt-1 inline-block text-xs font-medium hover:underline"
                                            style={{ color: accentColor }}
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            View Details →
                                        </a>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
