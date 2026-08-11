import axios from "axios";

/*
 * Central API service for the India Population Forecasting System.
 *
 * Frontend responsibilities:
 * - Call the FastAPI backend.
 * - Normalize common API responses.
 * - Provide consistent error handling.
 * - Keep endpoint definitions in one place.
 *
 * Backend responsibilities:
 * - Data loading
 * - ML forecasting
 * - Analytics
 * - Intelligence generation
 * - Data classification
 *
 * IMPORTANT:
 * The frontend never directly reads CSV/model files.
 */

// -----------------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------------

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    Accept: "application/json",
  },
});

// -----------------------------------------------------------------------------
// Error normalization
// -----------------------------------------------------------------------------

function getErrorMessage(error) {
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      return detail
        .map((item) => item?.msg || "Validation error")
        .join(", ");
    }

    return `API request failed with status ${status}.`;
  }

  if (error.request) {
    return (
      "Unable to reach the population forecasting API. " +
      "Make sure the FastAPI backend is running."
    );
  }

  return error.message || "An unexpected API error occurred.";
}

async function request(config) {
  try {
    const response = await api.request(config);
    return response.data;
  } catch (error) {
    const normalizedError = new Error(getErrorMessage(error));

    normalizedError.status = error.response?.status ?? null;
    normalizedError.code = error.code ?? null;
    normalizedError.originalError = error;

    throw normalizedError;
  }
}

// -----------------------------------------------------------------------------
// System / API
// -----------------------------------------------------------------------------

export async function getApiRoot() {
  return request({
    method: "GET",
    url: "/",
  });
}

// -----------------------------------------------------------------------------
// Population
// -----------------------------------------------------------------------------

/**
 * Get historical population data.
 *
 * Backend:
 * GET /api/population/historical
 *
 * Optional:
 * startYear
 * endYear
 */
export async function getHistoricalPopulation(startYear, endYear) {
  const params = {};

  if (Number.isInteger(startYear)) {
    params.start_year = startYear;
  }

  if (Number.isInteger(endYear)) {
    params.end_year = endYear;
  }

  return request({
    method: "GET",
    url: "/api/population/historical",
    params,
  });
}

/**
 * Get ML forecast data.
 *
 * Backend:
 * GET /api/population/forecast
 *
 * Optional:
 * startYear
 * endYear
 */
export async function getForecastPopulation(startYear, endYear) {
  const params = {};

  if (Number.isInteger(startYear)) {
    params.start_year = startYear;
  }

  if (Number.isInteger(endYear)) {
    params.end_year = endYear;
  }

  return request({
    method: "GET",
    url: "/api/population/forecast",
    params,
  });
}

/**
 * Get unified population intelligence data.
 *
 * Useful for:
 * - Timeline
 * - Dashboard charts
 * - Historical/estimated/forecast comparison
 */
export async function getUnifiedPopulation(startYear, endYear) {
  const params = {};

  if (Number.isInteger(startYear)) {
    params.start_year = startYear;
  }

  if (Number.isInteger(endYear)) {
    params.end_year = endYear;
  }

  return request({
    method: "GET",
    url: "/api/intelligence/population",
    params,
  });
}

/**
 * Get information for one specific year.
 */
export async function getPopulationYear(year) {
  if (!Number.isInteger(year)) {
    throw new Error("Year must be an integer.");
  }

  return request({
    method: "GET",
    url: `/api/population/year/${year}`,
  });
}

// -----------------------------------------------------------------------------
// Intelligence
// -----------------------------------------------------------------------------

/**
 * Get intelligence for one specific year.
 */
export async function getYearIntelligence(year) {
  if (!Number.isInteger(year)) {
    throw new Error("Year must be an integer.");
  }

  return request({
    method: "GET",
    url: `/api/intelligence/year/${year}`,
  });
}

/**
 * Get complete intelligence report.
 */
export async function getIntelligenceReport() {
  return request({
    method: "GET",
    url: "/api/intelligence/report",
  });
}

