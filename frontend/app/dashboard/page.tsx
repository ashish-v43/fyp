"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  Database,
  Download,
  FileText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import api from "../services/api";

type Task = {
  task?: string;
  owner?: string;
  priority?: string;
  deadline?: string;
};

type Decision = {
  decision?: string;
  item?: string;
  responsible_party?: string;
  owner?: string;
};

type Recommendation = {
  recommendation?: string;
  item?: string;
  responsible_party?: string;
  owner?: string;
};

const cardClass =
  "rounded-2xl border border-slate-200 bg-white shadow-[0_12px_32px_rgba(15,23,42,0.05)]";

export default function Dashboard() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("analysis");
    if (saved) setData(JSON.parse(saved));
  }, []);

  const result = data?.result;
  const tasks: Task[] = result?.tasks?.tasks ?? [];
  const decisions: Decision[] = result?.analysis?.key_decisions ?? [];
  const recommendations: Recommendation[] = result?.analysis?.recommendations ?? [];
  const sources = result?.retrieval ?? [];
  const insights = result?.report?.key_insights ?? [];
  const risks = result?.report?.top_risks ?? [];
  const securityScore = result?.report?.security_score ?? 0;

  const securityStatus = useMemo(() => {
    if (securityScore >= 90) return "Strong";
    if (securityScore >= 70) return "Review needed";
    return "Attention needed";
  }, [securityScore]);

  const downloadReport = async () => {
    if (!result) return;
    setIsDownloading(true);

    try {
      const response = await fetch(`${api.defaults.baseURL}/generate-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(result),
      });

      if (!response.ok) throw new Error("Report generation failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "Arkspace_Report.pdf";
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Report download failed:", error);
      alert("Unable to generate the report. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  if (!data) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 px-6 text-slate-950">
        <section className={`${cardClass} max-w-md p-8 text-center`}>
          <div className="mx-auto mb-5 grid h-12 w-12 place-items-center rounded-2xl bg-indigo-50 text-indigo-600">
            <FileText size={24} />
          </div>
          <h1 className="text-xl font-semibold">No analysis to display</h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Upload a meeting transcript to create an intelligence report.
          </p>
          <button
            onClick={() => router.push("/")}
            className="mt-6 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Analyze a meeting
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f7f8fc] text-slate-950">
      <div className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <header className="mx-auto flex max-w-7xl items-center justify-between gap-5 px-5 py-4 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-500 text-white shadow-lg shadow-indigo-200">
              <Brain size={21} />
            </div>
            <div>
              <p className="text-base font-bold tracking-tight">Arkspace</p>
              <p className="text-xs font-medium text-slate-500">Workplace intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={downloadReport}
              disabled={isDownloading}
              className="hidden items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-wait disabled:opacity-60 sm:flex"
            >
              <Download size={16} />
              {isDownloading ? "Preparing..." : "Export report"}
            </button>
            <button
              onClick={() => {
                localStorage.removeItem("analysis");
                router.push("/");
              }}
              className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              New analysis
            </button>
          </div>
        </header>
      </div>

      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8 lg:py-10">
        <section className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-indigo-600">
              <Sparkles size={14} /> Analysis complete
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Executive meeting brief</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
              A clear view of the meeting’s decisions, commitments, and areas that need attention.
            </p>
          </div>
          <button
            onClick={downloadReport}
            disabled={isDownloading}
            className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-wait disabled:opacity-60 sm:hidden"
          >
            <Download size={16} /> {isDownloading ? "Preparing..." : "Export report"}
          </button>
        </section>

        <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard icon={<CheckCircle2 size={19} />} label="Action items" value={tasks.length} detail="Ready to assign" tone="indigo" />
          <MetricCard icon={<AlertTriangle size={19} />} label="Risks identified" value={risks.length} detail="Review and mitigate" tone="rose" />
          <MetricCard icon={<ShieldCheck size={19} />} label="Security posture" value={`${securityScore}%`} detail={securityStatus} tone="emerald" />
          <MetricCard icon={<Database size={19} />} label="Knowledge sources" value={sources.length} detail="Applied to analysis" tone="amber" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(310px,0.8fr)]">
          <div className="space-y-6">
            <article className={`${cardClass} overflow-hidden`}>
              <div className="border-b border-slate-100 bg-gradient-to-r from-indigo-50 via-white to-white px-6 py-5">
                <div className="flex items-center gap-3">
                  <div className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-600 text-white"><FileText size={18} /></div>
                  <div>
                    <h2 className="font-semibold">Executive summary</h2>
                    <p className="mt-0.5 text-xs text-slate-500">The essential outcome of this conversation</p>
                  </div>
                </div>
              </div>
              <p className="px-6 py-6 text-sm leading-7 text-slate-600 sm:text-[15px]">
                {result?.report?.executive_summary || "No summary was returned for this meeting."}
              </p>
              <div className="mx-6 mb-6 rounded-xl border border-indigo-100 bg-indigo-50/60 px-4 py-3 text-sm leading-6 text-indigo-950">
                <span className="mr-2 font-semibold">Business impact:</span>
                {result?.report?.business_impact || "Analysis is ready for review."}
              </div>
            </article>

            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<CheckCircle2 size={18} />} title="Action items" subtitle="Commitments captured from the meeting" />
              {tasks.length ? (
                <div className="mt-5 overflow-hidden rounded-xl border border-slate-200">
                  <div className="hidden grid-cols-[minmax(0,1.6fr)_0.7fr_0.65fr] gap-4 bg-slate-50 px-4 py-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 sm:grid">
                    <span>Commitment</span><span>Owner</span><span>Due</span>
                  </div>
                  {tasks.map((task, index) => (
                    <div key={`${task.task}-${index}`} className="grid gap-3 border-t border-slate-100 px-4 py-4 first:border-t-0 sm:grid-cols-[minmax(0,1.6fr)_0.7fr_0.65fr] sm:items-center sm:gap-4">
                      <div className="flex gap-3"><span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-indigo-50 text-[10px] font-bold text-indigo-700">{index + 1}</span><span className="text-sm font-medium leading-5 text-slate-800">{task.task || "Unnamed task"}</span></div>
                      <InfoLabel label="Owner" value={task.owner || "Unassigned"} />
                      <InfoLabel label="Due" value={task.deadline || "Not specified"} />
                    </div>
                  ))}
                </div>
              ) : <EmptyState message="No action items were detected." />}
            </article>

            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<Brain size={18} />} title="Key decisions" subtitle="Choices and ownership recorded in the discussion" />
              {decisions.length ? (
                <div className="mt-5 grid gap-3">
                  {decisions.map((decision, index) => (
                    <div key={`${decision.decision}-${index}`} className="rounded-xl border border-slate-200 p-4 transition hover:border-indigo-200 hover:bg-indigo-50/30">
                      <p className="text-sm font-semibold text-slate-800">{decision.decision || decision.item || "Decision"}</p>
                      <p className="mt-2 text-xs text-slate-500">Owner: <span className="font-medium text-slate-700">{decision.responsible_party || decision.owner || "Not specified"}</span></p>
                    </div>
                  ))}
                </div>
              ) : <EmptyState message="No explicit decisions were detected." />}
            </article>

            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<Sparkles size={18} />} title="Recommendations" subtitle="Next best moves based on the discussion and company knowledge" />
              {recommendations.length ? (
                <div className="mt-5 space-y-3">
                  {recommendations.map((recommendation, index) => (
                    <div key={`${recommendation.recommendation}-${index}`} className="flex gap-3 rounded-xl bg-slate-50 p-4">
                      <span className="mt-0.5 text-indigo-600">✦</span>
                      <div><p className="text-sm font-medium leading-6 text-slate-800">{recommendation.recommendation || recommendation.item || "Recommendation"}</p><p className="mt-1 text-xs text-slate-500">Owner: {recommendation.responsible_party || recommendation.owner || "Not specified"}</p></div>
                    </div>
                  ))}
                </div>
              ) : <EmptyState message="No recommendations were generated." />}
            </article>
          </div>

          <aside className="space-y-6">
            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<AlertTriangle size={18} />} title="Risk watch" subtitle="Items that could affect delivery" />
              {risks.length ? <div className="mt-5 space-y-3">{risks.map((risk: any, index: number) => <div key={`${risk}-${index}`} className="rounded-xl border border-rose-100 bg-rose-50/60 p-4"><p className="text-sm font-medium leading-6 text-rose-950">{typeof risk === "string" ? risk : risk.risk || "Risk"}</p><p className="mt-2 text-xs font-semibold uppercase tracking-wide text-rose-600">Requires review</p></div>)}</div> : <EmptyState message="No major risks were identified." />}
            </article>

            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<Sparkles size={18} />} title="AI insights" subtitle="Productivity signals and observations" />
              {insights.length ? <ul className="mt-5 space-y-4">{insights.map((insight: any, index: number) => <li key={`${insight}-${index}`} className="flex gap-3 text-sm leading-6 text-slate-600"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-500" />{typeof insight === "string" ? insight : insight.insight || "Insight"}</li>)}</ul> : <EmptyState message="No productivity insights were generated." />}
            </article>

            <article className={`${cardClass} p-6`}>
              <SectionHeading icon={<Database size={18} />} title="Sources used" subtitle="Organizational context applied to this brief" />
              {sources.length ? <div className="mt-5 space-y-2">{sources.map((source: any, index: number) => <div key={`${source.document}-${index}`} className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3"><span className="min-w-0 truncate text-sm font-medium text-slate-700">{source.document}</span><span className="shrink-0 rounded-md bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-500">Score {source.score}</span></div>)}</div> : <EmptyState message="No company sources matched this transcript." />}
            </article>

            <article className="rounded-2xl bg-slate-950 p-6 text-white shadow-xl shadow-slate-300">
              <div className="flex items-center gap-3"><div className="grid h-9 w-9 place-items-center rounded-lg bg-white/10 text-indigo-200"><ShieldCheck size={18} /></div><div><h2 className="font-semibold">Security scan</h2><p className="text-xs text-slate-400">Automated content check</p></div></div>
              <div className="mt-5 flex items-end justify-between"><div><p className="text-4xl font-bold tracking-tight">{securityScore}<span className="text-xl text-slate-400">/100</span></p><p className="mt-1 text-sm text-slate-300">{securityStatus}</p></div><div className="h-14 w-14 rounded-full" style={{ background: `conic-gradient(#818cf8 ${securityScore * 3.6}deg, rgba(255,255,255,.12) 0deg)` }}><div className="m-[5px] h-[46px] w-[46px] rounded-full bg-slate-950" /></div></div>
            </article>
          </aside>
        </section>
      </div>
    </main>
  );
}

function MetricCard({ icon, label, value, detail, tone }: { icon: React.ReactNode; label: string; value: string | number; detail: string; tone: "indigo" | "rose" | "emerald" | "amber" }) {
  const tones = { indigo: "bg-indigo-50 text-indigo-600", rose: "bg-rose-50 text-rose-600", emerald: "bg-emerald-50 text-emerald-600", amber: "bg-amber-50 text-amber-600" };
  return <article className={`${cardClass} p-5`}><div className="flex items-start justify-between"><div><p className="text-sm font-medium text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{value}</p></div><div className={`grid h-10 w-10 place-items-center rounded-xl ${tones[tone]}`}>{icon}</div></div><p className="mt-4 text-xs font-medium text-slate-400">{detail}</p></article>;
}

function SectionHeading({ icon, title, subtitle }: { icon: React.ReactNode; title: string; subtitle: string }) {
  return <div className="flex items-center gap-3"><div className="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-slate-700">{icon}</div><div><h2 className="font-semibold text-slate-900">{title}</h2><p className="mt-0.5 text-xs text-slate-500">{subtitle}</p></div></div>;
}

function InfoLabel({ label, value }: { label: string; value: string }) {
  return <p className="text-sm text-slate-600"><span className="mr-1 text-xs font-semibold uppercase tracking-wide text-slate-400 sm:hidden">{label}: </span>{value}</p>;
}

function EmptyState({ message }: { message: string }) {
  return <p className="mt-5 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-center text-sm text-slate-500">{message}</p>;
}
