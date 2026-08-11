import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  BarChart3,
  BrainCircuit,
  Database,
  Gauge,
  Globe2,
  Info,
  Landmark,
  MapPin,
  Network,
  ShieldCheck,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react";
import { motion } from "framer-motion";

import Navbar from "../components/Navbar";
import { getYearIntelligence } from "../services/api";

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(Number(value));
}

function formatPopulation(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  const number = Number(value);

  if (number >= 1_000_000_000) {
    return `${(number / 1_000_000_000).toFixed(3)}B`;
  }

  if (number >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(2)}M`;
  }

  return formatNumber(number);
}

function formatPercent(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  return `${Number(value).toFixed(digits)}%`;
}

function formatSignedNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  const number = Number(value);

  return `${number >= 0 ? "+" : ""}${formatNumber(number)}`;
}

function getIndicatorIcon(category) {
  switch (category) {
    case "Workforce":
      return Users;

    case "Migration":
      return Globe2;

    default:
      return Activity;
  }
}

function StatusBadge({ children, tone = "cyan" }) {
  const tones = {
    cyan: "border-cyan-400/20 bg-cyan-400/10 text-cyan-300",
    emerald: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    amber: "border-amber-400/20 bg-amber-400/10 text-amber-300",
    violet: "border-violet-400/20 bg-violet-400/10 text-violet-300",
    slate: "border-white/10 bg-white/5 text-slate-300",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

function SectionHeading({ icon: Icon, eyebrow, title, description }) {
  return (
    <div className="mb-6">
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
        <Icon size={15} />
        {eyebrow}
      </div>

      <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
        {title}
      </h2>

      {description && (
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  accent = "cyan",
}) {
  const accentClasses = {
    cyan: "border-cyan-400/15 bg-cyan-400/[0.035] text-cyan-300",
    emerald: "border-emerald-400/15 bg-emerald-400/[0.035] text-emerald-300",
    violet: "border-violet-400/15 bg-violet-400/[0.035] text-violet-300",
    amber: "border-amber-400/15 bg-amber-400/[0.035] text-amber-300",
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 backdrop-blur-xl"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-2xl font-bold tracking-tight text-white">
            {value}
          </p>

          {detail && (
            <p className="mt-2 text-xs leading-5 text-slate-500">{detail}</p>
          )}
        </div>

        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${accentClasses[accent]}`}
        >
          <Icon size={19} />
        </div>
      </div>
    </motion.div>
  );
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-[#030712] text-white">
      <Navbar />

      <div className="flex min-h-screen items-center justify-center px-6 pt-20">
        <div className="text-center">
          <motion.div
            animate={{
              rotate: 360,
              scale: [1, 1.08, 1],
            }}
            transition={{
              rotate: {
                duration: 3,
                repeat: Infinity,
                ease: "linear",
              },
              scale: {
                duration: 1.5,
                repeat: Infinity,
              },
            }}
            className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300"
          >
            <BrainCircuit size={34} />
          </motion.div>

          <h1 className="mt-7 text-2xl font-bold">
            Building demographic intelligence
          </h1>

          <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-500">
            Retrieving the selected year, population forecast, analytical
            signals, model information, and data provenance.
          </p>

          <div className="mx-auto mt-6 h-1.5 w-56 overflow-hidden rounded-full bg-white/10">
            <motion.div
              animate={{ x: ["-100%", "100%"] }}
              transition={{
                duration: 1.4,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="h-full w-1/2 rounded-full bg-cyan-400"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ErrorScreen({ message, year }) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#030712] text-white">
      <Navbar />

      <div className="flex min-h-screen items-center justify-center px-6 pt-20">
        <div className="w-full max-w-xl rounded-3xl border border-red-400/20 bg-red-400/[0.04] p-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-red-400/20 bg-red-400/10 text-red-300">
            <Info size={25} />
          </div>

          <h1 className="mt-5 text-2xl font-bold">
            Unable to load year {year}
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {message}
          </p>

          <button
            onClick={() => navigate("/national")}
            className="mt-7 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100"
          >
            Return to Command Center
          </button>
        </div>
      </div>
    </div>
  );
}

export default function YearIntelligence() {
  const { year: yearParam } = useParams();

  const year = Number(yearParam);

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadReport() {
      setLoading(true);
      setError("");
      setReport(null);

      if (!Number.isInteger(year) || year < 1960 || year > 2050) {
        setError("Please select a year between 1960 and 2050.");
        setLoading(false);
        return;
      }

      try {
        const response = await getYearIntelligence(year);

        if (active) {
          setReport(response);
        }
      } catch (err) {
        if (active) {
          setError(
            err?.message ||
              "The demographic intelligence service could not return this year.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadReport();

    return () => {
      active = false;
    };
  }, [year]);

  const demographicIndicators = useMemo(() => {
    return report?.demographic_context?.indicators || [];
  }, [report]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !report) {
    return (
      <ErrorScreen
        message={error || "No intelligence report was returned."}
        year={yearParam}
      />
    );
  }

  const population = report.population || {};
  const forecastContext = report.forecast_context || {};
  const intelligence = report.intelligence || {};
  const insights = intelligence.insights || {};
  const growth = report.growth_analysis || {};
  const growthData = growth.data || {};
  const reliability = report.model_reliability || {};
  const provenance = report.data_provenance || {};
  const policySignals = report.policy_signals?.data || [];
  const limitations = report.limitations || [];

  const isForecast = population.classification === "Forecast";
  const isEstimated = population.classification === "Estimated";
  const isHistorical = population.classification === "Historical";

  const growthDirection =
    growthData.Growth_Direction || "Not available";

  const growthCategory =
    growthData.Growth_Category ||
    insights.Growth_Category ||
    "Not classified";

  const growthChange = Number(growthData.Growth_Rate_Change);

  const growthIcon =
    growthDirection === "Decelerating"
      ? TrendingDown
      : TrendingUp;

  const sourceTone = isForecast
    ? "violet"
    : isEstimated
      ? "amber"
      : "emerald";

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#030712] text-white">
      <Navbar />

      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[10%] top-[10%] h-96 w-96 rounded-full bg-cyan-500/[0.035] blur-3xl" />
        <div className="absolute right-[5%] top-[35%] h-96 w-96 rounded-full bg-violet-500/[0.035] blur-3xl" />

        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px)",
            backgroundSize: "50px 50px",
            maskImage:
              "linear-gradient(to bottom, black, transparent 75%)",
          }}
        />
      </div>

      <main className="mx-auto max-w-[1500px] px-5 pb-20 pt-28 sm:px-8">
        {/* Breadcrumb */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-wrap items-center justify-between gap-4"
        >
          <Link
            to="/national"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-cyan-300"
          >
            <ArrowLeft size={16} />
            Back to Command Center
          </Link>

          <div className="flex items-center gap-2">
            <StatusBadge tone="cyan">
              <MapPin size={12} className="mr-1" />
              India
            </StatusBadge>

            <StatusBadge tone={sourceTone}>
              {population.status || population.classification}
            </StatusBadge>
          </div>
        </motion.div>

        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.025] p-7 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-10"
        >
          <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-cyan-400/[0.06] blur-3xl" />

          <div className="relative grid gap-10 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
            <div>
              <div className="mb-5 flex flex-wrap items-center gap-2">
                <StatusBadge tone="cyan">
                  National Demographic Intelligence
                </StatusBadge>

                <StatusBadge tone={sourceTone}>
                  {population.label || population.status}
                </StatusBadge>
              </div>

              <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-400">
                Intelligence report
              </p>

              <h1 className="mt-3 text-5xl font-black tracking-[-0.04em] text-white sm:text-7xl">
                {year}
              </h1>

              <p className="mt-5 max-w-3xl text-base leading-7 text-slate-400">
                National demographic intelligence for India, combining the
                existing population forecasting pipeline with analytical
                signals, model evaluation, and transparent data provenance.
              </p>

              <div className="mt-7 flex flex-wrap gap-3">
                <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-600">
                    Source
                  </p>
                  <p className="mt-1 text-sm font-semibold text-slate-200">
                    {population.source || "—"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-600">
                    Classification
                  </p>
                  <p className="mt-1 text-sm font-semibold text-slate-200">
                    {population.classification || "—"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-600">
                    Coverage
                  </p>
                  <p className="mt-1 text-sm font-semibold text-slate-200">
                    1960–2050
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/[0.035] p-6">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-cyan-300">
                <Users size={15} />
                Population
              </div>

              <p className="mt-4 text-4xl font-black tracking-tight text-white">
                {formatPopulation(population.population)}
              </p>

              <p className="mt-2 text-sm text-slate-500">
                {formatNumber(population.population)} people
              </p>

              <div className="mt-6 border-t border-white/10 pt-5">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">
                    Annual growth
                  </span>

                  <span className="font-semibold text-cyan-300">
                    {formatPercent(population.growth_rate_percent, 4)}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between">
                  <span className="text-sm text-slate-500">
                    Population change
                  </span>

                  <span className="font-semibold text-white">
                    {formatSignedNumber(population.population_change)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Primary metrics */}
        <section className="mt-8">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              icon={Users}
              label="Population"
              value={formatPopulation(population.population)}
              detail="Year-specific population value"
              accent="cyan"
            />

            <MetricCard
              icon={Activity}
              label="Population change"
              value={formatSignedNumber(population.population_change)}
              detail="Change from previous year"
              accent="emerald"
            />

            <MetricCard
              icon={growthIcon}
              label="Growth rate"
              value={formatPercent(population.growth_rate_percent, 4)}
              detail={`${growthDirection} · ${growthCategory}`}
              accent="violet"
            />

            <MetricCard
              icon={Gauge}
              label="Previous population"
              value={formatPopulation(population.previous_population)}
              detail="Population used as previous-year reference"
              accent="amber"
            />
          </div>
        </section>

        {/* Forecast context */}
        <section className="mt-16">
          <SectionHeading
            icon={BrainCircuit}
            eyebrow="Forecast intelligence"
            title="What the model is actually saying"
            description="This section distinguishes the machine-learning forecast from demographic context that the model does not independently predict."
          />

          <div className="grid gap-5 lg:grid-cols-3">
            <div className="rounded-2xl border border-violet-400/15 bg-violet-400/[0.035] p-6 lg:col-span-2">
              <div className="flex items-start gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-violet-400/20 bg-violet-400/10 text-violet-300">
                  <BrainCircuit size={21} />
                </div>

                <div>
                  <h3 className="font-semibold text-white">
                    {population.status || "Model forecast"}
                  </h3>

                  <p className="mt-2 text-sm leading-7 text-slate-400">
                    {forecastContext.interpretation ||
                      "Population values for forecast years come from the existing forecasting pipeline."}
                  </p>
                </div>
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Forecast starts</p>
                  <p className="mt-1 text-lg font-bold text-white">
                    {forecastContext.forecast_start ?? "—"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Forecast horizon</p>
                  <p className="mt-1 text-lg font-bold text-white">
                    {forecastContext.forecast_start &&
                    forecastContext.forecast_end
                      ? `${forecastContext.forecast_start}–${forecastContext.forecast_end}`
                      : "—"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">
                    Years from latest official
                  </p>
                  <p className="mt-1 text-lg font-bold text-white">
                    {forecastContext.years_from_latest_official ?? "—"}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.035] p-6">
              <ShieldCheck className="text-emerald-300" size={24} />

              <h3 className="mt-4 font-semibold text-white">
                No fake certainty
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {reliability.interpretation ||
                  "Forecasts are model estimates and should not be interpreted as certainty."}
              </p>

              <div className="mt-5 rounded-xl border border-emerald-400/10 bg-emerald-400/5 p-4">
                <p className="text-xs text-slate-500">Selected model</p>
                <p className="mt-1 font-bold text-emerald-300">
                  {reliability.model || "—"}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Growth intelligence */}
        <section className="mt-16">
          <SectionHeading
            icon={BarChart3}
            eyebrow="Growth dynamics"
            title="Population growth intelligence"
            description="The annual growth signal provides context around whether population expansion is accelerating or decelerating."
          />

          <div className="grid gap-5 md:grid-cols-3">
            <MetricCard
              icon={growthIcon}
              label="Growth direction"
              value={growthDirection}
              detail="Compared with the previous growth signal"
              accent="violet"
            />

            <MetricCard
              icon={Activity}
              label="Growth category"
              value={growthCategory}
              detail="Backend analytical classification"
              accent="cyan"
            />

            <MetricCard
              icon={TrendingDown}
              label="Growth-rate change"
              value={formatPercent(growthChange, 4)}
              detail="Change in annual growth rate"
              accent="amber"
            />
          </div>

          {insights.Insight && (
            <div className="mt-5 rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6">
              <div className="flex gap-4">
                <Sparkles
                  size={21}
                  className="mt-1 shrink-0 text-cyan-300"
                />

                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.15em] text-cyan-400">
                    Intelligence interpretation
                  </p>

                  <p className="mt-2 text-sm leading-7 text-slate-300">
                    {insights.Insight}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Demographic context */}
        <section className="mt-16">
          <SectionHeading
            icon={Users}
            eyebrow="Demographic context"
            title="Supporting demographic indicators"
            description={
              report.demographic_context?.message ||
              "Indicators are shown according to their actual availability and source status."
            }
          />

          {demographicIndicators.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {demographicIndicators.map((indicator) => {
                const Icon = getIndicatorIcon(indicator.category);

                return (
                  <motion.div
                    key={indicator.key}
                    whileHover={{ y: -3 }}
                    className="rounded-2xl border border-white/10 bg-white/[0.025] p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.13em] text-slate-500">
                          {indicator.category || "Indicator"}
                        </p>

                        <h3 className="mt-2 font-semibold text-white">
                          {indicator.label}
                        </h3>
                      </div>

                      <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-400/15 bg-cyan-400/5 text-cyan-300">
                        <Icon size={17} />
                      </div>
                    </div>

                    <p className="mt-5 text-2xl font-bold text-white">
                      {formatNumber(indicator.value, 2)}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {indicator.unit || ""}
                    </p>

                    <div className="mt-5 border-t border-white/10 pt-4">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500">Source year</span>
                        <span className="font-semibold text-slate-300">
                          {indicator.source_year ?? "—"}
                        </span>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-slate-500">Status</span>
                        <span className="text-right font-medium text-cyan-300">
                          {indicator.source_status || "—"}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-6 text-sm text-slate-400">
              No supporting demographic indicators are currently available
              from the backend for this report.
            </div>
          )}
        </section>

        {/* Policy signals */}
        <section className="mt-16">
          <SectionHeading
            icon={Landmark}
            eyebrow="Policy intelligence"
            title="Planning signals"
            description="These are analytical interpretations generated by the intelligence layer, not official government recommendations."
          />

          {policySignals.length > 0 ? (
            <div className="grid gap-5 lg:grid-cols-2">
              {policySignals.map((signal, index) => (
                <motion.div
                  key={`${signal.type}-${index}`}
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="rounded-2xl border border-amber-400/15 bg-amber-400/[0.025] p-6"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/10 text-amber-300">
                      <Landmark size={19} />
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-[0.14em] text-amber-400">
                        {signal.type || "Analytical signal"}
                      </p>

                      <h3 className="mt-2 font-semibold text-white">
                        {signal.title}
                      </h3>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {signal.description}
                      </p>

                      {signal.policy_relevance && (
                        <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-4">
                          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                            Policy relevance
                          </p>

                          <p className="mt-2 text-sm leading-6 text-slate-300">
                            {signal.policy_relevance}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-6 text-sm text-slate-400">
              No policy signals were detected for this year.
            </div>
          )}

          {report.policy_signals?.disclaimer && (
            <p className="mt-4 text-xs leading-5 text-slate-600">
              {report.policy_signals.disclaimer}
            </p>
          )}
        </section>

        {/* Model reliability */}
        <section className="mt-16">
          <SectionHeading
            icon={Gauge}
            eyebrow="Model evaluation"
            title="How the forecasting system has performed"
            description="Historical backtesting provides evidence about model performance. It does not guarantee future forecast accuracy."
          />

          <div className="grid gap-5 lg:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-6">
              <div className="flex items-center gap-3">
                <Gauge className="text-cyan-300" size={21} />

                <div>
                  <p className="text-xs uppercase tracking-[0.13em] text-slate-500">
                    Selected model
                  </p>

                  <p className="mt-1 text-xl font-bold text-white">
                    {reliability.model || "—"}
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                {(reliability.backtesting || []).map((item) => (
                  <div
                    key={`${item.Start_Year}-${item.End_Year}`}
                    className="rounded-xl border border-white/10 bg-black/20 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-white">
                        {item.Start_Year}–{item.End_Year}
                      </span>

                      <span className="text-xs text-slate-500">
                        Backtest
                      </span>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-xs text-slate-600">MAE</p>
                        <p className="mt-1 font-semibold text-slate-300">
                          {formatNumber(item.MAE)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-600">RMSE</p>
                        <p className="mt-1 font-semibold text-slate-300">
                          {formatNumber(item.RMSE)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-600">R²</p>
                        <p className="mt-1 font-semibold text-slate-300">
                          {Number(item.R2).toFixed(5)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-600">MPE</p>
                        <p className="mt-1 font-semibold text-slate-300">
                          {formatPercent(item.Mean_Percentage_Error, 4)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-6">
              <div className="flex items-center gap-3">
                <Database className="text-violet-300" size={21} />

                <div>
                  <p className="text-xs uppercase tracking-[0.13em] text-slate-500">
                    Data provenance
                  </p>

                  <p className="mt-1 text-xl font-bold text-white">
                    Transparent by design
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Historical</p>
                  <p className="mt-1 font-semibold text-white">
                    {provenance.historical?.years || "1960–2024"}
                  </p>
                  <p className="mt-1 text-xs text-emerald-300">
                    {provenance.historical?.status || "Official historical data"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">2025</p>
                  <p className="mt-1 font-semibold text-white">
                    Model estimated
                  </p>
                  <p className="mt-1 text-xs text-amber-300">
                    Not treated as official historical observation
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Forecast</p>
                  <p className="mt-1 font-semibold text-white">
                    {provenance.forecast?.years || "2026–2050"}
                  </p>
                  <p className="mt-1 text-xs text-violet-300">
                    {provenance.forecast?.model || "Linear Regression"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Limitations */}
        <section className="mt-16">
          <SectionHeading
            icon={Info}
            eyebrow="Transparency"
            title="Interpretation limits"
            description="These limitations are part of the intelligence report and should remain visible to users."
          />

          <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6">
            <div className="grid gap-3 md:grid-cols-2">
              {limitations.map((limitation, index) => (
                <div
                  key={index}
                  className="flex gap-3 rounded-xl border border-white/5 bg-black/10 p-4"
                >
                  <Info
                    size={16}
                    className="mt-0.5 shrink-0 text-slate-500"
                  />

                  <p className="text-sm leading-6 text-slate-400">
                    {limitation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Bottom navigation */}
        <section className="mt-16">
          <div className="flex flex-col items-center justify-between gap-5 rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6 sm:flex-row">
            <div>
              <p className="font-semibold text-white">
                Explore another year
              </p>

              <p className="mt-1 text-sm text-slate-500">
                Return to the national command center and select another year
                between 1960 and 2050.
              </p>
            </div>

            <Link
              to="/national"
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
            >
              Open Year Explorer
              <ArrowLeft size={16} className="rotate-180" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}