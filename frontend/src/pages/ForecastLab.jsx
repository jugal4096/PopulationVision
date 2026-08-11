import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  GraduationCap,
  HeartPulse,
  Landmark,
  LockKeyhole,
  MapPinned,
  Mountain,
  Plane,
  Rocket,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import AmbientPopulationScene from "../components/AmbientPopulationScene";
import { getDashboardChart } from "../services/api";

function formatPopulation(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function normalizeRows(response) {
  if (Array.isArray(response)) {
    return response;
  }

  if (Array.isArray(response?.data)) {
    return response.data;
  }

  if (Array.isArray(response?.rows)) {
    return response.rows;
  }

  if (Array.isArray(response?.records)) {
    return response.records;
  }

  return [];
}

const modules = [
  {
    title: "Population Forecast",
    description:
      "Explore the existing recursive ML population forecasting pipeline from 2026 to 2050.",
    icon: Users,
    status: "available",
    accent: "cyan",
  },
  {
    title: "Population Growth",
    description:
      "Analyze projected annual population growth and the pace of demographic slowdown.",
    icon: TrendingUp,
    status: "available",
    accent: "emerald",
  },
  {
    title: "Literacy Rate",
    description:
      "Future literacy-rate modelling will be introduced after a dedicated validated forecasting pipeline is developed.",
    icon: GraduationCap,
    status: "coming",
    accent: "violet",
  },
  {
    title: "Fertility Rate",
    description:
      "A dedicated fertility forecasting model is planned for a future release.",
    icon: Users,
    status: "coming",
    accent: "pink",
  },
  {
    title: "Life Expectancy",
    description:
      "Future life-expectancy projections will require an independently validated demographic model.",
    icon: HeartPulse,
    status: "coming",
    accent: "rose",
  },
  {
    title: "Urbanization",
    description:
      "Urban population and urbanization trajectory forecasting is planned.",
    icon: Landmark,
    status: "coming",
    accent: "amber",
  },
  {
    title: "Labour Force",
    description:
      "Workforce participation and labour-force forecasting will be added in a future model layer.",
    icon: BriefcaseIcon,
    status: "coming",
    accent: "blue",
  },
  {
    title: "Net Migration",
    description:
      "A dedicated migration forecasting model is planned.",
    icon: Plane,
    status: "coming",
    accent: "sky",
  },
  {
    title: "GDP Growth",
    description:
      "Macroeconomic forecasting will remain a separate validated modelling module.",
    icon: BarChart3,
    status: "coming",
    accent: "orange",
  },
  {
    title: "Repo Rate",
    description:
      "Economic-policy indicator forecasting is reserved for a future macroeconomic intelligence layer.",
    icon: Landmark,
    status: "coming",
    accent: "yellow",
  },
];

function BriefcaseIcon(props) {
  return <Database {...props} />;
}

function ModuleCard({ module, index, onClick }) {
  const Icon = module.icon;

  const accentClasses = {
    cyan: "text-cyan-300 border-cyan-400/20 bg-cyan-400/5",
    emerald: "text-emerald-300 border-emerald-400/20 bg-emerald-400/5",
    violet: "text-violet-300 border-violet-400/20 bg-violet-400/5",
    pink: "text-pink-300 border-pink-400/20 bg-pink-400/5",
    rose: "text-rose-300 border-rose-400/20 bg-rose-400/5",
    amber: "text-amber-300 border-amber-400/20 bg-amber-400/5",
    blue: "text-blue-300 border-blue-400/20 bg-blue-400/5",
    sky: "text-sky-300 border-sky-400/20 bg-sky-400/5",
    orange: "text-orange-300 border-orange-400/20 bg-orange-400/5",
    yellow: "text-yellow-300 border-yellow-400/20 bg-yellow-400/5",
  };

  return (
    <motion.button
      type="button"
      onClick={() => onClick(module)}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.045 }}
      whileHover={{ y: -5 }}
      className="
        group w-full rounded-3xl
        border border-white/10
        bg-white/[0.025]
        p-5 text-left
        transition-all duration-300
        hover:border-white/20
        hover:bg-white/[0.045]
        hover:shadow-2xl hover:shadow-cyan-950/20
      "
    >
      <div className="flex items-start justify-between gap-4">
        <div
          className={[
            "flex h-11 w-11 items-center justify-center rounded-xl border",
            accentClasses[module.accent],
          ].join(" ")}
        >
          <Icon size={20} />
        </div>

        {module.status === "available" ? (
          <span
            className="
              flex items-center gap-1.5
              rounded-full
              border border-emerald-400/20
              bg-emerald-400/5
              px-2.5 py-1
              text-[10px] font-bold uppercase tracking-wider
              text-emerald-300
            "
          >
            <CheckCircle2 size={12} />
            Available
          </span>
        ) : (
          <span
            className="
              flex items-center gap-1.5
              rounded-full
              border border-amber-400/20
              bg-amber-400/5
              px-2.5 py-1
              text-[10px] font-bold uppercase tracking-wider
              text-amber-300
            "
          >
            <LockKeyhole size={12} />
            Coming Soon
          </span>
        )}
      </div>

      <h3 className="mt-5 text-lg font-bold text-white">
        {module.title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {module.description}
      </p>

      <div className="mt-5 flex items-center gap-2 text-xs font-semibold text-slate-500 transition group-hover:text-cyan-300">
        {module.status === "available" ? "Open module" : "View roadmap"}

        <ChevronRight
          size={15}
          className="transition-transform group-hover:translate-x-1"
        />
      </div>
    </motion.button>
  );
}

