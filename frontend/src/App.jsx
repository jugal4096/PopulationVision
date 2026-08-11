import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import ForecastLab from "./pages/ForecastLab";
import ResearchLab from "./pages/ResearchLab";
import DataModel from "./pages/DataModel";
import YearIntelligence from "./pages/YearIntelligence";

import Intro from "./pages/Intro";
import ScopeSelector from "./pages/ScopeSelector";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ============================================================
            MAIN APPLICATION
        ============================================================ */}

        <Route path="/" element={<Home />} />

        {/* ============================================================
            FORECAST LABORATORY
        ============================================================ */}

        <Route path="/forecast" element={<ForecastLab />} />

        {/* ============================================================
            RESEARCH LABORATORY
        ============================================================ */}

        <Route path="/research" element={<ResearchLab />} />

        {/* ============================================================
            DATA & MODEL OBSERVATORY
        ============================================================ */}

        <Route path="/about" element={<DataModel />} />

        {/* ============================================================
            YEAR INTELLIGENCE
        ============================================================ */}

        <Route
          path="/national/year/:year"
          element={<YearIntelligence />}
        />

        {/* ============================================================
            EXISTING INTRO / SCOPE ROUTES
        ============================================================ */}

        <Route path="/intro" element={<Intro />} />

        <Route path="/scope" element={<ScopeSelector />} />

        {/* ============================================================
            COMPATIBILITY ROUTES
        ============================================================ */}

        <Route
          path="/predict"
          element={<Navigate to="/forecast" replace />}
        />

        <Route
          path="/analytics"
          element={<Navigate to="/research" replace />}
        />

        {/* ============================================================
            FALLBACK
        ============================================================ */}

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}