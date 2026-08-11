import { useEffect, useState } from "react";
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  Database,
  GitBranch,
  Layers3,
  ShieldCheck,
  Target,
  Workflow,
  XCircle,
} from "lucide-react";
import { motion } from "framer-motion";

import Navbar from "../components/Navbar";
import AmbientPopulationScene from "../components/AmbientPopulationScene";

import {
  getDataStatus,
  getModelInfo,
  getYearRange,
} from "../services/api";

export default function DataModel() {
  const [model, setModel] = useState(null);
  const [dataStatus, setDataStatus] = useState(null);
  const [range, setRange] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      const results = await Promise.allSettled([
        getModelInfo(),
        getDataStatus(),
        getYearRange(),
      ]);

      if (!mounted) return;

      if (results[0].status === "fulfilled") {
        setModel(results[0].value);
      }

      if (results[1].status === "fulfilled") {
        setDataStatus(results[1].value);
      }

      if (results[2].status === "fulfilled") {
        setRange(results[2].value);
      }
    }

    load();

    return () => {
      mounted = false;
    };
  }, []);

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
            <div className="flex items-center gap-2 text-emerald-300">
              <ShieldCheck size={16} />

              <span className="text-[10px] font-bold uppercase tracking-[0.2em]">
                Data & Model Observatory
              </span>
            </div>

            <h1 className="mt-5 max-w-4xl text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Show the machinery.
              <span className="block text-emerald-400">
                Hide nothing important.
              </span>
            </h1>

            <p className="mt-6 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
              This page explains where the numbers come from, how the existing
              model works, how it was validated, and where its limitations
              begin.
            </p>
          </section>

          {/* ========================================================
              DATA CLASSIFICATION
          ======================================================== */}

          <section className="mt-10">
            <div className="mb-6">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-400">
                Data provenance
              </p>

              <h2 className="mt-2 text-3xl font-black">
                Three different kinds of numbers
              </h2>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <ProvenanceCard
                icon={Database}
                title="Official Historical"
                period="1960–2024"
                description="Historical population observations from the project's official source pipeline."
                tone="cyan"
              />

              <ProvenanceCard
                icon={Target}
                title="Model Estimated"
                period="2025"
                description="2025 is treated as a model estimate because an official 2025 population observation is not available in the project's historical source."
                tone="amber"
              />

              <ProvenanceCard
                icon={BrainCircuit}
                title="ML Forecast"
                period="2026–2050"
                description="Recursive forecasts produced by the existing Linear Regression population-change model."
                tone="violet"
              />
            </div>
          </section>

          {/* ========================================================
              MODEL
          ======================================================== */}

          <section className="mt-14 rounded-3xl border border-white/10 bg-white/[0.025] p-7 sm:p-9">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
                <BrainCircuit size={20} />
              </div>

              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400">
                  Existing ML model
                </p>

                <h2 className="mt-1 text-2xl font-black">
                  Linear Regression
                </h2>
              </div>
            </div>

            <p className="mt-6 max-w-3xl text-sm leading-7 text-slate-500">
              The selected model predicts annual population change rather
              than directly predicting the entire population as a static
              lookup. Forecasting is then performed recursively across the
              future horizon.
            </p>

            <div className="mt-8 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {[
                "Year",
                "Previous Population",
                "Population Lag 2",
                "Population Lag 3",
                "Population MA3",
                "Birth Rate Lag 1",
                "Death Rate Lag 1",
                "Fertility Rate Lag 1",
                "Life Expectancy Lag 1",
                "GDP Growth Lag 1",
                "Net Migration Lag 1",
                "Literacy Rate Lag 1",
                "Urban Population Lag 1",
                "Infant Mortality Lag 1",
                "Population Density Lag 1",
              ].map((feature, index) => (
                <div
                  key={feature}
                  className="flex items-center gap-3 rounded-xl border border-white/5 bg-black/10 p-3"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-md bg-cyan-400/10 text-[10px] font-bold text-cyan-300">
                    {index + 1}
                  </span>

                  <span className="text-xs text-slate-400">
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* ========================================================
              VALIDATION
          ======================================================== */}

          <section className="mt-14">
            <div className="mb-7">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-400">
                Validation
              </p>

              <h2 className="mt-2 text-3xl font-black">
                Model performance is visible.
              </h2>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <ValidationCard
                period="2010–2020"
                mae="491,073"
                rmse="640,566"
                r2="0.99984"
                mpe="0.0363%"
              />

              <ValidationCard
                period="2015–2024"
                mae="1,010,796"
                rmse="1,390,182"
                r2="0.99872"
                mpe="0.0713%"
              />
            </div>
          </section>

          {/* ========================================================
              PIPELINE
          ======================================================== */}

          <section className="mt-14 rounded-3xl border border-white/10 bg-white/[0.025] p-7 sm:p-9">
            <div className="flex items-center gap-3">
              <Workflow className="text-emerald-300" size={20} />

              <h2 className="text-2xl font-black">
                End-to-end architecture
              </h2>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["01", "Official Data"],
                ["02", "Preprocessing"],
                ["03", "Feature Engineering"],
                ["04", "Model Selection"],
                ["05", "Forecasting"],
                ["06", "Analytics"],
                ["07", "Intelligence"],
                ["08", "FastAPI"],
                ["09", "Interactive UI"],
                ["10", "Future Admin Layer"],
              ].map(([number, name]) => (
                <div
                  key={number}
                  className="rounded-xl border border-white/5 bg-black/10 p-4"
                >
                  <div className="text-[10px] font-bold text-emerald-400">
                    {number}
                  </div>

                  <div className="mt-2 text-sm font-semibold text-white">
                    {name}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ========================================================
              LIMITATIONS
          ======================================================== */}

          <section className="mt-14 grid gap-4 lg:grid-cols-2">
            <div className="rounded-3xl border border-amber-400/10 bg-amber-400/[0.025] p-7">
              <XCircle className="text-amber-300" size={20} />

              <h3 className="mt-5 text-xl font-bold">
                Forecasts are not certainties.
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-500">
                A strong historical backtest does not mean future outcomes
                are guaranteed. Structural demographic changes, migration,
                economic shocks, policy changes, and unexpected events can
                affect real-world population trajectories.
              </p>
            </div>

            <div className="rounded-3xl border border-cyan-400/10 bg-cyan-400/[0.025] p-7">
              <CheckCircle2 className="text-cyan-300" size={20} />

              <h3 className="mt-5 text-xl font-bold">
                Transparency is part of the model.
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-500">
                Historical, estimated, and forecast values remain explicitly
                classified so users can understand what they are actually
                looking at.
              </p>
            </div>
          </section>

          {/* ========================================================
              API SNAPSHOT
          ======================================================== */}

          <section className="mt-14 rounded-3xl border border-white/10 bg-white/[0.025] p-7">
            <div className="flex items-center gap-3">
              <Layers3 size={20} className="text-cyan-300" />

              <h2 className="text-xl font-bold">
                Live API connection
              </h2>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              <MiniStatus
                label="Model API"
                value={model ? "Connected" : "Loading"}
              />

              <MiniStatus
                label="Data status"
                value={dataStatus ? "Connected" : "Loading"}
              />

              <MiniStatus
                label="Coverage"
                value={
                  range
                    ? `${range.start_year ?? 1960}–${range.end_year ?? 2050}`
                    : "1960–2050"
                }
              />
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

function ProvenanceCard({
  icon: Icon,
  title,
  period,
  description,
  tone,
}) {
  const styles = {
    cyan: "border-cyan-400/15 bg-cyan-400/[0.025] text-cyan-300",
    amber: "border-amber-400/15 bg-amber-400/[0.025] text-amber-300",
    violet: "border-violet-400/15 bg-violet-400/[0.025] text-violet-300",
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className={`rounded-3xl border p-6 ${styles[tone]}`}
    >
      <Icon size={21} />

      <h3 className="mt-5 text-lg font-bold text-white">
        {title}
      </h3>

      <div className="mt-2 text-2xl font-black">
        {period}
      </div>

      <p className="mt-3 text-sm leading-6 text-slate-500">
        {description}
      </p>
    </motion.div>
  );
}

function ValidationCard({
  period,
  mae,
  rmse,
  r2,
  mpe,
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.025] p-6">
      <div className="flex items-center gap-3">
        <Activity className="text-violet-300" size={19} />

        <h3 className="font-bold">
          Backtest {period}
        </h3>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3">
        <Metric label="MAE" value={mae} />
        <Metric label="RMSE" value={rmse} />
        <Metric label="R²" value={r2} />
        <Metric label="MPE" value={mpe} />
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/10 p-3">
      <div className="text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </div>

      <div className="mt-1 text-sm font-bold text-white">
        {value}
      </div>
    </div>
  );
}

function MiniStatus({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/10 p-4">
      <div className="text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </div>

      <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-emerald-300">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        {value}
      </div>
    </div>
  );
}