export default function ForecastLab() {
  const navigate = useNavigate();

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function loadForecast() {
      try {
        const response = await getDashboardChart();

        if (mounted) {
          setRows(normalizeRows(response));
        }
      } catch (error) {
        console.error("Forecast laboratory data error:", error);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadForecast();

    return () => {
      mounted = false;
    };
  }, []);

  const forecastRows = useMemo(() => {
    return rows
      .filter((row) => {
        const year = Number(row.Year ?? row.year);
        return year >= 2026 && year <= 2050;
      })
      .sort(
        (a, b) =>
          Number(a.Year ?? a.year) -
          Number(b.Year ?? b.year),
      );
  }, [rows]);

  const firstForecast = forecastRows[0];
  const lastForecast = forecastRows[forecastRows.length - 1];

  const firstPopulation =
    firstForecast?.Population ?? firstForecast?.population;

  const lastPopulation =
    lastForecast?.Population ?? lastForecast?.population;

  const projectedChange =
    Number(firstPopulation) && Number(lastPopulation)
      ? Number(lastPopulation) - Number(firstPopulation)
      : null;

  function handleModule(module) {
    if (module.status === "available") {
      navigate("/national/year/2050");
      return;
    }

    setSelectedModule(module);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <main className="relative overflow-hidden pt-28">
        <AmbientPopulationScene />

        <div className="relative z-10 mx-auto max-w-[1500px] px-5 pb-20 sm:px-8">
          {/* ========================================================
              HERO
          ======================================================== */}

          <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.025] p-7 sm:p-10 lg:p-14">
            <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />

            <div className="relative max-w-4xl">
              <div className="flex items-center gap-2 text-cyan-300">
                <Rocket size={16} />

                <span className="text-[10px] font-bold uppercase tracking-[0.2em]">
                  Forecast Laboratory
                </span>
              </div>

              <h1 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
                Explore the future
                <span className="block text-cyan-400">
                  through models.
                </span>
              </h1>

              <p className="mt-6 max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
                PopulationVision separates available forecasting systems
                from future modelling modules. The population model is
                operational today; additional demographic and economic
                forecasts will only be released after their own validation.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <div className="flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-4 py-2 text-xs text-cyan-300">
                  <BrainCircuit size={14} />
                  Existing ML pipeline
                </div>

                <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-400">
                  <Database size={14} />
                  API-driven data
                </div>

                <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-400">
                  <ShieldCheckIcon />
                  Validation-first
                </div>
              </div>
            </div>
          </section>

          {/* ========================================================
              ACTIVE FORECAST
          ======================================================== */}

          <section className="mt-10">
            <div className="mb-6">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400">
                Active forecasting system
              </p>

              <h2 className="mt-2 text-3xl font-black">
                India population forecast
              </h2>
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <ForecastStat
                icon={Users}
                label="Forecast start"
                value={
                  loading
                    ? "Loading..."
                    : formatPopulation(firstPopulation)
                }
                subtitle="2026 ML forecast"
              />

              <ForecastStat
                icon={TrendingUp}
                label="Forecast endpoint"
                value={
                  loading
                    ? "Loading..."
                    : formatPopulation(lastPopulation)
                }
                subtitle="2050 ML forecast"
              />

              <ForecastStat
                icon={BarChart3}
                label="Projected change"
                value={
                  loading
                    ? "Loading..."
                    : formatPopulation(projectedChange)
                }
                subtitle="2026 → 2050"
              />
            </div>
          </section>

          {/* ========================================================
              MODULE GRID
          ======================================================== */}

          <section className="mt-14">
            <div className="mb-7">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-400">
                Forecast catalogue
              </p>

              <h2 className="mt-2 text-3xl font-black">
                Choose an intelligence module
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Some modules are operational. Others are intentionally
                locked until a dedicated data pipeline, model, validation
                process, and uncertainty framework are ready.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {modules.map((module, index) => (
                <ModuleCard
                  key={module.title}
                  module={module}
                  index={index}
                  onClick={handleModule}
                />
              ))}
            </div>
          </section>

          {/* ========================================================
              ROADMAP
          ======================================================== */}

          <section className="mt-14 rounded-3xl border border-white/10 bg-white/[0.025] p-7 sm:p-9">
            <div className="grid gap-8 lg:grid-cols-[1fr_1.5fr]">
              <div>
                <div className="flex items-center gap-2 text-violet-300">
                  <Sparkles size={18} />

                  <span className="text-xs font-bold uppercase tracking-wider">
                    Modelling roadmap
                  </span>
                </div>

                <h2 className="mt-3 text-2xl font-black">
                  One model should not pretend to predict everything.
                </h2>

                <p className="mt-3 text-sm leading-7 text-slate-500">
                  Each future indicator will require its own carefully
                  validated forecasting architecture. Keeping those systems
                  separate protects the credibility of the platform.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {[
                  "Data quality assessment",
                  "Feature engineering",
                  "Time-series validation",
                  "Model comparison",
                  "Uncertainty estimation",
                  "Production monitoring",
                ].map((step, index) => (
                  <div
                    key={step}
                    className="flex items-center gap-3 rounded-xl border border-white/5 bg-black/10 p-3"
                  >
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 text-xs font-bold text-cyan-300">
                      {index + 1}
                    </span>

                    <span className="text-xs text-slate-400">
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* ============================================================
          COMING SOON MODAL
      ============================================================ */}

      {selectedModule && (
        <div
          className="
            fixed inset-0 z-[100]
            flex items-center justify-center
            bg-black/70 p-5 backdrop-blur-md
          "
          onClick={() => setSelectedModule(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            onClick={(event) => event.stopPropagation()}
            className="
              w-full max-w-lg
              rounded-3xl
              border border-white/10
              bg-slate-950
              p-7
              shadow-2xl
            "
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/5 text-amber-300">
              <Clock3 size={21} />
            </div>

            <h2 className="mt-5 text-2xl font-black">
              {selectedModule.title}
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-500">
              This module is part of the platform roadmap but is not yet
              backed by a dedicated validated forecasting system.
            </p>

            <div className="mt-5 rounded-xl border border-amber-400/10 bg-amber-400/5 p-4 text-xs leading-6 text-amber-200/70">
              Coming Soon — model development, validation, uncertainty
              analysis, and API integration will be required before this
              module becomes available.
            </div>

            <button
              type="button"
              onClick={() => setSelectedModule(null)}
              className="
                mt-6 w-full rounded-xl
                bg-white/10 px-4 py-3
                text-sm font-semibold
                text-white
                transition hover:bg-white/15
              "
            >
              Return to Forecast Laboratory
            </button>
          </motion.div>
        </div>
      )}
    </div>
  );
}

function ForecastStat({ icon: Icon, label, value, subtitle }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-3xl border border-white/10 bg-white/[0.025] p-6"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
          <Icon size={19} />
        </div>

        <span className="text-xs uppercase tracking-wider text-slate-600">
          {label}
        </span>
      </div>

      <div className="mt-6 text-2xl font-black text-white">
        {value}
      </div>

      <p className="mt-1 text-xs text-slate-600">
        {subtitle}
      </p>
    </motion.div>
  );
}

function ShieldCheckIcon() {
  return (
    <span className="inline-flex h-3.5 w-3.5 items-center justify-center rounded-full border border-emerald-400/30 text-[8px] text-emerald-300">
      ✓
    </span>
  );
}