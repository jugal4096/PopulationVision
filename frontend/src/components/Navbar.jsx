import { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  BarChart3,
  BrainCircuit,
  Database,
  Menu,
  Search,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const links = [
  {
    name: "Command Center",
    path: "/",
    icon: BrainCircuit,
  },
  {
    name: "Forecast Lab",
    path: "/forecast",
    icon: BarChart3,
  },
  {
    name: "Research Lab",
    path: "/research",
    icon: Search,
  },
  {
    name: "Data & Model",
    path: "/data-model",
    icon: Database,
  },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-slate-950/85 backdrop-blur-xl"
    >
      <div className="mx-auto flex h-[72px] max-w-[1500px] items-center justify-between px-5 sm:px-8">

        {/* Brand */}
        <NavLink
          to="/"
          onClick={() => setOpen(false)}
          className="flex items-center gap-3"
        >
          <motion.div
            whileHover={{ scale: 1.05, rotate: 2 }}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300"
          >
            <BrainCircuit size={22} />
          </motion.div>

          <div className="hidden sm:block">
            <div className="text-[15px] font-bold tracking-wide text-white">
              PopulationVision
              <span className="ml-1 text-cyan-400">AI</span>
            </div>

            <div className="text-[10px] uppercase tracking-[0.16em] text-slate-500">
              Demographic Intelligence
            </div>
          </div>
        </NavLink>

        {/* Desktop navigation */}
        <nav className="hidden items-center gap-1 lg:flex">
          {links.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-cyan-400/10 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.08)]"
                      : "text-slate-400 hover:bg-white/5 hover:text-white",
                  ].join(" ")
                }
              >
                <Icon size={16} />
                {item.name}
              </NavLink>
            );
          })}
        </nav>

        {/* API status */}
        <div className="hidden items-center gap-3 md:flex">
          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>

            <span className="text-[11px] font-medium text-emerald-300">
              Intelligence API
            </span>
          </div>
        </div>

        {/* Mobile menu */}
        <button
          type="button"
          aria-label={open ? "Close navigation" : "Open navigation"}
          onClick={() => setOpen((current) => !current)}
          className="rounded-lg border border-white/10 p-2 text-slate-300 transition hover:bg-white/5 hover:text-white lg:hidden"
        >
          {open ? <X size={21} /> : <Menu size={21} />}
        </button>
      </div>

      {/* Mobile navigation */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-white/10 bg-slate-950 lg:hidden"
          >
            <nav className="mx-auto max-w-[1500px] px-5 py-3 sm:px-8">
              {links.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      [
                        "flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium",
                        isActive
                          ? "bg-cyan-400/10 text-cyan-300"
                          : "text-slate-400 hover:bg-white/5 hover:text-white",
                      ].join(" ")
                    }
                  >
                    <Icon size={17} />
                    {item.name}
                  </NavLink>
                );
              })}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}