// -----------------------------------------------------------------------------
// Analytics
// -----------------------------------------------------------------------------

/**
 * Get population growth analysis.
 */
export async function getGrowthAnalysis() {
  return request({
    method: "GET",
    url: "/api/analytics/growth",
  });
}

/**
 * Get population analytics.
 */
export async function getPopulationAnalytics() {
  return request({
    method: "GET",
    url: "/api/analytics/population",
  });
}

// -----------------------------------------------------------------------------
// Research
// -----------------------------------------------------------------------------

/**
 * Get configured research-period analysis.
 *
 * Expected periods include:
 * - 10-Year
 * - 20-Year
 * - 25-Year
 * - 50-Year
 * - 100-Year
 */
export async function getResearchPeriods() {
  return request({
    method: "GET",
    url: "/api/research/periods",
  });
}

/**
 * Get research insights.
 */
export async function getResearchInsights() {
  return request({
    method: "GET",
    url: "/api/research/insights",
  });
}

/**
 * Get complete research report.
 */
export async function getResearchReport() {
  return request({
    method: "GET",
    url: "/api/research/report",
  });
}

// -----------------------------------------------------------------------------
// Milestones
// -----------------------------------------------------------------------------

/**
 * Get detected population milestones.
 */
export async function getMilestones() {
  return request({
    method: "GET",
    url: "/api/milestones",
  });
}

/**
 * Get future milestones.
 */
export async function getFutureMilestones() {
  return request({
    method: "GET",
    url: "/api/milestones/future",
  });
}

// -----------------------------------------------------------------------------
// Data transparency
// -----------------------------------------------------------------------------

/**
 * Get backend data-status information.
 */
export async function getDataStatus() {
  return request({
    method: "GET",
    url: "/api/data/status",
  });
}

/**
 * Get model metadata.
 *
 * Includes:
 * - model existence
 * - selected model
 * - feature metadata
 * - prediction horizon
 */
export async function getModelInfo() {
  return request({
    method: "GET",
    url: "/api/model/info",
  });
}

/**
 * Get the dedicated dashboard chart dataset.
 */
export async function getDashboardChart() {
  return request({
    method: "GET",
    url: "/api/dashboard/chart",
  });
}

/**
 * Get overall available year range.
 */
export async function getYearRange() {
  return request({
    method: "GET",
    url: "/api/year-range",
  });
}

// -----------------------------------------------------------------------------
// Search
// -----------------------------------------------------------------------------

/**
 * Search for a specific year.
 *
 * Backend:
 * GET /api/search?year={year}
 *
 * Returns:
 * - year
 * - population
 * - source_type
 * - data_status
 * - intelligence
 */
export async function searchYear(year) {
  if (!Number.isInteger(year)) {
    throw new Error("Year must be an integer.");
  }

  return request({
    method: "GET",
    url: "/api/search",
    params: {
      year,
    },
  });
}

// -----------------------------------------------------------------------------
// Development / future admin preparation
// -----------------------------------------------------------------------------

/**
 * Reload already-existing backend pipeline outputs.
 *
 * IMPORTANT:
 * This does not modify source datasets or model artifacts.
 *
 * This function should NOT be exposed as a normal public UI action.
 * It exists here for controlled development/admin integration later.
 */
export async function reloadBackendData() {
  return request({
    method: "POST",
    url: "/api/system/reload",
  });
}

// -----------------------------------------------------------------------------
// Convenience object
// -----------------------------------------------------------------------------

const populationApi = {
  getApiRoot,

  getHistoricalPopulation,
  getForecastPopulation,
  getUnifiedPopulation,
  getPopulationYear,

  getYearIntelligence,
  getIntelligenceReport,

  getGrowthAnalysis,
  getPopulationAnalytics,

  getResearchPeriods,
  getResearchInsights,
  getResearchReport,

  getMilestones,
  getFutureMilestones,

  getDataStatus,
  getModelInfo,
  getDashboardChart,
  getYearRange,

  searchYear,

  reloadBackendData,
};

export default populationApi;