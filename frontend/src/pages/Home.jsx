import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  ArrowRight,
  BarChart3,
  Database,
  Globe2,
  LockKeyhole,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingDown,
  Users,
} from "lucide-react";

import { motion } from "framer-motion";

import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";

import { Line } from "react-chartjs-2";

import Navbar from "../components/Navbar";
import AmbientPopulationScene from "../components/AmbientPopulationScene";

import {
  getDashboardChart,
  getDataStatus,
  getModelInfo,
  getYearRange,
} from "../services/api";


/* ================================================================
   CHART.JS REGISTRATION
================================================================ */

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
);


/* ================================================================
   FORMATTERS
================================================================ */

function formatPopulation(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(Number(value));
}


function compactPopulation(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  if (number >= 1_000_000_000) {
    return `${(number / 1_000_000_000).toFixed(2)}B`;
  }

  if (number >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(2)}M`;
  }

  if (number >= 1_000) {
    return `${(number / 1_000).toFixed(1)}K`;
  }

  return formatPopulation(number);
}


/* ================================================================
   RESPONSE NORMALIZER
================================================================ */

function normalizeRows(response) {
  if (Array.isArray(response)) {
    return response;
  }

  if (Array.isArray(response?.data)) {
    return response.data;
  }

  return [];
}


/* ================================================================
   DATA SOURCE CLASSIFICATION
================================================================ */

function sourceType(row) {
  const source = String(
    row?.Source_Type ??
      row?.source_type ??
      "",
  ).toLowerCase();

  const status = String(
    row?.Data_Status ??
      row?.data_status ??
      "",
  ).toLowerCase();


  if (
    source.includes("forecast") ||
    source.includes("ml") ||
    status.includes("forecast")
  ) {
    return "forecast";
  }


  if (
    source.includes("estimated") ||
    status.includes("estimated") ||
    status.includes("model")
  ) {
    return "estimated";
  }


  return "historical";
}


/* ================================================================
   SOURCE LABEL
================================================================ */

function sourceLabel(type) {
  if (type === "forecast") {
    return "ML Forecast";
  }

  if (type === "estimated") {
    return "Model Estimated";
  }

  return "Historical / Official";
}


/* ================================================================
   SOURCE BADGE
================================================================ */

function SourceBadge({ type }) {
  const styles = {
    historical:
      "border-blue-400/20 bg-blue-400/10 text-blue-300",

    estimated:
      "border-amber-400/20 bg-amber-400/10 text-amber-300",

    forecast:
      "border-violet-400/20 bg-violet-400/10 text-violet-300",
  };


  return (
    <span
      className={[
        "inline-flex rounded-full border px-2.5 py-1",
        "text-[10px] font-semibold uppercase tracking-wide",
        styles[type] || styles.historical,
      ].join(" ")}
    >
      {sourceLabel(type)}
    </span>
  );
}


/* ================================================================
   ANIMATED NUMBER
================================================================ */

function AnimatedNumber({
  value,
  formatter = compactPopulation,
}) {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return <span>—</span>;
  }


  return (
    <motion.span
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.5,
      }}
    >
      {formatter(numericValue)}
    </motion.span>
  );
}


/* ================================================================
   STAT CARD
================================================================ */

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
  accent,
  loading,
}) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 18,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      whileHover={{
        y: -4,
      }}
      transition={{
        duration: 0.45,
      }}
      className="
        group
        rounded-2xl
        border
        border-white/10
        bg-white/[0.035]
        p-5
        backdrop-blur-sm
        transition
      "
    >
      <div className="flex items-start justify-between">

        <div>
          <p
            className="
              text-[10px]
              font-semibold
              uppercase
              tracking-[0.16em]
              text-slate-500
            "
          >
            {label}
          </p>


          {loading ? (
            <div
              className="
                mt-3
                h-8
                w-28
                animate-pulse
                rounded-lg
                bg-white/10
              "
            />
          ) : (
            <p
              className="
                mt-2
                text-2xl
                font-black
                tracking-tight
                text-white
              "
            >
              <AnimatedNumber value={value} />
            </p>
          )}


          <p className="mt-2 text-xs text-slate-500">
            {detail}
          </p>
        </div>


        <div
          className={[
            "rounded-xl border p-2.5",

            accent === "cyan"
              ? "border-cyan-400/10 bg-cyan-400/10 text-cyan-300"

              : accent === "blue"
                ? "border-blue-400/10 bg-blue-400/10 text-blue-300"

                : accent === "violet"
                  ? "border-violet-400/10 bg-violet-400/10 text-violet-300"

                  : "border-emerald-400/10 bg-emerald-400/10 text-emerald-300",
          ].join(" ")}
        >
          <Icon size={18} />
        </div>

      </div>
    </motion.div>
  );
}


/* ================================================================
   LOCKED FUTURE MODULE
================================================================ */

function LockedModule({
  icon: Icon,
  title,
  description,
  examples,
}) {
  return (
    <motion.div
      whileHover={{
        y: -5,
      }}
      className="
        group
        relative
        overflow-hidden
        rounded-2xl
        border
        border-white/10
        bg-white/[0.025]
        p-6
      "
    >

      <div
        className="
          absolute
          right-0
          top-0
          h-28
          w-28
          rounded-full
          bg-violet-400/5
          blur-3xl
        "
      />


      <div className="relative">

        <div className="flex items-start justify-between">

          <div
            className="
              rounded-xl
              border
              border-violet-400/15
              bg-violet-400/10
              p-3
              text-violet-300
            "
          >
            <Icon size={21} />
          </div>


          <span
            className="
              inline-flex
              items-center
              gap-1.5
              rounded-full
              border
              border-white/10
              bg-white/5
              px-2.5
              py-1
              text-[9px]
              font-bold
              uppercase
              tracking-wider
              text-slate-400
            "
          >
            <LockKeyhole size={11} />
            Coming Soon
          </span>

        </div>


        <h3 className="mt-5 text-lg font-bold text-white">
          {title}
        </h3>


        <p className="mt-2 text-sm leading-6 text-slate-500">
          {description}
        </p>


        <div className="mt-5 flex flex-wrap gap-2">
          {examples.map((example) => (
            <span
              key={example}
              className="
                rounded-lg
                border
                border-white/10
                bg-white/[0.03]
                px-2.5
                py-1.5
                text-[10px]
                text-slate-500
              "
            >
              {example}
            </span>
          ))}
        </div>

      </div>
    </motion.div>
  );
}


/* ================================================================
   MAIN HOME PAGE
================================================================ */

export default function Home() {

  /* --------------------------------------------------------------
     ROUTER
  -------------------------------------------------------------- */

  const navigate = useNavigate();


  /* --------------------------------------------------------------
     STATE
  -------------------------------------------------------------- */

  const [rows, setRows] = useState([]);

  const [yearRange, setYearRange] = useState(null);

  const [modelInfo, setModelInfo] = useState(null);

  const [dataStatus, setDataStatus] = useState([]);

  const [searchInput, setSearchInput] = useState("");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");


  /* ================================================================
     LOAD DASHBOARD DATA
  ================================================================ */

  useEffect(() => {

    async function load() {

      try {

        const [
          chartResponse,
          rangeResponse,
          modelResponse,
          statusResponse,
        ] = await Promise.all([
          getDashboardChart(),
          getYearRange(),
          getModelInfo(),
          getDataStatus(),
        ]);


        setRows(
          normalizeRows(chartResponse),
        );


        setYearRange(
          rangeResponse,
        );


        setModelInfo(
          modelResponse,
        );


        setDataStatus(
          normalizeRows(statusResponse),
        );

      } catch (err) {

        console.error(err);

        setError(
          err?.message ||
            "Unable to load population intelligence.",
        );

      } finally {

        setLoading(false);

      }
    }


    load();

  }, []);


  /* ================================================================
     SORT DATA
  ================================================================ */

  const sortedRows = useMemo(
    () =>
      [...rows].sort(
        (a, b) =>
          Number(a.Year) -
          Number(b.Year),
      ),
    [rows],
  );


  /* ================================================================
     DATA CLASSIFICATIONS
  ================================================================ */

  const historical = sortedRows.filter(
    (row) =>
      sourceType(row) === "historical",
  );


  const estimated = sortedRows.filter(
    (row) =>
      sourceType(row) === "estimated",
  );


  const forecast = sortedRows.filter(
    (row) =>
      sourceType(row) === "forecast",
  );


  /* ================================================================
     LATEST DATA POINTS
  ================================================================ */

  const latestHistorical =
    historical.at(-1);


  const latestEstimated =
    estimated.at(-1);


  const finalForecast =
    forecast.at(-1);


  /* ================================================================
     POPULATION CHART DATA
  ================================================================ */

  const chartData = {

    labels: sortedRows.map(
      (row) => row.Year,
    ),

    datasets: [

      {
        label: "Historical / Official",

        data: sortedRows.map(
          (row) =>
            sourceType(row) ===
            "historical"
              ? Number(row.Population)
              : null,
        ),

        borderColor: "#60a5fa",

        backgroundColor:
          "rgba(96,165,250,0.08)",

        borderWidth: 2,

        pointRadius: 0,

        pointHoverRadius: 5,

        tension: 0.28,

      },


      {
        label: "Model Estimated",

        data: sortedRows.map(
          (row) =>
            sourceType(row) ===
            "estimated"
              ? Number(row.Population)
              : null,
        ),

        borderColor: "#f59e0b",

        backgroundColor:
          "rgba(245,158,11,0.1)",

        borderWidth: 3,

        pointRadius: 5,

        pointHoverRadius: 7,

        tension: 0.28,

      },


      {
        label: "ML Forecast",

        data: sortedRows.map(
          (row) =>
            sourceType(row) ===
            "forecast"
              ? Number(row.Population)
              : null,
        ),

        borderColor: "#a78bfa",

        backgroundColor:
          "rgba(167,139,250,0.08)",

        borderWidth: 2,

        borderDash: [7, 6],

        pointRadius: 0,

        pointHoverRadius: 5,

        tension: 0.28,

      },

    ],
  };


  /* ================================================================
     CHART OPTIONS
  ================================================================ */

  const chartOptions = {

    responsive: true,

    maintainAspectRatio: false,

    interaction: {
      mode: "index",
      intersect: false,
    },


    animation: {
      duration: 1400,
      easing: "easeOutQuart",
    },


    plugins: {

      legend: {

        position: "bottom",

        labels: {

          color: "#94a3b8",

          usePointStyle: true,

          padding: 18,

          font: {
            size: 11,
          },

        },

      },


      tooltip: {

        backgroundColor: "#020617",

        borderColor:
          "rgba(255,255,255,0.1)",

        borderWidth: 1,

        padding: 12,

        callbacks: {

          label(context) {

            return `${
              context.dataset.label
            }: ${formatPopulation(
              context.raw,
            )}`;

          },

        },

      },

    },


    scales: {

      x: {

        grid: {
          color:
            "rgba(255,255,255,0.035)",
        },

        ticks: {

          color: "#64748b",

          maxTicksLimit: 12,

        },

      },


      y: {

        grid: {
          color:
            "rgba(255,255,255,0.035)",
        },

        ticks: {

          color: "#64748b",

          callback(value) {

            return `${(
              Number(value) /
              1_000_000_000
            ).toFixed(1)}B`;

          },

        },

      },

    },

  };


  /* ================================================================
     YEAR EXPLORER
     
     IMPORTANT:
     This no longer calls the API directly.
     
     It navigates to:
     
     /national/year/{year}
     
     The dedicated YearIntelligence page then calls:
     
     /api/intelligence/year/{year}
  ================================================================ */

  function handleYearSearch(event) {

    event.preventDefault();


    const year =
      Number(searchInput);


    /* --------------------------------------------------------------
       Empty / invalid input
    -------------------------------------------------------------- */

    if (!Number.isInteger(year)) {

      setError(
        "Enter a valid year.",
      );

      return;
    }


    /* --------------------------------------------------------------
       Supported range
    -------------------------------------------------------------- */

    if (
      year < 1960 ||
      year > 2050
    ) {

      setError(
        "Year must be between 1960 and 2050.",
      );

      return;
    }


    /* --------------------------------------------------------------
       Clear previous error
    -------------------------------------------------------------- */

    setError("");


    /* --------------------------------------------------------------
       OPEN DEDICATED YEAR PAGE
    -------------------------------------------------------------- */

    navigate(
      `/national/year/${year}`,
    );
  }


  /* ================================================================
     TABLE
  ================================================================ */

  const visibleRows = [
    ...sortedRows,
  ]
    .reverse()
    .slice(0, 10);


  /* ================================================================
     UI
  ================================================================ */

  return (

    <div
      className="
        min-h-screen
        overflow-hidden
        bg-slate-950
        text-white
      "
    >

      {/* ============================================================
          NAVBAR
      ============================================================ */}

      <Navbar />


      <main
        className="
          mx-auto
          max-w-[1500px]
          px-5
          pb-24
          pt-24
          sm:px-8
        "
      >

        {/* ==========================================================
            HERO
        ========================================================== */}

        <section
          className="
            relative
            min-h-[470px]
            overflow-hidden
            rounded-[2rem]
            border
            border-white/10
            bg-[#030712]
          "
        >

          <AmbientPopulationScene />


          <div
            className="
              relative
              z-10
              flex
              min-h-[470px]
              items-center
              p-7
              sm:p-12
              lg:p-16
            "
          >

            <div className="max-w-3xl">

              {/* Badge */}

              <motion.div
                initial={{
                  opacity: 0,
                  y: 15,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  duration: 0.7,
                }}
                className="
                  mb-5
                  inline-flex
                  items-center
                  gap-2
                  rounded-full
                  border
                  border-cyan-400/15
                  bg-cyan-400/5
                  px-3
                  py-1.5
                "
              >

                <Sparkles
                  size={13}
                  className="text-cyan-300"
                />

                <span
                  className="
                    text-[10px]
                    font-bold
                    uppercase
                    tracking-[0.18em]
                    text-cyan-300
                  "
                >
                  National Demographic Intelligence
                </span>

              </motion.div>


              {/* Main title */}

              <motion.h1
                initial={{
                  opacity: 0,
                  y: 25,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  duration: 0.8,
                  delay: 0.1,
                }}
                className="
                  text-4xl
                  font-black
                  tracking-[-0.04em]
                  sm:text-6xl
                  lg:text-7xl
                "
              >

                India&apos;s population,

                <span
                  className="
                    block
                    bg-gradient-to-r
                    from-cyan-300
                    via-blue-300
                    to-violet-300
                    bg-clip-text
                    text-transparent
                  "
                >
                  decoded by data.
                </span>

              </motion.h1>


              {/* Description */}

              <motion.p
                initial={{
                  opacity: 0,
                }}
                animate={{
                  opacity: 1,
                }}
                transition={{
                  duration: 0.8,
                  delay: 0.35,
                }}
                className="
                  mt-6
                  max-w-2xl
                  text-sm
                  leading-7
                  text-slate-400
                  sm:text-base
                "
              >
                Explore India&apos;s demographic trajectory from
                historical observations through model-estimated
                data and machine-learning forecasts to 2050.
              </motion.p>


              {/* CTA */}

              <motion.div
                initial={{
                  opacity: 0,
                  y: 10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  duration: 0.7,
                  delay: 0.5,
                }}
                className="mt-8 flex flex-wrap gap-3"
              >

                <a
                  href="#population-data"
                  className="
                    inline-flex
                    items-center
                    gap-2
                    rounded-xl
                    bg-cyan-400
                    px-5
                    py-3
                    text-sm
                    font-bold
                    text-slate-950
                    transition
                    hover:bg-cyan-300
                  "
                >
                  Explore population data

                  <ArrowRight size={16} />

                </a>


                <a
                  href="#year-explorer"
                  className="
                    inline-flex
                    items-center
                    gap-2
                    rounded-xl
                    border
                    border-white/10
                    bg-white/5
                    px-5
                    py-3
                    text-sm
                    font-semibold
                    text-slate-200
                    transition
                    hover:bg-white/10
                  "
                >
                  Explore a year
                </a>

              </motion.div>

            </div>

          </div>

        </section>


        {/* ==========================================================
            KPI CARDS
        ========================================================== */}

        <section
          className="
            mt-5
            grid
            gap-4
            sm:grid-cols-2
            xl:grid-cols-4
          "
        >

          <StatCard
            icon={Users}
            label={`Latest official · ${
              latestHistorical?.Year ?? "—"
            }`}
            value={
              latestHistorical?.Population
            }
            detail="Historical observation"
            accent="blue"
            loading={loading}
          />


          <StatCard
            icon={Activity}
            label={`Estimated · ${
              latestEstimated?.Year ?? "—"
            }`}
            value={
              latestEstimated?.Population
            }
            detail="Model-estimated year"
            accent="emerald"
            loading={loading}
          />


          <StatCard
            icon={TrendingDown}
            label={`ML forecast · ${
              finalForecast?.Year ?? "—"
            }`}
            value={
              finalForecast?.Population
            }
            detail="Forecast endpoint"
            accent="violet"
            loading={loading}
          />


          <StatCard
            icon={Globe2}
            label="Coverage"
            value={
              yearRange
                ? `${yearRange.start_year}–${yearRange.end_year}`
                : null
            }
            detail={`${
              yearRange?.total_years ?? "—"
            } available years`}
            accent="cyan"
            loading={loading}
          />

        </section>


        {/* ==========================================================
            ERROR MESSAGE
        ========================================================== */}

        {error && (

          <motion.div
            initial={{
              opacity: 0,
              y: -10,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            className="
              mt-5
              rounded-xl
              border
              border-red-400/20
              bg-red-400/5
              px-4
              py-3
              text-sm
              text-red-300
            "
          >
            {error}
          </motion.div>

        )}


        {/* ==========================================================
            POPULATION OBSERVATORY
        ========================================================== */}

        <section
          id="population-data"
          className="mt-14 scroll-mt-24"
        >

          <div
            className="
              mb-6
              flex
              flex-col
              justify-between
              gap-4
              lg:flex-row
              lg:items-end
            "
          >

            <div>

              <p
                className="
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-[0.2em]
                  text-cyan-400
                "
              >
                Population Observatory
              </p>


              <h2
                className="
                  mt-2
                  text-3xl
                  font-black
                  tracking-tight
                "
              >
                India&apos;s demographic trajectory
              </h2>


              <p
                className="
                  mt-2
                  max-w-2xl
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                One continuous view across the available national
                dataset, with every data classification explicitly
                labelled.
              </p>

            </div>


            <div
              className="
                flex
                items-center
                gap-2
                text-xs
                text-slate-500
              "
            >
              <Database size={14} />
              Live API data
            </div>

          </div>


          <div
            className="
              rounded-3xl
              border
              border-white/10
              bg-white/[0.025]
              p-5
              sm:p-7
            "
          >

            <div className="mb-5 flex flex-wrap gap-2">

              <SourceBadge type="historical" />

              <SourceBadge type="estimated" />

              <SourceBadge type="forecast" />

            </div>


            <div className="h-[400px]">

              {loading ? (

                <div
                  className="
                    h-full
                    animate-pulse
                    rounded-2xl
                    bg-white/[0.025]
                  "
                />

              ) : (

                <Line
                  data={chartData}
                  options={chartOptions}
                />

              )}

            </div>

          </div>

        </section>


        {/* ==========================================================
            YEAR EXPLORER
        ========================================================== */}

        <section
          id="year-explorer"
          className="mt-14 scroll-mt-24"
        >

          <div
            className="
              grid
              gap-6
              lg:grid-cols-[1fr_1.4fr]
            "
          >

            {/* ------------------------------------------------------
                SEARCH PANEL
            ------------------------------------------------------ */}

            <div
              className="
                rounded-3xl
                border
                border-white/10
                bg-gradient-to-br
                from-cyan-400/[0.06]
                to-transparent
                p-7
              "
            >

              <p
                className="
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-[0.2em]
                  text-cyan-400
                "
              >
                Year Explorer
              </p>


              <h2
                className="
                  mt-3
                  text-2xl
                  font-black
                "
              >
                Ask the demographic engine.
              </h2>


              <p
                className="
                  mt-3
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                Enter any year between 1960 and 2050 to open
                its complete national demographic intelligence
                report.
              </p>


              {/* SEARCH FORM */}

              <form
                onSubmit={handleYearSearch}
                className="mt-6 flex gap-2"
              >

                <div className="relative flex-1">

                  <Search
                    size={16}
                    className="
                      absolute
                      left-3
                      top-1/2
                      -translate-y-1/2
                      text-slate-600
                    "
                  />


                  <input
                    type="number"
                    min="1960"
                    max="2050"
                    value={searchInput}
                    onChange={(event) => {
                      setSearchInput(
                        event.target.value,
                      );

                      if (error) {
                        setError("");
                      }
                    }}
                    placeholder="Enter year..."
                    className="
                      w-full
                      rounded-xl
                      border
                      border-white/10
                      bg-black/20
                      py-3
                      pl-10
                      pr-3
                      text-sm
                      text-white
                      outline-none
                      transition
                      placeholder:text-slate-600
                      focus:border-cyan-400/30
                    "
                  />

                </div>


                <button
                  type="submit"
                  className="
                    rounded-xl
                    bg-cyan-400
                    px-4
                    text-sm
                    font-bold
                    text-slate-950
                    transition
                    hover:bg-cyan-300
                    hover:shadow-lg
                    hover:shadow-cyan-400/10
                  "
                >
                  Explore
                </button>

              </form>


              <div className="mt-4 flex flex-wrap gap-2">

                {[
                  1960,
                  2000,
                  2025,
                  2035,
                  2050,
                ].map((year) => (

                  <button
                    key={year}
                    type="button"
                    onClick={() => {
                      setSearchInput(
                        String(year),
                      );

                      setError("");

                      navigate(
                        `/national/year/${year}`,
                      );
                    }}
                    className="
                      rounded-lg
                      border
                      border-white/10
                      bg-white/[0.03]
                      px-2.5
                      py-1.5
                      text-[10px]
                      text-slate-500
                      transition
                      hover:border-cyan-400/20
                      hover:bg-cyan-400/5
                      hover:text-cyan-300
                    "
                  >
                    {year}
                  </button>

                ))}

              </div>

            </div>


            {/* ------------------------------------------------------
                INTELLIGENCE PREVIEW
            ------------------------------------------------------ */}

            <div
              className="
                rounded-3xl
                border
                border-white/10
                bg-white/[0.025]
                p-7
              "
            >

              <div
                className="
                  flex
                  h-full
                  min-h-[230px]
                  flex-col
                  justify-center
                "
              >

                <div
                  className="
                    flex
                    items-center
                    gap-3
                  "
                >

                  <div
                    className="
                      flex
                      h-11
                      w-11
                      items-center
                      justify-center
                      rounded-xl
                      border
                      border-cyan-400/15
                      bg-cyan-400/10
                      text-cyan-300
                    "
                  >
                    <Sparkles size={20} />
                  </div>


                  <div>

                    <p
                      className="
                        text-xs
                        font-bold
                        uppercase
                        tracking-[0.15em]
                        text-cyan-400
                      "
                    >
                      Full Intelligence Report
                    </p>


                    <h3
                      className="
                        mt-1
                        text-xl
                        font-bold
                        text-white
                      "
                    >
                      Explore an entire year
                    </h3>

                  </div>

                </div>


                <p
                  className="
                    mt-5
                    text-sm
                    leading-6
                    text-slate-500
                  "
                >
                  Every selected year opens a dedicated intelligence
                  page instead of displaying a small result card here.
                  The report can include population, growth dynamics,
                  forecast context, demographic indicators, model
                  reliability, policy signals, milestones, provenance,
                  and analytical insights.
                </p>


                <div
                  className="
                    mt-5
                    grid
                    gap-2
                    sm:grid-cols-2
                  "
                >

                  {[
                    "Population forecast",
                    "Growth intelligence",
                    "Model reliability",
                    "Policy signals",
                    "Demographic context",
                    "Data provenance",
                  ].map((item) => (

                    <div
                      key={item}
                      className="
                        rounded-lg
                        border
                        border-white/5
                        bg-black/10
                        px-3
                        py-2
                        text-xs
                        text-slate-500
                      "
                    >
                      <span className="text-cyan-400">
                        ✓
                      </span>{" "}
                      {item}
                    </div>

                  ))}

                </div>

              </div>

            </div>

          </div>

        </section>


        {/* ==========================================================
            LIVE DATA TABLE
        ========================================================== */}

        <section className="mt-14">

          <div
            className="
              mb-6
              flex
              items-end
              justify-between
            "
          >

            <div>

              <p
                className="
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-[0.2em]
                  text-cyan-400
                "
              >
                Data Explorer
              </p>


              <h2
                className="
                  mt-2
                  text-2xl
                  font-black
                "
              >
                Inspect the underlying timeline
              </h2>

            </div>


            <span
              className="
                hidden
                text-xs
                text-slate-600
                sm:block
              "
            >
              Latest 10 records
            </span>

          </div>


          <div
            className="
              overflow-hidden
              rounded-3xl
              border
              border-white/10
              bg-white/[0.025]
            "
          >

            <div className="overflow-x-auto">

              <table
                className="
                  w-full
                  min-w-[700px]
                  text-left
                "
              >

                <thead
                  className="
                    border-b
                    border-white/10
                    bg-white/[0.025]
                  "
                >

                  <tr>

                    <th
                      className="
                        px-5
                        py-4
                        text-[10px]
                        uppercase
                        tracking-wider
                        text-slate-600
                      "
                    >
                      Year
                    </th>


                    <th
                      className="
                        px-5
                        py-4
                        text-[10px]
                        uppercase
                        tracking-wider
                        text-slate-600
                      "
                    >
                      Population
                    </th>


                    <th
                      className="
                        px-5
                        py-4
                        text-[10px]
                        uppercase
                        tracking-wider
                        text-slate-600
                      "
                    >
                      Classification
                    </th>


                    <th
                      className="
                        px-5
                        py-4
                        text-[10px]
                        uppercase
                        tracking-wider
                        text-slate-600
                      "
                    >
                      Data status
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {visibleRows.map(
                    (row, index) => {

                      const type =
                        sourceType(row);


                      return (

                        <motion.tr
                          key={row.Year}
                          initial={{
                            opacity: 0,
                          }}
                          animate={{
                            opacity: 1,
                          }}
                          transition={{
                            delay:
                              index *
                              0.035,
                          }}
                          className="
                            border-b
                            border-white/[0.06]
                            transition
                            hover:bg-white/[0.025]
                          "
                        >

                          <td
                            className="
                              px-5
                              py-4
                              text-sm
                              font-semibold
                              text-white
                            "
                          >
                            {row.Year}
                          </td>


                          <td
                            className="
                              px-5
                              py-4
                              text-sm
                              text-slate-300
                            "
                          >
                            {formatPopulation(
                              row.Population,
                            )}
                          </td>


                          <td className="px-5 py-4">

                            <SourceBadge
                              type={type}
                            />

                          </td>


                          <td
                            className="
                              px-5
                              py-4
                              text-xs
                              text-slate-500
                            "
                          >
                            {row.Data_Status ||
                              row.data_status ||
                              "Available"}
                          </td>

                        </motion.tr>

                      );

                    },
                  )}

                </tbody>

              </table>

            </div>

          </div>

        </section>


        {/* ==========================================================
            FUTURE MODULES
        ========================================================== */}

        <section
          id="future"
          className="mt-16 scroll-mt-24"
        >

          <div className="mb-7">

            <p
              className="
                text-[10px]
                font-bold
                uppercase
                tracking-[0.2em]
                text-violet-400
              "
            >
              Expansion roadmap
            </p>


            <h2
              className="
                mt-2
                text-3xl
                font-black
              "
            >
              More intelligence is coming.
            </h2>


            <p
              className="
                mt-2
                max-w-2xl
                text-sm
                leading-6
                text-slate-500
              "
            >
              The current platform focuses exclusively on
              national-level India intelligence. These future
              modules are intentionally locked until their data,
              validation, and modelling architecture are ready.
            </p>

          </div>


          <div
            className="
              grid
              gap-4
              md:grid-cols-3
            "
          >

            <LockedModule
              icon={BarChart3}
              title="State Intelligence"
              description="
                State-level demographic analytics, regional trends,
                and forecasting will be introduced as a separate
                validated intelligence layer.
              "
              examples={[
                "Regional trends",
                "State forecasts",
                "Migration patterns",
              ]}
            />


            <LockedModule
              icon={Globe2}
              title="City Intelligence"
              description="
                A future city-level intelligence module for urban
                population dynamics, growth, and demographic
                transitions.
              "
              examples={[
                "Urban growth",
                "City forecasts",
                "Migration",
              ]}
            />


            <LockedModule
              icon={Users}
              title="Village Intelligence"
              description="
                Hyper-local demographic intelligence designed for
                village-level population and social-demographic
                analysis.
              "
              examples={[
                "Village population",
                "Local trends",
                "Micro analytics",
              ]}
            />

          </div>

        </section>


        {/* ==========================================================
            TRUST LAYER
        ========================================================== */}

        <section
          className="
            mt-16
            rounded-3xl
            border
            border-white/10
            bg-white/[0.025]
            p-7
            sm:p-9
          "
        >

          <div
            className="
              grid
              gap-8
              lg:grid-cols-3
            "
          >

            {/* TRANSPARENT */}

            <div>

              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-cyan-300
                "
              >

                <ShieldCheck size={18} />

                <span
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-wider
                  "
                >
                  Transparent
                </span>

              </div>


              <h3
                className="
                  mt-3
                  text-xl
                  font-bold
                "
              >
                Data classification stays visible.
              </h3>


              <p
                className="
                  mt-2
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                Historical observations, model-estimated values,
                and future ML forecasts are never presented as
                the same thing.
              </p>

            </div>


            {/* ML POWERED */}

            <div>

              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-violet-300
                "
              >

                <Sparkles size={18} />

                <span
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-wider
                  "
                >
                  ML powered
                </span>

              </div>


              <h3
                className="
                  mt-3
                  text-xl
                  font-bold
                "
              >
                The UI reads the existing model.
              </h3>


              <p
                className="
                  mt-2
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                Model metadata and forecast information come
                from the FastAPI layer rather than frontend
                hardcoding.
              </p>

            </div>


            {/* RESEARCH READY */}

            <div>

              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-emerald-300
                "
              >

                <Database size={18} />

                <span
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-wider
                  "
                >
                  Research ready
                </span>

              </div>


              <h3
                className="
                  mt-3
                  text-xl
                  font-bold
                "
              >
                Built for exploration.
              </h3>


              <p
                className="
                  mt-2
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                The interface is being expanded from a predictor
                into a national demographic research platform.
              </p>

            </div>

          </div>

        </section>


        {/* ==========================================================
            FOOTER
        ========================================================== */}

        <footer
          className="
            mt-12
            border-t
            border-white/10
            pt-6
            text-xs
            text-slate-600
          "
        >
          India Population Forecasting System · National Intelligence
          Platform ·{" "}
          {yearRange?.start_year ?? 1960}
          –
          {yearRange?.end_year ?? 2050}
        </footer>

      </main>

    </div>
  );
}