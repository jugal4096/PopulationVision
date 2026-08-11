import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Menu, X, BrainCircuit } from "lucide-react";
import { motion } from "framer-motion";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  const links = [
    { name: "Home", path: "/" },
    { name: "Prediction", path: "/predict" },
    { name: "Analytics", path: "/analytics" },
    { name: "About", path: "/about" },
  ];

  return (
    <motion.header
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-xl"
    >
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 p-3 shadow-lg">
            <BrainCircuit className="text-white" size={28} />
          </div>

          <div>
            <h1 className="text-xl font-bold text-slate-800">
              PopulationVision AI
            </h1>
            <p className="text-xs text-slate-500">
              Intelligent Demographic Forecasting
            </p>
          </div>
        </div>

        <nav className="hidden items-center gap-10 md:flex">
          {links.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `font-medium transition ${
                  isActive
                    ? "text-indigo-600"
                    : "text-slate-700 hover:text-indigo-600"
                }`
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>

        <button className="hidden rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-3 font-semibold text-white shadow-lg transition hover:scale-105 md:block">
          Predict Now
        </button>

        <button
          onClick={() => setOpen(!open)}
          className="md:hidden"
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>

      {open && (
        <div className="border-t bg-white md:hidden">
          {links.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={() => setOpen(false)}
              className="block px-6 py-4 hover:bg-slate-100"
            >
              {item.name}
            </NavLink>
          ))}
        </div>
      )}
    </motion.header>
  );
}