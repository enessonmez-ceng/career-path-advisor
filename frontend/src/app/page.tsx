"use client";

import React, { useState } from "react";
import FileUploader from "@/components/FileUploader";
import SkillsChart from "@/components/SkillsChart";
import RecommendationCard from "@/components/RecommendationCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AnalysisResult {
  name: string;
  email: string | null;
  target_role: string;
  current_skills: {
    name: string;
    category: string;
    level: string;
    years_experience: number | null;
  }[];
  experiences: {
    title: string;
    company: string;
    duration: string;
    description: string;
    skills_used: string[];
  }[];
  education: {
    degree: string;
    field: string;
    institution: string;
    year: number | null;
  }[];
  skill_gaps: {
    skill: string;
    current_level: string | null;
    target_level: string;
    priority: string;
    recommendation: string;
  }[];
  strengths: string[];
  areas_to_improve: string[];
  internship_recommendations: Opportunity[];
  course_recommendations: Opportunity[];
  event_recommendations: Opportunity[];
  certification_recommendations: Opportunity[];
  development_roadmap: string;
  final_report: string;
  critique: string;
  iterations: number;
}

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

type Tab = "skills" | "recommendations" | "roadmap" | "report";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("skills");
  const [progress, setProgress] = useState<string>("");

  const handleFileSelect = (f: File) => {
    setFile(f);
    setError(null);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    setResult(null);
    setProgress("Uploading CV...");

    try {
      const formData = new FormData();
      formData.append("file", file);
      if (targetRole) formData.append("target_role", targetRole);

      setProgress("Analyzing your CV with AI... This may take 1-2 minutes.");

      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Analysis failed (${res.status})`);
      }

      const data: AnalysisResult = await res.json();
      setResult(data);
      setActiveTab("skills");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsAnalyzing(false);
      setProgress("");
    }
  };

  const tabs: { key: Tab; label: string; icon: string }[] = [
    { key: "skills", label: "Skills", icon: "⚡" },
    { key: "recommendations", label: "Recommendations", icon: "🎯" },
    { key: "roadmap", label: "Roadmap", icon: "🗺️" },
    { key: "report", label: "Full Report", icon: "📄" },
  ];

  return (
    <main className="min-h-screen">
      {/* Hero / Header */}
      <header className="relative overflow-hidden border-b border-[var(--border)] px-4 py-16 text-center">
        {/* Background gradient */}
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            background:
              "radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.2) 0%, transparent 60%)",
          }}
        />

        <div className="relative mx-auto max-w-2xl">
          <h1 className="gradient-text mb-4 text-4xl font-extrabold tracking-tight md:text-5xl">
            Career Path Advisor
          </h1>
          <p className="text-lg text-[var(--muted)]">
            Upload your CV and get AI-powered career recommendations —
            internships, courses, events, and a personalized development roadmap.
          </p>
        </div>
      </header>

      {/* Upload Section */}
      {!result && (
        <section className="mx-auto max-w-xl animate-slide-up px-4 py-12">
          <FileUploader onFileSelect={handleFileSelect} isLoading={isAnalyzing} />

          {/* Target Role */}
          <div className="mt-6">
            <label className="mb-2 block text-sm font-medium text-[var(--muted)]">
              Target Role (optional)
            </label>
            <input
              id="target-role-input"
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Backend Developer, Data Scientist..."
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm text-[var(--foreground)] placeholder-[var(--muted)] outline-none transition-colors focus:border-[var(--primary)]"
              disabled={isAnalyzing}
            />
          </div>

          {/* Analyze button */}
          <button
            id="analyze-button"
            onClick={handleAnalyze}
            disabled={!file || isAnalyzing}
            className="mt-6 w-full rounded-xl px-6 py-3.5 text-sm font-semibold text-white transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-40"
            style={{
              background:
                file && !isAnalyzing
                  ? "linear-gradient(135deg, var(--primary), var(--primary-dark))"
                  : "var(--border)",
            }}
          >
            {isAnalyzing ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="3"
                    fill="none"
                    strokeDasharray="32"
                    strokeLinecap="round"
                  />
                </svg>
                Analyzing...
              </span>
            ) : (
              "🚀 Analyze My CV"
            )}
          </button>

          {/* Progress message */}
          {progress && (
            <p className="mt-4 text-center text-sm text-[var(--accent)]">
              {progress}
            </p>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}
        </section>
      )}

      {/* Results Section */}
      {result && (
        <section className="mx-auto max-w-5xl animate-slide-up px-4 py-8">
          {/* Profile Header */}
          <div className="glass-card mb-6 flex flex-col items-start gap-4 p-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-2xl font-bold text-[var(--foreground)]">
                {result.name}
              </h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Target: <span className="text-[var(--primary-light)]">{result.target_role}</span>
                {result.email && <span> · {result.email}</span>}
              </p>
            </div>
            <button
              id="new-analysis-button"
              onClick={() => {
                setResult(null);
                setFile(null);
                setTargetRole("");
              }}
              className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--muted)] transition-colors hover:border-[var(--primary)] hover:text-[var(--foreground)]"
            >
              ← New Analysis
            </button>
          </div>

          {/* Tab Navbar */}
          <div className="mb-6 flex gap-1 overflow-x-auto rounded-xl bg-[var(--card)] p-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${activeTab === tab.key
                    ? "bg-[var(--primary)] text-white shadow"
                    : "text-[var(--muted)] hover:text-[var(--foreground)]"
                  }`}
              >
                <span className="mr-1.5">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="animate-fade-in">
            {activeTab === "skills" && (
              <SkillsChart
                skills={result.current_skills}
                strengths={result.strengths}
                areasToImprove={result.areas_to_improve}
              />
            )}

            {activeTab === "recommendations" && (
              <div className="space-y-6">
                <RecommendationCard
                  opportunities={result.internship_recommendations}
                  title="Internships"
                  icon="💼"
                  accentColor="#6366f1"
                />
                <RecommendationCard
                  opportunities={result.course_recommendations}
                  title="Courses"
                  icon="📚"
                  accentColor="#06b6d4"
                />
                <RecommendationCard
                  opportunities={result.event_recommendations}
                  title="Events & Workshops"
                  icon="🗓️"
                  accentColor="#10b981"
                />
                <RecommendationCard
                  opportunities={result.certification_recommendations}
                  title="Certifications"
                  icon="🏅"
                  accentColor="#f59e0b"
                />
              </div>
            )}

            {activeTab === "roadmap" && (
              <div className="glass-card p-6">
                <h3 className="mb-4 text-lg font-semibold gradient-text">
                  Development Roadmap
                </h3>
                <div className="prose prose-invert max-w-none text-sm leading-relaxed text-[var(--foreground)] opacity-90">
                  {result.development_roadmap.split("\n").map((line, i) => {
                    if (line.startsWith("###")) {
                      return (
                        <h4 key={i} className="mb-2 mt-5 text-base font-semibold text-[var(--primary-light)]">
                          {line.replace(/^###\s*/, "")}
                        </h4>
                      );
                    }
                    if (line.startsWith("##")) {
                      return (
                        <h3 key={i} className="mb-3 mt-6 text-lg font-bold gradient-text">
                          {line.replace(/^##\s*/, "")}
                        </h3>
                      );
                    }
                    if (line.startsWith("- **")) {
                      const [label, ...rest] = line.replace(/^- \*\*/, "").split("**");
                      return (
                        <p key={i} className="mb-1 ml-4">
                          <strong className="text-[var(--accent)]">{label}</strong>
                          {rest.join("**")}
                        </p>
                      );
                    }
                    if (line.trim() === "") return <br key={i} />;
                    return <p key={i} className="mb-1">{line}</p>;
                  })}
                </div>
              </div>
            )}

            {activeTab === "report" && (
              <div className="glass-card p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-lg font-semibold gradient-text">
                    Full Career Report
                  </h3>
                  <span className="text-xs text-[var(--muted)]">
                    {result.iterations} review iteration(s)
                  </span>
                </div>
                <div className="prose prose-invert max-w-none text-sm leading-relaxed text-[var(--foreground)] opacity-90">
                  {result.final_report.split("\n").map((line, i) => {
                    if (line.startsWith("# ")) {
                      return (
                        <h2 key={i} className="mb-3 mt-6 text-xl font-bold text-[var(--foreground)]">
                          {line.replace(/^#\s*/, "")}
                        </h2>
                      );
                    }
                    if (line.startsWith("## ")) {
                      return (
                        <h3 key={i} className="mb-2 mt-5 text-lg font-semibold gradient-text">
                          {line.replace(/^##\s*/, "")}
                        </h3>
                      );
                    }
                    if (line.startsWith("### ")) {
                      return (
                        <h4 key={i} className="mb-2 mt-4 text-base font-semibold text-[var(--primary-light)]">
                          {line.replace(/^###\s*/, "")}
                        </h4>
                      );
                    }
                    if (line.startsWith("- **")) {
                      const [label, ...rest] = line.replace(/^- \*\*/, "").split("**");
                      return (
                        <p key={i} className="mb-1 ml-4">
                          <strong className="text-[var(--accent)]">{label}</strong>
                          {rest.join("**")}
                        </p>
                      );
                    }
                    if (line.startsWith("- ")) {
                      return (
                        <p key={i} className="mb-1 ml-4 text-[var(--foreground)]">
                          • {line.replace(/^- /, "")}
                        </p>
                      );
                    }
                    if (line.startsWith("**")) {
                      return (
                        <p key={i} className="mb-2 font-semibold text-[var(--foreground)]">
                          {line.replace(/\*\*/g, "")}
                        </p>
                      );
                    }
                    if (line.trim() === "" || line.trim() === "---") return <br key={i} />;
                    return <p key={i} className="mb-1">{line}</p>;
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Skill Gaps */}
          {activeTab === "skills" && result.skill_gaps.length > 0 && (
            <div className="mt-6 glass-card p-5">
              <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--danger)]">
                🎯 Skill Gaps
              </h3>
              <div className="space-y-3">
                {result.skill_gaps.map((gap, i) => (
                  <div
                    key={i}
                    className="rounded-lg border border-[var(--border)] p-3 transition-colors hover:border-[var(--primary)]/30"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-[var(--foreground)]">
                        {gap.skill}
                      </span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${gap.priority === "high"
                            ? "bg-[var(--danger)]/15 text-[var(--danger)]"
                            : gap.priority === "medium"
                              ? "bg-[var(--warning)]/15 text-[var(--warning)]"
                              : "bg-[var(--muted)]/15 text-[var(--muted)]"
                          }`}
                      >
                        {gap.priority}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      {gap.current_level || "none"} → {gap.target_level}
                    </p>
                    <p className="mt-1 text-xs text-[var(--foreground)] opacity-70">
                      {gap.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* Footer */}
      <footer className="mt-16 border-t border-[var(--border)] px-4 py-6 text-center text-xs text-[var(--muted)]">
        Career Path Advisor · Built with LangGraph, FastAPI & Next.js
      </footer>
    </main>
  );
}
