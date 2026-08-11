import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  ChartNoAxesCombined,
  Clock3,
  Database,
  Gauge,
  GitCompareArrows,
  Lightbulb,
  Radar,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingDown,
  Users,
} from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import AmbientPopulationScene from "../components/AmbientPopulationScene";

import {
  getDashboardChart,
  getDataStatus,
} from "../services/api";

function normalizeRows(response) {
  if (Array.isArray(response)) return response;

  if (Array.isArray(response?.data)) return response.data;

  if (Array.isArray(response?.rows)) return response.rows;

  return [];
}

function value(row, ...keys) {
  for (const key of keys) {
    if (row?.[key] !== undefined && row?.[key] !== null) {
      return row[key];
    }
  }

  return null;
}

function formatPopulation(number) {
  if (number === null || number === undefined) return "—";

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(Number(number));
}

export default function ResearchLab() {
  const navigate = useNavigate();

  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const [chartResponse, statusResponse] =
          await Promise.allSettled([
            getDashboardChart(),
            getDataStatus(),
          ]);

        if (!mounted) return;

        if (chartResponse.status === "fulfilled") {
          setRows(normalizeRows(chartResponse.value));
        }

        if (statusResponse.status === "fulfilled") {
          setStatus(statusResponse.value);
        }
      } catch (error) {
        console.error("Research laboratory error:", error);
      }
    }

    load();

    return () => {
      mounted = false;
    };
  }, []);

  const researchStats = useMemo(() => {
    if (!rows.length) {
      return {
        start: null,
        end: null,
        change: null,
      };
    }

    const sorted = [...rows].sort(
      (a, b) =>
        Number(value(a, "Year", "year")) -
        Number(value(b, "Year", "year")),
    );

    const first = sorted[0];
    const last = sorted[sorted.length - 1];

    const startPopulation = Number(
      value(first, "Population", "population"),
    );

    const endPopulation = Number(
      value(last, "Population", "population"),
    );

    return {
      start: startPopulation,
      end: endPopulation,
      change:
        Number.isFinite(startPopulation) &&
        Number.isFinite(endPopulation)
          ? endPopulation - startPopulation
          : null,
    };
  }, [rows]);

  const researchModules = [
    {
      icon: Radar,
      title: "Demographic Transition Scanner",
      description:
        "Detect changes in population growth dynamics and identify periods where demographic momentum changes.",
      status: "Active concept",
    },
    {
      icon: TrendingDown,
      title: "Growth Deceleration Monitor",
      description:
        "Track whether annual population growth is accelerating, stable, or slowing across the available timeline.",
      status: "Data-driven",
    },
    {
      icon: Target,
      title: "Population Milestone Explorer",
      description:
        "Surface important population thresholds and major changes detected by the intelligence layer.",
      status: "Data-driven",
    },
    {
      icon: GitCompareArrows,
      title: "Historical vs Forecast",
      description:
        "Compare observed historical population dynamics with the trajectory produced by the existing ML forecast.",
      status: "Analysis",
    },
    {
      icon: Gauge,
      title: "Long-Term Scenario Observatory",
      description:
        "Explore 10-, 20-, 25-, 50-, and 100-year research windows using available data.",
      status: "Research mode",
    },
    {
      icon: Lightbulb,
      title: "Policy Signal Observatory",
      description:
        "Translate demographic changes into analytical planning signals without presenting them as official policy recommendations.",
      status: "Analytical",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <main className="relative overflow-hidden pt-28">
        <AmbientPopulationScene />

        <div className="relative z-10 mx-auto max-w-[1500px] px-5 pb-20 sm:px-8">
          {/* ========================================================
              HERO
          ======================================================== */}

          <section className="rounded-[2rem] border border-white/10 bg-white/[0.025] p-7 sm:p-10 lg:p-14">
            <div className="flex items-center gap-2 text-violet-300">
              <FlaskIcon />

              <span className="text-[10px] font-bold uppercase tracking-[0.2em]">
                AI Demographic Research Lab
              </span>
            </div>

            <h1 className="mt-5 max-w-4xl text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Don't just predict population.
              <span className="block text-violet-400">
                Understand the transition.
              </span>
            </h1>

            <p className="mt-6 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
              This research layer turns the forecasting pipeline into a
              demographic observatory: trends, transitions, milestones,
              comparisons, long-term windows, and policy-relevant analytical
              signals.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <ResearchBadge icon={BrainCircuit} text="AI-assisted analysis" />
              <ResearchBadge icon={Database} text="Backend intelligence" />
              <ResearchBadge icon={ShieldCheck} text="Transparent methodology" />
            </div>
          </section>

          {/* ========================================================
              LIVE RESEARCH SNAPSHOT
          ======================================================== */}

          <section className="mt-10 grid gap-4 md:grid-cols-3">
            <ResearchStat
              icon={Users}
              label="Available records"
              value={rows.length || "—"}
              description="Timeline records currently exposed by the API"
            />

            <ResearchStat
              icon={ChartNoAxesCombined}
              label="Latest population"
              value={
                researchStats.end
                  ? formatPopulation(researchStats.end)
                  : "—"
              }
              description="Latest record available to the frontend"
            />

            <ResearchStat
              icon={Activity}
              label="Data status"
              value={status ? "Connected" : "Checking"}
              description="FastAPI intelligence layer"
            />
          </section>

          {/* ========================================================
              RESEARCH MODULES
          ======================================================== */}

          <section className="mt-14">
            <div className="mb-7">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-400">
                Research instruments
              </p>

              <h2 className="mt-2 text-3xl font-black">
                Intelligence beyond a single forecast
              </h2>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {researchModules.map((module, index) => {
                const Icon = module.icon;

                return (
                  <motion.div
                    key={module.title}
                    initial={{ opacity: 0, y: 18 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.06 }}
                    whileHover={{ y: -5 }}
                    className="
                      group rounded-3xl
                      border border-white/10
                      bg-white/[0.025]
                      p-6
                      transition
                      hover:border-violet-400/20
                      hover:bg-violet-400/[0.025]
                    "
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-violet-400/15 bg-violet-400/5 text-violet-300">
                        <Icon size={20} />
                      </div>

                      <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
                        {module.status}
                      </span>
                    </div>

                    <h3 className="mt-5 text-lg font-bold">
                      {module.title}
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      {module.description}
                    </p>

                    <div className="mt-5 flex items-center gap-2 text-xs font-semibold text-violet-300 opacity-70 transition group-hover:opacity-100">
                      Research instrument
                      <ArrowRight size={14} />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </section>

          {/* ========================================================
              RESEARCH WINDOWS
          ======================================================== */}

          <section className="mt-14 rounded-3xl border border-white/10 bg-white/[0.025] p-7 sm:p-9">
            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400">
                  Research windows
                </p>

                <h2 className="mt-2 text-2xl font-black">
                  Study India across time
                </h2>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Open the Year Intelligence system for individual years or
                  use these research horizons as the conceptual basis for
                  longitudinal analysis.
                </p>
              </div>

              <Clock3 className="hidden text-slate-700 sm:block" size={36} />
            </div>

            <div className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {[10, 20, 25, 50, 100].map((years) => (
                <motion.button
                  key={years}
                  whileHover={{ y: -3 }}
                  type="button"
                  onClick={() => navigate("/national/year/2050")}
                  className="
                    rounded-2xl
                    border border-white/10
                    bg-black/10
                    p-4 text-left
                    transition hover:border-cyan-400/20
                  "
                >
                  <div className="text-2xl font-black text-white">
                    {years}
                  </div>

                  <div className="mt-1 text-xs text-slate-600">
                    year research mode
                  </div>
                </motion.button>
              ))}
            </div>
          </section>

          {/* ========================================================
              POLICY INTELLIGENCE
          ======================================================== */}

          <section className="mt-14 grid gap-4 lg:grid-cols-2">
            <InsightCard
              icon={Search}
              eyebrow="Research principle"
              title="Separate observation from interpretation."
              text="Historical observations, model estimates, forecast values, and analytical interpretations should remain visibly distinct."
            />

            <InsightCard
              icon={Sparkles}
              eyebrow="Platform direction"
              title="Turn numbers into questions."
              text="The research layer is designed to help users investigate why demographic dynamics change, not merely display a predicted number."
            />
          </section>
        </div>
      </main>
    </div>
  );
}

function ResearchBadge({ icon: Icon, text }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-400">
      <Icon size={14} className="text-violet-300" />
      {text}
    </div>
  );
}

function ResearchStat({ icon: Icon, label, value, description }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.025] p-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-400/10 text-violet-300">
          <Icon size={18} />
        </div>

        <span className="text-xs uppercase tracking-wider text-slate-600">
          {label}
        </span>
      </div>

      <div className="mt-5 text-2xl font-black text-white">
        {value}
      </div>

      <p className="mt-1 text-xs leading-5 text-slate-600">
        {description}
      </p>
    </div>
  );
}

function InsightCard({ icon: Icon, eyebrow, title, text }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.025] p-7">
      <Icon size={20} className="text-cyan-300" />

      <p className="mt-5 text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400">
        {eyebrow}
      </p>

      <h3 className="mt-2 text-xl font-bold">
        {title}
      </h3>

      <p className="mt-3 text-sm leading-7 text-slate-500">
        {text}
      </p>
    </div>
  );
}

function FlaskIcon() {
  return (
    <span className="flex h-5 w-5 items-center justify-center rounded-md border border-violet-400/20 bg-violet-400/10 text-violet-300">
      ✦
    </span>
  );
}